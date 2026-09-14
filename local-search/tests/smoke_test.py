#!/usr/bin/env python3
"""Smoke tests for project-policy generation and deterministic corpus staging."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "local_search_tools.py"
TGREP_INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install_tgrep_userspace.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def run_tgrep_installer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TGREP_INSTALLER), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> int:
    capabilities = run("qmd-capabilities", check=False)
    qmd = json.loads(capabilities.stdout)
    assert qmd["status"] in {"OK", "MISSING", "UNUSABLE"}
    if qmd["status"] == "OK":
        assert qmd["capabilities"]["bounded_get"]
        assert qmd["capabilities"]["batch_get"]
        assert qmd["capabilities"]["structured_query"]
        assert qmd["capabilities"]["score_explain"]

    doctor = run("doctor", "--json")
    doctor_records = json.loads(doctor.stdout)
    qmd_doctor = next(row for row in doctor_records if row["tool"] == "qmd-capabilities")
    assert qmd_doctor["status"] == qmd["status"]
    tgrep_doctor = next(row for row in doctor_records if row["tool"] == "tgrep")
    assert tgrep_doctor["status"] in {"OK", "MISSING"}
    if tgrep_doctor["status"] == "OK":
        tgrep_smoke = run("tgrep-smoke")
        assert json.loads(tgrep_smoke.stdout)["status"] == "PASS"

    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        release_fixture = base / "tgrep-release.json"
        release_fixture.write_text(
            json.dumps(
                {
                    "tag_name": "v9.8.7",
                    "published_at": "2099-01-02T03:04:05Z",
                    "html_url": "https://example.invalid/tgrep/v9.8.7",
                    "assets": [
                        {
                            "name": f"tgrep-v9.8.7-{target}{suffix}",
                            "browser_download_url": "https://example.invalid/binary",
                        }
                        for target, suffix in (
                            ("aarch64-apple-darwin", ".tar.gz"),
                            ("x86_64-apple-darwin", ".tar.gz"),
                            ("aarch64-unknown-linux-musl", ".tar.gz"),
                            ("x86_64-unknown-linux-musl", ".tar.gz"),
                            ("aarch64-pc-windows-msvc", ".zip"),
                            ("x86_64-pc-windows-msvc", ".zip"),
                        )
                    ]
                    + [
                        {
                            "name": "checksums.txt",
                            "browser_download_url": "https://example.invalid/checksums",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        release_check = run_tgrep_installer(
            "--check",
            "--metadata-file",
            str(release_fixture),
            "--installed-version",
            "tgrep 1.0.4",
        )
        release = json.loads(release_check.stdout)
        assert release["latest"]["version"] == "9.8.7"
        assert release["update_available"] is True
        assert release["mutation"] == "none"

        project = base / "example-project"
        (project / "docs").mkdir(parents=True)
        (project / "docs" / "generated").mkdir()
        (project / "generated").mkdir()
        (project / "README.md").write_text("# Project\n", encoding="utf-8")
        (project / "docs" / "source.md").write_text("canonical evidence\n", encoding="utf-8")
        (project / "docs" / "generated" / "nested.md").write_text(
            "nested derivative\n", encoding="utf-8"
        )
        (project / "generated" / "note.md").write_text("derivative\n", encoding="utf-8")

        policy = project / "local_search_policy.json"
        run(
            "init-policy",
            str(project),
            "--name",
            "Example Corpus",
            "--output",
            str(policy),
        )
        payload = json.loads(policy.read_text(encoding="utf-8"))
        assert payload["collection_name"] == "example-corpus"
        assert payload["qmd"] == {
            "recommended": True,
            "required": False,
            "index_location": "per-machine",
            "activate_when": [
                "ranked retrieval is repeatedly useful",
                "the correct file is often unknown",
                "cross-language or semantic retrieval matters",
            ],
        }
        assert payload["tgrep"]["required"] is False
        assert payload["tgrep"]["index_location"] == "per-machine-outside-project"

        staged = base / "staged-corpus"
        run("stage-policy", str(policy), str(staged))
        assert (staged / "README.md").is_file()
        assert (staged / "docs" / "source.md").is_file()
        assert not (staged / "generated" / "note.md").exists()
        assert not (staged / "docs" / "generated" / "nested.md").exists()
        manifest = json.loads(
            (staged / "_local_search_manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["count"] == 2

        (project / "STATE.md").write_text(
            "# State\n\nCurrent verdict: NEGATIVE-COMPLETE.\n",
            encoding="utf-8",
        )
        (project / "docs" / "contract.md").write_text(
            "# Contract\n\n## NEGATIVE-COMPLETE definition\n\nTerminal validator owns it.\n",
            encoding="utf-8",
        )
        bundle = run(
            "claim-bundle",
            str(project),
            "NEGATIVE-COMPLETE",
            "--include",
            "**/*.md",
        )
        claim = json.loads(bundle.stdout)
        assert claim["result_count"] == 2
        assert "current" in claim["role_counts"]
        assert "definition" in claim["role_counts"]

    print("local-search smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
