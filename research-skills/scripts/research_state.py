#!/usr/bin/env python3
"""Research state API over project registries (stdlib only).

  research_state.py status        [--project P]   compact current-state capsule (open directions, units, gates, last milestones)
  research_state.py show ID       [--project P]   one row by stable id + children + cross-references, bounded
  research_state.py lint          [--project P]   referential integrity, duplicates, required fields, dead evidence paths
  research_state.py find TERM     [--project P]   bounded rg locators across registries and declared search roots
  research_state.py repeat-check "question text"  units/attempts most similar to a proposed question (repeat guard)
  research_state.py init-schema   [--project P]   write research_state_schema.json (default layout) for a new project
  research_state.py adopt         [--project P] [--apply]  bring an unmanaged project under management: scaffold the minimal
                                   registry set (empty, with headers incl. milestone_type), STATE.md capsule, and a
                                   DOCUMENT_CATALOG seeded from existing Markdown/TSV/JSON files (dry run by default)

Schema: <project>/research_state_schema.json declares registries, id/parent/status columns and search roots.
Read commands emit bounded locators. Write commands stage, validate and journal
changes; use --help for document, view, refresh, validate and recovery commands."""
from __future__ import annotations
import argparse, csv, json, os, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

def _skill_version():
    try:
        return (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"
SKILL_VERSION = _skill_version()

DEFAULT_SCHEMA = {
  "schema_version": 1,
  "registries": {
    "direction": {"path": "research_organization/DIRECTION_REGISTRY.tsv", "id": "direction_id", "parent": "parent_direction_id", "status": "status", "title": "title", "text": ["question"], "child_of": None, "pointer": "current_unit_id", "pointer_to": "unit"},
    "unit":      {"path": "research_organization/UNIT_EXPERIMENT_REGISTRY.tsv", "id": "unit_id", "parent": "direction_id", "status": "promotion_verdict", "title": "title", "text": ["question", "test_case"], "child_of": "direction", "paths": ["primary_evidence"], "gate": "next_gate", "ceiling": "claim_ceiling"},
    "attempt":   {"path": "research_organization/ATTEMPT_REGISTRY.tsv", "id": "attempt_id", "parent": "unit_id", "status": "operational_status", "title": "scientific_role", "text": ["notes"], "child_of": "unit", "paths": ["runbook_or_receipt", "result_or_failure_audit"]},
    "document":  {"path": "research_organization/DOCUMENT_CATALOG.tsv", "id": "document_id", "parent": "unit_id", "status": "status", "title": "title", "text": ["role"], "child_of": "unit", "paths": ["path"]},
    "milestone": {"path": "research_dashboard/MILESTONE_HISTORY.tsv", "id": "milestone", "parent": None, "status": "verdict", "title": "question", "text": ["observation", "preserved_claim"], "child_of": None, "gate": "next_gate", "type": "milestone_type"},
    "claim":     {"path": "research_dashboard/CLAIM_REGISTER.tsv", "id": "claim_id", "parent": None, "status": "epistemic_status", "title": "claim", "text": ["condition_fingerprint"], "child_of": None, "paths": ["evidence_locator"]}
  },
  "open_status_exclude": ["TERMINAL", "CLOSED", "RETIRED", "SUPERSEDED", "ARCHIVED"],
  "search_roots": ["research_organization", "research_dashboard", "plans", "campaigns", "results", "interpretations", "decisions", "ops_knowhow"],
  "search_exclude": ["**/views/**", "**/*.html", "**/archive*/**"],
  "path_bases": [".", ".."],
  "tgrep_index": None,
  "capsule_max_lines": 120
}

def load_schema(project: Path):
    p = project / "research_state_schema.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else DEFAULT_SCHEMA

def read_tsv(path: Path):
    if not path.exists(): return [], []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t"); cols = reader.fieldnames or []; rows = list(reader)
    if len(cols) != len(set(cols)) or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("malformed TSV: " + str(path))
    return cols, rows

class State:
    def __init__(self, project: Path):
        self.project = project; self.schema = load_schema(project); self.reg = {}
        for name, spec in self.schema["registries"].items():
            cols, rows = read_tsv(project / spec["path"])
            self.reg[name] = {"spec": spec, "cols": cols, "rows": rows, "by_id": {r.get(spec["id"], ""): (i + 2, r) for i, r in enumerate(rows)}}
    def locate(self, sid):
        for name, r in self.reg.items():
            if sid in r["by_id"]: return name, r["by_id"][sid][0], r["by_id"][sid][1]
        return None, None, None
    def children(self, name, sid):
        out = []
        for cname, r in self.reg.items():
            if r["spec"].get("child_of") == name:
                pc = r["spec"]["parent"]
                out += [(cname, x.get(r["spec"]["id"], ""), x) for x in r["rows"] if x.get(pc) == sid]
        return out
    def is_open(self, status):
        s = (status or "").upper()
        return not any(k in s for k in self.schema["open_status_exclude"])
    def path_exists(self, pth: str) -> bool:
        return any((root / b / pth).exists() for root in (self.project, getattr(self, "source_project", self.project)) for b in self.schema.get("path_bases", ["."]))

def trunc(s, n=110):
    s = (s or "").replace("\n", " ").strip(); return s if len(s) <= n else s[:n-1] + "…"

def cmd_status(st: State, a):
    L = []
    L.append("project: %s" % getattr(st, "source_project", st.project))
    rec = (st.schema.get("managed_by") or {}).get("version", "unrecorded")
    L.append("managed by: research-skills %s (tool %s)%s" % (rec, SKILL_VERSION, "" if rec in (SKILL_VERSION, "unrecorded") else "  [version drift: rerun render to restamp]"))
    L.append("registries: " + ", ".join("%s=%d" % (n, len(r["rows"])) for n, r in st.reg.items() if r["rows"]))
    d = st.reg.get("direction"); u = st.reg.get("unit")
    if d and d["rows"]:
        opened = [r for r in d["rows"] if st.is_open(r.get(d["spec"]["status"]))]
        L.append(""); L.append("open directions (%d):" % len(opened))
        for r in opened:
            did = r[d["spec"]["id"]]; cur = r.get(d["spec"].get("pointer") or "", "")
            L.append("  %-28s %-34s current=%s" % (did, trunc(r.get(d["spec"]["status"]), 34), cur))
            if u and cur in u["by_id"]:
                ur = u["by_id"][cur][1]
                L.append("     unit %-22s verdict=%s gate=%s" % (cur, trunc(ur.get(u["spec"]["status"]), 30), trunc(ur.get(u["spec"].get("gate", ""), ""), 70)))
                if u["spec"].get("ceiling"): L.append("     ceiling: %s" % trunc(ur.get(u["spec"]["ceiling"], ""), 100))
    if u and u["rows"]:
        c = Counter(trunc(r.get(u["spec"]["status"]), 30) or "(empty)" for r in u["rows"])
        L.append(""); L.append("unit verdicts: " + ", ".join("%s×%d" % kv for kv in c.most_common(8)))
    at = st.reg.get("attempt")
    if at and at["rows"]:
        c = Counter(r.get(at["spec"]["status"], "") or "(empty)" for r in at["rows"])
        L.append("attempts: " + ", ".join("%s×%d" % kv for kv in c.most_common(6)))
    m = st.reg.get("milestone")
    if m and m["rows"]:
        L.append(""); L.append("last milestones:")
        for r in m["rows"][:5]:
            L.append("  %-10s %-14s %s" % (r.get(m["spec"]["id"]), trunc(r.get(m["spec"]["status"]), 14), trunc(r.get(m["spec"]["title"]), 90)))
            if r.get(m["spec"].get("gate", ""), ""): L.append("             next: %s" % trunc(r.get(m["spec"]["gate"]), 90))
        if m["spec"].get("type") and m["spec"]["type"] not in m["cols"]:
            L.append("  (no %s column yet; achievements are not separable from history)" % m["spec"]["type"])
    lint = run_lint(st); L.append(""); L.append("lint: %d BLOCK, %d WARN  (research_state.py lint for details)" % (sum(1 for x in lint if x[0]=="BLOCK"), sum(1 for x in lint if x[0]=="WARN")))
    L = L[: st.schema.get("capsule_max_lines", 120)]
    print(json.dumps({"lines": L}, ensure_ascii=False) if a.json else "\n".join(L)); return 0

def cmd_show(st: State, a):
    name, line, row = st.locate(a.id)
    if not name: print("no registry row with id", a.id); return 1
    spec = st.reg[name]["spec"]; out = {"registry": name, "locator": "%s:%d" % (spec["path"], line), "row": {}}
    for k, v in row.items():
        if v: out["row"][k] = v if a.full else trunc(v, 160)
    kids = st.children(name, a.id)
    out["children"] = [{"registry": c, "id": cid, "status": trunc(x.get(st.reg[c]["spec"]["status"]), 30), "title": trunc(x.get(st.reg[c]["spec"]["title"]), 80)} for c, cid, x in kids]
    refs = []
    for rname, r in st.reg.items():
        if rname == name: continue
        for i, x in enumerate(r["rows"]):
            if any(a.id in (v or "") for k, v in x.items() if k != r["spec"]["id"]):
                refs.append({"registry": rname, "id": x.get(r["spec"]["id"]), "locator": "%s:%d" % (r["spec"]["path"], i + 2)})
    out["referenced_by"] = refs[:20]
    missing = []
    for col in spec.get("paths", []):
        for pth in re.split(r"[;,\s]+", row.get(col, "") or ""):
            if pth and not pth.startswith(("http", "qmd://")) and not st.path_exists(pth): missing.append(pth)
    if missing: out["missing_paths"] = missing
    if a.json: print(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        print("[%s] %s  @ %s" % (name, a.id, out["locator"]))
        for k, v in out["row"].items(): print("  %-24s %s" % (k, v))
        if out["children"]: print("  children (%d):" % len(out["children"])); [print("    %-9s %-30s %-28s %s" % (c["registry"], c["id"], c["status"], c["title"])) for c in out["children"]]
        if refs: print("  referenced by (%d shown):" % len(out["referenced_by"])); [print("    %-9s %-30s %s" % (x["registry"], x["id"], x["locator"])) for x in out["referenced_by"]]
        if missing: print("  MISSING paths: " + ", ".join(missing))
    return 0

def run_lint(st: State):
    items = []
    for name, r in st.reg.items():
        spec = r["spec"]
        if not r["rows"]: items.append(("INFO", name, "registry absent or empty: " + spec["path"])); continue
        ids = [x.get(spec["id"], "") for x in r["rows"]]
        for i, v in enumerate(ids):
            if not v: items.append(("BLOCK", name, "empty id at %s:%d" % (spec["path"], i + 2)))
        for dup, n in Counter(ids).items():
            if dup and n > 1: items.append(("BLOCK", name, "duplicate id %s ×%d" % (dup, n)))
        parent = spec.get("parent"); pname = spec.get("child_of")
        if parent and pname and pname in st.reg:
            for i, x in enumerate(r["rows"]):
                pv = x.get(parent, "")
                if pv and pv not in st.reg[pname]["by_id"]: items.append(("BLOCK", name, "%s -> %s %r not in %s registry (%s:%d)" % (x.get(spec["id"]), parent, pv, pname, spec["path"], i + 2)))
                if not pv: items.append(("WARN", name, "%s has empty %s" % (x.get(spec["id"]), parent)))
        if spec.get("pointer") and spec.get("pointer_to") in st.reg:
            for x in r["rows"]:
                pv = x.get(spec["pointer"], "")
                if pv and pv not in st.reg[spec["pointer_to"]]["by_id"]: items.append(("BLOCK", name, "%s.%s=%r not found" % (x.get(spec["id"]), spec["pointer"], pv)))
        for col in spec.get("paths", []):
            for i, x in enumerate(r["rows"]):
                for pth in re.split(r"[;,\s]+", x.get(col, "") or ""):
                    if pth and not pth.startswith(("http", "qmd://", "<")) and "/" in pth and not re.fullmatch(r"[\d/]+", pth) and not st.path_exists(pth):
                        items.append(("WARN", name, "%s: %s path missing: %s" % (x.get(spec["id"]), col, pth)))
        if spec.get("ceiling"):
            for x in r["rows"]:
                if not x.get(spec["ceiling"]): items.append(("WARN", name, "%s has no claim ceiling" % x.get(spec["id"])))
        if spec.get("type") and spec["type"] not in r["cols"]: items.append(("INFO", name, "column %s absent (milestone_type not yet adopted)" % spec["type"]))
    u = st.reg.get("unit"); at = st.reg.get("attempt")
    if u and at and u["rows"] and at["rows"]:
        have = {x.get(at["spec"]["parent"]) for x in at["rows"]}
        for x in u["rows"]:
            if x.get(u["spec"]["id"]) not in have and st.is_open(x.get(u["spec"]["status"])): items.append(("WARN", "unit", "%s open with no registered attempt" % x.get(u["spec"]["id"])))
    import research_records
    items.extend(research_records.lint_metadata(st))
    return items

def cmd_lint(st: State, a):
    items = run_lint(st)
    if a.json: print(json.dumps([{"severity": s, "registry": r, "detail": d} for s, r, d in items], ensure_ascii=False, indent=1))
    else:
        c = Counter(s for s, _, _ in items); print("lint: " + ", ".join("%s=%d" % kv for kv in sorted(c.items())))
        for s, r, d in items:
            if s != "INFO" or a.verbose: print("%-5s %-9s %s" % (s, r, d))
    return 1 if any(s == "BLOCK" for s, _, _ in items) else 0

def cmd_find(st: State, a):
    roots = [st.project / p for p in st.schema["search_roots"] if (st.project / p).exists()]
    if not roots: print("ZERO-RESULT (no declared search roots exist)"); return 0
    cmd = ["rg", "-n", "-i", "-m", str(a.max), "--no-heading", "--color", "never"]
    for g in st.schema.get("search_exclude", []): cmd += ["--glob", "!" + g]
    cmd += ["--", a.term] + [str(r) for r in roots]
    if st.schema.get("tgrep_index") and Path(os.path.expanduser(st.schema["tgrep_index"])).exists() and a.tgrep:
        cmd = ["tgrep", "-n", "-m", str(a.max), "--index-path", os.path.expanduser(st.schema["tgrep_index"]), a.term] + [str(r) for r in roots]
    try: p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc: print("SEARCH-UNAVAILABLE:", exc); return 2
    if p.returncode not in (0, 1): print("SEARCH-ERROR:", p.stderr[:500]); return 2
    hits = defaultdict(list)
    for ln in p.stdout.splitlines():
        try: f, n, txt = ln.split(":", 2)
        except ValueError: continue
        rel = str(Path(f).resolve().relative_to(st.project.resolve())) if Path(f).resolve().is_relative_to(st.project.resolve()) else f
        ids = re.findall(r"\b(?:[UDA]-[A-Z0-9-]{3,}|R\d+-M\d+|CL-[A-Z0-9-]+|DOC-[A-Z0-9-]+)\b", txt)
        hits[rel].append((int(n), sorted(set(ids))[:4], trunc(txt, 100)))
    total = sum(len(v) for v in hits.values())
    print("find %r: %d hits in %d files (tier: %s)" % (a.term, total, len(hits), cmd[0]))
    for f, rows in sorted(hits.items(), key=lambda kv: -len(kv[1]))[: a.files]:
        print("  %s (%d)" % (f, len(rows)))
        for n, ids, txt in rows[: a.per_file]: print("    :%-5d %-32s %s" % (n, ",".join(ids), txt))
    if total == 0: print("  ZERO-RESULT (query/scope/tier: rg over %s)" % ", ".join(st.schema["search_roots"]))
    return 0

WORD = re.compile(r"[^\W_][\w-]{1,}", re.UNICODE)
def toks(s): return set(WORD.findall((s or "").lower()))

def cmd_repeat(st: State, a):
    q = toks(a.text); scored = []
    for name in ("unit", "attempt", "milestone", "direction"):
        r = st.reg.get(name)
        if not r or not r["rows"]: continue
        spec = r["spec"]
        for x in r["rows"]:
            bag = toks(" ".join([x.get(spec["title"], "")] + [x.get(c, "") for c in spec.get("text", [])]))
            if not bag: continue
            j = len(q & bag) / max(1, len(q | bag)); ov = len(q & bag)
            if ov >= 3: scored.append((j, ov, name, x.get(spec["id"]), trunc(x.get(spec["status"]), 28), trunc(x.get(spec["title"]), 80)))
    scored.sort(reverse=True)
    print("repeat-check for: %s" % trunc(a.text, 120))
    if not scored: print("  no similar registered work (>=3 shared terms)"); return 0
    for j, ov, name, sid, status, title in scored[: a.top]:
        print("  %.2f %2d %-9s %-30s %-28s %s" % (j, ov, name, sid, status, title))
    print("  reopen the top ids with: research_state.py show <id>")
    return 0

def cmd_init(st: State, a):
    p = st.project / "research_state_schema.json"
    if p.exists() and not a.force: print("exists:", p); return 1
    p.write_text(json.dumps(DEFAULT_SCHEMA, indent=2)); print("wrote", p); return 0

HEADERS = {
    "direction": ["direction_id","period_start","period_end","title","lane","question","status","current_unit_id","parent_direction_id","edge_type","canonical_owner","claim_ceiling","next_gate","topic_tags"],
    "unit": ["unit_id","direction_id","period_start","period_end","title","question","test_case","contract_id","comparator_id","metric_id","metric_value","metric_unit","metric_direction","gate_value","mechanism_verdict","promotion_verdict","branch_disposition","closure_basis","claim_ceiling","primary_evidence","next_gate","primary_topic","topic_tags"],
    "attempt": ["attempt_id","unit_id","timestamp_utc","job_id","attempt_namespace","operational_status","scientific_role","source_runtime_fingerprint","runbook_or_receipt","result_or_failure_audit","primary","notes"],
    "document": ["document_id","unit_id","direction_id","role","status","title","path","authority","retention","topic_tags"],
    "milestone": ["milestone","milestone_type","question","observation","verdict","failure_class","preserved_claim","next_gate"],
    "claim": ["claim_id","epistemic_status","claim","condition_fingerprint","authority","evidence_locator","contradictor_or_falsifier","claim_ceiling","updated_kst"],
}
ROLE_GUESS = [("STATE", "state-capsule"), ("HANDOFF", "handoff"), ("README", "hub"), ("HUB", "hub"), ("DESIGN", "design"), ("DECISION", "decision"),
              ("AUDIT", "audit"), ("RESULT", "result"), ("RECEIPT", "receipt"), ("PLAN", "plan"), ("CONTRACT", "contract"), ("LEDGER", "ledger"), ("CHANGELOG", "history")]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".sync-backup", "archive", "views", "logs", "tmp", "generated"}

def cmd_adopt(st: State, a):
    P = st.project; plan = []
    schema = P / "research_state_schema.json"
    if not schema.exists(): plan.append(("write", schema, json.dumps(DEFAULT_SCHEMA, indent=2)))
    for name, spec in st.schema["registries"].items():
        p = P / spec["path"]
        if not p.exists() and name != "document":
            if name not in HEADERS: raise ValueError("custom registry needs existing header: " + name)
            plan.append(("write", p, "\t".join(HEADERS[name]) + "\n"))
    docs = []
    source = getattr(st, "source_project", P)
    for f in sorted(source.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".md", ".tsv", ".json", ".yaml", ".yml") : continue
        if any(part in SKIP_DIRS for part in f.relative_to(source).parts): continue
        rel = f.relative_to(source).as_posix()
        if rel.startswith(("research_organization/", "research_dashboard/")) or rel == "research_state_schema.json": continue
        up = f.stem.upper(); role = next((r for k, r in ROLE_GUESS if k in up), "unclassified")
        docs.append(("DOC-%03d" % (len(docs) + 1), rel, role, f.stem[:80]))
    cat = P / st.schema["registries"]["document"]["path"]
    if not cat.exists():
        body = "\t".join(HEADERS["document"]) + "\n" + "".join("\t".join([d, "", "", role, "INVENTORY-UNREVIEWED", title, rel, "UNKNOWN", "", ""]) + "\n" for d, rel, role, title in docs)
        plan.append(("write", cat, body))
    state = P / "STATE.md"
    if not state.exists() and not list(P.glob("*STATE*.md")):
        tpl = Path(__file__).resolve().parents[1] / "assets" / "state-capsule-template.md"
        plan.append(("write", state, tpl.read_text(encoding="utf-8") if tpl.exists() else "# STATE\n"))
    print("adopt plan for %s (%s):" % (P, "APPLY" if a.apply else "dry run"))
    for op, p, body in plan: print("  %-5s %-60s %d bytes" % (op, p.relative_to(P), len(body)))
    if docs: print("  document inventory: %d files (roles guessed: %s)" % (len(docs), ", ".join("%s×%d" % kv for kv in Counter(r for _, _, r, _ in docs).most_common(6))))
    if not plan: print("  nothing to do: already managed")
    if a.apply:
        for op, p, body in plan: p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body, encoding="utf-8")
        readme = P / "README.md"
        if not readme.exists(): readme.write_text("# Research project\n\nDescribe the objective here.\n\n- [Current state](STATE.md)\n- [Document links](research_dashboard/views/links.md)\n- [Timeline](research_dashboard/views/timeline.md)\n- [Context](research_dashboard/views/context.md)\n", encoding="utf-8")
        print("next: fill STATE.md, review DOCUMENT_CATALOG roles, register the first direction/unit, then run lint and status")
    return 0


