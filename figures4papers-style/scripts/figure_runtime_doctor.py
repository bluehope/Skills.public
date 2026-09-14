#!/usr/bin/env python3
"""Stable specialist entrypoint; implementation remains owned by scientific-figure-making."""
from pathlib import Path
import runpy
import sys


def main():
    # Both grouped canonical trees and flat copy-only installs have sibling owners.
    owner = Path(__file__).resolve().parents[2] / "scientific-figure-making" / "scripts" / "figure_runtime_doctor.py"
    if not owner.is_file():
        print("UNAVAILABLE: required sibling scientific-figure-making/scripts/figure_runtime_doctor.py; "
              "restore that registered dependency, do not substitute a parser.", file=sys.stderr)
        return 2
    runpy.run_path(str(owner), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
