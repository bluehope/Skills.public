#!/usr/bin/env python3
"""Build a self-contained decision-oriented research history view from TSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable


REQUIRED = (
    "event_id", "sequence", "timestamp_utc", "question_id", "branch_id",
    "unit_id", "test_case_id", "contract_id", "lane", "intervention",
    "factor_family", "comparator_id", "metric_id", "metric_value",
    "metric_unit", "metric_direction", "gate_value", "baseline_value",
    "comparison_tolerance", "expected_relation", "scientific_status",
    "decision", "artifact_path", "note",
)
OPTIONAL = (
    "metric_role", "mechanism_verdict", "promotion_verdict",
    "branch_disposition", "closure_basis", "closure_scope",
    "closure_argument_path", "failed_gate_id", "surviving_claim",
    "revisit_trigger", "next_gate", "parent_event_id", "edge_type",
)
EXPECTED = {"BETTER", "WORSE", "NO-CHANGE", "UNCERTAIN"}
DIRECTIONS = {"MIN", "MAX"}
DEFAULT_ELIGIBLE = {"VALID", "ACCEPTED", "GATE-PASS"}
METRIC_ROLES = {
    "PRIMARY-PROMOTION", "MECHANISM-DIAGNOSTIC", "GUARDRAIL", "SANITY-CONTROL",
}
MECHANISM_VERDICTS = {"SUPPORTED", "CONTRADICTED", "MIXED", "UNRESOLVED"}
PROMOTION_VERDICTS = {"PASSED", "FAILED", "NOT-TESTED"}
BRANCH_DISPOSITIONS = {
    "ACTIVE", "PAUSED", "DEPRIORITIZED", "MERGED", "BLOCKED", "HARD-CLOSED",
    "HISTORICAL-SCOPED",
}
CLOSURE_BASES = {
    "FORMAL-DERIVATION", "EXACT-PHYSICAL-LAW", "CONTRACT-PROOF",
    "SCOPED-EMPIRICAL", "HEURISTIC", "OPERATIONAL",
}
EDGE_TYPES = {
    "SUPPORTS-MECHANISM", "CONTRADICTS", "FALSIFIES-WITHIN-SCOPE",
    "BLOCKS-PROMOTION", "DEPRIORITIZES", "REQUIRES", "REOPENS",
    "SUPERSEDES", "OUT-OF-SCOPE",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def optional_float(value: str, field: str, event_id: str) -> float | None:
    if not value.strip():
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{event_id}: {field} must be numeric or empty") from exc
    if not math.isfinite(number):
        raise ValueError(f"{event_id}: {field} must be finite")
    return number


def load_events(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        missing = [field for field in REQUIRED if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {', '.join(missing)}")
        events: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        seen_sequences: set[int] = set()
        for line_number, raw in enumerate(reader, start=2):
            event_id = raw["event_id"].strip()
            if not event_id:
                raise ValueError(f"line {line_number}: empty event_id")
            if event_id in seen_ids:
                raise ValueError(f"duplicate event_id: {event_id}")
            try:
                sequence = int(raw["sequence"])
            except ValueError as exc:
                raise ValueError(f"{event_id}: sequence must be an integer") from exc
            if sequence in seen_sequences:
                raise ValueError(f"duplicate sequence: {sequence}")
            direction = raw["metric_direction"].strip().upper()
            expected = raw["expected_relation"].strip().upper()
            if direction not in DIRECTIONS:
                raise ValueError(f"{event_id}: metric_direction must be MIN or MAX")
            if expected not in EXPECTED:
                raise ValueError(
                    f"{event_id}: expected_relation must be one of {sorted(EXPECTED)}"
                )
            event: dict[str, object] = {
                key: (raw.get(key) or "").strip() for key in REQUIRED + OPTIONAL
            }
            event["sequence"] = sequence
            event["metric_direction"] = direction
            event["expected_relation"] = expected
            for field in ("metric_value", "gate_value", "baseline_value", "comparison_tolerance"):
                event[field] = optional_float(raw[field], field, event_id)
            validate_decision_semantics(event)
            event["observed_relation"], event["surprise_class"] = classify(event)
            events.append(event)
            seen_ids.add(event_id)
            seen_sequences.add(sequence)
    if not events:
        raise ValueError("history snapshot contains no events")
    ordered = sorted(events, key=lambda item: int(item["sequence"]))
    validate_edges(ordered)
    return ordered


def validate_choice(event: dict[str, object], field: str, allowed: set[str]) -> None:
    value = str(event[field])
    if value and value not in allowed:
        raise ValueError(f'{event["event_id"]}: {field} must be one of {sorted(allowed)}')


def validate_decision_semantics(event: dict[str, object]) -> None:
    validate_choice(event, "metric_role", METRIC_ROLES)
    validate_choice(event, "mechanism_verdict", MECHANISM_VERDICTS)
    validate_choice(event, "promotion_verdict", PROMOTION_VERDICTS)
    validate_choice(event, "branch_disposition", BRANCH_DISPOSITIONS)
    validate_choice(event, "closure_basis", CLOSURE_BASES)
    validate_choice(event, "edge_type", EDGE_TYPES)
    disposition = str(event["branch_disposition"])
    basis = str(event["closure_basis"])
    if disposition == "HARD-CLOSED":
        if basis not in {"FORMAL-DERIVATION", "EXACT-PHYSICAL-LAW"}:
            raise ValueError(
                f'{event["event_id"]}: HARD-CLOSED requires FORMAL-DERIVATION '
                "or EXACT-PHYSICAL-LAW"
            )
        for field in ("closure_scope", "closure_argument_path"):
            if not str(event[field]):
                raise ValueError(f'{event["event_id"]}: HARD-CLOSED requires {field}')
    if disposition == "DEPRIORITIZED":
        if basis != "HEURISTIC":
            raise ValueError(
                f'{event["event_id"]}: DEPRIORITIZED requires closure_basis HEURISTIC'
            )
        if not str(event["revisit_trigger"]):
            raise ValueError(
                f'{event["event_id"]}: DEPRIORITIZED requires revisit_trigger'
            )


def validate_edges(events: list[dict[str, object]]) -> None:
    by_id = {str(event["event_id"]): event for event in events}
    for event in events:
        event_id = str(event["event_id"])
        parent_id = str(event["parent_event_id"])
        edge_type = str(event["edge_type"])
        if edge_type and not parent_id:
            raise ValueError(f"{event_id}: edge_type requires parent_event_id")
        if parent_id and not edge_type:
            raise ValueError(f"{event_id}: parent_event_id requires edge_type")
        if not parent_id:
            continue
        if parent_id not in by_id:
            raise ValueError(f"{event_id}: unknown parent_event_id {parent_id}")
        if parent_id == event_id:
            raise ValueError(f"{event_id}: self-edge is not allowed")
        parent_sequence = int(by_id[parent_id]["sequence"])
        if parent_sequence >= int(event["sequence"]):
            raise ValueError(
                f"{event_id}: parent_event_id {parent_id} must have an earlier sequence"
            )


def classify(event: dict[str, object]) -> tuple[str, str]:
    value = event["metric_value"]
    baseline = event["baseline_value"]
    expected = str(event["expected_relation"])
    if value is None or baseline is None:
        return "NOT-COMPARABLE", "INCOMPARABLE"
    tolerance = event["comparison_tolerance"] or 0.0
    raw_delta = float(value) - float(baseline)
    if abs(raw_delta) <= float(tolerance):
        observed = "NO-CHANGE"
    elif (event["metric_direction"] == "MAX" and raw_delta > 0) or (
        event["metric_direction"] == "MIN" and raw_delta < 0
    ):
        observed = "BETTER"
    else:
        observed = "WORSE"
    if expected == "UNCERTAIN":
        surprise = "NO-PRIOR"
    elif expected == observed:
        surprise = "AS-EXPECTED"
    elif {expected, observed} == {"BETTER", "WORSE"}:
        surprise = "DIRECTION-REVERSAL"
    elif observed == "BETTER":
        surprise = "BETTER-THAN-EXPECTED"
    else:
        surprise = "WORSE-THAN-EXPECTED"
    return observed, surprise


def group_by(items: Iterable[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in items:
        grouped.setdefault(str(item[key]), []).append(item)
    return grouped


def consistent(rows: list[dict[str, object]], fields: Iterable[str], unit_id: str) -> None:
    for field in fields:
        values = {str(row[field]) for row in rows}
        if len(values) > 1:
            raise ValueError(f"unit {unit_id}: incompatible {field}: {sorted(values)}")


def fmt(value: object) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def summarize(events: list[dict[str, object]], eligible: set[str]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for unit_id, rows in group_by(events, "unit_id").items():
        consistent(
            rows,
            ("question_id", "branch_id", "test_case_id", "contract_id", "metric_id",
             "metric_unit", "metric_direction", "comparator_id"),
            unit_id,
        )
        numeric = [
            row for row in rows
            if row["metric_value"] is not None and str(row["scientific_status"]) in eligible
        ]
        values = [float(row["metric_value"]) for row in numeric]
        direction = str(rows[0]["metric_direction"])
        best_row = None
        if numeric:
            best_row = (max if direction == "MAX" else min)(
                numeric, key=lambda row: float(row["metric_value"])
            )
        baselines = [float(row["baseline_value"]) for row in numeric if row["baseline_value"] is not None]
        baseline = statistics.median(baselines) if baselines else None
        median_value = statistics.median(values) if values else None
        improvement = None
        if baseline is not None and median_value is not None:
            improvement = median_value - baseline if direction == "MAX" else baseline - median_value
        surprises = [
            row for row in rows
            if row["surprise_class"] not in {"AS-EXPECTED", "NO-PRIOR"}
        ]
        latest = max(rows, key=lambda row: int(row["sequence"]))
        summaries.append({
            "unit_id": unit_id,
            "first_sequence": min(int(row["sequence"]) for row in rows),
            "last_sequence": max(int(row["sequence"]) for row in rows),
            "question_id": rows[0]["question_id"],
            "branch_id": rows[0]["branch_id"],
            "test_case_id": rows[0]["test_case_id"],
            "contract_id": rows[0]["contract_id"],
            "metric_id": rows[0]["metric_id"],
            "metric_unit": rows[0]["metric_unit"],
            "metric_direction": direction,
            "comparator_id": rows[0]["comparator_id"],
            "factor_families": ", ".join(sorted({str(row["factor_family"]) for row in rows})),
            "expected_relations": ", ".join(sorted({str(row["expected_relation"]) for row in rows})),
            "observed_relations": ", ".join(sorted({str(row["observed_relation"]) for row in rows})),
            "status_mix": ", ".join(
                f"{status}:{sum(str(row['scientific_status']) == status for row in rows)}"
                for status in sorted({str(row["scientific_status"]) for row in rows})
            ),
            "attempt_count": len(rows),
            "eligible_count": len(numeric),
            "baseline_median": baseline,
            "metric_median": median_value,
            "best_value": best_row["metric_value"] if best_row else None,
            "best_event_id": best_row["event_id"] if best_row else "",
            "direction_aware_delta": improvement,
            "surprise_count": len(surprises),
            "latest_event_id": latest["event_id"],
            "latest_decision": latest["decision"],
            "latest_artifact": latest["artifact_path"],
            "metric_role": latest["metric_role"],
            "mechanism_verdict": latest["mechanism_verdict"],
            "promotion_verdict": latest["promotion_verdict"],
            "branch_disposition": latest["branch_disposition"],
            "closure_basis": latest["closure_basis"],
            "closure_scope": latest["closure_scope"],
            "closure_argument_path": latest["closure_argument_path"],
            "failed_gate_id": latest["failed_gate_id"],
            "surviving_claim": latest["surviving_claim"],
            "revisit_trigger": latest["revisit_trigger"],
            "next_gate": latest["next_gate"],
            "parent_event_id": latest["parent_event_id"],
            "edge_type": latest["edge_type"],
        })
    return sorted(summaries, key=lambda item: int(item["first_sequence"]))


def select_current(
    summaries: list[dict[str, object]], current_unit_id: str,
) -> tuple[dict[str, object] | None, str]:
    current_unit_id = current_unit_id.strip()
    if current_unit_id:
        matches = [item for item in summaries if str(item["unit_id"]) == current_unit_id]
        if not matches:
            raise ValueError(f"unknown current unit: {current_unit_id}")
        return matches[0], "EXPLICIT"
    active = [item for item in summaries if str(item["branch_disposition"]) == "ACTIVE"]
    if len(active) == 1:
        return active[0], "INFERRED-SINGLE-ACTIVE"
    if active:
        return None, "UNKNOWN-MULTIPLE-ACTIVE"
    return None, "UNKNOWN-NO-ACTIVE"


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: "" if row.get(field) in (None, "") else fmt(row[field])
                for field in fields
            })


def artifact_link(path: object, label: str = "artifact") -> str:
    target = str(path)
    if not target:
        return "—"
    return f'<a href="{html.escape(target, quote=True)}">{html.escape(label)}</a>'


def metric_panel(
    key: tuple[str, str, str, str, str],
    rows: list[dict[str, object]],
    eligible: set[str],
) -> str:
    numeric = [row for row in rows if row["metric_value"] is not None]
    if not numeric:
        return ""
    width, height, left, right, top, bottom = 900, 260, 70, 20, 24, 48
    sequences = [int(row["sequence"]) for row in numeric]
    values = [float(row["metric_value"]) for row in numeric]
    references = [
        float(row[field]) for row in numeric for field in ("baseline_value", "gate_value")
        if row[field] is not None
    ]
    ymin, ymax = min(values + references), max(values + references)
    if math.isclose(ymin, ymax):
        pad = abs(ymin) * 0.05 or 1.0
        ymin, ymax = ymin - pad, ymax + pad
    xmin, xmax = min(sequences), max(sequences)
    if xmin == xmax:
        xmin, xmax = xmin - 1, xmax + 1
    x = lambda seq: left + (seq - xmin) * (width - left - right) / (xmax - xmin)
    y = lambda val: top + (ymax - val) * (height - top - bottom) / (ymax - ymin)
    palette = ("#2563eb", "#059669", "#d97706", "#7c3aed", "#db2777", "#0891b2")
    families = {name: palette[index % len(palette)] for index, name in enumerate(sorted({str(row["factor_family"]) for row in rows}))}
    svg = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="metric history">']
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>')
    svg.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>')
    for field, css, label in (("baseline_value", "baseline", "baseline"), ("gate_value", "gate", "gate")):
        refs = [float(row[field]) for row in numeric if row[field] is not None]
        if refs and all(math.isclose(refs[0], value) for value in refs[1:]):
            yy = y(refs[0])
            svg.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" class="{css}"/>')
            svg.append(f'<text x="{width-right-4}" y="{yy-4:.1f}" text-anchor="end">{label} {fmt(refs[0])}</text>')
    for row in numeric:
        color = families[str(row["factor_family"])]
        status = html.escape(str(row["scientific_status"]))
        surprise = html.escape(str(row["surprise_class"]))
        title = html.escape(
            f'{row["event_id"]}: {fmt(row["metric_value"])} {row["metric_unit"]}; '
            f'{status}; {surprise}'
        )
        css = "point muted" if str(row["scientific_status"]) not in eligible else "point"
        svg.append(
            f'<a href="{html.escape(str(row["artifact_path"]), quote=True)}">'
            f'<circle cx="{x(int(row["sequence"])):.1f}" cy="{y(float(row["metric_value"])):.1f}" '
            f'r="5" fill="{color}" class="{css}"><title>{title}</title></circle></a>'
        )
    svg.append(f'<text x="{left}" y="{top-6}">{fmt(ymax)} {html.escape(key[2])}</text>')
    svg.append(f'<text x="{left}" y="{height-8}">sequence {xmin}</text>')
    svg.append(f'<text x="{width-right}" y="{height-8}" text-anchor="end">{xmax}</text>')
    svg.append("</svg>")
    legend = " ".join(
        f'<span class="legend"><i style="background:{color}"></i>{html.escape(name)}</span>'
        for name, color in families.items()
    )
    roles = sorted({str(row["metric_role"]) for row in rows if str(row["metric_role"])})
    role_text = ", ".join(roles) or "role unknown"
    return (
        f'<section><h3>{html.escape(key[0])} · {html.escape(key[1])}</h3>'
        f'<p class="subtle">contract {html.escape(key[3])} · comparator '
        f'{html.escape(key[4])} · metric unit {html.escape(key[2])} · '
        f'{html.escape(role_text)}</p>'
        + "".join(svg) + f'<p>{legend}</p></section>'
    )


def semantic_fmt(value: object) -> str:
    return "UNKNOWN" if value in (None, "") else fmt(value)


def verdict_cell(label: str, value: object) -> str:
    return (
        '<div class="verdict">'
        f'<span>{html.escape(label)}</span><strong>{html.escape(semantic_fmt(value))}</strong>'
        '</div>'
    )


def edge_label(parent: dict[str, object], child: dict[str, object]) -> str:
    edge_type = str(child["edge_type"])
    css_class = edge_type.lower()
    relation = (
        f'Relation {parent["event_id"]} ({parent["unit_id"]}) → '
        f'{child["event_id"]} ({child["unit_id"]}): {edge_type}'
    )
    return (
        f'<div class="edge-label edge-{html.escape(css_class, quote=True)}">'
        f'<span class="sr-only">Research relationship: </span>{html.escape(relation)}'
        '</div>'
    )


def render_html(
    title: str,
    source: Path,
    source_hash: str,
    cutoff: str,
    events: list[dict[str, object]],
    summaries: list[dict[str, object]],
    eligible: set[str],
    current_item: dict[str, object] | None,
    current_source: str,
) -> str:
    events_by_id = {str(event["event_id"]): event for event in events}
    incoming_by_unit: dict[str, list[tuple[dict[str, object], dict[str, object]]]] = {}
    for event in events:
        parent_id = str(event["parent_event_id"])
        if parent_id:
            incoming_by_unit.setdefault(str(event["unit_id"]), []).append(
                (events_by_id[parent_id], event)
            )
    route: list[str] = []
    for item in summaries:
        basis = str(item["closure_basis"])
        disposition = str(item["branch_disposition"])
        classes = ["unit"]
        if disposition == "HARD-CLOSED":
            classes.append("hard-closed")
        elif basis == "HEURISTIC":
            classes.append("heuristic")
        elif disposition in {"PAUSED", "BLOCKED", "HISTORICAL-SCOPED"}:
            classes.append("paused")
        details = []
        if item["failed_gate_id"]:
            details.append(f'failed gate: {html.escape(str(item["failed_gate_id"]))}')
        if item["surviving_claim"]:
            details.append(f'survives: {html.escape(str(item["surviving_claim"]))}')
        if item["revisit_trigger"]:
            details.append(f'revisit: {html.escape(str(item["revisit_trigger"]))}')
        if item["next_gate"]:
            details.append(f'next: {html.escape(str(item["next_gate"]))}')
        relations = "".join(
            edge_label(parent, child)
            for parent, child in incoming_by_unit.get(str(item["unit_id"]), [])
        )
        parts = [
            f'<article class="{" ".join(classes)}">',
            f'<div class="eyebrow">seq {item["first_sequence"]}–{item["last_sequence"]} · {html.escape(str(item["branch_id"]))}</div>',
            relations,
            f'<h3>{html.escape(str(item["unit_id"]))}</h3>',
            f'<p>{html.escape(str(item["question_id"]))} · {html.escape(str(item["test_case_id"]))}</p>',
            '<div class="verdict-grid">',
            verdict_cell("Mechanism", item["mechanism_verdict"]),
            verdict_cell("Promotion", item["promotion_verdict"]),
            verdict_cell("Branch", item["branch_disposition"]),
            verdict_cell("Basis", item["closure_basis"]),
            '</div>',
            f'<p>{html.escape(str(item["factor_families"]))} · {html.escape(str(item["expected_relations"]))} → {html.escape(str(item["observed_relations"]))}</p>',
            f'<p><b>{fmt(item["metric_median"])}</b> median; <b>{fmt(item["best_value"])}</b> best ({html.escape(str(item["metric_unit"]))})</p>',
            f'<p>{item["attempt_count"]} attempts · {item["surprise_count"]} surprises · {html.escape(str(item["latest_decision"]) or "no decision")}</p>',
        ]
        if details:
            parts.append(f'<p class="decision-detail">{" · ".join(details)}</p>')
        parts.extend([f'<p>{artifact_link(item["latest_artifact"])}</p>', '</article>'])
        route.append("".join(parts))
    panels: dict[tuple[str, str, str, str, str], list[dict[str, object]]] = {}
    for event in events:
        key = (
            str(event["test_case_id"]), str(event["metric_id"]),
            str(event["metric_unit"]), str(event["contract_id"]),
            str(event["comparator_id"]),
        )
        panels.setdefault(key, []).append(event)
    plots = "".join(metric_panel(key, rows, eligible) for key, rows in sorted(panels.items()))
    summary_rows = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape(fmt(item[field]))}</td>" for field in (
                "unit_id", "test_case_id", "factor_families", "attempt_count",
                "eligible_count", "expected_relations", "observed_relations",
                "metric_median", "best_value", "direction_aware_delta",
                "mechanism_verdict", "promotion_verdict", "branch_disposition",
                "closure_basis", "failed_gate_id", "surprise_count", "latest_decision",
            )
        ) + f'<td>{artifact_link(item["latest_artifact"])}</td></tr>'
        for item in summaries
    )
    surprising = [event for event in events if event["surprise_class"] not in {"AS-EXPECTED", "NO-PRIOR"}]
    surprise_rows = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape(fmt(event[field]))}</td>" for field in (
                "sequence", "event_id", "unit_id", "intervention", "expected_relation",
                "observed_relation", "surprise_class", "scientific_status", "decision",
            )
        ) + f'<td>{artifact_link(event["artifact_path"])}</td></tr>'
        for event in surprising
    ) or '<tr><td colspan="10">No classified surprises at this cutoff.</td></tr>'
    if current_item is None:
        active_count = sum(
            str(item["branch_disposition"]) == "ACTIVE" for item in summaries
        )
        current = "".join([
            '<section class="current current-unknown"><div>',
            f'<p class="eyebrow">Current decision · {html.escape(current_source)}</p>',
            '<h2>CURRENT UNKNOWN</h2>',
            f'<p class="current-claim">No explicit current unit and {active_count} ACTIVE units.</p>',
            '<p>Provide <code>--current-unit-id</code> or resolve the active frontier.</p>',
            '</div><div class="verdict-grid current-verdicts">',
            verdict_cell("Mechanism", ""), verdict_cell("Promotion", ""),
            verdict_cell("Branch", ""), verdict_cell("Basis", ""),
            '</div></section>',
        ])
    else:
        current_claim = str(
            current_item["surviving_claim"] or current_item["latest_decision"]
        )
        current = "".join([
            '<section class="current"><div>',
            f'<p class="eyebrow">Current decision · {html.escape(current_source)} · '
            f'{html.escape(str(current_item["unit_id"]))} · seq {current_item["last_sequence"]}</p>',
            f'<h2>{html.escape(str(current_item["question_id"]))}</h2>',
            f'<p class="current-claim">{html.escape(current_claim or "No current claim recorded")}</p>',
            f'<p><b>Next gate:</b> {html.escape(semantic_fmt(current_item["next_gate"]))}</p></div>',
            '<div class="verdict-grid current-verdicts">',
            verdict_cell("Mechanism", current_item["mechanism_verdict"]),
            verdict_cell("Promotion", current_item["promotion_verdict"]),
            verdict_cell("Branch", current_item["branch_disposition"]),
            verdict_cell("Basis", current_item["closure_basis"]),
            '</div></section>',
        ])
    frontier = [
        item for item in summaries
        if str(item["branch_disposition"]) in {"ACTIVE", "PAUSED", "DEPRIORITIZED", "BLOCKED"}
    ]
    frontier_rows = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape(fmt(item[field]))}</td>" for field in (
                "branch_id", "mechanism_verdict", "promotion_verdict",
                "branch_disposition", "closure_basis", "next_gate",
            )
        ) + f'<td>{artifact_link(item["latest_artifact"])}</td></tr>'
        for item in frontier
    ) or '<tr><td colspan="7">No active or revisit-able unit recorded.</td></tr>'
    decision_rows = "".join(
        "<tr>" + "".join(
            f"<td>{html.escape(fmt(event[field]))}</td>" for field in (
                "sequence", "timestamp_utc", "branch_id", "unit_id", "decision",
                "mechanism_verdict", "promotion_verdict", "branch_disposition",
                "closure_basis", "next_gate",
            )
        ) + f'<td>{artifact_link(event["artifact_path"])}</td></tr>'
        for event in sorted(events, key=lambda item: int(item["sequence"]), reverse=True)
    )
    css = """
    :root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f4f7fb}
    body{max-width:1180px;margin:auto;padding:28px} h1{margin-bottom:4px} h2{margin-top:34px}
    .subtle,.eyebrow{color:#617087}.eyebrow{text-transform:uppercase;font-size:.75rem;letter-spacing:.05em}
    .summary{display:flex;gap:12px;flex-wrap:wrap}.pill{background:#e8eef8;border-radius:999px;padding:8px 12px}
    .current{display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,.75fr);gap:20px;border-left:6px solid #2563eb;margin-top:20px}.current h2{margin:2px 0 8px}.current-claim{font-size:1.1rem}
    .current-unknown{border-left-color:#b45309}
    .timeline{position:relative;margin:12px 0 0 18px;padding:2px 0 2px 34px}.timeline:before{content:"";position:absolute;left:8px;top:0;bottom:0;width:2px;background:#b9c6d8}.unit{position:relative;margin:0 0 16px}.unit:before{content:"";position:absolute;left:-42px;top:24px;width:14px;height:14px;border:3px solid #2563eb;border-radius:50%;background:#f4f7fb}.unit:after{content:"↓";position:absolute;left:-40px;bottom:-18px;color:#718198}.unit:last-child:after{display:none}.unit.hard-closed{border-left:6px double #7f1d1d}.unit.hard-closed:before{border-color:#7f1d1d}.unit.heuristic{border-left:5px dashed #a16207}.unit.heuristic:before{border-style:dashed;border-color:#a16207}.unit.paused{border-left:5px solid #64748b}.unit.paused:before{border-color:#64748b}
    .unit,section{background:white;border:1px solid #dbe3ef;border-radius:12px;padding:16px;box-shadow:0 2px 8px #1020400c}
    .verdict-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.verdict{border-top:2px solid #cad5e5;padding-top:5px}.verdict span{display:block;color:#617087;font-size:.72rem;text-transform:uppercase}.verdict strong{font-size:.82rem;word-break:break-word}.decision-detail{border-left:3px solid #cbd5e1;padding-left:10px;color:#475569}
    .edge-label{display:block;margin:8px 0;padding:6px 9px;border-left:5px solid #475569;background:#f8fafc;font-size:.8rem}.edge-deprioritizes{border-left-style:dashed;border-left-color:#a16207}.edge-falsifies-within-scope{border-left-style:double;border-left-width:7px;border-left-color:#991b1b}.edge-blocks-promotion{border-left-color:#7e22ce}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    table{width:100%;border-collapse:collapse;background:white;font-size:.88rem}th,td{padding:9px;border:1px solid #dbe3ef;text-align:left;vertical-align:top}th{background:#eaf0f8;position:sticky;top:0}
    .scroll{overflow:auto}.axis{stroke:#53627a;stroke-width:1}.baseline{stroke:#53627a;stroke-dasharray:5 4}.gate{stroke:#dc2626;stroke-dasharray:8 4}.point{stroke:white;stroke-width:1.5}.muted{opacity:.35}svg text{font-size:11px;fill:#53627a}.legend{margin-right:14px}.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:4px}
    a{color:#1d4ed8}@media(max-width:720px){body{padding:14px}th,td{padding:6px}.current{grid-template-columns:1fr}.verdict-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.timeline{margin-left:8px;padding-left:28px}.unit:before{left:-36px}}
    """
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head><body>
    <header><h1>{html.escape(title)}</h1><p class="subtle">Decision-oriented research trail · evidence cutoff {html.escape(cutoff or 'unspecified')} · source SHA-256 {source_hash[:12]}…</p>
    <div class="summary"><span class="pill">{len(events)} attempts</span><span class="pill">{len(summaries)} unit experiments</span><span class="pill">{len(surprising)} surprises</span></div></header>{current}
    <h2>Active frontier</h2><div class="scroll"><table><thead><tr><th>Branch</th><th>Mechanism</th><th>Promotion</th><th>Disposition</th><th>Closure basis</th><th>Next gate</th><th>Evidence</th></tr></thead><tbody>{frontier_rows}</tbody></table></div>
    <h2>How we got here</h2><p class="subtle">Chronological top-to-bottom trail. Promotion failure, mechanism verdict, and branch closure are independent.</p><div class="timeline">{''.join(route)}</div>
    <h2>Compatible metric histories</h2>{plots or '<p>No numeric metrics.</p>'}
    <h2>Unit-experiment scorecard</h2><div class="scroll"><table><thead><tr><th>Unit</th><th>Test case</th><th>Factor family</th><th>Attempts</th><th>Eligible</th><th>Expected</th><th>Observed</th><th>Median</th><th>Best</th><th>Δ better</th><th>Mechanism</th><th>Promotion</th><th>Disposition</th><th>Closure basis</th><th>Failed gate</th><th>Surprises</th><th>Decision</th><th>Evidence</th></tr></thead><tbody>{summary_rows}</tbody></table></div>
    <h2>Surprises and incomparable results</h2><div class="scroll"><table><thead><tr><th>Seq</th><th>Event</th><th>Unit</th><th>Intervention</th><th>Expected</th><th>Observed</th><th>Class</th><th>Status</th><th>Decision</th><th>Evidence</th></tr></thead><tbody>{surprise_rows}</tbody></table></div>
    <h2>Decision log</h2><p class="subtle">Newest first. Operational logs belong in a separate lower section when supplied by the project.</p><div class="scroll"><table><thead><tr><th>Seq</th><th>Time</th><th>Branch</th><th>Unit</th><th>Decision</th><th>Mechanism</th><th>Promotion</th><th>Disposition</th><th>Basis</th><th>Next gate</th><th>Evidence</th></tr></thead><tbody>{decision_rows}</tbody></table></div>
    <footer><p class="subtle">Rendered from {html.escape(str(source))}. This view does not replace the experiment ledger, design authority, or immutable evidence artifacts.</p></footer></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="normalized history TSV")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--title", default="Research Trail")
    parser.add_argument("--evidence-cutoff", default="")
    parser.add_argument(
        "--current-unit-id", default="",
        help="explicit current unit from the state capsule or living decision owner",
    )
    parser.add_argument("--eligible-status", action="append", default=[])
    args = parser.parse_args()
    try:
        events = load_events(args.input.resolve())
        eligible = set(args.eligible_status) or DEFAULT_ELIGIBLE
        summaries = summarize(events, eligible)
        current_item, current_source = select_current(summaries, args.current_unit_id)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        source_hash = sha256(args.input)
        summary_fields = list(summaries[0].keys())
        write_tsv(args.output_dir / "unit-summary.tsv", summaries, summary_fields)
        surprising = [event for event in events if event["surprise_class"] not in {"AS-EXPECTED", "NO-PRIOR"}]
        surprise_fields = list(REQUIRED) + list(OPTIONAL) + ["observed_relation", "surprise_class"]
        write_tsv(args.output_dir / "surprises.tsv", surprising, surprise_fields)
        index = args.output_dir / "index.html"
        index.write_text(
            render_html(
                args.title, args.input.resolve(), source_hash, args.evidence_cutoff,
                events, summaries, eligible, current_item, current_source,
            ),
            encoding="utf-8",
        )
        outputs = [index, args.output_dir / "unit-summary.tsv", args.output_dir / "surprises.tsv"]
        manifest = {
            "schema_version": 2,
            "generator": str(Path(__file__).resolve()),
            "source": str(args.input.resolve()),
            "source_sha256": source_hash,
            "evidence_cutoff": args.evidence_cutoff or None,
            "attempt_count": len(events),
            "unit_experiment_count": len(summaries),
            "surprise_count": len(surprising),
            "eligible_statuses": sorted(eligible),
            "current_selection": {
                "source": current_source,
                "unit_id": current_item["unit_id"] if current_item else None,
            },
            "outputs": {path.name: sha256(path) for path in outputs},
        }
        (args.output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"attempts": len(events), "units": len(summaries), "output": str(index)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