# ---------------------------------------------------------------- write API (append-only) ----------------------------------------------------------------
IDENTITY_COLS = {"direction": {"direction_id"}, "unit": {"unit_id", "direction_id", "question", "contract_id", "comparator_id", "metric_id"},
                 "attempt": {"attempt_id", "unit_id", "job_id"}, "document": {"document_id", "path"}, "milestone": {"milestone", "question"}, "claim": {"claim_id", "claim"}}
ID_PREFIX = {"direction": "D", "unit": "U", "attempt": "A", "document": "DOC", "milestone": "M", "claim": "CL"}
CHANGELOG = "research_organization/STATE_CHANGELOG.tsv"

def clean(v): return re.sub(r"[\t\r\n]+", " ", str(v if v is not None else "")).strip()

def slug(s): return re.sub(r"[^\w-]+", "-", (s or "").upper()).strip("-")[:28] or "X"

def write_registry(st, kind):
    r = st.reg[kind]; p = st.project / r["spec"]["path"]
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=r["cols"], delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(r["rows"])

def next_id(st: State, kind: str, hint: str = ""):
    r = st.reg[kind]; spec = r["spec"]; ids = list(r["by_id"])
    if kind == "milestone":
        nums = [(m.group(1), int(m.group(2))) for i in ids for m in [re.match(r"^(R\d+-M)(\d+)$", i)] if m]
        if nums: pre, n = max(nums, key=lambda x: x[1]); return "%s%d" % (pre, n + 1)
        return "M-%03d" % (len(ids) + 1)
    base = "%s-%s" % (ID_PREFIX[kind], slug(hint)); cand = base; k = 2
    while cand in r["by_id"]: cand = "%s-%d" % (base, k); k += 1
    return cand

