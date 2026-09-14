#!/usr/bin/env python3
"""Known-answer and regression tests for operational know-how management."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "operational_knowhow.py"


def run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
        capture_output=True, text=True,
    )


def incident(identifier: str, status: str = "NORMALIZED") -> dict[str, str]:
    return {
        "incident_id": identifier,
        "occurred_at_utc": "2026-08-16T00:00:00Z",
        "operation_kind": "copy",
        "environment_scope": "test-host:/bounded/project",
        "action_ref": "receipts/copy.txt",
        "symptom_class": "permission-denied",
        "normalized_signature": "transfer:executable-bit-lost",
        "severity": "MEDIUM",
        "impact": "child script did not execute",
        "evidence_path": "evidence/exit-126.log",
        "immediate_fix": "invoke child with bash",
        "existing_helper_checked": "YES",
        "candidate_target_skill": "hpc-skills",
        "status": status,
        "transfer_id": "",
        "redaction_status": "NO-SENSITIVE-DATA",
        "note": "",
    }


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def analysis_rows(project: Path) -> list[dict[str, str]]:
    path = project / "ops_knowhow" / "analysis.tsv"
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def analysis_by_signature(project: Path) -> dict[str, dict[str, str]]:
    return {row["normalized_signature"]: row for row in analysis_rows(project)}


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary) / "project"
        project.mkdir()
        initialized = run("init", project)
        assert initialized.returncode == 0, initialized.stdout + initialized.stderr
        workspace = project / "ops_knowhow"
        assert (workspace / "incidents.tsv").is_file()

        for number in (1, 2):
            record = project / f"incident-{number}.json"
            write_json(record, incident(f"OPS-00{number}"))
            logged = run("log", project, "--record", record)
            assert logged.returncode == 0, logged.stdout + logged.stderr
        rows = analysis_by_signature(project)
        recurring = rows["transfer:executable-bit-lost"]
        assert recurring["analysis_state"] == "PROMOTION-CANDIDATE"
        assert recurring["next_action"] == "PILOT-REUSABLE-GUARD"

        high_record = project / "high.json"
        write_json(high_record, incident("OPS-010") | {
            "operation_kind": "terminal",
            "normalized_signature": "shell:remote-quoting-expanded-locally",
            "severity": "HIGH",
            "existing_helper_checked": "NO",
        })
        high = run("log", project, "--record", high_record)
        assert high.returncode == 0, high.stdout + high.stderr
        high_row = analysis_by_signature(project)["shell:remote-quoting-expanded-locally"]
        assert high_row["analysis_state"] == "REVIEW-NOW"
        assert high_row["next_action"] == "SEARCH-EXISTING"

        duplicate = project / "duplicate.json"
        write_json(duplicate, incident("OPS-001"))
        rejected = run("log", project, "--record", duplicate)
        assert rejected.returncode == 2
        assert "duplicate incident_id" in rejected.stderr

        target = project / "target-skill-rule.md"
        target.write_text("validated reusable guard\n", encoding="utf-8")
        target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        pending = workspace / "transfers" / "pending" / "KHW-001.json"
        receipt = {
            "schema_version": 1,
            "transfer_id": "KHW-001",
            "signature": "transfer:executable-bit-lost",
            "source_incident_ids": ["OPS-001", "OPS-002"],
            "target_skill": "hpc-skills",
            "target_artifact": str(target.resolve()),
            "target_sha256": target_hash,
            "verified_artifacts": [{
                "role": "canonical-and-runtime",
                "path": str(target.resolve()),
                "sha256": target_hash,
            }],
            "change_type": "COMBINED",
            "existing_helper_decision": "PATCH",
            "minimal_delta": "validate mode after transfer",
            "validation_commands": ["known-answer", "exit-126 negative"],
            "validation_status": "PASS",
            "activation_status": "VERIFIED",
            "approved_by": "test-owner",
            "completed_at_utc": "2026-08-16T01:00:00Z",
            "scope": "transferred child scripts",
            "non_goals": [],
        }
        write_json(pending, receipt | {"target_sha256": "0" * 64})
        bad_hash = run("mark-transferred", project, "--receipt", pending)
        assert bad_hash.returncode == 2
        assert "SHA-256" in bad_hash.stderr and pending.is_file()

        write_json(pending, receipt)
        marked = run("mark-transferred", project, "--receipt", pending)
        assert marked.returncode == 0, marked.stdout + marked.stderr
        archived = workspace / "quarantine" / "transferred" / pending.name
        assert archived.is_file() and not pending.exists()
        transferred_row = analysis_by_signature(project)["transfer:executable-bit-lost"]
        assert transferred_row["analysis_state"] == "QUARANTINED"

        repeated = run("mark-transferred", project, "--receipt", pending)
        assert repeated.returncode == 0, repeated.stdout + repeated.stderr

        regression_record = project / "regression.json"
        write_json(regression_record, incident("OPS-003", status="REGRESSION"))
        regression = run("log", project, "--record", regression_record)
        assert regression.returncode == 0, regression.stdout + regression.stderr
        regression_row = analysis_by_signature(project)["transfer:executable-bit-lost"]
        assert regression_row["analysis_state"] == "REGRESSION"

        # Existing project headers and custom columns survive additive metadata.
        table = workspace / "incidents.tsv"
        with table.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            old_fields = [field for field in reader.fieldnames if field not in {
                "skills_used", "resolution_status", "verification_ref", "resolution_history",
            }] + ["project_note"]
            old_rows = list(reader)
        with table.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=old_fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(row | {"project_note": "keep me"} for row in old_rows)
        before_lookup = table.read_bytes()
        queried = run("lookup", project, "--incident-id", "OPS-001")
        assert queried.returncode == 0, queried.stderr
        assert json.loads(queried.stdout)["incidents"][0]["resolution_status"] == "UNKNOWN"
        assert table.read_bytes() == before_lookup, "lookup must not migrate or write"

        versioned = incident("unused") | {
            "normalized_signature": "parse:unsupported-format",
            "skills_used": {"example-skill": "2026.09.13", "project-helper": "unknown"},
            "immediate_fix": "No correction attempted yet",
            "resolution_status": "UNRESOLVED",
        }
        del versioned["incident_id"]
        del versioned["occurred_at_utc"]
        write_json(project / "versioned.json", versioned)
        logged = run("log", project, "--record", project / "versioned.json", "--compact")
        assert logged.returncode == 0, logged.stderr
        generated_id = json.loads(logged.stdout)["incident_id"]
        assert generated_id.startswith("OPS-")
        with table.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            assert reader.fieldnames[:len(old_fields)] == old_fields
            assert next(reader)["project_note"] == "keep me"

        update = project / "resolution.json"
        write_json(update, {"immediate_fix": "Use the supported reader", "resolution_status": "VERIFIED"})
        before_invalid = table.read_bytes()
        bad_resolution = run("resolve", project, "--incident-id", generated_id, "--record", update)
        assert bad_resolution.returncode == 2 and "verification_ref" in bad_resolution.stderr
        assert table.read_bytes() == before_invalid
        write_json(update, {
            "immediate_fix": "Use the supported reader", "resolution_status": "VERIFIED",
            "verification_ref": "receipts/known-answer.txt",
        })
        solved = run("resolve", project, "--incident-id", generated_id, "--record", update)
        assert solved.returncode == 0, solved.stderr
        after_resolve = table.read_bytes()
        replay = run("resolve", project, "--incident-id", generated_id, "--record", update)
        assert replay.returncode == 0 and table.read_bytes() == after_resolve
        queried = run("lookup", project, "--skill", "example-skill", "--limit", "1")
        assert queried.returncode == 0, queried.stderr
        result = json.loads(queried.stdout)
        assert result["matches"] == 1 and len(result["incidents"]) == 1
        assert result["incidents"][0]["resolution_status"] == "VERIFIED"
        assert "resolution_history" not in result["incidents"][0]
        with table.open(encoding="utf-8", newline="") as stream:
            saved = next(row for row in csv.DictReader(stream, delimiter="\t")
                         if row["incident_id"] == generated_id)
        assert json.loads(saved["resolution_history"])[0]["previous"]["resolution_status"] == "UNRESOLVED"
        assert run("analyze", project).returncode == 0
        assert analysis_by_signature(project)["parse:unsupported-format"]["total_count"] == "1"

        # Failed fixes remove stale verification; lifecycle/transfer is independent.
        write_json(update, {"immediate_fix": "Correction did not reproduce", "resolution_status": "FAILED"})
        failed = run("resolve", project, "--incident-id", generated_id, "--record", update)
        assert failed.returncode == 0 and json.loads(failed.stdout)["verification_ref"] == ""
        assert run("lookup", project, "--limit", "0").returncode == 2
        assert run("lookup", project, "--directory", "../escape").returncode == 2
        invalid = versioned | {"skills_used": ["example-skill"]}
        write_json(project / "invalid.json", invalid)
        assert run("log", project, "--record", project / "invalid.json").returncode == 2

        empty_project = Path(temporary) / "empty"
        empty_project.mkdir()
        empty = run("lookup", empty_project)
        assert empty.returncode == 0 and json.loads(empty.stdout)["status"] == "NOT-INITIALIZED"
        assert not (empty_project / "ops_knowhow").exists()
        assert run("init", empty_project).returncode == 0
        minimal = empty_project / "minimal.json"
        write_json(minimal, {
            "operation_kind": "ssh", "symptom_class": "connection-error",
            "severity": "MEDIUM", "evidence_path": "receipts/error.txt",
            "redaction_status": "NO-SENSITIVE-DATA",
        })
        recorded = run("log", empty_project, "--record", minimal)
        assert recorded.returncode == 0, recorded.stderr
        minimal_result = json.loads(recorded.stdout)
        assert minimal_result["existing_helper_checked"] == "UNKNOWN"
        assert minimal_result["skills_used"] == "{}"
        assert minimal_result["resolution_status"] == "UNKNOWN"

    print("operational know-how smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
