#!/usr/bin/env python3
"""Smoke-test the research-skills/local-search integration without mutating QMD."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "setup_local_search.py"


def main() -> int:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--skill-root", str(ROOT), "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "DRY_RUN"
    assert payload["collection"] == "research-skills"
    assert payload["index"] == "research-skills"
    assert payload["include_count"] == len(json.loads((ROOT / "local_search_policy.json").read_text())["include"]) >= 3
    assert Path(payload["local_search_root"]).is_dir()
    print("research local-search integration smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