def append_row(st: State, kind: str, fields: dict):
    r = st.reg[kind]; spec = r["spec"]; path = st.project / spec["path"]
    if not path.exists() or not r["cols"]:
        cols = HEADERS[kind]; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("\t".join(cols) + "\n", encoding="utf-8"); r["cols"] = cols
    cols = r["cols"]; unknown = sorted(set(fields) - set(cols))
    if unknown: raise ValueError("unknown columns for %s: %s (allowed: %s)" % (kind, unknown, cols))
    hint = fields.get(spec.get("title") or "", "") or fields.get("question", "")
    if kind == "attempt": hint = "%s-%s" % (re.sub(r"^U-", "", fields.get("unit_id", "")), fields.get("job_id") or fields.get("timestamp_utc", "")[:10])
    if kind == "document": hint = Path(fields.get("path", "")).stem or hint
    idc = spec["id"]; sid = clean(fields.get(idc)) or next_id(st, kind, hint)
    if sid in r["by_id"]:
        oldline, old = r["by_id"][sid]
        if all(old.get(k, "") == clean(v) for k, v in fields.items()): return sid, "%s:%d" % (spec["path"], oldline)
        raise ValueError("%s %s already exists (use update)" % (kind, sid))
    parent = spec.get("parent"); pkind = spec.get("child_of")
    if parent and pkind and fields.get(parent) and fields[parent] not in st.reg[pkind]["by_id"]:
        raise ValueError("%s.%s=%r not found in %s registry" % (kind, parent, fields[parent], pkind))
    if spec.get("ceiling") and not fields.get(spec["ceiling"]): raise ValueError("%s requires %s" % (kind, spec["ceiling"]))
    if kind == "milestone" and "milestone_type" in cols and fields.get("milestone_type") not in ("ACHIEVEMENT", "NEGATIVE-FINDING", "METHOD", "INFRASTRUCTURE", "DECISION"):
        raise ValueError("milestone_type must be one of ACHIEVEMENT|NEGATIVE-FINDING|METHOD|INFRASTRUCTURE|DECISION")
    row = {c: clean(fields.get(c, "")) for c in cols}; row[idc] = sid
    with path.open("a", encoding="utf-8") as f: f.write("\t".join(row[c] for c in cols) + "\n")
    line = len(r["rows"]) + 2; r["rows"].append(row); r["by_id"][sid] = (line, row)
    log_change(st, kind, sid, "registered", "", json.dumps(row, ensure_ascii=False))
    return sid, "%s:%d" % (spec["path"], line)

