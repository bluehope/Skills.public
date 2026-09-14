# Operational error recording

Use for one consequential skill-assisted operational error or its recovery,
in any project; scientific attempts/results keep their own ledger. No full
research adoption, dashboard, or promotion review is needed to record an error.

## Location and authority

Use the confirmed project root, not the current shell/Campaign/Attempt folder:

```text
<project-root>/ops_knowhow/
  incidents.tsv                  # canonical errors and recovery history
  analysis.tsv                   # generated recurrence view
  intake/<UUID>.json              # optional unmerged input, not another registry
  evidence/<incident-id>/         # optional bounded redacted verification
```

Create optional directories only when used. Keep an explicitly mapped legacy
location via `--directory` in project instructions; never create parallel logs.
No confirmed root? Ask for a location if durable recording is needed. Link
existing attempt logs with project-relative paths or redacted remote locators,
not duplicate raw data. Never persist passwords, tokens, private keys, full
environment dumps or unbounded output. REVIEW-REQUIRED is not permission to
store sensitive data. The registry records association with a skill, not blame.

## Query before repeating a known failure

Resolve the actual installed research-skills root; use `--help` if the helper's
version/capabilities are unknown. Examples use `<helper>` for that root's
`scripts/operational_knowhow.py`; replace placeholders before execution.

```bash
python <helper> lookup <project-root> --incident-id OPS-ID
python <helper> lookup <project-root> --signature shell:remote-quoting-expanded-locally
python <helper> lookup <project-root> --skill ssh-skills --limit 5
```

Lookup is read-only even before init: at most 5 records by default/20 on request,
no full recovery history. Reopen selected evidence and compare environment,
version and operation before reusing a fix. For unknown wording use scoped `rg`;
broader local-search only if needed. No full-corpus scan or indexing per error.

## Capture once, update the same incident

Log rework, risk, wasted compute, ambiguity or repeated manual corrections;
exclude harmless typos, expected negative fixtures and informational nonzero
exits. Capture after a bounded recovery attempt or before handoff if unresolved.
Respect request scope: read-only analysis reports findings without writing a
log. An error never authorizes extra submissions, installations, SSH config
changes, deletion or unlimited retries. Report the saved ID briefly.

Minimal JSON needs `operation_kind`, `symptom_class`, `severity`, `evidence_path`
and `redaction_status`. Add actual `skills_used` as `{ "skill-id": "version" }`;
use the installed version, `sha256:<hash>` or `unknown`, never the latest
canonical version, candidate skills or repeated whole-tree hashing. Supported
severity is LOW/MEDIUM/HIGH/CRITICAL; redaction is REDACTED/NO-SENSITIVE-DATA/
REVIEW-REQUIRED. For richer records use
[operational-incident-record-template.json](../assets/operational-incident-record-template.json).

```bash
python <helper> init <project-root>
python <helper> log <project-root> --record <record.json> --compact
python <helper> resolve <project-root> --incident-id OPS-ID --record <resolution.json>
```

Only init a missing workspace for authorized recording. Omitted incident IDs
and timestamps are generated on direct registration; supply the known event
time when registering later. For queued imports assign an ID once and retain
it for retries (duplicates are rejected). Unassessed scope/impact/helper/owner
stay unknown, not guessed. A known normalized signature names the preventable
mechanism, not one command/job ID; otherwise keep it blank and status OBSERVED.

Resolution JSON has `immediate_fix`, `resolution_status`, optional
`verification_ref`. Outcomes are UNKNOWN, UNRESOLVED, ATTEMPTED, VERIFIED, FAILED.
VERIFIED needs a same-scope check and verification locator; the helper validates
fields, not whether a referenced check truly ran/passed. Workarounds retain
their limits. `resolve` preserves prior outcomes without adding another error
count; identical retries add no history. Later recurrence is a NEW incident.
Legacy/custom TSV columns survive writes. Recovery does not change promotion
status or establish scientific acceptance.

## Single writer and fallback

All write commands require one designated writer. Atomic replacement is not a
distributed lock or Dropbox conflict protocol. Concurrent/offline sessions use
separate reviewed `intake/<UUID>.json` files; after sync, one owner imports them.
Retain inputs until import is confirmed, then archive outside active intake.
On a conflict stop merging and preserve both inputs; do not assume sync is done.
Without Python keep unverified JSON intake and defer registration; do not claim
it is counted by analyze. No automatic watcher or universal error hook exists.

Only for recurrence review or a proposed skill change read
[operational-knowhow-lifecycle.md](operational-knowhow-lifecycle.md). A verified
fix does not authorize automatic global promotion or publication of project data.
