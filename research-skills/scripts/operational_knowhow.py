#!/usr/bin/env python3
"""Manage operational incident recurrence, transfer receipts, and quarantine."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Iterable
from uuid import uuid4


LEGACY_INCIDENT_FIELDS = (
    "incident_id", "occurred_at_utc", "operation_kind", "environment_scope",
    "action_ref", "symptom_class", "normalized_signature", "severity", "impact",
    "evidence_path", "immediate_fix", "existing_helper_checked",
    "candidate_target_skill", "status", "transfer_id", "redaction_status", "note",
)
INCIDENT_FIELDS = LEGACY_INCIDENT_FIELDS + (
    "skills_used", "resolution_status", "verification_ref", "resolution_history",
)
INCIDENT_DEFAULTS = {
    "skills_used": "{}", "resolution_status": "UNKNOWN",
    "verification_ref": "", "resolution_history": "[]",
}
LOG_DEFAULTS = {
    "environment_scope": "unknown", "impact": "not-assessed",
    "immediate_fix": "none recorded", "existing_helper_checked": "UNKNOWN",
    "candidate_target_skill": "unknown", "status": "OBSERVED",
}
RESOLUTIONS = {"UNKNOWN", "UNRESOLVED", "ATTEMPTED", "VERIFIED", "FAILED"}
ANALYSIS_FIELDS = (
    "normalized_signature", "active_count", "total_count", "maximum_severity",
    "operation_kinds", "environment_scopes", "incident_ids", "candidate_target_skills",
    "existing_helper_search", "analysis_state", "next_action",
)
TRANSFER_FIELDS = (
    "transfer_id", "normalized_signature", "target_skill", "target_artifact",
    "target_sha256", "completed_at_utc", "receipt_path", "incident_count", "status",
)
SEVERITY = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
STATUSES = {
    "OBSERVED", "NORMALIZED", "CANDIDATE", "PILOTING", "TRANSFERRED",
    "LOCAL-ONLY", "REJECTED", "SUPERSEDED", "REGRESSION",
}
INACTIVE = {"TRANSFERRED", "LOCAL-ONLY", "REJECTED", "SUPERSEDED"}
HELPER_CHECK = {"YES", "NO", "UNKNOWN"}
REDACTION = {"REDACTED", "NO-SENSITIVE-DATA", "REVIEW-REQUIRED"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def tsv_text(rows: Iterable[dict[str, str]], fields: tuple[str, ...]) -> str:
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return stream.getvalue()


def workspace(project_root: Path, directory: str = "ops_knowhow") -> Path:
    project = project_root.resolve()
    if not project.is_dir():
        raise ValueError(f"project root is not a directory: {project}")
    root = (project / directory).resolve()
    if project != root and project not in root.parents:
        raise ValueError("know-how directory escapes the project root")
    return root


def initialize(root: Path) -> None:
    for directory in (
        root / "transfers" / "pending",
        root / "quarantine" / "transferred",
        root / "quarantine" / "rejected",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    for path, fields in (
        (root / "incidents.tsv", INCIDENT_FIELDS),
        (root / "analysis.tsv", ANALYSIS_FIELDS),
        (root / "transfer-index.tsv", TRANSFER_FIELDS),
    ):
        if not path.exists():
            atomic_write(path, tsv_text([], fields))


def read_tsv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"missing required file: {path}")
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        missing = [field for field in fields if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(missing)}")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"{path}: malformed TSV row")
            rows.append({field: value.strip() for field, value in row.items()})
        return rows


def write_incidents(root: Path, rows: list[dict[str, str]]) -> None:
    """Preserve legacy/custom header order; append new columns only on writes.

    Atomic replacement is not a distributed lock. This workspace has one writer.
    """
    path = root / "incidents.tsv"
    with path.open(encoding="utf-8", newline="") as stream:
        header = next(csv.reader(stream, delimiter="\t"))
    fields = tuple(dict.fromkeys(header + list(INCIDENT_FIELDS)))
    atomic_write(path, tsv_text(rows, fields))


def validate_incident(record: dict[str, str]) -> None:
    required = (
        "incident_id", "occurred_at_utc", "operation_kind", "environment_scope",
        "symptom_class", "severity", "impact", "evidence_path", "immediate_fix",
        "existing_helper_checked", "candidate_target_skill", "status", "redaction_status",
    )
    missing = [field for field in required if not record.get(field, "").strip()]
    if missing:
        raise ValueError(f"incident record has empty required fields: {', '.join(missing)}")
    if record["severity"] not in SEVERITY:
        raise ValueError(f"invalid severity: {record['severity']}")
    if record["status"] not in STATUSES:
        raise ValueError(f"invalid status: {record['status']}")
    if record["existing_helper_checked"] not in HELPER_CHECK:
        raise ValueError("existing_helper_checked must be YES, NO, or UNKNOWN")
    if record["redaction_status"] not in REDACTION:
        raise ValueError(f"invalid redaction_status: {record['redaction_status']}")
    if record["status"] != "OBSERVED" and not record["normalized_signature"]:
        raise ValueError("a non-OBSERVED incident requires normalized_signature")
    if record["status"] == "TRANSFERRED" and not record["transfer_id"]:
        raise ValueError("TRANSFERRED requires transfer_id")
    skills = json.loads(record.get("skills_used") or "{}")
    if not isinstance(skills, dict) or any(
        not isinstance(key, str) or not key.strip()
        or not isinstance(value, str) or not value.strip()
        for key, value in skills.items()
    ):
        raise ValueError("skills_used must map skill IDs to versions/hashes or unknown")
    resolution = record.get("resolution_status") or "UNKNOWN"
    if resolution not in RESOLUTIONS:
        raise ValueError("invalid resolution_status")
    if resolution == "VERIFIED" and not record.get("verification_ref", "").strip():
        raise ValueError("VERIFIED requires verification_ref (not proof of verification)")
    history = json.loads(record.get("resolution_history") or "[]")
    if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
        raise ValueError("resolution_history must be a list of objects")


def load_incidents(root: Path) -> list[dict[str, str]]:
    rows = read_tsv(root / "incidents.tsv", LEGACY_INCIDENT_FIELDS)
    seen: set[str] = set()
    for row in rows:
        for field, value in INCIDENT_DEFAULTS.items():
            row[field] = row.get(field) or value
        validate_incident(row)
        if row["incident_id"] in seen:
            raise ValueError(f"duplicate incident_id: {row['incident_id']}")
        seen.add(row["incident_id"])
    return rows


def log_incident(root: Path, record_path: Path) -> dict[str, str]:
    data = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("incident JSON must be an object")
    now = datetime.now(timezone.utc)
    data.setdefault("incident_id", f"OPS-{now:%Y%m%d}-{uuid4().hex[:12]}")
    data.setdefault("occurred_at_utc", now.isoformat(timespec="seconds"))
    for field, value in LOG_DEFAULTS.items():
        data.setdefault(field, value)
    for field in ("skills_used", "resolution_history"):
        if field in data and not isinstance(data[field], str):
            data[field] = json.dumps(data[field], ensure_ascii=False, separators=(",", ":"))
    record = {
        field: str(data.get(field, INCIDENT_DEFAULTS.get(field, ""))).strip()
        for field in INCIDENT_FIELDS
    }
    validate_incident(record)
    rows = load_incidents(root)
    if any(row["incident_id"] == record["incident_id"] for row in rows):
        raise ValueError(f"duplicate incident_id: {record['incident_id']}")
    rows.append(record)
    write_incidents(root, rows)
    return record


def resolve_incident(root: Path, incident_id: str, record_path: Path) -> dict[str, str]:
    """Update one recovery outcome without counting it as another incident."""
    data = json.loads(record_path.read_text(encoding="utf-8"))
    fields = ("immediate_fix", "resolution_status", "verification_ref")
    if not isinstance(data, dict) or set(data) - set(fields):
        raise ValueError("resolution JSON accepts only immediate_fix, resolution_status, verification_ref")
    if not all(isinstance(data.get(field), str) and data[field].strip() for field in fields[:2]):
        raise ValueError("resolution requires immediate_fix and resolution_status")
    if "verification_ref" in data and not isinstance(data["verification_ref"], str):
        raise ValueError("verification_ref must be a string")
    rows = load_incidents(root)
    record = next((row for row in rows if row["incident_id"] == incident_id), None)
    if record is None:
        raise ValueError(f"unknown incident_id: {incident_id}")
    previous = {field: record.get(field, "") for field in fields}
    current = {field: data.get(field, "").strip() for field in fields}
    candidate = record | current
    validate_incident(candidate)
    if current != previous:
        history = json.loads(record["resolution_history"])
        history.append({
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "previous": previous, "current": current,
        })
        record.update(current)
        record["resolution_history"] = json.dumps(history, ensure_ascii=False, separators=(",", ":"))
        write_incidents(root, rows)
    return {field: record[field] for field in ("incident_id", *fields)}


def lookup_incidents(root: Path, args: argparse.Namespace) -> dict[str, object]:
    if not 1 <= args.limit <= 20:
        raise ValueError("lookup limit must be between 1 and 20")
    path = root / "incidents.tsv"
    if not path.exists():
        return {"status": "NOT-INITIALIZED", "matches": 0, "incidents": []}
    rows = load_incidents(root)
    matches = [row for row in rows
               if (not args.incident_id or row["incident_id"] == args.incident_id)
               and (not args.signature or row["normalized_signature"] == args.signature)
               and (not args.skill or args.skill in json.loads(row["skills_used"]))]
    fields = ("incident_id", "occurred_at_utc", "normalized_signature", "symptom_class",
              "skills_used", "resolution_status", "immediate_fix", "verification_ref", "evidence_path")
    items = []
    for row in matches[-args.limit:][::-1]:
        item = {field: row[field] for field in fields}
        for field in ("symptom_class", "immediate_fix"):
            if len(item[field]) > 240:
                item[field] = item[field][:237] + "..."
        item["skills_used"] = json.loads(row["skills_used"])
        items.append(item)
    return {"status": "OK", "matches": len(matches), "incidents": items}


def analyze_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        signature = row["normalized_signature"] or f"UNNORMALIZED:{row['incident_id']}"
        groups.setdefault(signature, []).append(row)
    output: list[dict[str, str]] = []
    for signature, group in sorted(groups.items()):
        active = [row for row in group if row["status"] not in INACTIVE]
        maximum = max(group, key=lambda row: SEVERITY[row["severity"]])["severity"]
        transferred = any(row["status"] == "TRANSFERRED" for row in group)
        helper_values = {row["existing_helper_checked"] for row in active or group}
        if signature.startswith("UNNORMALIZED:"):
            state, action = "UNNORMALIZED", "NORMALIZE-MECHANISM"
        elif transferred and active:
            state, action = "REGRESSION", "AUDIT-TRANSFER-ACTIVATION-AND-COVERAGE"
        elif not active:
            state, action = "QUARANTINED", "SEARCH-ON-DEMAND"
        elif maximum in {"HIGH", "CRITICAL"}:
            state = "REVIEW-NOW"
            action = "SEARCH-EXISTING" if helper_values != {"YES"} else "PILOT-REUSABLE-GUARD"
        elif len(group) >= 2:
            state = "PROMOTION-CANDIDATE"
            action = "SEARCH-EXISTING" if helper_values != {"YES"} else "PILOT-REUSABLE-GUARD"
        else:
            state, action = "WATCH", "NORMALIZE-AND-MONITOR"
        output.append({
            "normalized_signature": signature,
            "active_count": str(len(active)),
            "total_count": str(len(group)),
            "maximum_severity": maximum,
            "operation_kinds": ",".join(sorted({row["operation_kind"] for row in group})),
            "environment_scopes": ",".join(sorted({row["environment_scope"] for row in group})),
            "incident_ids": ",".join(row["incident_id"] for row in group),
            "candidate_target_skills": ",".join(sorted({row["candidate_target_skill"] for row in group})),
            "existing_helper_search": ",".join(sorted(helper_values)),
            "analysis_state": state,
            "next_action": action,
        })
    return output


def write_analysis(root: Path) -> list[dict[str, str]]:
    analysis = analyze_rows(load_incidents(root))
    atomic_write(root / "analysis.tsv", tsv_text(analysis, ANALYSIS_FIELDS))
    return analysis


def receipt_candidate(root: Path, requested: Path) -> tuple[Path, bool]:
    pending = (root / "transfers" / "pending").resolve()
    transferred = (root / "quarantine" / "transferred").resolve()
    path = requested.resolve()
    if path.is_file() and path.parent == pending:
        return path, False
    archived = transferred / requested.name
    if archived.is_file():
        return archived, True
    raise ValueError("receipt must exist directly under transfers/pending or transferred quarantine")


def validate_receipt(data: dict[str, object]) -> None:
    required = (
        "transfer_id", "signature", "source_incident_ids", "target_skill",
        "target_artifact", "target_sha256", "verified_artifacts", "change_type",
        "existing_helper_decision",
        "validation_commands", "validation_status", "activation_status", "approved_by",
        "completed_at_utc", "scope",
    )
    missing = [field for field in required if data.get(field) in (None, "", [])]
    if missing:
        raise ValueError(f"transfer receipt has empty required fields: {', '.join(missing)}")
    if data["validation_status"] != "PASS":
        raise ValueError("transfer receipt validation_status must be PASS")
    if data["activation_status"] not in {"VERIFIED", "NOT-APPLICABLE"}:
        raise ValueError("transfer receipt activation_status must be VERIFIED or NOT-APPLICABLE")
    if data["existing_helper_decision"] not in {"REUSE", "PATCH", "EXTEND", "NEW"}:
        raise ValueError("invalid existing_helper_decision")
    if not isinstance(data["verified_artifacts"], list):
        raise ValueError("verified_artifacts must be a nonempty list")
    for item in data["verified_artifacts"]:
        if not isinstance(item, dict) or not all(item.get(key) for key in ("role", "path", "sha256")):
            raise ValueError("each verified_artifact requires role, path, and sha256")


def mark_transferred(root: Path, requested_receipt: Path) -> dict[str, str]:
    receipt_path, already_archived = receipt_candidate(root, requested_receipt)
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("transfer receipt must be a JSON object")
    validate_receipt(data)
    artifact = Path(str(data["target_artifact"])).resolve()
    if not artifact.is_file():
        raise ValueError(f"target artifact does not exist: {artifact}")
    actual_hash = sha256(artifact)
    if actual_hash != data["target_sha256"]:
        raise ValueError("target artifact SHA-256 does not match transfer receipt")
    verified_primary = False
    for item in data["verified_artifacts"]:
        verified_path = Path(str(item["path"])).resolve()
        if not verified_path.is_file() or sha256(verified_path) != item["sha256"]:
            raise ValueError(f"verified artifact is missing or has a SHA-256 mismatch: {verified_path}")
        if verified_path == artifact and item["sha256"] == actual_hash:
            verified_primary = True
    if not verified_primary:
        raise ValueError("verified_artifacts does not include the primary target artifact")

    index = read_tsv(root / "transfer-index.tsv", TRANSFER_FIELDS)
    transfer_id = str(data["transfer_id"])
    matching_index = [row for row in index if row["transfer_id"] == transfer_id]
    expected_index = {
        "transfer_id": transfer_id,
        "normalized_signature": str(data["signature"]),
        "target_skill": str(data["target_skill"]),
        "target_artifact": str(artifact),
        "target_sha256": actual_hash,
    }
    if matching_index:
        row = matching_index[0]
        if any(row[field] != value for field, value in expected_index.items()):
            raise ValueError("transfer_id is already indexed for different content")
        if not already_archived:
            raise ValueError("indexed transfer unexpectedly has a pending receipt")
        return row

    incidents = load_incidents(root)
    source_ids = {str(item) for item in data["source_incident_ids"]}
    candidates = [
        row for row in incidents
        if row["normalized_signature"] == data["signature"] and row["status"] not in INACTIVE
    ]
    if not candidates:
        raise ValueError("no active incidents match the transfer signature")
    if not source_ids.issubset({row["incident_id"] for row in incidents}):
        raise ValueError("receipt names unknown source_incident_ids")
    if not {row["incident_id"] for row in candidates}.issubset(source_ids):
        raise ValueError("receipt does not cover every active incident with this signature")
    for row in candidates:
        row["status"] = "TRANSFERRED"
        row["transfer_id"] = transfer_id

    destination = root / "quarantine" / "transferred" / receipt_path.name
    if destination.exists():
        raise ValueError(f"quarantine destination already exists: {destination}")
    index_row = expected_index | {
        "completed_at_utc": str(data["completed_at_utc"]),
        "receipt_path": str(destination.relative_to(root)),
        "incident_count": str(len(candidates)),
        "status": "TRANSFERRED",
    }
    write_incidents(root, incidents)
    atomic_write(root / "transfer-index.tsv", tsv_text(index + [index_row], TRANSFER_FIELDS))
    os.replace(receipt_path, destination)
    write_analysis(root)
    return index_row


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "analyze"):
        command = subparsers.add_parser(name)
        command.add_argument("project_root", type=Path)
        command.add_argument("--directory", default="ops_knowhow")
    log = subparsers.add_parser("log")
    log.add_argument("project_root", type=Path)
    log.add_argument("--directory", default="ops_knowhow")
    log.add_argument("--record", required=True, type=Path)
    log.add_argument("--compact", action="store_true", help="return only ID and resolution status")
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("project_root", type=Path)
    resolve.add_argument("--directory", default="ops_knowhow")
    resolve.add_argument("--incident-id", required=True)
    resolve.add_argument("--record", required=True, type=Path)
    lookup = subparsers.add_parser("lookup")
    lookup.add_argument("project_root", type=Path)
    lookup.add_argument("--directory", default="ops_knowhow")
    lookup.add_argument("--incident-id")
    lookup.add_argument("--signature")
    lookup.add_argument("--skill")
    lookup.add_argument("--limit", type=int, default=5)
    mark = subparsers.add_parser("mark-transferred")
    mark.add_argument("project_root", type=Path)
    mark.add_argument("--directory", default="ops_knowhow")
    mark.add_argument("--receipt", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = workspace(args.project_root, args.directory)
        if args.command == "init":
            initialize(root)
            result: object = {"workspace": str(root), "status": "READY"}
        elif args.command == "lookup":
            result = lookup_incidents(root, args)
        else:
            if not root.is_dir():
                raise ValueError(f"know-how workspace is not initialized: {root}")
            if args.command == "log":
                result = log_incident(root, args.record.resolve())
                write_analysis(root)
                if args.compact:
                    result = {key: result[key] for key in ("incident_id", "resolution_status")}
            elif args.command == "resolve":
                result = resolve_incident(root, args.incident_id, args.record.resolve())
            elif args.command == "analyze":
                analysis = write_analysis(root)
                result = {
                    "groups": len(analysis),
                    "review_now": sum(row["analysis_state"] == "REVIEW-NOW" for row in analysis),
                    "promotion_candidates": sum(
                        row["analysis_state"] == "PROMOTION-CANDIDATE" for row in analysis
                    ),
                    "regressions": sum(row["analysis_state"] == "REGRESSION" for row in analysis),
                }
            else:
                result = mark_transferred(root, args.receipt)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
