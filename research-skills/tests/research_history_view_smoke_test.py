#!/usr/bin/env python3
"""Known-answer and fail-closed tests for the research history renderer."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_research_history_view.py"
FIELDS = (ROOT / "assets" / "research-history-snapshot-template.tsv").read_text(
    encoding="utf-8"
).strip().split("\t")
V1_FIELDS = FIELDS[:24]


def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str] = FIELDS) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def minimal_row(event_id: str, sequence: int, unit_id: str) -> dict[str, str]:
    return {
        "event_id": event_id, "sequence": str(sequence),
        "timestamp_utc": f"2026-08-16T00:{sequence:02d}:00Z",
        "question_id": "Q-STATE", "branch_id": unit_id.replace("U-", "B-"),
        "unit_id": unit_id, "test_case_id": "TC-STATE", "contract_id": "C-STATE",
        "lane": "EXPLORATORY", "intervention": event_id,
        "factor_family": "state", "comparator_id": "base",
        "metric_id": "state:loss", "metric_value": "1", "metric_unit": "1",
        "metric_direction": "MIN", "gate_value": "0.8", "baseline_value": "1.2",
        "comparison_tolerance": "0", "expected_relation": "BETTER",
        "scientific_status": "VALID", "decision": "CONTINUE",
        "artifact_path": f"artifacts/{event_id}.json", "note": "",
    }


def write_fixture(path: Path, duplicate: bool = False) -> None:
    common = {
        "timestamp_utc": "2026-08-16T00:00:00Z", "question_id": "Q-1",
        "branch_id": "B-A", "test_case_id": "TC-1", "contract_id": "C-1",
        "lane": "EXPLORATORY", "factor_family": "optimizer", "comparator_id": "base-v1",
        "metric_id": "eval-v1:loss", "metric_unit": "1", "metric_direction": "MIN",
        "gate_value": "0.8", "baseline_value": "1.0", "comparison_tolerance": "0.01",
        "scientific_status": "VALID", "artifact_path": "artifacts/result.json", "note": "",
        "metric_role": "MECHANISM-DIAGNOSTIC", "mechanism_verdict": "SUPPORTED",
        "promotion_verdict": "FAILED", "branch_disposition": "PAUSED",
        "closure_basis": "SCOPED-EMPIRICAL", "failed_gate_id": "G-PROMOTE",
        "surviving_claim": "mechanism direction remains supported",
        "revisit_trigger": "independent physical parameter becomes available",
        "next_gate": "bounded diagnostic continuation",
    }
    rows = [
        common | {"event_id": "E-001", "sequence": "1", "unit_id": "U-1",
                  "intervention": "optimizer-a", "metric_value": "0.9",
                  "expected_relation": "BETTER", "decision": "CONTINUE"},
        common | {"event_id": "E-002", "sequence": "2", "unit_id": "U-1",
                  "intervention": "optimizer-b", "metric_value": "1.2",
                  "expected_relation": "BETTER", "decision": "FOCUS"},
        common | {"event_id": "E-002" if duplicate else "E-003", "sequence": "3",
                  "unit_id": "U-2", "intervention": "optimizer-c", "metric_value": "0.7",
                  "expected_relation": "UNCERTAIN", "decision": "PROMOTE-CANDIDATE",
                  "comparator_id": "base-v2", "branch_id": "B-HEURISTIC",
                  "promotion_verdict": "NOT-TESTED", "branch_disposition": "DEPRIORITIZED",
                  "closure_basis": "HEURISTIC", "failed_gate_id": "",
                  "surviving_claim": "direction remains plausible",
                  "revisit_trigger": "cheaper discriminator or contrary evidence",
                  "next_gate": "revisit only on trigger", "parent_event_id": "E-002",
                  "edge_type": "DEPRIORITIZES"},
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_large_fixture(path: Path) -> None:
    rows = []
    for index in range(1, 121):
        rows.append({
            "event_id": f"E-{index:03d}", "sequence": str(index),
            "timestamp_utc": f"2026-08-{1 + (index - 1) // 20:02d}T00:00:00Z",
            "question_id": "Q-LONG", "branch_id": "B-MAIN",
            "unit_id": f"U-{1 + (index - 1) // 10:02d}", "test_case_id": "TC-ROBUST",
            "contract_id": "C-1" if index <= 60 else "C-2", "lane": "EXPLORATORY",
            "intervention": f"variant-{index:03d}",
            "factor_family": ("optimizer", "augmentation", "architecture")[index % 3],
            "comparator_id": "base-v1" if index <= 60 else "base-v2",
            "metric_id": "eval-v1:loss" if index <= 60 else "eval-v2:loss",
            "metric_value": f"{1.0 - index / 1000:.3f}", "metric_unit": "1",
            "metric_direction": "MIN", "gate_value": "0.85", "baseline_value": "1.0",
            "comparison_tolerance": "0.001", "expected_relation": "BETTER",
            "scientific_status": "VALID", "decision": "CONTINUE",
            "artifact_path": f"artifacts/E-{index:03d}/result.json", "note": "",
            "metric_role": "PRIMARY-PROMOTION", "mechanism_verdict": "UNRESOLVED",
            "promotion_verdict": "NOT-TESTED", "branch_disposition": "ACTIVE",
            "closure_basis": "", "next_gate": "next bounded unit",
        })
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_v1_fixture(path: Path) -> None:
    row = {
        "event_id": "E-V1", "sequence": "1", "timestamp_utc": "2026-08-01T00:00:00Z",
        "question_id": "Q-V1", "branch_id": "B-V1", "unit_id": "U-V1",
        "test_case_id": "TC-V1", "contract_id": "C-V1", "lane": "EXPLORATORY",
        "intervention": "legacy", "factor_family": "legacy", "comparator_id": "base",
        "metric_id": "legacy:loss", "metric_value": "1", "metric_unit": "1",
        "metric_direction": "MIN", "gate_value": "0.5", "baseline_value": "1.2",
        "comparison_tolerance": "0", "expected_relation": "BETTER",
        "scientific_status": "VALID", "decision": "CONTINUE",
        "artifact_path": "artifacts/legacy.json", "note": "v1 schema",
    }
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=V1_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def write_closure_fixture(path: Path, basis: str, revisit: str = "") -> None:
    common = {
        "event_id": "E-CLOSE", "sequence": "1", "timestamp_utc": "2026-08-16T00:00:00Z",
        "question_id": "Q-CLOSE", "branch_id": "B-CLOSE", "unit_id": "U-CLOSE",
        "test_case_id": "TC-CLOSE", "contract_id": "C-CLOSE", "lane": "CONFIRMATORY",
        "intervention": "rank proof", "factor_family": "formal", "comparator_id": "exact",
        "metric_id": "proof:rank", "metric_value": "0", "metric_unit": "1",
        "metric_direction": "MIN", "gate_value": "0", "baseline_value": "1",
        "comparison_tolerance": "0", "expected_relation": "BETTER",
        "scientific_status": "VALID", "decision": "CLOSE", "artifact_path": "proof.md",
        "note": "", "metric_role": "MECHANISM-DIAGNOSTIC",
        "mechanism_verdict": "CONTRADICTED", "promotion_verdict": "NOT-TESTED",
        "branch_disposition": "HARD-CLOSED", "closure_basis": basis,
        "closure_scope": "declared finite-dimensional mapping",
        "closure_argument_path": "proof.md", "revisit_trigger": revisit,
    }
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerow(common)


def write_state_transition_fixture(path: Path) -> None:
    earlier = minimal_row("E-OLD", 1, "U-STATE") | {
        "mechanism_verdict": "SUPPORTED", "promotion_verdict": "FAILED",
        "branch_disposition": "DEPRIORITIZED", "closure_basis": "HEURISTIC",
        "revisit_trigger": "new evidence", "next_gate": "wait",
    }
    current = minimal_row("E-CURRENT", 2, "U-STATE") | {
        "branch_disposition": "ACTIVE", "mechanism_verdict": "",
        "promotion_verdict": "", "closure_basis": "", "revisit_trigger": "",
        "next_gate": "",
    }
    write_rows(path, [earlier, current])


def write_two_active_fixture(path: Path) -> None:
    rows = [
        minimal_row("E-ACTIVE-1", 1, "U-A") | {"branch_disposition": "ACTIVE"},
        minimal_row("E-ACTIVE-2", 2, "U-B") | {"branch_disposition": "ACTIVE"},
    ]
    write_rows(path, rows)


def write_explicit_current_fixture(path: Path) -> None:
    rows = [
        minimal_row("E-MAIN", 1, "U-MAIN") | {
            "branch_disposition": "ACTIVE", "next_gate": "main next gate",
        },
        minimal_row("E-AUX", 2, "U-AUX") | {
            "branch_disposition": "PAUSED", "closure_basis": "SCOPED-EMPIRICAL",
            "surviving_claim": "auxiliary branch paused",
        },
    ]
    write_rows(path, rows)


def write_edge_fixture(
    path: Path, parent_id: str, edge_type: str,
    parent_sequence: int = 1, child_sequence: int = 2,
) -> None:
    rows = [
        minimal_row("E-PARENT", parent_sequence, "U-PARENT"),
        minimal_row("E-CHILD", child_sequence, "U-CHILD") | {
            "parent_event_id": parent_id, "edge_type": edge_type,
        },
    ]
    write_rows(path, rows)


def write_edge_style_fixture(path: Path) -> None:
    rows = [minimal_row("E-ROOT", 1, "U-ROOT")]
    for sequence, edge_type in enumerate(
        ("DEPRIORITIZES", "FALSIFIES-WITHIN-SCOPE", "BLOCKS-PROMOTION"), start=2
    ):
        rows.append(minimal_row(f"E-{sequence}", sequence, f"U-{sequence}") | {
            "parent_event_id": "E-ROOT", "edge_type": edge_type,
        })
    write_rows(path, rows)


def run(
    source: Path, output: Path, current_unit_id: str = "",
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable, str(SCRIPT), "--input", str(source), "--output-dir", str(output),
        "--title", "Known Answer Trail", "--evidence-cutoff", "2026-08-16T01:00:00Z",
    ]
    if current_unit_id:
        command.extend(["--current-unit-id", current_unit_id])
    return subprocess.run(
        command,
        capture_output=True, text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "history.tsv"
        output = root / "view"
        write_fixture(source)
        passed = run(source, output, current_unit_id="U-1")
        assert passed.returncode == 0, passed.stdout + passed.stderr
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["schema_version"] == 2
        assert manifest["attempt_count"] == 3
        assert manifest["unit_experiment_count"] == 2
        assert manifest["surprise_count"] == 1
        assert manifest["current_selection"] == {"source": "EXPLICIT", "unit_id": "U-1"}
        page = (output / "index.html").read_text(encoding="utf-8")
        assert "How we got here" in page and "DIRECTION-REVERSAL" in page
        assert "Current decision" in page and "Active frontier" in page
        assert "SUPPORTED" in page and "FAILED" in page
        assert "DEPRIORITIZED" in page and "HEURISTIC" in page
        assert "EXPLICIT · U-1" in page
        assert "Relation E-002 (U-1) → E-003 (U-2): DEPRIORITIZES" in page
        assert "edge-deprioritizes" in page
        assert page.index("U-1") < page.index("U-2")
        assert "comparator base-v1" in page and "comparator base-v2" in page
        assert "self-contained" not in page.lower() or "<script src=" not in page

        edge_styles = root / "edge-styles.tsv"
        edge_styles_output = root / "edge-styles-view"
        write_edge_style_fixture(edge_styles)
        edge_styles_run = run(edge_styles, edge_styles_output)
        assert edge_styles_run.returncode == 0, edge_styles_run.stdout + edge_styles_run.stderr
        edge_styles_page = (edge_styles_output / "index.html").read_text(encoding="utf-8")
        for edge_type in (
            "DEPRIORITIZES", "FALSIFIES-WITHIN-SCOPE", "BLOCKS-PROMOTION",
        ):
            assert f": {edge_type}" in edge_styles_page
            assert f'edge-{edge_type.lower()}' in edge_styles_page

        invalid = root / "duplicate.tsv"
        write_fixture(invalid, duplicate=True)
        failed = run(invalid, root / "invalid-view")
        assert failed.returncode == 2
        assert "duplicate event_id" in failed.stderr

        legacy = root / "legacy-v1.tsv"
        write_v1_fixture(legacy)
        legacy_run = run(legacy, root / "legacy-view")
        assert legacy_run.returncode == 0, legacy_run.stdout + legacy_run.stderr
        legacy_page = (root / "legacy-view" / "index.html").read_text(encoding="utf-8")
        assert "How we got here" in legacy_page and "CURRENT UNKNOWN" in legacy_page
        legacy_manifest = json.loads(
            (root / "legacy-view" / "manifest.json").read_text(encoding="utf-8")
        )
        assert legacy_manifest["current_selection"] == {
            "source": "UNKNOWN-NO-ACTIVE", "unit_id": None,
        }
        with (root / "legacy-view" / "unit-summary.tsv").open(
            encoding="utf-8", newline=""
        ) as stream:
            legacy_summary = next(csv.DictReader(stream, delimiter="\t"))
        assert legacy_summary["mechanism_verdict"] == ""
        assert legacy_summary["branch_disposition"] == ""

        transition = root / "state-transition.tsv"
        transition_output = root / "state-transition-view"
        write_state_transition_fixture(transition)
        transition_run = run(transition, transition_output)
        assert transition_run.returncode == 0, transition_run.stdout + transition_run.stderr
        with (transition_output / "unit-summary.tsv").open(
            encoding="utf-8", newline=""
        ) as stream:
            transition_summary = next(csv.DictReader(stream, delimiter="\t"))
        assert transition_summary["branch_disposition"] == "ACTIVE"
        assert transition_summary["mechanism_verdict"] == ""
        assert transition_summary["promotion_verdict"] == ""
        assert transition_summary["closure_basis"] == ""
        assert transition_summary["next_gate"] == ""
        transition_page = (transition_output / "index.html").read_text(encoding="utf-8")
        assert "INFERRED-SINGLE-ACTIVE · U-STATE" in transition_page
        current_block = transition_page.split("Current decision", 1)[1].split("</section>", 1)[0]
        assert "ACTIVE" in current_block and "UNKNOWN" in current_block
        assert "HEURISTIC" not in current_block

        multiple_active = root / "multiple-active.tsv"
        multiple_output = root / "multiple-active-view"
        write_two_active_fixture(multiple_active)
        multiple_run = run(multiple_active, multiple_output)
        assert multiple_run.returncode == 0, multiple_run.stdout + multiple_run.stderr
        multiple_page = (multiple_output / "index.html").read_text(encoding="utf-8")
        assert "CURRENT UNKNOWN" in multiple_page
        multiple_manifest = json.loads(
            (multiple_output / "manifest.json").read_text(encoding="utf-8")
        )
        assert multiple_manifest["current_selection"] == {
            "source": "UNKNOWN-MULTIPLE-ACTIVE", "unit_id": None,
        }

        explicit_current = root / "explicit-current.tsv"
        explicit_output = root / "explicit-current-view"
        write_explicit_current_fixture(explicit_current)
        explicit_run = run(explicit_current, explicit_output, "U-MAIN")
        assert explicit_run.returncode == 0, explicit_run.stdout + explicit_run.stderr
        explicit_page = (explicit_output / "index.html").read_text(encoding="utf-8")
        explicit_block = explicit_page.split("Current decision", 1)[1].split(
            "</section>", 1
        )[0]
        assert "EXPLICIT · U-MAIN" in explicit_block
        assert "main next gate" in explicit_block
        assert "U-AUX" not in explicit_block

        unknown_parent = root / "unknown-parent.tsv"
        write_edge_fixture(unknown_parent, "E-MISSING", "REQUIRES")
        unknown_parent_run = run(unknown_parent, root / "unknown-parent-view")
        assert unknown_parent_run.returncode == 2
        assert "unknown parent_event_id" in unknown_parent_run.stderr

        edge_without_parent = root / "edge-without-parent.tsv"
        write_edge_fixture(edge_without_parent, "", "BLOCKS-PROMOTION")
        edge_without_parent_run = run(edge_without_parent, root / "edge-without-parent-view")
        assert edge_without_parent_run.returncode == 2
        assert "edge_type requires parent_event_id" in edge_without_parent_run.stderr

        parent_without_edge = root / "parent-without-edge.tsv"
        write_edge_fixture(parent_without_edge, "E-PARENT", "")
        parent_without_edge_run = run(parent_without_edge, root / "parent-without-edge-view")
        assert parent_without_edge_run.returncode == 2
        assert "parent_event_id requires edge_type" in parent_without_edge_run.stderr

        self_edge = root / "self-edge.tsv"
        write_edge_fixture(self_edge, "E-CHILD", "REQUIRES")
        self_edge_run = run(self_edge, root / "self-edge-view")
        assert self_edge_run.returncode == 2
        assert "self-edge is not allowed" in self_edge_run.stderr

        reverse_edge = root / "reverse-edge.tsv"
        write_edge_fixture(reverse_edge, "E-PARENT", "REQUIRES", 3, 2)
        reverse_edge_run = run(reverse_edge, root / "reverse-edge-view")
        assert reverse_edge_run.returncode == 2
        assert "must have an earlier sequence" in reverse_edge_run.stderr

        unknown_current = run(source, root / "unknown-current-view", "U-MISSING")
        assert unknown_current.returncode == 2
        assert "unknown current unit" in unknown_current.stderr

        formal = root / "formal.tsv"
        write_closure_fixture(formal, "FORMAL-DERIVATION")
        formal_run = run(formal, root / "formal-view")
        assert formal_run.returncode == 0, formal_run.stdout + formal_run.stderr
        formal_page = (root / "formal-view" / "index.html").read_text(encoding="utf-8")
        assert "HARD-CLOSED" in formal_page and "FORMAL-DERIVATION" in formal_page

        invalid_closure = root / "invalid-closure.tsv"
        write_closure_fixture(invalid_closure, "SCOPED-EMPIRICAL")
        invalid_closure_run = run(invalid_closure, root / "invalid-closure-view")
        assert invalid_closure_run.returncode == 2
        assert "HARD-CLOSED requires" in invalid_closure_run.stderr

        large = root / "large-history.tsv"
        write_large_fixture(large)
        large_output = root / "large-view"
        scaled = run(large, large_output)
        assert scaled.returncode == 0, scaled.stdout + scaled.stderr
        scaled_manifest = json.loads(
            (large_output / "manifest.json").read_text(encoding="utf-8")
        )
        assert scaled_manifest["attempt_count"] == 120
        assert scaled_manifest["unit_experiment_count"] == 12
        large_page = (large_output / "index.html").read_text(encoding="utf-8")
        assert large_page.count("<circle") == 120
        assert "contract C-1" in large_page and "contract C-2" in large_page

    print("research history view smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
