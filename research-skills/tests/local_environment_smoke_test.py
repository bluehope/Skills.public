#!/usr/bin/env python3
"""Known-answer smoke test for redacted environment snapshots and comparison."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "capture_local_environment.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary) / "project"
        project.mkdir()
        baseline = Path(temporary) / "baseline.json"
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(project), "--output", str(baseline)],
            check=True,
            capture_output=True,
            text=True,
        )
        first = json.loads(completed.stdout)
        assert baseline.is_file()
        assert len(first["fingerprint_sha256"]) == 64
        assert "PATH" not in first["environment_controls"]
        assert "items" not in first["packages"]

        compared = subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(project), "--compare", str(baseline)],
            check=True,
            capture_output=True,
            text=True,
        )
        second = json.loads(compared.stdout)
        assert second["comparison"]["match"] is True
        assert second["comparison"]["change_count"] == 0

    print("local environment tracking smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
