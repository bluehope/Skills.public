# State Registry API (`scripts/research_state.py`)

Access project registries by ID and reopen only necessary evidence. Writes
are staged and journaled; updates preserve history rather than being strictly
append-only. Read [project-records-and-views.md](project-records-and-views.md)
for document/create/move, capability, views, refresh and recovery commands.

## Project contract

A project declares its registries in `research_state_schema.json` (create with
`init-schema`; the default matches the `research_organization/` +
`research_dashboard/` layout). Each registry names its id, parent, status,
title and free-text columns, path columns, and optional pointer/gate/ceiling
columns. Column names are project-local; the tool is global. Projects may add
registries or columns without changing the skill.

## Commands and when to use them

| command | use at | output bound |
|---|---|---|
| `status` | orientation or a record/execute decision needing project state; not every isolated query | ≤120 lines by default: open directions, current units with verdict/gate/ceiling, verdict and attempt counts, last milestones, lint totals |
| `show ID` | before reopening a document about a unit/direction/attempt/milestone/claim | one row (truncated), children, cross-references as locators, missing paths |
| `lint` | after any registry edit; before handoff | referential integrity, duplicate/empty ids, dead evidence paths, open units without attempts, missing claim ceilings, absent `milestone_type` |
| `find TERM` | when the owning id is unknown | bounded `rg` (or tgrep when `tgrep_index` is set) over declared search roots; returns `file:line` locators and the ids on each line |
| `repeat-check "text"` | before opening a new unit, attempt, or campaign | most similar registered units/attempts/milestones by term overlap, with their verdicts |
| `flow [--detail ID] [--recent N]` | "연구 흐름을 보여줘"; orientation in a new session | direction tree (● open / ○ terminal), units and attempts under one direction or unit, recent attempts, latest milestones, open gates |
| `adopt [--apply]` | authorized durable management of a project without registries; preview before apply | minimal scaffold + seeded document inventory; no automatic adoption during analysis |

## Write commands (agent-assisted within authorized work, or manual)

| command | effect |
|---|---|
| `register KIND --field COL=VAL ...` | append one row; id auto-generated from title/unit+job when omitted; parent must exist; unit needs a claim ceiling; milestone needs `milestone_type` |
| `register --batch items.json` | same for a list of `{"kind": ..., col: val}` objects, in order (direction before its units, units before attempts) |
| `update ID --set COL=VAL [--note ...]` | change transition columns only (status, verdict, gate, next_gate, period_end, disposition); identity columns are refused; every change is appended to `research_organization/STATE_CHANGELOG.tsv` |
| `render` | regenerate the marked block of `STATE.md` from registries; text outside the markers is preserved |

For a durable record authorized by the task, register/update prints
`registered KIND ID @ file:line` or
`updated ...` and then re-renders `STATE.md`, so the next session starts from
`status`/`flow` without reading the chat. The automatic path is: the agent
turns the conversation into a batch JSON (see
`assets/conversation-intake-template.md` for the fields), runs `register`,
and reports the ids. Read-only questions never trigger this path. The manual
path is the same commands typed by a person.
Rows are never deleted; supersede by `update` on status or by a new row.

Treat every output as locators. Reopen the canonical row or document for any
number, verdict, or claim you will act on. `find` is tier 1 of the local-search
ladder; escalate to QMD only when it returns `ZERO-RESULT` for a term that
should exist.

## Token discipline

Do not paste registries or dashboards into context. Use `status` when orientation
is needed; otherwise go directly to `show` for the ID and its cited evidence.
A terminal `repeat-check` hit is a candidate for reuse, not proof of an
equivalent question. Compare fingerprint, comparator, gate and evidence before
avoiding a rerun. Search misses do not establish absence.
