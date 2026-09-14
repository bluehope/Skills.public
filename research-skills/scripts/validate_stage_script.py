#!/usr/bin/env python3
"""Fail-closed static preflight for short Bash/Sbatch stage wrappers.

This is intentionally a small heuristic checker, not a Bash parser. It blocks
the one silent-failure pattern that has recurred in research-stage wrappers:
``set -e`` without an ERR trap that prints both the failing line and command.
It also reports review warnings for conditional lists, late log redirection,
opaque hard gates, and non-idempotent link/directory creation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    line: int
    message: str


SET_E = re.compile(r"\bset\s+-[A-Za-z]*e[A-Za-z]*\b|\bset\s+-o\s+errexit\b")
ERR_TRAP = re.compile(r"\btrap\b.*\bERR\b")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(?:[^=].*)?$")
HARD_GATE = re.compile(r"\btest\b[^\n]*(?:-eq|-ne|-gt|-ge|-lt|-le)\b|\bgrep\s+-q\b")


def active(line: str) -> str:
    """Return the non-comment portion sufficient for conservative heuristics."""
    return line.split("#", 1)[0].strip()


def has_visible_err_trap(text: str) -> bool:
    return bool(ERR_TRAP.search(text) and "LINENO" in text and "BASH_COMMAND" in text)


def is_prologue(command: str) -> bool:
    return (
        not command
        or command.startswith("#!")
        or SET_E.search(command) is not None
        or command.startswith("trap ")
        or command.startswith("umask ")
        or ASSIGNMENT.fullmatch(command) is not None
    )


def validate(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: list[Finding] = []
    if SET_E.search(text) and not has_visible_err_trap(text):
        findings.append(Finding(
            "BLOCK", "E001", 0,
            "set -e/errexit requires an ERR trap that prints $LINENO and $BASH_COMMAND.",
        ))

    first_exec_log: int | None = None
    for number, original in enumerate(lines, start=1):
        command = active(original)
        if re.match(r"^exec\s+.*(?:>|&>)", command):
            first_exec_log = number
            break
    if first_exec_log is not None:
        prelog = [
            (number, active(original))
            for number, original in enumerate(lines[: first_exec_log - 1], start=1)
            if not is_prologue(active(original))
        ]
        if prelog:
            findings.append(Finding(
                "WARN", "W001", prelog[0][0],
                "command executes before process-wide log redirection; capture its stderr explicitly or move exec earlier.",
            ))

    for number, original in enumerate(lines, start=1):
        command = active(original)
        if not command:
            continue
        if "&&" in command and not command.startswith("if ") and "||" not in command:
            findings.append(Finding(
                "WARN", "W002", number,
                "&& conditional list under errexit can terminate the wrapper when its condition is false; use if/then or an explicit fallback.",
            ))
        if HARD_GATE.search(command) and not command.startswith("if ") and "||" not in command:
            findings.append(Finding(
                "WARN", "W003", number,
                "hard gate has no visible failure message; use `|| { echo ... >&2; exit N; }` or an if/else diagnostic.",
            ))
        if re.search(r"\bmkdir\s+(?!-p(?:\s|$))", command):
            findings.append(Finding(
                "WARN", "W004", number,
                "mkdir lacks -p; repeated submissions may fail before the scientific gate.",
            ))
        if re.search(r"\bln\s+-s(?:\s|$)", command) and "-sf" not in command:
            context = "\n".join(active(item) for item in lines[max(0, number - 3):number])
            if not re.search(r"(?:test|\[)\s*!\s*-e", context):
                findings.append(Finding(
                    "WARN", "W005", number,
                    "ln -s lacks a nearby no-clobber/idempotency guard; use `if test ! -e ...; then ln -s ...; fi`.",
                ))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--warnings-as-errors", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--shellcheck", action="store_true", help="Run shellcheck too when installed.")
    args = parser.parse_args()

    if not args.script.is_file():
        parser.error(f"not a regular file: {args.script}")
    syntax = subprocess.run(["bash", "-n", str(args.script)], text=True, capture_output=True)
    findings = validate(args.script)
    if syntax.returncode:
        findings.append(Finding("BLOCK", "E000", 0, f"bash -n: {syntax.stderr.strip()}"))
    if args.shellcheck:
        executable = shutil.which("shellcheck")
        if executable is None:
            findings.append(Finding("WARN", "W000", 0, "shellcheck requested but is not installed."))
        else:
            checked = subprocess.run([executable, str(args.script)], text=True, capture_output=True)
            if checked.returncode:
                findings.append(Finding("WARN", "W006", 0, f"shellcheck: {checked.stdout.strip()}"))

    blocked = any(item.severity == "BLOCK" for item in findings)
    warnings = any(item.severity == "WARN" for item in findings)
    if args.as_json:
        print(json.dumps({"script": str(args.script), "findings": [asdict(item) for item in findings]}, indent=2))
    else:
        for item in findings:
            location = f":{item.line}" if item.line else ""
            print(f"{item.severity} {item.code} {args.script}{location}: {item.message}", file=sys.stderr)
        print("STAGE_SCRIPT_PASS" if not findings else "STAGE_SCRIPT_REVIEW", file=sys.stderr)
    return 2 if blocked or (args.warnings_as_errors and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