def log_change(st: State, kind, sid, col, old, new, note=""):
    p = st.project / CHANGELOG; hdr = "timestamp_utc\tregistry\tid\tcolumn\told\tnew\tnote\n"
    if not p.exists(): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(hdr, encoding="utf-8")
    import datetime as _dt
    with p.open("a", encoding="utf-8") as f: f.write("\t".join([_dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), kind, sid, col, clean(old), clean(new), clean(note)]) + "\n")

def cmd_register(st: State, a):
    batch = []
    if a.batch:
        data = json.loads(Path(a.batch).read_text(encoding="utf-8")); batch = data if isinstance(data, list) else data.get("items", [])
    else:
        if not a.kind: print("kind required (or --batch)"); return 2
        fields = {}
        for kv in a.field or []:
            k, _, v = kv.partition("="); fields[k] = v
        batch = [{"kind": a.kind, **fields}]
    done = []
    for item in batch:
        kind = item.pop("kind"); sid, loc = append_row(st, kind, item); done.append((kind, sid, loc)); print("registered %-9s %-30s @ %s" % (kind, sid, loc))
    if done and not a.no_render: render_state(st); print("STATE.md updated")
    return 0

def cmd_update(st: State, a):
    kind, line, row = st.locate(a.id)
    if not kind: print("no row", a.id); return 1
    if kind == "document":
        print("use document --id for revisions; frozen records require a successor"); return 1
    spec = st.reg[kind]["spec"]; path = st.project / spec["path"]; cols = st.reg[kind]["cols"]
    changes = {}
    for kv in a.set: k, _, v = kv.partition("="); changes[k] = v
    allowed = set(spec.get("mutable_columns", ["status", "operational_status", "promotion_verdict", "mechanism_verdict", "verdict", "epistemic_status", "next_gate", "gate", "period_end", "branch_disposition", "disposition", "current_unit_id", "notes"]))
    bad = [k for k in changes if k in IDENTITY_COLS.get(kind, set()) or k not in cols or k not in allowed]
    if bad: print("refused: identity/unknown columns %s (register a new row instead)" % bad); return 1
    lines = path.read_text(encoding="utf-8").split("\n"); parts = lines[line - 1].split("\t")
    while len(parts) < len(cols): parts.append("")
    for k, v in changes.items():
        i = cols.index(k); log_change(st, kind, a.id, k, parts[i], v, a.note or ""); parts[i] = clean(v)
    lines[line - 1] = "\t".join(parts); path.write_text("\n".join(lines), encoding="utf-8")
    print("updated %s %s: %s  (history in %s)" % (kind, a.id, ", ".join("%s=%s" % kv for kv in changes.items()), CHANGELOG))
    if not a.no_render:
        source = getattr(st, "source_project", st.project)
        st.__init__(st.project); st.source_project = source
        render_state(st); print("STATE.md updated")
    return 0

