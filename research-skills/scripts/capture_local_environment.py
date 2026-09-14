#!/usr/bin/env python3
"""Capture and compare a redacted, reproducible local research environment."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any


TOOLS = ("git", "rg", "rga", "qmd", "node", "npm", "pdftotext", "pandoc", "nvidia-smi")
CORE_PACKAGES = (
    "numpy",
    "scipy",
    "pandas",
    "polars",
    "scikit-learn",
    "xgboost",
    "torch",
    "tensorflow",
    "jax",
    "ase",
    "pymatgen",
    "mace-torch",
)
ENV_ALLOWLIST = (
    "CONDA_DEFAULT_ENV",
    "CUDA_VISIBLE_DEVICES",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "QMD_FORCE_CPU",
)


def sanitize_path(value: str | None, project_root: Path) -> str | None:
    if not value:
        return None
    path = str(Path(value).resolve())
    replacements = ((str(project_root), "$PROJECT"), (str(Path.home()), "~"))
    for prefix, token in replacements:
        if path.lower().startswith(prefix.lower()):
            return token + path[len(prefix) :].replace("\\", "/")
    return Path(path).name


def run(command: list[str], cwd: Path, timeout: int = 20) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except Exception as exc:
        return 127, f"unavailable: {type(exc).__name__}"
    output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    return completed.returncode, output


def first_line(value: str) -> str | None:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return lines[0] if lines else None


def tool_versions(project_root: Path) -> dict[str, dict[str, str | None]]:
    records: dict[str, dict[str, str | None]] = {}
    for name in TOOLS:
        executable = shutil.which(name)
        if not executable:
            records[name] = {"status": "missing", "version": None}
            continue
        flag = "-v" if name in {"node", "pdftotext"} else "--version"
        code, output = run([executable, flag], project_root)
        records[name] = {
            "status": "ok" if code == 0 else "unusable",
            "version": first_line(output),
        }
    return records


def package_inventory(include_packages: bool) -> dict[str, Any]:
    packages = sorted(
        ({"name": dist.metadata["Name"].lower(), "version": dist.version} for dist in importlib.metadata.distributions()),
        key=lambda row: (row["name"], row["version"]),
    )
    encoded = json.dumps(packages, sort_keys=True, separators=(",", ":")).encode()
    by_name = {row["name"]: row["version"] for row in packages}
    record: dict[str, Any] = {
        "count": len(packages),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "core": {name: by_name.get(name) for name in CORE_PACKAGES},
    }
    if include_packages:
        record["items"] = packages
    return record


def git_state(project_root: Path) -> dict[str, Any]:
    code, root = run(["git", "rev-parse", "--show-toplevel"], project_root)
    if code != 0:
        return {"repository": False, "commit": None, "dirty": None}
    code, commit = run(["git", "rev-parse", "HEAD"], project_root)
    status_code, status = run(["git", "status", "--porcelain"], project_root)
    return {
        "repository": True,
        "root": sanitize_path(first_line(root), project_root),
        "commit": first_line(commit) if code == 0 else None,
        "dirty": bool(status) if status_code == 0 else None,
    }


def gpu_state(project_root: Path) -> list[dict[str, str]]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return []
    code, output = run(
        [
            executable,
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader,nounits",
        ],
        project_root,
    )
    if code != 0:
        return []
    rows = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) == 3:
            rows.append({"name": parts[0], "driver": parts[1], "memory_mib": parts[2]})
    return rows


def fingerprint_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in snapshot.items()
        if key not in {"captured_at_utc", "fingerprint_sha256", "comparison"}
    }


def fingerprint(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(fingerprint_payload(snapshot), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in sorted(value.items()):
            child = f"{prefix}.{key}" if prefix else key
            output.update(flatten(item, child))
        return output
    return {prefix: value}


def compare(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_flat = flatten(fingerprint_payload(current))
    baseline_flat = flatten(fingerprint_payload(baseline))
    changes = []
    for key in sorted(set(current_flat) | set(baseline_flat)):
        before = baseline_flat.get(key)
        after = current_flat.get(key)
        if before != after:
            changes.append({"field": key, "before": before, "after": after})
    return {
        "baseline_fingerprint": baseline.get("fingerprint_sha256"),
        "match": not changes,
        "change_count": len(changes),
        "changes": changes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output")
    parser.add_argument("--compare")
    parser.add_argument("--include-packages", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        raise SystemExit(f"project root not found: {project_root}")

    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "system": {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": sanitize_path(sys.executable, project_root),
            "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
            "conda_prefix": sanitize_path(os.environ.get("CONDA_PREFIX"), project_root),
            "virtual_env": sanitize_path(os.environ.get("VIRTUAL_ENV"), project_root),
        },
        "environment_controls": {key: os.environ.get(key) for key in ENV_ALLOWLIST},
        "packages": package_inventory(args.include_packages),
        "tools": tool_versions(project_root),
        "gpus": gpu_state(project_root),
        "project": git_state(project_root),
    }
    snapshot["fingerprint_sha256"] = fingerprint(snapshot)

    if args.compare:
        baseline_path = Path(args.compare).resolve()
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        snapshot["comparison"] = compare(snapshot, baseline)

    payload = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
