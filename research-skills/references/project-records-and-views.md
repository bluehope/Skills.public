# Project records, folders and views

## Ownership and human navigation

Use this layout for new projects, creating folders only when used. Existing
projects keep their layout: map registry paths in research_state_schema.json;
adopt previews inventory and does not move their files.

| Location | Owner / content |
|---|---|
| README.md | stable purpose, entry points and instructions |
| STATE.md | current objective, conclusion, blocker, next action; generated block plus manual notes |
| research_organization/ | stable-ID registries, relationships, changes, capabilities |
| plans/ | research plans and experiment contracts |
| campaigns/ | execution envelopes linking units and attempts |
| outputs/<unit-id>/<attempt-id>/ | actual inputs, logs, checkpoints, raw output; failed attempts stay here |
| results/ | frozen result packets, including negative results; metrics and evidence manifests |
| interpretations/ | revisable explanations, limitations and alternative mechanisms |
| decisions/ | decisions, pivots and meaningful scientific lessons |
| reports/sources/ | external source cards and preserved sources |
| .skills/ | project-owned procedures, helpers and checks |
| ops_knowhow/ | consequential operational incidents and verified preventions |
| research_dashboard/ | existing registries, observations and generated views |
| archive/ | superseded editable documents and historical views |

Names: `<stable-id>--<short-title>.md` or an equivalent folder. Korean and
English titles are supported. IDs survive renaming. Avoid final2/latest_final.
Directory categories are not the scientific parent hierarchy. A campaign may
coordinate many units; results and attempts are linked rather than duplicated
under every direction/campaign. Large evidence stays at its original immutable
location, identified by locator and hash. PATH_MAP locates environments and
builds; it does not own values or verdicts. Do not move failed attempts into a
failure folder or relocate evidence when its interpretation changes.

## Registration boundary and commands

Register durable plans, interpretations, results, decisions, meaningful
attempts/failures/lessons and explicitly requested records. Do not register
every read, harmless typo or transient connection error. Read-only analysis
ends with an answer. Scientific lessons retain expectation, observation,
condition, evidence, scoped conclusion and revisit trigger; operational
prevention belongs to ops_knowhow with cross-links when relevant.

Run commands with `python <skill-root>/scripts/research_state.py --project PROJECT`.
The following are subcommands (place --project before the subcommand):

```text
adopt                          # inventory / dry-run
adopt --apply                  # preserve existing paths and headers
document --role plan --title "Plan" --create --related U-1 --request-key plan-1
document --role interpretation --title "Explanation" --path interpretations/note.md --related U-1
document --role result --title "Negative result" --path results/result.md --status FROZEN --related U-1
document --role lesson --title "Lesson" --create --related DOC-EXISTING --event-at 2026-09-12T10:00:00Z
document --id DOC-EXISTING --role plan --title "Revised plan" --path plans/plan.md
move-document DOC-EXISTING --to plans/DOC-EXISTING--new-title.md --title "New title"
view timeline --limit 20
view context --id D-1 --limit 20
view links --limit 20
view capabilities --limit 20
render
validate
recover                        # inspect pending local transaction
recover --apply                # finish only if expected hashes still match
```

`document --template FILE --create` copies a chosen Markdown template. The
document catalog retains existing columns; RECORD_METADATA.json owns new
event/record times, related IDs, hashes, request keys, supersedes and revision
history. The catalog owns title/path/status; metadata snapshots record revisions.
Use --supersedes ID for a frozen result's successor. File hash validation is
not scientific acceptance. Editing a frozen file outside the CLI is detected
by lint; living-document changes require re-registration with the existing ID.
Unknown event dates remain unknown, never inferred from registration time.

`register --batch FILE --request-key KEY` validates the full batch in a bounded
staging tree. Exact retries return the prior receipt; changed requests with the
same key are refused. Explicit ID retries must match the existing fields.
Without an explicit ID or request key, generic register does not promise
semantic deduplication. Similarity hits require condition comparison.

Writes use a local exclusive lock, before-hash checks, per-file atomic replace
and a recovery journal. Multi-file publication is recoverable, not one atomic
filesystem operation. CLI reads refuse a pending journal. Conflicted sync
copies block writing. Dropbox is not a distributed lock: serialize writers
across machines and wait for sync before handing off; offline concurrent edits
cannot be guaranteed detectable before sync. Keep the journal for recovery,
and never remove a lock without resolving its ownership.

Moving a document updates the catalog, metadata and generated links. Prose
links are not blindly rewritten: inspect and update their declared owners.
Existing project migration starts with inventory; physical moves are explicit.

## Project capabilities and reuse

Reuse an existing capability index if available. Otherwise `capability --record
FILE` maintains research_organization/CAPABILITIES.json. Input fields:
`id`, `function`, `applies_when`, `owner`, `code`, `invocation`, `validation`.
Owner/code/validation are existing project-relative file paths; the command
records the helper hash. `view capabilities` returns locators and does not
execute the invocation. Lint flags changed helpers for revalidation.
External shared skills may be routed through a project-local owner document.

Before making a helper, search capabilities, project skills and relevant
ops_knowhow by mechanism. Follow SEARCH → VERIFY → REUSE → PATCH → EXTEND → NEW.
A project-local skill is a permanent valid owner; global promotion is optional.
Project rules specialize conditions and environments without silently waiving
evidence requirements or expanding the user's request.

## Generated views and version interpretation

`render` preserves text outside STATE markers and generates timeline.md,
context.md, links.md and capabilities.md under research_dashboard/views/.
These are projections, not independent truth. Context follows related IDs;
timeline distinguishes event and registration dates and puts unknown dates last.
Use bounded `view` output before opening selected canonical records.

VERSION is the skill release; schema_version is the registry format contract.
Project managed_by records created_with (unknown for legacy projects),
last_written_with and written_at. validated_with records the version, time,
explicit structural lint scope and registry hashes; it remains a historical
receipt after edits, not a claim that current content still passes. `version`
is read-only. `render` does not grant migration or scientific approval.

No Python: preserve durable content in an UNVERIFIED intake Markdown document,
then register and lint in the next available session. Do not manually append
unchecked rows while presenting them as validated registrations.

## Cross-model evaluation (not yet executed)

`tests/fixtures/progressive_loading_cases.json` supplies shared review prompts
and expected reading routes; `tests/progressive_loading_test.py` checks their
local references and reports static character counts only. It does not run a
model, prove route selection, or measure token usage. Additional specialist
skills and their references must be included in any real cost comparison.

Use isolated copies of the same fixture for each available model: read-only
status, draft plan, record a negative result, recover prior equivalent work,
and find a local helper. Score cited-ID correctness, unauthorized writes,
duplicate attempts, retrieved bytes and task time. Script tests establish
mechanics only; do not claim cross-model behavioral validation without runs.