BEGIN, END = "<!-- research_state:begin (generated; edit outside these markers) -->", "<!-- research_state:end -->"

def capture(fn, st, **kw):
    import io, contextlib
    class A: pass
    a = A(); a.json = False
    for k, v in kw.items(): setattr(a, k, v)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): fn(st, a)
    return buf.getvalue().rstrip()

def render_state(st: State):
    import datetime as _dt
    body = "\n".join([BEGIN, "", "_generated %s by research_state.py (research-skills %s); registries are the source of truth_" % (_dt.datetime.now().strftime("%Y-%m-%d %H:%M"), SKILL_VERSION), "",
                      "```text", capture(cmd_status, st), "```", "", "```text", capture(cmd_flow, st, detail=None, recent=8), "```", END])
    p = st.project / "STATE.md"
    if p.exists():
        t = p.read_text(encoding="utf-8")
        if BEGIN in t and END in t: t = t[: t.index(BEGIN)] + body + t[t.index(END) + len(END):]
        else: t = t.rstrip() + "\n\n## Current state (generated)\n\n" + body + "\n"
    else:
        t = "# STATE\n\n(manual notes above this line are preserved)\n\n## Current state (generated)\n\n" + body + "\n"
    p.write_text(t, encoding="utf-8")
    import research_records
    research_records.views(st)

