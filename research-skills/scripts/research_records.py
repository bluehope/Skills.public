"""Project documents, capability locators and generated views (stdlib only)."""
import datetime as dt
import hashlib
import html
import json
import re
import uuid
from pathlib import Path
from urllib.parse import quote
from research_transaction import safe_path

META = "research_organization/RECORD_METADATA.json"
CAPS = "research_organization/CAPABILITIES.json"
SNAP = "research_dashboard/observations/current.json"
VIEW = "research_dashboard/views"
FOLDERS = {"plan": "plans", "interpretation": "interpretations", "result": "results",
           "decision": "decisions", "lesson": "decisions", "campaign": "campaigns"}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p, default): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def metadata(st): return load(st.project / META, {})
def lint_metadata(st):
    issues = []; origin = getattr(st, "source_project", st.project)
    for sid, rec in metadata(st).items():
        if not st.locate(sid)[0]: issues.append(("BLOCK", "document", "metadata id missing: " + sid))
        for related in rec.get("related_ids", []) + ([rec["supersedes"]] if rec.get("supersedes") else []):
            if related == sid or not st.locate(related)[0]: issues.append(("BLOCK", "document", "invalid relation: " + sid + " -> " + related))
        p = safe_path(st.project, rec["path"])
        if not p.exists(): p = safe_path(origin, rec["path"])
        if not p.is_file(): issues.append(("BLOCK", "document", "missing registered file: " + sid))
        elif rec.get("sha256") and sha(p) != rec["sha256"]:
            issues.append(("BLOCK" if rec.get("status", "").upper() == "FROZEN" else "WARN", "document", "content changed since registration: " + sid))
    for sid, rec in load(st.project / CAPS, {}).items():
        p = safe_path(origin, rec["code"])
        if not p.is_file() or sha(p) != rec["code_sha256"]:
            issues.append(("WARN", "capability", "revalidate changed/missing helper: " + sid))
    return issues
def links(st, ids):
    for sid in ids:
        if not st.locate(sid)[0]: raise ValueError("unknown related id: " + sid)
def stamp_time(value):
    if not value: return "unknown"
    d = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None: raise ValueError("timestamp requires timezone")
    return d.astimezone(dt.timezone.utc).isoformat()

def document(st, a, api):
    meta = metadata(st); original = getattr(st, "source_project", st.project)
    related = a.related or []; links(st, related)
    if a.supersedes: links(st, [a.supersedes])
    title = a.title
    sid = a.id or "DOC-" + (hashlib.sha256(a.request_key.encode()).hexdigest()[:12].upper() if a.request_key else uuid.uuid4().hex[:12].upper())
    if not re.fullmatch(r"[\w-]+", sid): raise ValueError("invalid document id")
    if sid in related or a.supersedes == sid: raise ValueError("self-reference is not permitted")
    if a.create:
        slug = re.sub(r"[^\w-]+", "-", title, flags=re.UNICODE).strip("-")[:60] or "record"
        rel = a.path or f"{FOLDERS[a.role]}/{sid}--{slug}.md"
        target = safe_path(st.project, rel)
        if target.exists() and not a.request_key: raise ValueError("create destination exists; revise without --create")
        sections = {
            "plan": ["Question and hypothesis", "Conditions and comparator", "Gate and stopping rule", "Evidence and related IDs"],
            "result": ["Outcome (including negative findings)", "Conditions and metrics", "Evidence manifest and locators", "Validation status and claim ceiling"],
            "interpretation": ["Related result IDs", "Interpretation", "Alternatives and limitations", "Next discriminating check"],
            "decision": ["Decision and rationale", "Evidence IDs", "Rejected alternatives", "Revisit condition"],
            "lesson": ["Expected and observed", "Conditions and evidence IDs", "Lesson and limits", "Reuse or revisit condition"],
            "campaign": ["Objective and contract", "Unit and attempt links", "Progress and blockers", "Closure and next gate"],
        }
        text = Path(a.template).read_text(encoding="utf-8") if a.template else f"# {title}\n\n" + "\n".join("## " + s + "\n\nUnrecorded.\n" for s in sections[a.role])
        if safe_path(original, rel).exists() and sid not in meta: raise ValueError("create destination exists in project")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_text(encoding="utf-8") != text: raise ValueError("create retry differs from existing content")
        target.write_text(text, encoding="utf-8")
    else:
        if not a.path: raise ValueError("document requires --path or --create")
        rel = a.path; target = safe_path(st.project, rel)
        if not target.is_file(): raise ValueError("document file missing: " + rel)
    content_hash = sha(target)
    event = stamp_time(a.event_at)
    payload = {"role": a.role, "title": title, "related_ids": related,
               "supersedes": a.supersedes, "event_at": event, "status": a.status,
               "sha256": content_hash}
    # Same request key returns the original record, or refuses changed content.
    for key, rec in meta.items():
        if a.request_key and rec.get("request_key") == a.request_key:
            if rec.get("payload") != payload: raise ValueError("request key reused with different content")
            print("existing document", key, rec["path"]); return 0
    existing = st.locate(sid)
    for key, rec in meta.items():
        if rec.get("path") == rel and key != sid:
            if rec.get("payload") == payload: print("existing document", key, rel); return 0
            raise ValueError("path already registered; revise using --id " + key)
    for row in st.reg["document"]["rows"]:
        if row.get("path") == rel and row.get(st.reg["document"]["spec"]["id"]) != sid:
            raise ValueError("path already catalogued; supply its --id")
    if existing[0]:
        if existing[0] != "document": raise ValueError("id belongs to another registry")
        old = meta.get(sid, {})
        if old.get("status", existing[2].get("status", "")).upper() == "FROZEN":
            raise ValueError("frozen result: create successor with --supersedes")
        if existing[2].get("path") != rel: raise ValueError("use move-document for path changes")
        # Explicit document revisions may change title/role, never id or path.
        row = existing[2]; row.update(title=title, role=a.role, status=a.status)
        api.write_registry(st, "document")
    else:
        fields = {"document_id": sid, "title": title, "role": a.role, "path": rel,
                  "status": a.status, "authority": "REGISTERED-NOT-SCIENTIFICALLY-APPROVED"}
        for kind, col in (("direction", "direction_id"), ("unit", "unit_id")):
            found = [x for x in related if st.locate(x)[0] == kind]
            if found: fields[col] = found[0]
        api.append_row(st, "document", fields)
    old = meta.get(sid)
    history = (old or {}).get("revisions", [])
    if old: history = history + [{k: v for k, v in old.items() if k != "revisions"}]
    meta[sid] = {**payload, "payload": payload, "path": rel, "recorded_at": now(),
                 "request_key": a.request_key, "revisions": history}
    save(st.project / META, meta)
    api.log_change(st, "document", sid, "revision", (old or {}).get("sha256", ""), content_hash)
    print("registered document", sid, "@", rel, "(structure checked; scientific approval not implied)")
    return 0

