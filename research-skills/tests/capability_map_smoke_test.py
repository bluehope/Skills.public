#!/usr/bin/env python3
"""Verify that the capability map resolves every bundled helper and test."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "references" / "capability-code-map.md"


def resolve_bundled_path(value: str) -> Path:
    """Resolve canonical nested children and flattened runtime siblings."""
    local = ROOT / value
    if local.exists():
        return local
    if value.startswith(NESTED_CHILD + "/"):
        return ROOT.parent / value
    return local


def main() -> int:
    text = MAP.read_text(encoding="utf-8")
    mapped_scripts: set[str] = set()
    mapped_tests: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "`scripts/" in line or "/scripts/" in line:
            assert "/tests/" in line or "`tests/" in line, "missing capability test: " + line
        for value in re.findall(r"`([^`]+)`", line):
            if "/scripts/" in f"/{value}":
                mapped_scripts.add(value)
            if "/tests/" in f"/{value}":
                mapped_tests.add(value)
            if value.startswith(("scripts/", "references/", "assets/", "tests/")):
                assert resolve_bundled_path(value).exists(), value

    actual_scripts = {str(path.relative_to(ROOT)) for path in ROOT.glob("**/scripts/*.py")}
    child = ROOT / NESTED_CHILD
    if not child.exists():
        child = ROOT.parent / NESTED_CHILD
    if child.exists():
        actual_scripts.update(
            f"{NESTED_CHILD}/{path.relative_to(child)}"
            for path in child.glob("scripts/*.py")
        )
    assert mapped_scripts == actual_scripts, (mapped_scripts, actual_scripts)
    assert mapped_tests, "every executable capability needs test coverage; shared integration tests are allowed"
    print("capability map smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