def cmd_render(st: State, a): render_state(st); print("rendered", st.project / "STATE.md"); return 0

def cmd_version(st: State, a):
    rec = (st.schema.get("managed_by") or {}).get("version", "unrecorded")
    print("tool: research-skills %s" % SKILL_VERSION)
    print("project records: %s%s" % (rec, "" if rec in (SKILL_VERSION, "unrecorded") else "  (drift; a write op restamps)"))
    print(json.dumps(st.schema.get("managed_by", {}), ensure_ascii=False, indent=2))
    return 0

def cmd_flow(st: State, a):
    d = st.reg.get("direction"); u = st.reg.get("unit"); at = st.reg.get("attempt"); m = st.reg.get("milestone")
    L = ["== big picture: directions =="]
    if d and d["rows"]:
        kids = defaultdict(list)
        for r in d["rows"]: kids[r.get(d["spec"].get("parent") or "", "") or ""].append(r)
        def walk(pid, depth):
            for r in kids.get(pid, []):
                did = r[d["spec"]["id"]]; mark = "●" if st.is_open(r.get(d["spec"]["status"])) else "○"
                L.append("%s%s %-30s %-32s %s" % ("  " * depth, mark, did, trunc(r.get(d["spec"]["status"]), 32), trunc(r.get(d["spec"]["title"]), 60)))
                if depth < 6: walk(did, depth + 1)
        roots = [k for k in kids if k == "" or k not in d["by_id"]]
        for k in roots: walk(k, 0)
    else: L.append("  (no directions registered)")
    if getattr(a, "detail", None):
        did = a.detail; L.append(""); L.append("== detail: %s ==" % did)
        units = [x for x in (u["rows"] if u else []) if x.get(u["spec"]["parent"]) == did] if did in (d["by_id"] if d else {}) else ([u["by_id"][did][1]] if u and did in u["by_id"] else [])
        for x in units:
            uid = x[u["spec"]["id"]]
            L.append("  unit %-28s %-30s %s" % (uid, trunc(x.get(u["spec"]["status"]), 30), trunc(x.get(u["spec"]["title"]), 60)))
            L.append("       q: %s" % trunc(x.get("question", ""), 110))
            if x.get(u["spec"].get("gate", ""), ""): L.append("       gate: %s" % trunc(x.get(u["spec"]["gate"]), 100))
            for y in (at["rows"] if at else []):
                if y.get(at["spec"]["parent"]) == uid: L.append("       - %-32s %-10s %s" % (y[at["spec"]["id"]], trunc(y.get(at["spec"]["status"]), 10), trunc(y.get(at["spec"]["title"]), 50)))
        if not units: L.append("  (no units under %s)" % did)
    n = getattr(a, "recent", 8) or 8
    L.append(""); L.append("== recent focus (last %d) ==" % n)
    if at and at["rows"]:
        rows = sorted(at["rows"], key=lambda y: y.get("timestamp_utc", ""), reverse=True)[:n]
        for y in rows: L.append("  attempt %-30s %-10s unit=%s %s" % (y[at["spec"]["id"]], trunc(y.get(at["spec"]["status"]), 10), y.get(at["spec"]["parent"], ""), trunc(y.get("timestamp_utc", ""), 20)))
        touched = Counter(y.get(at["spec"]["parent"], "") for y in rows)
        if u: L.append("  active units: " + ", ".join("%s×%d" % kv for kv in touched.most_common(5)))
    if m and m["rows"]:
        for r in m["rows"][:min(n, 5)]: L.append("  milestone %-10s %-14s %s" % (r.get(m["spec"]["id"]), trunc(r.get("milestone_type") or r.get(m["spec"]["status"]), 14), trunc(r.get(m["spec"]["title"]), 80)))
    if u:
        opens = [x for x in u["rows"] if st.is_open(x.get(u["spec"]["status"])) and x.get(u["spec"].get("gate", ""), "")]
        if opens:
            L.append("  open gates:")
            for x in opens[:6]: L.append("    %-28s %s" % (x[u["spec"]["id"]], trunc(x.get(u["spec"]["gate"]), 95)))
    print(json.dumps({"lines": L}, ensure_ascii=False) if getattr(a, "json", False) else "\n".join(L)); return 0