def move_document(st, a, api):
    kind, _, row = st.locate(a.id)
    if kind != "document": raise ValueError("unknown document id")
    meta = metadata(st); rec = meta.get(a.id, {})
    if rec.get("status", row.get("status", "")).upper() == "FROZEN": raise ValueError("frozen document cannot move")
    old = row["path"]; src = safe_path(st.project, old); dst = safe_path(st.project, a.to)
    if not src.is_file() or dst.exists(): raise ValueError("missing source or destination exists")
    dst.parent.mkdir(parents=True, exist_ok=True); src.rename(dst)
    row["path"] = a.to
    if a.title: row["title"] = a.title
    api.write_registry(st, kind)
    rec.update(path=a.to, title=row.get("title"), recorded_at=now(), sha256=sha(dst))
    meta[a.id] = rec; save(st.project / META, meta)
    api.log_change(st, kind, a.id, "path", old, a.to)
    print("moved", a.id, old, "->", a.to, "; generated links refreshed; prose links require review")
    return 0

def capability(st, a):
    records = load(st.project / CAPS, {})
    record = load(Path(a.record), None)
    for k in ("id", "function", "applies_when", "owner", "code", "invocation", "validation"):
        if not record.get(k): raise ValueError("capability requires " + k)
    origin = getattr(st, "source_project", st.project)
    for k in ("owner", "code", "validation"):
        if not safe_path(origin, record[k]).is_file(): raise ValueError("missing capability " + k)
    record["code_sha256"] = sha(safe_path(origin, record["code"]))
    records[record["id"]] = record; save(st.project / CAPS, records)
    print("capability registered", record["id"]); return 0

def rows(st):
    meta = metadata(st); out = []
    for kind, reg in st.reg.items():
        spec = reg["spec"]
        for i, row in enumerate(reg["rows"]):
            sid = row.get(spec["id"], ""); m = meta.get(sid, {})
            related = list(m.get("related_ids", []))
            for k in ("direction_id", "unit_id", "campaign_id"):
                if row.get(k) and row[k] != sid: related.append(row[k])
            out.append({"id": sid, "kind": kind, "role": row.get("role", kind),
                        "title": row.get(spec["title"], ""), "status": row.get(spec["status"], ""),
                        "path": row.get("path") or spec["path"], "line": i + 2,
                        "event_at": m.get("event_at") or row.get("timestamp_utc") or row.get("period_start") or "unknown",
                        "recorded_at": m.get("recorded_at", "unknown"), "related_ids": sorted(set(related)),
                        "next_gate": row.get(spec.get("gate", "next_gate"), ""),
                        "claim_ceiling": row.get("claim_ceiling", ""), "milestone_type": row.get("milestone_type", "")})
    return out

