"""Recoverable local multi-file commits; cloud sync is not a distributed lock."""
import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path

JOURNAL = "research_organization/.state-transaction.json"
LOCK = "research_organization/.state-write.lock"

def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None

def safe_path(root, rel):
    p = root / rel
    if Path(rel).is_absolute() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError("path must stay inside project: " + str(rel))
    for part in [p, *p.parents]:
        if part == root.parent: break
        if part.is_symlink(): raise ValueError("symlink is not a writable project path: " + str(part))
    return p

def read(p):
    return p.read_bytes() if p.exists() else None

def atomic(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    if data is None:
        if p.exists(): p.unlink()
        return
    fd, tmp = tempfile.mkstemp(prefix=".state-", dir=p.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

class Transaction:
    def __init__(self, root, paths):
        self.root = root.resolve()
        self.paths = set(paths)
        self.before = {}

    def __enter__(self):
        lock = safe_path(self.root, LOCK)
        lock.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.write(self.fd, str(os.getpid()).encode())
        try:
            if safe_path(self.root, JOURNAL).exists():
                raise ValueError("pending transaction: run recover before writing")
            # Conflict copies must be reconciled before trusting this local view.
            if any("conflicted copy" in p.name.lower() for p in lock.parent.rglob("*")):
                raise ValueError("sync conflict copy found; reconcile before writing")
            self.temp = tempfile.TemporaryDirectory(prefix="research-state-")
            self.stage = Path(self.temp.name)
            for rel in self.paths:
                data = read(safe_path(self.root, rel)); self.before[rel] = data
                if data is not None: atomic(safe_path(self.stage, rel), data)
            return self
        except BaseException:
            os.close(self.fd); lock.unlink()
            if hasattr(self, "temp"): self.temp.cleanup()
            raise

    def commit(self):
        after = {p.relative_to(self.stage).as_posix(): p.read_bytes()
                 for p in self.stage.rglob("*") if p.is_file()}
        for rel in self.paths: after.setdefault(rel, None)
        # Validate every input before writing the journal, including unchanged inputs.
        for rel in set(self.before) | set(after):
            if read(safe_path(self.root, rel)) != self.before.get(rel):
                raise ValueError("concurrent change; no commit: " + rel)
        entries = []
        for rel, data in after.items():
            if data != self.before.get(rel):
                entries.append({"path": rel, "before": digest(self.before.get(rel)),
                                "after": digest(data), "data": base64.b64encode(data).decode() if data is not None else None})
        if not entries: return
        atomic(safe_path(self.root, JOURNAL), json.dumps(entries).encode())
        finish(self.root, entries)
        safe_path(self.root, JOURNAL).unlink()

    def __exit__(self, *exc):
        self.temp.cleanup(); os.close(self.fd)
        safe_path(self.root, LOCK).unlink()

def finish(root, entries):
    # Precheck all paths before resuming a partial commit.
    for e in entries:
        if digest(read(safe_path(root, e["path"]))) not in (e["before"], e["after"]):
            raise ValueError("recovery conflict; preserve journal: " + e["path"])
    for e in entries:
        p = safe_path(root, e["path"])
        if digest(read(p)) == e["after"]: continue
        if digest(read(p)) != e["before"]: raise ValueError("concurrent change during commit: " + e["path"])
        data = base64.b64decode(e["data"]) if e["data"] is not None else None
        if digest(data) != e["after"]: raise ValueError("corrupt journal payload")
        atomic(p, data)

def recover(root, apply=False):
    lock = safe_path(root, LOCK); journal = safe_path(root, JOURNAL)
    if lock.exists():
        try:
            pid = int(lock.read_text()); os.kill(pid, 0)
        except ProcessLookupError:
            if not apply: print("stale local lock; recover --apply to clear")
            else: lock.unlink()
        else: raise ValueError("writer active or lock ownership uncertain; recovery refused")
    if not journal.exists(): print("no pending journal"); return 0
    entries = json.loads(journal.read_text())
    print("pending paths:", ", ".join(e["path"] for e in entries))
    if apply:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(fd, str(os.getpid()).encode()); finish(root, entries); journal.unlink()
        finally: os.close(fd); lock.unlink()
    return 0
