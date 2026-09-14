#!/usr/bin/env python3
"""Known-answer tests for the research document audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_research_docs.py"


def run(project: Path, policy: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(project), "--policy", str(policy)],
        capture_output=True,
        text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary) / "project"
        project.mkdir()
        (project / "PROJECT_HUB.md").write_text(
            "# Hub\n\nNEGATIVE-COMPLETE-AT-METHOD-BOUNDARY\n\n[Goal](GOAL.md)\n",
            encoding="utf-8",
        )
        (project / "GOAL.md").write_text(
            "# Goal\n\n## Negative scientific completion -- `NEGATIVE-COMPLETE`\n\n"
            "Artifact literal `NEGATIVE-COMPLETE`; living "
            "`NEGATIVE-COMPLETE-AT-METHOD-BOUNDARY`.\n",
            encoding="utf-8",
        )
        (project / "MONITOR.md").write_text(
            "# Monitor\n\nStatus: TERMINAL / VALIDATED\n",
            encoding="utf-8",
        )
        (project / "receipt.csv").write_text(
            "timestamp,question,tier,query,scope,result_count,adopted_source,status,reason\n",
            encoding="utf-8",
        )
        policy = project / "audit.json"
        policy.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "canonical_documents": {
                        "hub": "PROJECT_HUB.md",
                        "goal": "GOAL.md",
                        "monitor": "MONITOR.md",
                    },
                    "current_documents": ["PROJECT_HUB.md", "GOAL.md", "MONITOR.md"],
                    "status_contracts": [
                        {
                            "term": "NEGATIVE-COMPLETE",
                            "definition_owner": "GOAL.md",
                            "definition_heading": "## Negative scientific completion -- `NEGATIVE-COMPLETE`",
                            "artifact_literal": "NEGATIVE-COMPLETE",
                            "living_interpretation": "NEGATIVE-COMPLETE-AT-METHOD-BOUNDARY",
                            "required_current_documents": ["PROJECT_HUB.md", "GOAL.md"],
                        }
                    ],
                    "ambiguous_terms": [],
                    "link_documents": ["PROJECT_HUB.md"],
                    "search_receipts": ["receipt.csv"],
                    "required_search_receipt_columns": ["timestamp", "question", "status"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        passed = run(project, policy)
        assert passed.returncode == 0, passed.stdout + passed.stderr
        passed_report = json.loads(passed.stdout)
        assert passed_report["ready"] is True
        assert passed_report["exit_code"] == 0
        assert len(passed_report["tool_sha256"]) == 64
        assert len(passed_report["policy_sha256"]) == 64
        assert len(passed_report["search_receipts"][0]["sha256"]) == 64
        assert set(passed_report["input_document_hashes"]) == {
            "PROJECT_HUB.md",
            "GOAL.md",
            "MONITOR.md",
        }

        (project / "MONITOR.md").write_text(
            "# Monitor\n\nStatus: EXECUTION PENDING\n\n## Terminal outcome\nVALIDATED\n",
            encoding="utf-8",
        )
        failed = run(project, policy)
        assert failed.returncode == 1
        codes = {item["code"] for item in json.loads(failed.stdout)["checks"]}
        assert "STALE_STATUS_HEADER" in codes

        (project / "MONITOR.md").write_text(
            "# Monitor\n\nStatus: TERMINAL / VALIDATED\n", encoding="utf-8"
        )
        (project / "litmus.json").write_text("{}\n", encoding="utf-8")
        (project / "registry.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "entries": [
                        {"id": "REF-001", "observable_id": "g-sym-v1", "unit_id": "meV"}
                    ],
                }
            ),
            encoding="utf-8",
        )

        def write_registration(**changes: object) -> None:
            fields: dict[str, object] = {
                "registration_schema_version": 1,
                "candidate_id": "CAND-001",
                "reference_id": "REF-001",
                "reference_litmus": "litmus.json",
                "observable_id": "g-sym-v1",
                "unit_id": "meV",
                "consumer_id": "assembler-v2:sha256:abc",
                "condition_fingerprint": "sha256:" + "d" * 64,
                "workflow_profile": "core",
                "consumer_identity_recorded": True,
                "same_observable_reference_checked": True,
                "route_equal_control_status": "completed",
                "self_reference_used_as_validation": False,
                "user_named_raw_status": "not-applicable",
            }
            fields.update(changes)
            lines = ["---"]
            for key, value in fields.items():
                if value is True:
                    rendered = "true"
                elif value is False:
                    rendered = "false"
                elif value is None:
                    rendered = "null"
                else:
                    rendered = str(value)
                lines.append(f"{key}: {rendered}")
            lines.extend(["---", "", "# Registration"])
            (project / "registration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

        policy_data = json.loads(policy.read_text(encoding="utf-8"))
        policy_data["stable_id_registry"] = "registry.json"
        policy_data["registration_receipts"] = ["registration.md"]
        policy.write_text(json.dumps(policy_data, indent=2), encoding="utf-8")

        write_registration()
        registered = run(project, policy)
        assert registered.returncode == 0, registered.stdout + registered.stderr
        registered_report = json.loads(registered.stdout)
        assert registered_report["registration_receipts"][0]["sha256"]
        assert registered_report["stable_id_registry"]["sha256"]

        write_registration(candidate_id="REF-001")
        self_reference = run(project, policy)
        assert self_reference.returncode == 1
        assert "SELF_REFERENCE" in {
            item["code"] for item in json.loads(self_reference.stdout)["checks"]
        }

        write_registration(observable_id="proxy-v1")
        mismatch = run(project, policy)
        assert mismatch.returncode == 1
        assert "REFERENCE_IDENTITY_MISMATCH" in {
            item["code"] for item in json.loads(mismatch.stdout)["checks"]
        }

        write_registration(same_observable_reference_checked="not-applicable")
        bypass = run(project, policy)
        assert bypass.returncode == 1
        assert "REFERENCE_CHECK_NOT_COMPLETED" in {
            item["code"] for item in json.loads(bypass.stdout)["checks"]
        }

        write_registration(consumer_id=None)
        missing = run(project, policy)
        assert missing.returncode == 1
        assert "REGISTRATION_REQUIRED_FIELD" in {
            item["code"] for item in json.loads(missing.stdout)["checks"]
        }

        write_registration(condition_fingerprint="sha256:short")
        invalid_fingerprint = run(project, policy)
        assert invalid_fingerprint.returncode == 1
        assert "INVALID_CONDITION_FINGERPRINT" in {
            item["code"] for item in json.loads(invalid_fingerprint.stdout)["checks"]
        }

        write_registration(reference_litmus="absent.json")
        broken = run(project, policy)
        assert broken.returncode == 1
        assert "MISSING_REFERENCE_LITMUS" in {
            item["code"] for item in json.loads(broken.stdout)["checks"]
        }

        (project / "artifact.bin").write_bytes(b"ok")
        policy_data["registration_profiles"] = {
            "slurm": {
                "required_fields": ["slurm_job_id", "artifact_path"],
                "path_fields": ["artifact_path"],
            }
        }
        policy.write_text(json.dumps(policy_data, indent=2), encoding="utf-8")
        write_registration(
            workflow_profile="slurm", slurm_job_id="12345", artifact_path="artifact.bin"
        )
        profiled = run(project, policy)
        assert profiled.returncode == 0, profiled.stdout + profiled.stderr

        write_registration(
            workflow_profile="slurm", slurm_job_id="12345", artifact_path="missing.bin"
        )
        missing_profile_path = run(project, policy)
        assert missing_profile_path.returncode == 1
        assert "PROFILE_PATH_MISSING" in {
            item["code"] for item in json.loads(missing_profile_path.stdout)["checks"]
        }

    print("research document audit smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
