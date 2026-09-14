# Operational Know-How Lifecycle

## Contents

1. Purpose and authority
2. Workspace and record contract
3. Normalize for reuse
4. Analyze recurrence and choose an action
5. Prefer scripts and existing code
6. Transfer to the owning skill
7. Quarantine completed knowledge
8. Validate and review

## 1. Purpose And Authority

Use this workflow for consequential or repeated operational mistakes in terminal work, remote
access, scheduler submission, execution, copying, moving, permissions,
compression, cleanup, polling, parsing, or other support operations. Its goal
is to turn small recurring failures into durable guardrails without confusing
them with scientific evidence.

Keep authority separate:

- `EXPERIMENT-LEDGER` owns scientific attempts and decisions.
- `EVIDENCE-ARTIFACT` owns scientific measurements.
- `OPS-KNOWHOW-LOG` owns operational incidents, normalized signatures,
  preventions, automation candidates, and transfer status.
- the target skill owns a prevention only after its rule, script, or test is
  actually installed and validated there.

An SSH quoting error, failed `sbatch`, wrong host, permission mismatch, or bad
archive command can explain missing evidence, but it is not itself a negative
scientific result. Cross-link the records; do not merge their state machines.

## 2. Workspace And Record Contract

For initial capture, lookup, recovery updates, paths, privacy and single-writer
intake, use [operational-error-recording.md](operational-error-recording.md).
Do not load this whole lifecycle for an ordinary error. It governs recurrence
analysis and transfer to a durable prevention owner, not automatic logging.

The recording reference owns `ops_knowhow/incidents.tsv`. This maintenance
workflow additionally uses generated `analysis.tsv`, `transfer-index.tsv`,
`transfers/pending/`, and `quarantine/transferred/` or `quarantine/rejected/`.
Use `assets/knowhow-transfer-receipt-template.json` for transfer closure.
Receipts/indexes do not replace scientific evidence or the incident owner.

## 3. Normalize For Reuse

Normalize the signature around the preventable mechanism, not the literal
command or one job ID. Good signatures are stable and parameter-free:

```text
slurm:gpu-exclusive-accidental
slurm:partition-host-mismatch
transfer:executable-bit-lost
shell:remote-quoting-expanded-locally
filesystem:recursive-search-unbounded
archive:source-deleted-before-verification
monitor:polling-cadence-too-fast
```

Keep distinct mechanisms separate even when they share an error message. If
the mechanism is unknown, leave the signature blank and status `OBSERVED`
rather than guessing.

Use these lifecycle states:

```text
OBSERVED -> NORMALIZED -> CANDIDATE -> PILOTING -> TRANSFERRED
                     \-> LOCAL-ONLY | REJECTED | SUPERSEDED
TRANSFERRED + recurrence -> REGRESSION
```

## 4. Analyze Recurrence And Choose An Action

Generate a deterministic recurrence view:

```bash
python <research-skills>/scripts/operational_knowhow.py analyze <project-root>
```

The analyzer groups by normalized signature, excludes transferred/rejected
records from the active queue, and reports:

```text
active and total count
maximum severity
operation and environment scopes
incident IDs and candidate target skills
existing-helper search status
analysis state and next action
```

Use these default triggers:

- one `HIGH` or `CRITICAL` incident: review immediately;
- the same signature twice: require an existing-helper search and prevention
  candidate;
- the third manual implementation of the same operation: require a reusable
  script or an explicit reason automation is unsafe;
- recurrence after transfer: classify `REGRESSION` and audit activation,
  discoverability, invocation, and coverage before writing another rule.

Frequency alone does not justify global promotion. A project-specific path,
cluster, credential flow, or one-off exception may remain `LOCAL-ONLY`.
Review these groups when the user requests a skill update or during a relevant
maintenance pass, not after every error. The analyzer's PROMOTION-CANDIDATE is
a review queue label, not proof that global promotion gates passed. Aggregate
across projects by `(project locator, incident_id)` and signature only when
requested; preserve each project's log as the owner, with no central duplicate.

## 5. Prefer Scripts And Existing Code

For repeated deterministic work, use this implementation ladder:

```text
SEARCH -> VERIFY -> REUSE -> PATCH -> EXTEND -> NEW
```

Before writing code:

1. Search the project and relevant skill `scripts/`, tests, profiles, and
   canonical instructions by operation semantics, not only filename.
2. Verify the existing helper against one known-good and one known-failure
   case in the current environment.
3. Reuse it unchanged when possible.
4. Otherwise parameterize or patch the smallest owned boundary.
5. Extend through a wrapper only when the canonical helper must remain stable.
6. Create a new helper only after recording why no existing helper is a safe
   owner.

