#!/usr/bin/env python3
"""Initialize a non-destructive project-local workspace for optional ado use."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "ado-project-template"
DIRECTORIES = (
    "configs/actuators",
    "configs/operations",
    "configs/samplestores",
    "configs/spaces",
    "imports",
    "exports",
    "receipts",
)


def default_project_name(project_root: Path) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", project_root.name.lower()).strip("-_")
    return slug or "ado-project"


def yaml_scalar(value: str | None) -> str:
    return "null" if value is None else json.dumps(value, ensure_ascii=False)


def render(template: str, replacements: dict[str, str]) -> str:
    for key, value in replacements.items():
        template = template.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"{{[A-Z0-9_]+}}", template)))
    if unresolved:
        raise ValueError(f"Unresolved template fields: {', '.join(unresolved)}")
    return template


def write_if_missing(path: Path, content: str) -> str:
    if path.exists():
        return "kept"
    path.write_text(content, encoding="utf-8")
    return "created"


def initialize(
    project_root: Path,
    mode: str,
    ado_project: str | None,
    context_name: str | None,
) -> list[tuple[str, Path]]:
    project_root = project_root.expanduser().resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root is not a directory: {project_root}")

    ado_project = ado_project.strip() if ado_project else default_project_name(project_root)
    if not ado_project or any(char in ado_project for char in "\r\n/\\"):
        raise ValueError("ado project name must be non-empty and cannot contain a path separator")

    context_name = context_name.strip() if context_name else None
    if context_name is not None and (
        not context_name or any(char in context_name for char in "\r\n/\\")
    ):
        raise ValueError("context name must be non-empty and cannot contain a path separator")

    recommended_backend = "mysql" if mode == "shared" else "sqlite"
    created_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    replacements = {
        "MODE": mode,
        "MODE_YAML": yaml_scalar(mode),
        "ADO_PROJECT": ado_project,
        "ADO_PROJECT_YAML": yaml_scalar(ado_project),
        "CONTEXT_NAME_DISPLAY": context_name or "not configured",
        "CONTEXT_NAME_YAML": yaml_scalar(context_name),
        "CREATED_AT_UTC": created_at,
        "CREATED_AT_UTC_YAML": yaml_scalar(created_at),
        "RECOMMENDED_BACKEND_YAML": yaml_scalar(recommended_backend),
    }

    ado_root = project_root / "ado"
    ado_root.mkdir(exist_ok=True)
    actions: list[tuple[str, Path]] = [("ready", ado_root)]
    for relative in DIRECTORIES:
        directory = ado_root / relative
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        actions.append(("kept" if existed else "created", directory))

    templated_files = {
        "ADO.md.tmpl": ado_root / "ADO.md",
        "ado-project.yaml.tmpl": ado_root / "ado-project.yaml",
        "gitignore.tmpl": ado_root / ".gitignore",
    }
    for template_name, destination in templated_files.items():
        template = (TEMPLATE_ROOT / template_name).read_text(encoding="utf-8")
        actions.append((write_if_missing(destination, render(template, replacements)), destination))

    receipt_template = (TEMPLATE_ROOT / "RECEIPT-TEMPLATE.yaml").read_text(
        encoding="utf-8"
    )
    receipt_destination = ado_root / "receipts" / "RECEIPT-TEMPLATE.yaml"
    actions.append((write_if_missing(receipt_destination, receipt_template), receipt_destination))
    return actions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create missing files for an optional project-local ado workspace."
    )
    parser.add_argument("project_root", type=Path)
    parser.add_argument(
        "--mode",
        choices=("catalog", "local-active", "shared"),
        default="catalog",
    )
    parser.add_argument("--ado-project")
    parser.add_argument("--context-name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        actions = initialize(
            project_root=args.project_root,
            mode=args.mode,
            ado_project=args.ado_project,
            context_name=args.context_name,
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    for action, path in actions:
        print(f"{action:7} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
