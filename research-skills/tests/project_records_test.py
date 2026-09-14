"""End-to-end fixtures; never touches real research projects."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from research_transaction import Transaction, JOURNAL, LOCK, digest, recover

class Records(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.p = Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def runcli(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPTS / "research_state.py"), "--project", str(self.p), *args], capture_output=True, text=True, timeout=15)
        if ok: self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        else: self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout
    def init(self):
        self.runcli("adopt", "--apply")
        self.runcli("register", "direction", "--field", "direction_id=D-1", "--field", "title=질문", "--field", "status=OPEN")
        self.runcli("register", "unit", "--field", "unit_id=U-1", "--field", "direction_id=D-1", "--field", "title=실험", "--field", "claim_ceiling=provisional")
    def tree(self): return {str(p.relative_to(self.p)): p.read_bytes() for p in self.p.rglob("*") if p.is_file()}
    def test_unmanaged_read_and_version(self):
        self.assertIn("unrecorded", self.runcli("version")); self.assertEqual(self.tree(), {})
        self.init()
        schema = self.p / "research_state_schema.json"; d = json.loads(schema.read_text())
        d["managed_by"]["created_with"] = "older"; schema.write_text(json.dumps(d))
        self.runcli("register", "attempt", "--field", "unit_id=U-1", "--field", "job_id=1", "--no-render")
        d = json.loads(schema.read_text()); self.assertEqual(d["managed_by"]["created_with"], "older")
        self.assertTrue(d["managed_by"]["last_written_with"])
        self.assertIsNone(d["managed_by"]["validated_with"])
        self.runcli("validate"); self.assertIn("registry_hashes", json.loads(schema.read_text())["managed_by"]["validated_with"])
    def test_batch_all_or_nothing_and_retry(self):
        self.init(); batch = self.p / "batch.json"
        batch.write_text(json.dumps([{"kind":"attempt", "unit_id":"U-1", "job_id":"10"}, {"kind":"unit", "title":"missing ceiling"}]))
        before = self.tree(); self.runcli("register", "--batch", str(batch), ok=False); self.assertEqual(before, self.tree())
        batch.write_text(json.dumps([{"kind":"attempt", "unit_id":"U-1", "job_id":"10"}]))
        self.runcli("register", "--batch", str(batch), "--request-key", "r1")
        before = self.tree(); self.runcli("register", "--batch", str(batch), "--request-key", "r1"); self.assertEqual(before, self.tree())
    def test_header_preserved_and_custom_layout(self):
        self.runcli("init-schema")
        schema = self.p / "research_state_schema.json"; d = json.loads(schema.read_text())
        d["registries"]["direction"]["path"] = "old-layout/directions.tsv"
        schema.write_text(json.dumps(d))
        p = self.p / "old-layout/directions.tsv"; p.parent.mkdir(); p.write_text("direction_id\ttitle\tstatus\tcustom\n")
        self.runcli("adopt", "--apply")
        self.runcli("register", "direction", "--field", "title=기존 구조", "--field", "custom=kept")
        self.assertEqual(p.read_text().splitlines()[0], "direction_id\ttitle\tstatus\tcustom")
        self.assertIn("kept", p.read_text())
    def test_documents_move_freeze_views(self):
        self.init()
        args = ("document", "--create", "--role", "plan", "--title", "연구 기획", "--related", "U-1", "--request-key", "plan1")
        self.runcli(*args); self.runcli(*args)
        meta = json.loads((self.p / "research_organization/RECORD_METADATA.json").read_text()); self.assertEqual(len(meta), 1)
        sid, rec = next(iter(meta.items()))
        self.runcli("move-document", sid, "--to", "plans/renamed.md")
        self.assertFalse((self.p / rec["path"]).exists()); self.assertTrue((self.p / "plans/renamed.md").exists())
        self.assertIn("renamed.md", (self.p / "research_dashboard/views/links.md").read_text())
        self.runcli("document", "--id", sid, "--path", "plans/renamed.md", "--role", "result", "--title", "Negative result", "--status", "FROZEN", "--related", "U-1")
        self.runcli("document", "--id", sid, "--path", "plans/renamed.md", "--role", "result", "--title", "change", ok=False)
        self.assertIn(sid, self.runcli("view", "context", "--id", "D-1"))
        (self.p / "plans/renamed.md").write_text("tampered")
        self.assertIn("content changed", self.runcli("validate", ok=False))
    def test_missing_reference_and_create_collision(self):
        self.init(); before = self.tree()
        self.runcli("document", "--create", "--role", "lesson", "--title", "failed lesson", "--related", "U-missing", ok=False)
        self.assertEqual(before, self.tree())
        (self.p / "keep.md").write_text("keep")
        self.runcli("document", "--create", "--path", "keep.md", "--role", "plan", "--title", "new", ok=False)
        self.assertEqual((self.p / "keep.md").read_text(), "keep")
    def test_refresh_stale_error_unchanged_and_escape(self):
        self.init(); p = self.p / "observation.json"
        p.write_text(json.dumps({"observed_at":"2020-01-01T00:00:00Z", "items":[{"id":"U-1", "operational_status":"COMPLETED", "metric":"<script>alert(1)</script>", "value": None}]}))
        self.runcli("refresh", "--observation", str(p), "--dashboard")
        manifest = json.loads((self.p / "research_dashboard/views/index.manifest.json").read_text())
        for rel, expected in manifest["sources"].items():
            self.assertEqual(hashlib.sha256((self.p / rel).read_bytes()).hexdigest(), expected)
        page = (self.p / "research_dashboard/views/index.html").read_text()
        self.assertIn("STALE", page); self.assertIn("&lt;script&gt;", page); self.assertIn("unknown", page)
        self.assertIn('"notifications": []', self.runcli("refresh", "--observation", str(p)))
        self.runcli("refresh", "--collection-error")
        snap = json.loads((self.p / "research_dashboard/observations/current.json").read_text())
        self.assertEqual(snap["items"][0]["operational_status"], "COMPLETED"); self.assertEqual(snap["last_success_at"], "2020-01-01T00:00:00+00:00")
        p.write_text(json.dumps({"observed_at":"2020-01-01T00:00:00Z", "token":"secret", "items":[]}))
        self.runcli("refresh", "--observation", str(p), ok=False)
    def test_local_concurrent_change_and_recovery(self):
        p = self.p / "file.md"; p.write_bytes(b"before")
        with Transaction(self.p, {"file.md"}) as tx:
            (tx.stage / "file.md").write_bytes(b"after"); p.write_bytes(b"external")
            with self.assertRaises(ValueError): tx.commit()
        self.assertEqual(p.read_bytes(), b"external")
        journal = self.p / JOURNAL
        journal.write_text(json.dumps([{"path":"file.md", "before":digest(b"external"), "after":digest(b"after"), "data":base64.b64encode(b"after").decode()}]))
        recover(self.p, True); self.assertEqual(p.read_bytes(), b"after"); self.assertFalse(journal.exists())
    def test_capability_and_frozen_hash(self):
        self.init()
        for f in (".skills/test/SKILL.md", "scripts/helper.py", "tests/proof.md"):
            p = self.p / f; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("fixture")
        rec = self.p / "cap.json"
        rec.write_text(json.dumps({"id":"CAP-1", "function":"reuse", "applies_when":"same input", "owner":".skills/test/SKILL.md", "code":"scripts/helper.py", "invocation":"python scripts/helper.py", "validation":"tests/proof.md"}))
        self.runcli("capability", "--record", str(rec)); self.assertIn("CAP-1", self.runcli("view", "capabilities"))

if __name__ == "__main__": unittest.main()