For an `errexit` (`set -e`) stage wrapper, do not submit unless an `ERR` trap
prints both `$LINENO` and `$BASH_COMMAND`; run the available stage-script
preflight first. A BLOCK result is a submission gate, not a warning to waive.

```bash
python3 <research-skills>/scripts/validate_stage_script.py stage.sbatch
```

Prefer Python for structured parsing, validation, state transitions, atomic
writes, and cross-platform logic. Prefer Bash for short, bounded Unix command
composition when quoting and failure semantics remain transparent. Do not use
an LLM to regenerate a fragile multi-line shell pipeline on every occurrence.

Every reusable operational helper should have, in proportion to risk:

- explicit arguments and bounded targets;
- `--dry-run` or an inspectable preflight for state-changing work;
- idempotent behavior or explicit duplicate protection;
- fail-closed validation before destructive, remote, or costly actions;
- quoted paths, stable exit codes, and useful stderr;
- no embedded credentials or machine secrets;
- positive known-answer and negative/corrupted tests;
- one canonical owner, version/hash, and minimal invocation example.

Do not create a second helper because adapting an existing one feels less
convenient. New code must remove a named incompatibility, not merely rename or
reformat an existing operation.

The LLM should choose the operation, locate the helper, bind parameters,
inspect results, and explain exceptions. The script should perform repeated
mechanics and validation.

## 6. Transfer To The Owning Skill

Choose the narrowest durable owner, for example `hpc-skills` for scheduler and
shared-filesystem safeguards, `local-search` for bounded retrieval, or a
project/server skill for machine-specific behavior.

A project-local skill is a normal first-class owner, not an exception, failed
global promotion, or temporary fallback. It may permanently own procedures,
scripts, profiles, tests, and rules whose correct scope is that project. A
verified transfer to it uses the same `TRANSFERRED` state and receipt gates as
a transfer to a shared skill. Global promotion is optional and justified only
when the rule genuinely generalizes across projects.

`LOCAL-ONLY` means a record remains an untransferred project note or policy; it
does not describe knowledge already owned by a project-local skill.

A transfer packet includes:

```text
normalized signature and source incident IDs
general mechanism and excluded project-specific details
existing helper search and reuse/patch/new decision
target skill and exact target artifact
rule/script/test delta
known-good and known-failure validation
canonical and installed activation status
approver, completion time, and target SHA-256
```

Do not mark `TRANSFERRED` merely because a recommendation was written or sent
in chat. Require all of:

1. the target skill/reference/script is updated at its canonical owner;
2. a reusable helper is used when repeated mechanics are involved;
3. relevant positive and negative tests pass;
4. any runtime-installed copy is synchronized and discoverable;
5. the receipt names the exact target artifact and verified hash;
6. the target owner or user approves the transfer.

Prepare the JSON receipt under `transfers/pending/`, then close it with:

```bash
python <research-skills>/scripts/operational_knowhow.py mark-transferred \
  <project-root> --receipt ops_knowhow/transfers/pending/<transfer-id>.json
```

The command verifies the target hash and receipt gates before changing status.
When canonical and runtime copies are distinct, list both under
`verified_artifacts`; each path and SHA-256 is checked before closure.
It is idempotent for an already indexed identical transfer and rejects an ID
reused for different content.

## 7. Quarantine Completed Knowledge

After a verified transfer:

- mark matching active incident rows `TRANSFERRED` with the transfer ID;
- append one row to `transfer-index.tsv`;
- move the closed receipt to `quarantine/transferred/`;
- exclude transferred incidents from the active analysis queue;
- retain the original incident facts and evidence links.

Quarantine means preserved, inactive, and search-on-demand. It does not mean
deleted, untrusted, or safe to rewrite. Exclude quarantine from default startup
context and routine active searches, but include it when auditing regressions
or provenance.

If the same signature recurs, append a new `REGRESSION` incident linked to the
old transfer. Do not reactivate or edit the frozen receipt. Open a successor
transfer only after determining whether the failure was missing activation,
bad invocation, uncovered scope, stale environment, or an ineffective guard.

Rejected or unsafe automation packets move to `quarantine/rejected/` with the
reason retained. Never delete a failed prevention and later rediscover it as a
new idea.

## 8. Validate And Review

At a periodic review or project handoff:

1. resolve blank signatures and redaction reviews;
2. inspect `REVIEW-NOW`, `PROMOTION-CANDIDATE`, and `REGRESSION` groups;
3. verify every candidate searched existing helpers;
4. merge duplicate helper proposals under one canonical owner;
5. confirm transferred receipts still point to the installed artifact hash;
6. report active counts, pending transfers, regressions, and quarantined
   completions separately.

Do not judge this system by the number of rules or scripts created. Prefer
fewer canonical helpers, fewer repeated incidents, successful negative tests,
and faster recovery by a fresh session without chat memory.
