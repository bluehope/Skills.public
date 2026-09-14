#!/usr/bin/env python3
"""Validate canonical and optionally installed scientific-figure routes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def skill_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*([^\s]+)\s*$", text, flags=re.MULTILINE)
    if not match:
        raise AssertionError(f"missing skill name: {path}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--allow-missing", action="append", default=[], help="explicit optional sibling omitted from this distribution")
    args = parser.parse_args()
    data = json.loads((ROOT / "references/capability-map.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["umbrella"] == "scientific-figure-making"
    ids: set[str] = set()
    skills: set[str] = set()
    allowed = {"ACTIVE", "EXPERIMENTAL", "TEMPORARY"}
    for item in data["capabilities"]:
        assert item["id"] not in ids
        assert item["skill"] not in skills
        assert item["maturity"] in allowed
        ids.add(item["id"])
        skills.add(item["skill"])
        canonical = (ROOT / item["canonical"]).resolve()
        if not canonical.is_file():
            canonical = ROOT.parent / item["installed"]
        if not canonical.is_file() and item["skill"] in args.allow_missing:
            print("UNAVAILABLE optional sibling:", item["skill"])
            continue
        assert canonical.is_file(), canonical
        assert skill_name(canonical) == item["skill"]
        if args.installed_root:
            installed = args.installed_root.expanduser().resolve() / item["installed"]
            assert installed.is_file(), installed
            assert skill_name(installed) == item["skill"]
    print(f"scientific figure routing smoke test: PASS ({len(ids)} capabilities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