def view_rows(st, mode="links", context=None):
    result = rows(st)
    if context:
        selected = {context}
        for _ in range(len(result)):
            extra = {r["id"] for r in result if selected.intersection(r["related_ids"])}
            if extra <= selected: break
            selected |= extra
        result = [r for r in result if r["id"] in selected]
    if mode == "timeline": return sorted(result, key=lambda r: (r["event_at"] == "unknown", r["event_at"], r["recorded_at"], r["id"]))
    return sorted(result, key=lambda r: (r["related_ids"], r["kind"], r["id"]))

def views(st):
    target = st.project / VIEW; target.mkdir(parents=True, exist_ok=True)
    def cell(s): return str(s).replace("|", "\\|").replace("\n", " ").replace("<", "&lt;")
    for mode in ("timeline", "context", "links"):
        lines = [f"# Research {mode}", "", "Generated from registries; edit their owners.", "",
                 "| ID | Role / status | Title | Related | Event / recorded | Source |", "|---|---|---|---|---|---|"]
        for r in view_rows(st, mode):
            path = quote("../../../" + r["path"], safe="/")
            lines.append("| " + " | ".join([cell(r["id"]), cell(r["role"] + " / " + r["status"]), cell(r["title"]),
                           cell(", ".join(r["related_ids"])), cell(r["event_at"] + " / " + r["recorded_at"]), f"[source]({path})"]) + " |")
        (target / (mode + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    caps = load(st.project / CAPS, {})
    lines = ["# Project capabilities", "", "Generated locators; verify code and validation before reuse.", ""]
    for key, c in sorted(caps.items()):
        lines.append(f"- {key}: {c['function']} — {c['applies_when']} | owner: {c['owner']} | code: {c['code']} | run: {c['invocation']} | validation: {c['validation']}")
    (target / "capabilities.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def observation(st, a):
    previous = load(st.project / SNAP, {})
    current_time = now()
    if a.observation:
        packet = load(Path(a.observation), None)
        # Strict whitelist: arbitrary command output/secrets never copied into views.
        allowed = {"observed_at", "items"}
        if set(packet) - allowed: raise ValueError("observation contains unsupported fields")
        if re.search(r"(?i)(?:bearer\s+\S+|(?:api[_-]?key|password|secret|token)\s*[:=]\s*\S+|-----BEGIN .*PRIVATE KEY-----)", json.dumps(packet)):
            raise ValueError("possible secret in observation; redact at collector")
        observed = stamp_time(packet.get("observed_at"))
        if observed == "unknown": raise ValueError("observed_at required")
        if dt.datetime.fromisoformat(observed) > dt.datetime.now(dt.timezone.utc): raise ValueError("future observation")
        items = packet.get("items")
        if not isinstance(items, list): raise ValueError("items must be a list")
        columns = {"id", "operational_status", "scientific_status", "adoption_status", "blocker", "next_gate", "metric", "value", "target", "comparator", "evidence"}
        seen = set()
        for item in items:
            if set(item) - columns: raise ValueError("unsupported observation item fields")
            if not item.get("id") or item["id"] in seen: raise ValueError("missing/duplicate observation id")
            links(st, [item["id"]]); seen.add(item["id"])
            for key, value in item.items():
                if isinstance(value, (dict, list)) or len(str(value)) > 500: raise ValueError("unbounded observation field")
            # Values and labels are adapter assertions, not newly granted scientific approval.
        result = {"observed_at": observed, "last_success_at": observed, "items": items, "collection_error": None}
    elif a.collection_error:
        result = {**previous, "collection_error": "COLLECTION-FAILED", "failed_at": current_time}
    else:
        result = previous or {"observed_at": None, "last_success_at": None, "items": [], "collection_error": "NOT-COLLECTED"}
    result["generated_at"] = current_time
    before = {i["id"]: i for i in previous.get("items", [])}
    changes = []
    for item in result.get("items", []):
        old = before.get(item["id"], {})
        for field in ("operational_status", "blocker", "next_gate", "scientific_status"):
            if old.get(field) != item.get(field):
                if field != "operational_status" or item.get(field) in ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"):
                    changes.append({"id": item["id"], "field": field, "old": old.get(field), "new": item.get(field)})
    result["notifications"] = changes
    result["poll_seconds"] = int(st.schema.get("monitor", {}).get("poll_seconds", 300))
    if result["poll_seconds"] <= 0: raise ValueError("poll_seconds must be positive")
    result["stale_after_seconds"] = int(st.schema.get("monitor", {}).get("stale_after_seconds", 3 * result["poll_seconds"]))
    result["continue_polling"] = any(i.get("operational_status") in ("PENDING", "RUNNING", "SUBMITTED") for i in result.get("items", []))
    if result.get("collection_error") and not result.get("items"): result["continue_polling"] = None
    save(st.project / SNAP, result)
    if a.observation or a.collection_error:
        save(st.project / "research_dashboard/observations/history" / (uuid.uuid4().hex + ".json"), result)
    return result

def dashboard(st, snapshot):
    data = rows(st); cfg = st.schema.get("project", {})
    esc = lambda x: html.escape(str(x if x is not None else "unknown"))
    observed = snapshot.get("observed_at")
    stale = not observed or (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(observed)).total_seconds() > snapshot["stale_after_seconds"]
    parts = ["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>",
             "<meta http-equiv='refresh' content='60'><title>Research dashboard</title>",
             "<style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:.5rem;text-align:left}a{color:#145da0}</style></head><body>",
             "<h1>" + esc(cfg.get("objective", "Project objective not recorded")) + "</h1>",
             "<p>Supported conclusion: " + esc(cfg.get("supported_conclusion")) + "</p><p>Next decision: " + esc(cfg.get("next_decision")) + "</p>",
             "<p>Observed: " + esc(observed) + " | generated: " + esc(snapshot["generated_at"]) + " | last success: " + esc(snapshot.get("last_success_at")) + " | " + ("STALE" if stale else "FRESH") + " | " + esc(snapshot.get("collection_error") or "OK") + "</p>"]
    for heading, selection in (("Achievements and lessons", [r for r in data if r["milestone_type"] in ("ACHIEVEMENT", "NEGATIVE-FINDING") or r["role"] == "lesson"]),
                               ("Campaigns and units", [r for r in data if r["kind"] == "unit" or r["role"] == "campaign"])):
        parts += ["<h2>" + heading + "</h2><ul>"]
        for r in selection:
            parts.append("<li><a href='" + quote("../../../" + r["path"], safe="/") + "'>" + esc(r["id"] + " " + r["title"]) + "</a> — " + esc(r["status"]) + " | next gate: " + esc(r["next_gate"]) + " | ceiling: " + esc(r["claim_ceiling"]) + "</li>")
        parts.append("</ul>")
    parts.append("<h2>Observed execution and metrics</h2><p>Adapter observations; completion does not grant scientific acceptance.</p><table><tr>")
    cols = ["id", "operational_status", "scientific_status", "adoption_status", "metric", "value", "target", "comparator", "blocker", "next_gate", "evidence"]
    parts += ["<th>" + esc(c) + "</th>" for c in cols]; parts.append("</tr>")
    for item in snapshot.get("items", []): parts.append("<tr>" + "".join("<td>" + esc(item.get(c)) + "</td>" for c in cols) + "</tr>")
    parts.append("</table><h2>Recent changes</h2><pre>" + esc(json.dumps(snapshot.get("notifications", []), ensure_ascii=False, indent=2)) + "</pre>")
    parts.append("<p><a href='timeline.md'>Timeline</a> · <a href='context.md'>Context</a> · <a href='links.md'>Links</a> · <a href='capabilities.md'>Capabilities</a></p></body></html>")
    # Client only updates freshness from the local page timestamp. No remote fetch.
    freshness = "<p id='freshness'></p><script>const observed=" + json.dumps(observed) + ";const threshold=" + str(snapshot["stale_after_seconds"]) + ";function tick(){document.getElementById('freshness').textContent=(!observed || (Date.now()-Date.parse(observed))/1000>threshold)?'Observation: STALE':'Observation: FRESH'}tick();setInterval(tick,1000);</script>"
    parts[-1] = parts[-1].replace("</body>", freshness + "</body>")
    p = st.project / VIEW / "index.html"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(parts), encoding="utf-8")
    save(p.with_suffix(".manifest.json"), {"generator": "research_records.py", "generated_at": snapshot["generated_at"],
         "artifact_sha256": sha(p), "sources": {rel: sha(st.project / rel) for rel in [r["spec"]["path"] for r in st.reg.values()] + [META, SNAP, "research_state_schema.json"] if (st.project / rel).exists()}})