def managed_write(project, a, handler):
    """Execute on a bounded staging tree, publish through a recoverable journal."""
    import contextlib, hashlib, io
    import research_records as rr
    from research_transaction import Transaction
    schema = load_schema(project)
    paths = {"research_state_schema.json", "STATE.md", "README.md", CHANGELOG, rr.META, rr.CAPS, rr.SNAP,
             "research_organization/REQUESTS.json"}
    paths.update(s["path"] for s in schema["registries"].values())
    for p in (project / rr.VIEW).glob("*"):
        if p.is_file(): paths.add(p.relative_to(project).as_posix())
    if a.cmd == "document" and a.path: paths.add(a.path)
    if a.cmd == "document":
        for sid, rec in rr.load(project / rr.META, {}).items():
            if sid == a.id or (a.request_key and rec.get("request_key") == a.request_key):
                paths.add(rec["path"])
    if a.cmd == "move-document":
        kind, _, row = State(project).locate(a.id)
        if kind != "document": raise ValueError("document id not found")
        paths.update((row["path"], a.to))
    with Transaction(project, paths) as tx:
        st = State(tx.stage); st.source_project = project
        request_key = getattr(a, "request_key", None)
        ledger_path = tx.stage / "research_organization/REQUESTS.json"
        ledger = rr.load(ledger_path, {})
        request = {k: str(v) for k, v in vars(a).items() if k not in ("project", "json")}
        if getattr(a, "batch", None): request["batch_content"] = Path(a.batch).read_text()
        signature = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        if request_key and a.cmd != "document" and request_key in ledger:
            if ledger[request_key]["signature"] != signature: raise ValueError("request key reused with different arguments")
            print(ledger[request_key]["output"]); return 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = handler(st, a)
        if rc:
            print(buf.getvalue(), end=""); return rc
        sch = rr.load(tx.stage / "research_state_schema.json", schema)
        old = sch.get("managed_by", {})
        mb = dict(old)
        mb.setdefault("created_with", SKILL_VERSION if a.cmd in ("adopt", "init-schema") and not (project / "research_state_schema.json").exists() else "unknown")
        mb.setdefault("validated_with", None)
        mb.update(skill="research-skills", version=SKILL_VERSION, last_written_with=SKILL_VERSION, written_at=rr.now())
        if a.cmd == "validate":
            mb["validated_with"] = {"version": SKILL_VERSION, "at": rr.now(), "scope": "registry structural lint; not scientific validation",
                "registry_hashes": {r["spec"]["path"]: rr.sha(st.project / r["spec"]["path"]) for r in st.reg.values() if (st.project / r["spec"]["path"]).exists()}}
        sch["managed_by"] = mb
        rr.save(tx.stage / "research_state_schema.json", sch)
        if old != mb: log_change(st, "management", "research-skills", "version", json.dumps(old), json.dumps(mb))
        if not getattr(a, "no_render", False):
            st = State(tx.stage); st.source_project = project
            render_state(st)
            if (st.project / rr.VIEW / "index.html").exists():
                snap = rr.load(st.project / rr.SNAP, {})
                snap["generated_at"] = rr.now()
                rr.dashboard(st, snap)
        output = buf.getvalue().replace(str(tx.stage), str(project))
        if request_key and a.cmd != "document":
            ledger[request_key] = {"signature": signature, "output": output}; rr.save(ledger_path, ledger)
        tx.commit()
        print(output, end="")
    return 0

