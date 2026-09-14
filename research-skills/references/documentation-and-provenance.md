# Documentation And Provenance

## Contents

1. Document roles
2. Canonical ownership and formats
3. Project navigation and state capsule
4. Report/source intake
5. Mirrors, corrections, and handoff
6. Derived research reports (DeepResearch)

## 1. Document Roles

| Role | Owns | Does not own |
|---|---|---|
| `LITERATURE-SYNTHESIS` | cited external landscape at a cutoff | live project results |
| `DECISION-RESEARCH` | candidate comparison and recommendation | execution proof |
| `DESIGN-SSOT` | current contract, hypotheses, gates | scheduler state |
| `QUESTION-REGISTER` | active questions, alternatives, status, revisit triggers | raw evidence or attempt history |
| `DIRECTION-CHANGE` | pivot trigger and branch disposition | rewritten historical evidence |
| `LIVE-MONITOR` | jobs, current blocker, verified timestamp | permanent decision history |
| `EXPERIMENT-LEDGER` | attempt and decision history | duplicated raw metrics |
| `EVIDENCE-ARTIFACT` | reproducible numbers and pass/fail | prose narrative |
| `OPS-KNOWHOW-LOG` | operational incidents, normalized recurrence, prevention and skill-transfer status | scientific verdicts or raw secrets |
| `CONTEXT-CACHE` | condition-aware claim keys and canonical locators | independent evidence or a second ledger |
| `EXTERNAL-NARRATIVE` | approved audience-facing snapshot | new authority |

One claim has one canonical home. Other documents link to it with an evidence
cutoff. Do not copy live tables into reports or copy frozen report wording into
living design documents.

`EXPERIMENTAL` pilot row (not yet in the table above): `LOCATOR-MAP` owns the
verified locations, hashes, and execution environment of a mission's builds,
runtimes, checkpoints, inputs, and result roots; it may not own numbers or
verdicts. See `locator-map.md`.

## 2. Canonical Ownership And Formats

- Prefer editable Markdown as project-authored canonical content.
- Use PDF as the layout-faithful reading snapshot when figures matter.
- Use DOCX/PPTX as rendered or legacy binary snapshots unless explicitly
  declared canonical.
- For a legacy binary mirror, prepend:
  `MIRROR OF <file> · <date> · <tool> · do not hand-edit`.
- Mark direction: `source.md -> render` or `binary -> extracted mirror`.
- Keep decision rationale in its canonical Markdown owner. Registered identity,
  relationships and transitions live in the declared structured registries;
  generate lists and views from them. Avoid parallel hand-maintained status tables.
- Before appending to any structured registry (TSV/CSV with a header schema),
  read the header and conform to it; free-form rows are forbidden and must
  fail the registry's validator if one exists.

Minimum report metadata:

```text
report_id / version / draft|reviewed|frozen|superseded
role / intended audience
evidence cutoff / source corpus or search protocol
project-evidence cutoff
allowed claim level / explicit non-claims
downstream living owner
supersedes / superseded-by
```

## 3. Project Navigation And State Capsule

For the optional default folder layout and Python registration/move/view
commands, read [project-records-and-views.md](project-records-and-views.md).

Maintain one project hub with:

- Situation at a glance: objective, current decision, best evidence, blocker,
  next hard gate;
- document map and human lookup aliases;
- key findings linked to their canonical owner;
- roadmap and active job summary.

Each active goal gets one compact state capsule containing:

```text
locked goal / claim ceiling / current decision
canonical data and code commit / environment
current best and explicitly non-promoted candidates
active jobs with verified-at timestamp
last completed artifact and verdict
next hard gate and exact pass rule
known blockers / forbidden actions
```

Keep the newest session working set near the top:

```text
current direction / active question / claim ceiling
last accepted evidence / blocker / next hard gate / verified-at
```

Use a separate question register when several competing explanations or
branches are active. Use a direction-change record for a major pivot. Keep
cache state in a compact context-cache file rather than expanding `STATE.md`
with historical summaries.

Update the capsule when state changes, not on every heartbeat. A new session
reads the capsule, latest ledger entry, and active-job authority before chat.

## 4. Report And Source Intake

Use `reports_tmp/` only as an inbox. Triage into:

- project-authored deliverable: `reports/<RPT-id>/` and report register;
- external paper/database/data documentation: `reports/sources/<SRC-id>/`,
  where DOI/publisher/database remains canonical.

When several sibling projects share papers, prefer one workspace-level
`papers/` library over project-local `reports/sources/` duplicates. Follow
`literature-management.md` for stable source IDs, source cards, topic
synthesis, search order, and literature-to-design gates.

Assign an ID, role, claim ceiling, source, and cutoff. Create the canonical or
mirror pair, index it, verify links, and only then move the original into a
recoverable `reports_tmp/moved/` tray. Do not delete automatically.

Derived interpretations flow into a living decision/design owner, not back
into the frozen report. Computed numbers flow into immutable outputs.

## 5. Mirrors, Corrections, And Handoff

- A remote evidence mirror records canonical remote path, copied-at time,
  hashes, evidence cutoff, included artifacts, and omissions.
- A PDF alone is not closure when numerical claims rely on metrics or report
  sidecars. Missing pieces make the mirror `partial`.
- Time-sensitive status includes `verified_at`. Historical `RUNNING` text does
  not override scheduler state.
- When a conclusion changes, preserve the old text or artifact and mark
  `CORRECTION` or `SUPERSEDED BY` with reason and replacement path.
- Planned documents are labeled `PLANNED`; do not render nonexistent links as
  if they were evidence.
- Human aliases are navigation only. Reproducible citation uses exact IDs.

## 6. Derived Research Reports (DeepResearch)

Treat a user-provided DeepResearch report as a derived source, not as a primary
paper or execution witness. Unless a project has a stricter documented policy,
use this default layout:

```text
<project>/reports/sources/deepresearch/<SRC-YYYYMMDD-DEEPRESEARCH-ID>/
  SOURCE_CARD.md
  <preserved-report>.md | .pdf | .docx
```

- Keep a short `reports/sources/deepresearch/README.md` registry when the
  project has more than one such report. It states the scope and links each
  stable source ID to its downstream owner.
- Record the intake path, SHA256, format/layout status, claim ceiling,
  relationship to sibling Markdown/PDF versions, and downstream living owner
  in `SOURCE_CARD.md`. Preserve Markdown and layout-faithful PDF separately
  when they are materially different; do not overwrite one with the other.
- Put primary papers in the workspace paper library or the general
  `reports/sources/<SRC-id>/` collection instead. Do not present DeepResearch
  citation tokens as portable primary citations.
- Keep analyses, audits, dashboards, and design documents as link-only
  consumers of this collection. They may summarize a report with an explicit
  claim ceiling, but must not retain duplicate editable source copies.
- Hash and verify a source copy before moving the original from an inbox such
  as Downloads. Retain the moved intake under the project's recoverable
  `reports_tmp/moved/` tray when practical; never delete it automatically.
