#!/usr/bin/env python3
"""Read-only, policy-driven audit for research documentation consistency."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import sys


PENDING = re.compile(r"\b(PENDING|RUNNING|HELD)\b", re.IGNORECASE)
TERMINAL = re.compile(r"\b(TERMINAL|VALIDATED|COMPLETED|FINALIZER)\b", re.IGNORECASE)
CORRECTION = re.compile(r"\b(CORRECTION|SUPERSEDED|histor(?:y|ical))\b", re.IGNORECASE)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CORE_REGISTRATION_FIELDS = ("candidate_id", "consumer_id", "condition_fingerprint")
REFERENCE_FIELDS = ("reference_id", "reference_litmus", "observable_id", "unit_id")
SHA256_FINGERPRINT = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_hits(text: str, needle: str) -> list[int]:
    return [i for i, line in enumerate(text.splitlines(), 1) if needle in line]


def resolve(project: Path, relative: str) -> Path:
    path = Path(relative)
    return path.resolve() if path.is_absolute() else (project / path).resolve()


def current_scope(text: str, boundaries: list[str]) -> str:
    positions = [text.find(marker) for marker in boundaries if marker in text]
    return text[: min(positions)] if positions else text


def add(checks: list[dict], severity: str, code: str, message: str, **evidence: object) -> None:
    checks.append({"severity": severity, "code": code, "message": message, **evidence})


def blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def frontmatter_scalar(value: str) -> object:
    value = value.strip()
    if value.lower() in {"null", "none", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def read_registration(path: Path) -> dict[str, object]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("registration JSON must be an object")
        return data
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("registration Markdown must start with YAML-like frontmatter")
    data: dict[str, object] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = frontmatter_scalar(value)
    raise ValueError("registration frontmatter is not closed")


def audit(args: argparse.Namespace) -> int:
    project = Path(args.project_root).resolve()
    policy_path = Path(args.policy).resolve()
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if policy.get("schema_version") != 1:
        raise SystemExit("unsupported policy schema_version")

    checks: list[dict] = []
    documents: dict[str, dict] = {}
    texts: dict[str, str] = {}
    canonical = policy.get("canonical_documents", {})
    for role, relative in canonical.items():
        path = resolve(project, relative)
        exists = path.is_file()
        documents[role] = {
            "path": str(path),
            "exists": exists,
            "sha256": sha256(path) if exists else None,
        }
        if not exists:
            add(checks, "BLOCK", "MISSING_DOCUMENT", f"missing canonical {role}", path=str(path))
            continue
        texts[relative] = path.read_text(encoding="utf-8", errors="replace")

    boundaries = policy.get("historical_boundaries", {})
    for relative, markers in boundaries.items():
        text = texts.get(relative)
        if text is None:
            continue
        missing = [marker for marker in markers if marker not in text]
        if missing:
            add(
                checks,
                "WARN",
                "MISSING_HISTORY_BOUNDARY",
                "declared historical boundary is absent",
                path=relative,
                markers=missing,
            )

    current_documents = policy.get("current_documents", list(canonical.values()))
    for relative in current_documents:
        text = texts.get(relative)
        if text is None:
            path = resolve(project, relative)
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="replace")
                texts[relative] = text
            else:
                continue
        scope = current_scope(text, boundaries.get(relative, []))
        header = "\n".join(scope.splitlines()[:40])
        if PENDING.search(header) and TERMINAL.search(scope) and not CORRECTION.search(header):
            add(
                checks,
                "BLOCK",
                "STALE_STATUS_HEADER",
                "pending/running/held header conflicts with terminal current scope without correction",
                path=relative,
            )

    for contract in policy.get("status_contracts", []):
        term = contract["term"]
        owner = contract["definition_owner"]
        heading = contract["definition_heading"]
        owner_text = texts.get(owner, "")
        if heading not in owner_text:
            add(
                checks,
                "BLOCK",
                "MISSING_STATUS_DEFINITION",
                f"definition heading missing for {term}",
                path=owner,
                heading=heading,
            )
        literal = contract.get("artifact_literal")
        living = contract.get("living_interpretation")
        for label, value in (("artifact_literal", literal), ("living_interpretation", living)):
            if value and value not in owner_text:
                add(
                    checks,
                    "BLOCK",
                    "MISSING_SEMANTIC_BINDING",
                    f"{label} for {term} is not bound in definition owner",
                    path=owner,
                    value=value,
                )
        for relative in contract.get("required_current_documents", []):
            text = current_scope(texts.get(relative, ""), boundaries.get(relative, []))
            accepted = [value for value in (term, literal, living) if value]
            if text and not any(value in text for value in accepted):
                add(
                    checks,
                    "WARN",
                    "STATUS_NOT_ROUTED",
                    f"{term} is not routed in a declared current document",
                    path=relative,
                )

    for rule in policy.get("ambiguous_terms", []):
        owner = rule["guidance_owner"]
        term = rule["term"]
        text = texts.get(owner, "")
        if term not in text:
            add(
                checks,
                "WARN",
                "MISSING_TERM_GUIDANCE",
                f"ambiguous term lacks guidance in its owner: {term}",
                path=owner,
            )

    for relative in policy.get("link_documents", current_documents):
        text = texts.get(relative, "")
        source = resolve(project, relative)
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^(https?://|mailto:|qmd://|/gpfs/)", target):
                continue
            destination = (source.parent / target).resolve()
            if not destination.exists():
                add(
                    checks,
                    "BLOCK",
                    "BROKEN_MARKDOWN_LINK",
                    "local Markdown link does not resolve",
                    path=relative,
                    target=target,
                )

    required_columns = set(policy.get("required_search_receipt_columns", []))
    search_receipt_reports: list[dict[str, object]] = []
    for relative in policy.get("search_receipts", []):
        path = resolve(project, relative)
        search_receipt_reports.append(
            {"path": str(path), "exists": path.is_file(), "sha256": sha256(path) if path.is_file() else None}
        )
        if not path.is_file():
            add(checks, "WARN", "MISSING_SEARCH_RECEIPT", "search receipt is absent", path=relative)
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
        missing = sorted(required_columns - set(header))
        if missing:
            add(
                checks,
                "BLOCK",
                "SEARCH_RECEIPT_SCHEMA",
                "search receipt lacks required columns",
                path=relative,
                missing=missing,
            )

    registry: dict[str, dict[str, object]] = {}
    registry_info: dict[str, object] | None = None
    registry_relative = policy.get("stable_id_registry")
    if registry_relative:
        registry_path = resolve(project, registry_relative)
        registry_info = {"path": str(registry_path), "exists": registry_path.is_file()}
        if not registry_path.is_file():
            add(checks, "BLOCK", "MISSING_STABLE_ID_REGISTRY", "stable-ID registry is absent", path=str(registry_path))
        else:
            registry_info["sha256"] = sha256(registry_path)
            try:
                registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
                if registry_data.get("schema_version") != 1 or not isinstance(registry_data.get("entries"), list):
                    raise ValueError("registry requires schema_version 1 and an entries array")
                for entry in registry_data["entries"]:
                    if not isinstance(entry, dict) or blank(entry.get("id")):
                        raise ValueError("every registry entry requires a nonempty id")
                    stable_id = str(entry["id"])
                    if stable_id in registry:
                        raise ValueError(f"duplicate stable ID: {stable_id}")
                    registry[stable_id] = entry
            except (json.JSONDecodeError, ValueError, AttributeError) as exc:
                add(checks, "BLOCK", "INVALID_STABLE_ID_REGISTRY", str(exc), path=str(registry_path))

    registration_reports: list[dict[str, object]] = []
    profiles = policy.get("registration_profiles", {})
    for relative in policy.get("registration_receipts", []):
        path = resolve(project, relative)
        receipt_report: dict[str, object] = {"path": str(path), "exists": path.is_file()}
        registration_reports.append(receipt_report)
        if not path.is_file():
            add(checks, "BLOCK", "MISSING_REGISTRATION_RECEIPT", "registration receipt is absent", path=relative)
            continue
        receipt_report["sha256"] = sha256(path)
        try:
            receipt = read_registration(path)
        except (json.JSONDecodeError, ValueError) as exc:
            add(checks, "BLOCK", "INVALID_REGISTRATION_RECEIPT", str(exc), path=relative)
            continue
        if receipt.get("registration_schema_version") not in {1, "1"}:
            add(checks, "BLOCK", "REGISTRATION_SCHEMA", "registration_schema_version must be 1", path=relative)

        for field in CORE_REGISTRATION_FIELDS:
            if blank(receipt.get(field)):
                add(checks, "BLOCK", "REGISTRATION_REQUIRED_FIELD", f"registration field is blank: {field}", path=relative, field=field)
        fingerprint = receipt.get("condition_fingerprint")
        if not blank(fingerprint) and not SHA256_FINGERPRINT.fullmatch(str(fingerprint)):
            add(
                checks,
                "BLOCK",
                "INVALID_CONDITION_FINGERPRINT",
                "condition_fingerprint must be sha256 followed by 64 hexadecimal characters",
                path=relative,
                observed=fingerprint,
            )

        reference_id = receipt.get("reference_id")
        has_reference = not blank(reference_id) and str(reference_id).upper() not in {"NONE", "N/A", "NOT-APPLICABLE"}
        if has_reference:
            for field in REFERENCE_FIELDS:
                if blank(receipt.get(field)):
                    add(checks, "BLOCK", "REGISTRATION_REQUIRED_FIELD", f"reference field is blank: {field}", path=relative, field=field)
            if str(reference_id) == str(receipt.get("candidate_id")):
                add(checks, "BLOCK", "SELF_REFERENCE", "candidate cannot validate itself", path=relative, stable_id=str(reference_id))
            if not registry_relative:
                add(checks, "BLOCK", "MISSING_STABLE_ID_REGISTRY", "a reference requires stable_id_registry in policy", path=relative)
            elif str(reference_id) not in registry:
                add(checks, "BLOCK", "UNKNOWN_REFERENCE_ID", "reference ID is absent from registry", path=relative, stable_id=str(reference_id))
            else:
                reference_entry = registry[str(reference_id)]
                for field in ("observable_id", "unit_id"):
                    expected = reference_entry.get(field)
                    observed = receipt.get(field)
                    if not blank(expected) and expected != observed:
                        add(checks, "BLOCK", "REFERENCE_IDENTITY_MISMATCH", f"{field} differs from reference registry", path=relative, field=field, expected=expected, observed=observed)
            litmus = receipt.get("reference_litmus")
            if not blank(litmus) and not resolve(project, str(litmus)).is_file():
                add(checks, "BLOCK", "MISSING_REFERENCE_LITMUS", "reference-litmus target is absent", path=relative, target=str(litmus))
            if receipt.get("same_observable_reference_checked") is not True:
                add(checks, "BLOCK", "REFERENCE_CHECK_NOT_COMPLETED", "a declared reference requires an exact same-observable check", path=relative)

        checklist = {
            "consumer_identity_recorded": {True},
            "same_observable_reference_checked": {True, "not-applicable"},
            "route_equal_control_status": {"completed", "not-applicable"},
            "self_reference_used_as_validation": {False},
            "user_named_raw_status": {"opened", "not-applicable"},
        }
        for field, allowed in checklist.items():
            value = receipt.get(field)
            if value not in allowed:
                add(checks, "BLOCK", "REGISTRATION_CHECKLIST", f"checklist field has no passing value: {field}", path=relative, field=field, observed=value, allowed=sorted(map(str, allowed)))

        profile = str(receipt.get("workflow_profile") or "core")
        if profile != "core":
            profile_rule = profiles.get(profile) if isinstance(profiles, dict) else None
            if not isinstance(profile_rule, dict):
                add(checks, "BLOCK", "UNKNOWN_REGISTRATION_PROFILE", "receipt names an undeclared workflow profile", path=relative, profile=profile)
            else:
                for field in profile_rule.get("required_fields", []):
                    if blank(receipt.get(field)):
                        add(checks, "BLOCK", "PROFILE_REQUIRED_FIELD", f"profile field is blank: {field}", path=relative, profile=profile, field=field)
                for field in profile_rule.get("path_fields", []):
                    value = receipt.get(field)
                    if not blank(value) and not resolve(project, str(value)).exists():
                        add(checks, "BLOCK", "PROFILE_PATH_MISSING", f"profile path does not exist: {field}", path=relative, profile=profile, field=field, target=str(value))

    counts = {
        severity: sum(1 for item in checks if item["severity"] == severity)
        for severity in ("BLOCK", "WARN", "INFO")
    }
    exit_code = 1 if counts["BLOCK"] else (2 if args.strict_warnings and counts["WARN"] else 0)
    report = {
        "audit": "research-document-audit",
        "tool_sha256": sha256(Path(__file__).resolve()),
        "runtime": {"python": platform.python_version(), "executable": sys.executable},
        "project_root": str(project),
        "policy": str(policy_path),
        "policy_sha256": sha256(policy_path),
        "ready": counts["BLOCK"] == 0,
        "exit_code": exit_code,
        "counts": counts,
        "documents": documents,
        "input_document_hashes": {
            relative: sha256(resolve(project, relative)) for relative in texts
        },
        "search_receipts": search_receipt_reports,
        "stable_id_registry": registry_info,
        "registration_receipts": registration_reports,
        "checks": checks,
        "human_review_required": bool(checks) or bool(policy.get("status_contracts")) or bool(registration_reports),
        "non_claim": "This audit detects documentary mechanics and semantic-risk candidates; it does not validate scientific truth.",
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--output")
    parser.add_argument("--strict-warnings", action="store_true")
    return audit(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
