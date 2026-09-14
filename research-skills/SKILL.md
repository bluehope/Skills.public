---
name: research-skills
description: "Plan/audit scientific decisions and authorized research execution, durable records or handoff. Ordinary project file lookup or edits do not trigger research management."
metadata:
  version: "2026.09.14.1"
---

# Research Skills

Files, executed code and immutable artifacts are authority; chat memory is a
locator hint. Keep project state clear with the least sufficient reading and
bookkeeping. Use existing Python helpers for mechanics, not new LLM-generated
registries or wrappers. Read [quickstart-map.md](references/quickstart-map.md)
for onboarding only, not before every task.

> **Registration invariants:** fingerprint every claim through its actual consumer/assembler identity.
> Compare an independent reference only through the same observable and unit.
> Pair every required `DIFFER` with a matched `EQUAL` control.
> After an order-of-magnitude miss, test the measurement route before physical reinterpretation.
> Render a self-comparison as `—`, never as validating zero.
> When the user names an artifact, inspect that artifact's raw input before rebuilt or sibling data.

## Scope and smallest useful input

Ordinary file lookup, typo fixes and isolated helper changes do not need this skill merely because the folder is a research project. Research analysis reads existing evidence; scientific decisions apply the gates below; execution and durable recording require the corresponding authorization. Diagnosis/planning does not authorize a fix, registration, submission or installation. An authorized fix includes reproduction and local testing. For consequential ambiguity use [request-classification.md](references/request-classification.md); do not repeatedly renegotiate an already clear scope.

Read the user-named artifact's raw input first, then its known ID/path or the smallest state needed for this decision. Do not preload hub, design, ledger, history and dashboard. Current-state labels are claims, not evidence.

Existing `scripts/research_state.py --project PROJECT` commands:
`show ID` / `find TERM` for known details; `status` for orientation (120-line default cap); `repeat-check "experiment"` before a new scientific Unit/Attempt. Similarity is not condition identity. Recover matching accepted artifacts before recompute; never duplicate RUNNING/PENDING work.

No registry? Answer from files; do not adopt automatically. For authorized adoption/document work read [project-records-and-views.md](references/project-records-and-views.md); preview before `adopt --apply`. For an unfamiliar registry command read [state-registry-api.md](references/state-registry-api.md). Without compatible Python use bounded STATE/TSV lookup; durable intake remains UNVERIFIED until registered/linted, never fabricated validated rows.

Known paths use direct reads, simple names scoped `rg`. Broad/conflicting/binary/semantic retrieval uses [local-search.md](references/local-search.md) and `local-search` only as needed. No policy/index/receipt creation for read-only questions. Search hits locate canonical/original evidence; ZERO-RESULT is scoped missing coverage.

Reuse a known helper directly. Consult [capability-code-map.md](references/capability-code-map.md) when ownership/invocation is unresolved before adding/replacing a helper: SEARCH → VERIFY → REUSE → PATCH → EXTEND → NEW. Project-local ownership may be permanent; do not initialize a global index to find one function.

Read selected instructions fully, not every linked reference. A helper owner does not imply its whole Skill workflow. Bound ordinary output to 2,000 tokens; parse requested log/JSONL fields, not raw conversation or executable dumps. Reuse unchanged verified inputs unless new reasoning needs them.

## Scientific decisions and execution

Before defining/auditing an experiment, scientific implementation or costly compute, read [scientific-gates.md](references/scientific-gates.md); for its formal evidence contract also [evidence-and-validation.md](references/evidence-and-validation.md). Ordinary status lookup or a document typo does not need these procedures.

Preserve the evidence ladder SOURCE → CODE → FIT → HOLDOUT → PHYSICS and its claim ceilings. Non-fitted interventions use COVERAGE of the actual production consumer, not a fictitious holdout. Same observable/units, matched DIFFER/EQUAL controls, source/consumer identity and representative preflight remain mandatory for scientific acceptance. Missing gates never authorize new compute.

## Select Only The Needed Research Mode

