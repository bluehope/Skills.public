#!/usr/bin/env python3
"""Known-answer tests for the optional ado project workspace initializer."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_ado_workspace.py"


def run(project: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(project), *arguments],
        capture_output=True,
        text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary) / "Example Research"
        project.mkdir()

        first = run(project, "--mode", "catalog", "--context-name", "ado-example")
        assert first.returncode == 0, first.stdout + first.stderr

        ado_root = project / "ado"
        expected = {
            ado_root / "ADO.md",
            ado_root / "ado-project.yaml",
            ado_root / ".gitignore",
            ado_root / "receipts" / "RECEIPT-TEMPLATE.yaml",
        }
        assert all(path.is_file() for path in expected)
        assert all(
            (ado_root / relative).is_dir()
            for relative in (
                "configs/actuators",
                "configs/operations",
                "configs/samplestores",
                "configs/spaces",
                "imports",
                "exports",
                "receipts",
            )
        )
        manifest = (ado_root / "ado-project.yaml").read_text(encoding="utf-8")
        assert 'mode: "catalog"' in manifest
        assert 'project: "example-research"' in manifest
        assert 'context_name: "ado-example"' in manifest
        assert "external_requires_source_validation: true" in manifest
        assert "locator_only_origins:\n    - MATCHED" in manifest
        assert not list(ado_root.rglob("*.db"))

        marker = "\nuser_owned: preserve-me\n"
        manifest_path = ado_root / "ado-project.yaml"
        manifest_path.write_text(manifest + marker, encoding="utf-8")
        second = run(project, "--mode", "shared", "--ado-project", "different")
        assert second.returncode == 0, second.stdout + second.stderr
        assert marker in manifest_path.read_text(encoding="utf-8")
        assert "kept" in second.stdout

    print("ado workspace initializer smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
