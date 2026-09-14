#!/usr/bin/env python3
"""Smoke test for research_state.py on a synthetic project (known-good passes, known-bad is flagged)."""
import json, subprocess, sys, tempfile
from pathlib import Path
S = Path(__file__).resolve().parents[1] / "scripts" / "research_state.py"
def w(p, rows): p.parent.mkdir(parents=True, exist_ok=True); p.write_text("\n".join("\t".join(r) for r in rows) + "\n")
with tempfile.TemporaryDirectory() as td:
    P = Path(td); ev = P / "ev.md"; ev.write_text("x")
    w(P/"research_organization/DIRECTION_REGISTRY.tsv", [["direction_id","period_start","period_end","title","lane","question","status","current_unit_id","parent_direction_id","edge_type","canonical_owner","claim_ceiling","next_gate","topic_tags"],["D-1","","","dir one","L","why","OPEN","U-1","","","","c","g",""]])
    w(P/"research_organization/UNIT_EXPERIMENT_REGISTRY.tsv", [["unit_id","direction_id","title","question","test_case","promotion_verdict","claim_ceiling","primary_evidence","next_gate"],["U-1","D-1","unit one","does lambda improve Si","Si","PASS","electronic only","ev.md","open P1B"],["U-2","D-9","orphan","q","t","OPEN","","missing/x.md",""]])
    w(P/"research_organization/ATTEMPT_REGISTRY.tsv", [["attempt_id","unit_id","timestamp_utc","job_id","operational_status","scientific_role","notes","runbook_or_receipt","result_or_failure_audit"],["A-1","U-1","2026-09-01T00:00:00Z","1","COMPLETED","producer","","ev.md","ev.md"]])
    r = subprocess.run([sys.executable, str(S), "--project", td, "--json", "lint"], capture_output=True, text=True)
    items = json.loads(r.stdout); det = " ".join(i["detail"] for i in items)
    assert r.returncode == 1 and "D-9" in det and "missing/x.md" in det and "U-2 has no claim ceiling" in det, det
    r = subprocess.run([sys.executable, str(S), "--project", td, "status"], capture_output=True, text=True); assert "open directions (1)" in r.stdout and "U-1" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(S), "--project", td, "show", "U-1"], capture_output=True, text=True); assert "children (1)" in r.stdout and "A-1" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(S), "--project", td, "repeat-check", "does lambda improve Si electronic"], capture_output=True, text=True); assert "U-1" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(S), "--project", td, "register", "attempt", "--field", "unit_id=U-1", "--field", "job_id=777", "--field", "operational_status=RUNNING", "--field", "timestamp_utc=2026-09-12T00:00:00Z"], capture_output=True, text=True); assert "registered attempt   A-1-777" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(S), "--project", td, "register", "unit", "--field", "direction_id=D-1", "--field", "title=no ceiling"], capture_output=True, text=True); assert "requires claim_ceiling" in (r.stdout + r.stderr)
    r = subprocess.run([sys.executable, str(S), "--project", td, "update", "A-1-777", "--set", "operational_status=COMPLETED"], capture_output=True, text=True); assert "updated attempt A-1-777" in r.stdout, r.stdout
    r = subprocess.run([sys.executable, str(S), "--project", td, "update", "U-1", "--set", "question=x"], capture_output=True, text=True); assert "refused" in r.stdout
    assert (P / "STATE.md").exists() and "research_state:begin" in (P / "STATE.md").read_text() and (P / "research_organization/STATE_CHANGELOG.tsv").exists()
    r = subprocess.run([sys.executable, str(S), "--project", td, "flow", "--detail", "D-1"], capture_output=True, text=True); assert "A-1-777" in r.stdout and "big picture" in r.stdout, r.stdout
    print("research_state smoke test: PASS")