These are independent entry points, not a checklist to read in sequence.

| Current operation | Read before that operation |
|---|---|
| Major pivot, branch expansion or scientific handoff | [hypothesis-graph-and-direction-change.md](references/hypothesis-graph-and-direction-change.md); default at most two scientific branches plus one debug branch unless a project exception is justified |
| Repeated comparable measurements / Campaign planning | [structured-experiment-campaigns.md](references/structured-experiment-campaigns.md); a Campaign coordinates Units/Attempts, not scientific verdicts |
| Several candidates sharing a gate sequence | Use a project-owned matrix with distinct per-gate outcomes; no project-specific template is bundled |
| Research history/flow requested or hard to follow | [research-history-and-loop-visualization.md](references/research-history-and-loop-visualization.md); existing `flow` / `view timeline`, `view context`, `view links` first |
| Record disagrees with the object or measurement it names | [provenance-and-identity.md](references/provenance-and-identity.md) |
| Verified build/environment/remote-path lookup or PATH_MAP update | [locator-map.md](references/locator-map.md); EXPERIMENTAL, one LOCATOR-MAP per mission, linked from Hub/STATE/SSOT, never owner of numbers or verdicts |
| Literature acquisition, synthesis or design justification | [literature-management.md](references/literature-management.md) |
| Research figure registration, recovery or reproduction | [research-figure-reproducibility.md](references/research-figure-reproducibility.md); rendering alone is not evidence acceptance |
| Compute execution, recording, restart or artifact readiness | [compute-and-artifacts.md](references/compute-and-artifacts.md) |
| Accept a local run or compare changed runtime/package/machine conditions | [local-environment-tracking.md](references/local-environment-tracking.md); reuse the redacted capture helper |
| Build/update a requested monitor or HTML research view | [research-monitor-dashboard.md](references/research-monitor-dashboard.md) |
| Need a reusable context cache after repeated costly retrieval | [research-context-cache.md](references/research-context-cache.md); optional, condition-aware locators rather than copied evidence |

Keep scientific comparison at the Unit level; an Arm/Attempt belongs to its
declared Unit and a successful job is not an achievement. Never duplicate
RUNNING/PENDING work. A new attempt follows a named terminal reason and the
required authorization. Submission acceptance, execution completion, numerical
convergence, artifact readiness and scientific permission remain distinct;
missing/stale observations are unknown, not zero or success.

For rendering across figure types use `$scientific-figure-making`; for a known
narrow rendering task use the applicable specialist. Browser report acquisition
is an optional external workflow, not bundled here. Treat a supplied external
research report as a derived source, not a primary paper
or execution witness; its source-card intake is in
[documentation-and-provenance.md](references/documentation-and-provenance.md).

## Record only authorized durable changes

For plans/results/decisions and meaningful attempts, read [durable-records.md](references/durable-records.md) and the operation-specific [project-records-and-views.md](references/project-records-and-views.md). Stable IDs and one owner per fact; do not register every read or typo. Before RESULT/EVIDENCE admission apply [registration-checklist.md](references/registration-checklist.md). Registration does not approve a claim.

For operational incidents read [operational-error-recording.md](references/operational-error-recording.md): existing `ops_knowhow/incidents.tsv`, lookup then one compact incident with resolve history. This is not scientific-negative-result storage or permission for retries. Recurrence/policy changes alone need [operational-knowhow-lifecycle.md](references/operational-knowhow-lifecycle.md).

Optional graph/cache/pilot policies and durable closure are in [durable-records.md](references/durable-records.md); none requires installation, global promotion or new project state at invocation. For document-policy changes use [research-document-audit.md](references/research-document-audit.md). Read-only work ends with the answer; durable work reports IDs, evidence, achieved ceiling, next gate, and only affected state updates. Commit only when requested.

Keep dependency installs, caches and links/junctions/hard links/mounts outside cloud-synced trees. Existing links are evidence, not cleanup authorization. `VERSION` is this Skill release, distinct from project/schema versions.
