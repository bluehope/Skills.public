# Durable records, ownership and closure

## Keep Durable Records And Local Knowledge Findable

Within authorized work, register durable plans, results, interpretations,
decisions, meaningful attempts/failures/lessons and user-requested records.
Do not register every read or harmless typo. Use existing `research_state.py`
document/register/update operations and stable IDs; do not hand-invent IDs or
paste the registries into context. Read
[project-records-and-views.md](project-records-and-views.md) before
writing; apply [registration-checklist.md](registration-checklist.md)
before RESULT/EVIDENCE admission. Registration does not approve a claim.

One owner per fact: source cards for external material, living design/decision
for current reasoning, STATE/monitor for current jobs/blockers, experiment
ledger for scientific history, immutable artifacts for measured numbers, and
versioned narrative for publication. Link these rather than copy their tables.
Preserve failed evidence. Correct stale prose with CORRECTION/SUPERSEDED BY,
and use a successor packet rather than editing a frozen result. For ownership,
intake or correction details read
[documentation-and-provenance.md](documentation-and-provenance.md).

Use the project records folder conventions lazily: plans, outputs, results
(including negative results), interpretations and decisions remain distinct;
existing projects keep their paths until an explicit move is authorized.
Conversation-only durable knowledge may use
[conversation-intake-template.md](../assets/conversation-intake-template.md) within
an authorized record/handoff task, not as a side effect of analysis.

For consequential operational errors, not negative scientific findings, use
`<project-root>/ops_knowhow/incidents.tsv`. Read the short
[operational-error-recording.md](operational-error-recording.md)
when capturing/updating an error: `lookup` first for a familiar failure,
`log --compact` once per incident, `resolve` for recovery history. Preserve
actual skill versions and failed fixes; one writer or separate intake files.
No error authorizes extra retries, installs, submissions or unrelated edits.
Only for recurrence review or skill changes read
[operational-knowhow-lifecycle.md](operational-knowhow-lifecycle.md).
Verified recovery is not automatic global promotion.

## Optional Policies And Closure

Core evidence rules are ACTIVE. Graphify navigation is EXPERIMENTAL and cannot
raise a claim ceiling; read [graphify-integration.md](graphify-integration.md)
only when using it. Consider ado only for stable repeated workflows with exact
reuse/query needs: [ado-experiment-management.md](ado-experiment-management.md).
Install or initialize neither merely because this skill was invoked.

Project-specific pilots are TEMPORARY; packet PARTIAL/BLOCKED/READY/REJECTED is
separate from policy maturity. Before a pilot/iteration or promotion read
[temporary-policy-lifecycle.md](temporary-policy-lifecycle.md).
Keep project exceptions local; preserve rejected iterations. Promotion needs
independent use, realistic failure/revision, file-only resumption, owner approval
and verified canonical/runtime activation. Archive the pilot with a pointer;
do not leave two editable owners. Project-local ownership may be permanent.

Close at the requested scope: answer-only work stops without writes. For
durable changes report IDs, evidence, achieved claim ceiling and next gate;
refresh only affected state owners. Keep current state at the top and marked
history below; generated STATE blocks/views/HTML are not hand-edited or second
authorities. If the project has an audit policy, run its existing document audit
after terminal transitions and before handoff/cleanup; for policy changes read
[research-document-audit.md](research-document-audit.md).
Commit only when requested. `VERSION` identifies the skill release; project
origin, last-write, scoped-validation and data-schema versions stay distinct.
`status`/`version` are read-only; a render is neither migration nor approval.

Inside cloud-synced trees, do not create links/junctions/hard links/mounts or
dependency installs such as node_modules, even in temporary directories. Use
per-machine caches/runtimes outside sync and copy back verified outputs only.
Existing links are inspection evidence, not automatic cleanup targets.
Machine-specific policies belong in user/project instructions, not global rules.
