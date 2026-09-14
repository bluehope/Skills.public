#!/usr/bin/env python3
"""Build a disposable research-skills corpus and a dedicated QMD index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def find_local_search(explicit: str | None, skill_root: Path) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            skill_root.parent / "local-search",
            Path.home() / ".codex" / "skills" / "local-search",
        ]
    )
    for candidate in candidates:
        script = candidate.resolve() / "scripts" / "local_search_tools.py"
        if script.is_file():
            return candidate.resolve()
    raise SystemExit("local-search skill not found; pass --local-search-root")


def run(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}{completed.stderr}"
        )
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--local-search-root")
    parser.add_argument("--stage-dir", default=str(Path.home() / ".cache" / "local-search" / "research-skills-corpus"))
    parser.add_argument("--index", default="research-skills")
    parser.add_argument("--collection", default="research-skills")
    parser.add_argument("--embed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    policy = skill_root / "local_search_policy.json"
    if not policy.is_file():
        raise SystemExit(f"policy not found: {policy}")
    policy_data = json.loads(policy.read_text(encoding="utf-8"))
    local_search = find_local_search(args.local_search_root, skill_root)
    helper = local_search / "scripts" / "local_search_tools.py"
    stage_dir = Path(args.stage_dir).resolve()
    qmd = shutil.which("qmd")

    plan = {
        "skill_root": str(skill_root),
        "policy": str(policy),
        "local_search_root": str(local_search),
        "stage_dir": str(stage_dir),
        "index": args.index,
        "collection": args.collection,
        "qmd_available": bool(qmd),
        "embed": args.embed,
        "include_count": len(policy_data.get("include", [])),
    }
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", **plan}, indent=2))
        return 0
    if not qmd:
        raise SystemExit("qmd not found; exact local-search remains available")

    run(
        [sys.executable, str(helper), "stage-policy", str(policy), str(stage_dir), "--replace"],
        args.timeout,
    )
    prefix = [qmd, "--index", args.index]
    shown = subprocess.run(
        [*prefix, "collection", "show", args.collection],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=args.timeout,
    )
    if shown.returncode != 0:
        run([*prefix, "collection", "add", str(stage_dir), "--name", args.collection, "--mask", "**/*.md"], args.timeout)
    context = str(policy_data.get("context", "Search hits are locators, not evidence."))
    subprocess.run(
        [*prefix, "context", "rm", f"qmd://{args.collection}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=args.timeout,
    )
    run([*prefix, "context", "add", f"qmd://{args.collection}", context], args.timeout)
    run([*prefix, "update"], args.timeout)
    if args.embed:
        run([*prefix, "embed", "-c", args.collection], args.timeout)

    status = run([*prefix, "status"], args.timeout)
    print(json.dumps({"status": "OK", **plan}, indent=2))
    print(status.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
