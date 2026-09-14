#!/usr/bin/env python3
"""Known-answer checks for validate_stage_script.py."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_stage_script.py"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        good = root / "good.sbatch"
        good.write_text("""#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo \"FAIL line=$LINENO cmd=$BASH_COMMAND rc=$rc\" >&2; exit $rc' ERR
exec >stage.log 2>&1
test \"$nw\" -eq \"$expected\" || { echo \"WFC_COUNT_MISMATCH\" >&2; exit 3; }
if test ! -e \"$dst\"; then ln -s \"$src\" \"$dst\"; fi
mkdir -p receipt
""", encoding="utf-8")
        passed = run(good)
        assert passed.returncode == 0, passed.stderr
        assert "STAGE_SCRIPT_PASS" in passed.stderr

        bad = root / "bad.sbatch"
        bad.write_text("""#!/usr/bin/env bash
set -e
test -e \"$src\" && ln -s \"$src\" \"$dst\"
test \"$nw\" -eq \"$expected\"
""", encoding="utf-8")
        blocked = run(bad)
        assert blocked.returncode == 2, blocked.stderr
        assert "E001" in blocked.stderr and "W002" in blocked.stderr and "W003" in blocked.stderr
    print("validate_stage_script test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