def main() -> int:
    import research_records as rr
    ap = argparse.ArgumentParser(); ap.add_argument("--project", type=Path, default=Path.cwd()); ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("show"); s.add_argument("id"); s.add_argument("--full", action="store_true")
    l = sub.add_parser("lint"); l.add_argument("--verbose", action="store_true")
    f = sub.add_parser("find"); f.add_argument("term"); f.add_argument("--max", type=int, default=20); f.add_argument("--files", type=int, default=8); f.add_argument("--per-file", type=int, default=4); f.add_argument("--tgrep", action="store_true")
    rc = sub.add_parser("repeat-check"); rc.add_argument("text"); rc.add_argument("--top", type=int, default=5)
    i = sub.add_parser("init-schema"); i.add_argument("--force", action="store_true")
    ad = sub.add_parser("adopt"); ad.add_argument("--apply", action="store_true")
    rg_ = sub.add_parser("register"); rg_.add_argument("kind", nargs="?", choices=list(ID_PREFIX)); rg_.add_argument("--field", action="append", metavar="COL=VAL"); rg_.add_argument("--batch"); rg_.add_argument("--no-render", action="store_true")
    rg_.add_argument("--request-key")
    up = sub.add_parser("update"); up.add_argument("id"); up.add_argument("--set", action="append", required=True, metavar="COL=VAL"); up.add_argument("--note"); up.add_argument("--no-render", action="store_true")
    sub.add_parser("render")
    sub.add_parser("version")
    sub.add_parser("validate")
    rec = sub.add_parser("recover"); rec.add_argument("--apply", action="store_true")
    doc = sub.add_parser("document")
    doc.add_argument("--role", required=True, choices=list(rr.FOLDERS)); doc.add_argument("--title", required=True)
    doc.add_argument("--id"); doc.add_argument("--path"); doc.add_argument("--create", action="store_true"); doc.add_argument("--template")
    doc.add_argument("--related", action="append"); doc.add_argument("--supersedes"); doc.add_argument("--event-at")
    doc.add_argument("--status", default="DRAFT"); doc.add_argument("--request-key")
    mv = sub.add_parser("move-document"); mv.add_argument("id"); mv.add_argument("--to", required=True); mv.add_argument("--title")
    cap = sub.add_parser("capability"); cap.add_argument("--record", required=True)
    vw = sub.add_parser("view"); vw.add_argument("mode", choices=["timeline", "context", "links", "capabilities"])
    vw.add_argument("--id"); vw.add_argument("--limit", type=int, default=20)
    rf = sub.add_parser("refresh"); rf.add_argument("--observation"); rf.add_argument("--collection-error", action="store_true"); rf.add_argument("--dashboard", action="store_true")
    fl = sub.add_parser("flow"); fl.add_argument("--detail", metavar="DIRECTION_OR_UNIT_ID"); fl.add_argument("--recent", type=int, default=8)
    a = ap.parse_args(); project = a.project.resolve()
    def refresh(st, a):
        snap = rr.observation(st, a)
        if a.dashboard or (st.project / rr.VIEW / "index.html").exists(): rr.dashboard(st, snap)
        print(json.dumps({"notifications": snap["notifications"], "continue_polling": snap["continue_polling"], "poll_seconds": snap["poll_seconds"]})); return 0
    def view(st, a):
        if a.limit < 1: raise ValueError("limit must be positive")
        data = list(rr.load(st.project / rr.CAPS, {}).values()) if a.mode == "capabilities" else rr.view_rows(st, a.mode, a.id)
        print(json.dumps({"total": len(data), "records": data[:a.limit]}, ensure_ascii=False, indent=2)); return 0
    handlers = {"status": cmd_status, "show": cmd_show, "lint": cmd_lint, "find": cmd_find, "repeat-check": cmd_repeat, "init-schema": cmd_init, "adopt": cmd_adopt, "register": cmd_register, "update": cmd_update, "render": cmd_render, "version": cmd_version, "flow": cmd_flow,
                "document": lambda st, a: rr.document(st, a, sys.modules[__name__]),
                "move-document": lambda st, a: rr.move_document(st, a, sys.modules[__name__]),
                "capability": rr.capability, "view": view, "refresh": refresh,
                "validate": lambda st, a: cmd_lint(st, argparse.Namespace(json=False, verbose=False))}
    try:
        if a.cmd == "recover":
            from research_transaction import recover
            return recover(project, a.apply)
        from research_transaction import JOURNAL
        if (project / JOURNAL).exists(): raise ValueError("pending transaction: run recover before reading or writing state")
        writes = {"register", "update", "render", "init-schema", "document", "move-document", "capability", "refresh", "validate"}
        if a.cmd in writes or (a.cmd == "adopt" and a.apply): return managed_write(project, a, handlers[a.cmd])
        return handlers[a.cmd](State(project), a)
    except (ValueError, OSError, KeyError) as exc:
        print("refused:", exc); return 2

if __name__ == "__main__":
    sys.exit(main())
