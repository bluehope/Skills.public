# Compute And Artifacts

## Contents

1. Scheduler and live status
2. Immutable attempt layout
3. Minimum artifact schema
4. Comparison lifecycle
5. Metric identity and result origin
6. Operational guardrails
7. Completion, convergence, and downstream permission

## 1. Scheduler And Live Status

Run heavy compute through the scheduler, not login nodes. Document environment,
profile/module loading, partition, resource limits, and task-to-partition
mapping near project start.

Track each job with:

```text
job id, command/submit script, partition, resources, submitted time, status,
artifact path, verdict, verified_at, canonical machine path/hash
```

Respect concurrent-job limits. Use dependencies or staged submissions rather
than flooding shared queues.

## 2. Immutable Attempt Layout

Prefer:

```text
outputs/<study-id>/attempts/job_<scheduler-id>/
outputs/<study-id>/attempts/attempt_<UTC>_<short-config-hash>/
```

Never overwrite a previous attempt. Keep logs and failure reason for failed
runs. `latest` is a mutable convenience pointer and cannot support a claim.

Checkpoint continuations record parent path/hash, start/end step, strict load,
and changed settings.

## 3. Minimum Artifact Schema

```text
identity:
  artifact_id, created_at_utc, artifact_role, claim_level
reproduction:
  scheduler/job, exact command, config path/hash, code repo/commit,
  environment, seed, deterministic flags, tolerance
data_contract:
  data manifest/hash/split, source/derived target, unit/sign/transform,
  label provenance, cell/graph/grid contract, mask/aggregation
lineage:
  checkpoint input/output hashes, resume parent, preflight artifacts
evidence:
  metrics with target and observed-property identity, result origin and source
  validation, pass/fail rule, limitations, raw logs, next decision
```

Store `unknown` with a reason instead of silently omitting a required field.

## 4. Comparison Lifecycle

A reference or candidate advances through:

```text
prepared -> executed -> contract-validated -> comparable -> report-included
```

Execution alone does not make artifacts comparable. Validate primitive/input,
profile, path, masks, evaluator, and metric identity first.

If a process exits nonzero or reports post-write warnings, accept it only as
`accepted_with_warning` when raw logs, artifact completeness, and a written
rationale all pass. Otherwise mark `failed` or `incomplete`.

## 5. Metric Identity And Result Origin

Separate the scientific target from the method-specific observation:

```text
target_property: the scientific quantity of interest
observed_property: <experiment-or-evaluator-id>:<fully-defined-metric>
```

Record evaluator/experiment contract, representation, reference, mask,
aggregation, unit, split, tolerance, and evidence cutoff with every observed
metric. A shared target label does not make two observed values comparable.

Classify result origin independently of scientific status:

| Origin | Meaning | Evidence rule |
|---|---|---|
| `DIRECT` | produced under the current operation and contract | ordinary validation still required |
| `REUSED-EXACT` | reused after full condition-fingerprint equality | require an equivalence receipt |
| `MATCHED` | similar result found by a looser search | locator only; never auto-accept |
| `EXTERNAL` | produced outside the current execution path | require source validation `VERIFIED` |

Do not infer `REUSED-EXACT` from a name, path, tag, `latest`, or major version.
Keep origin separate from `VALID`, `DIAGNOSTIC-ONLY`, acceptance, and claim
level. Read
[structured-experiment-campaigns.md](structured-experiment-campaigns.md) when
the results belong to a repeated campaign.

## 6. Operational Guardrails

- Keep recurring terminal, scheduler, connection, transfer, file, and archive
  incidents in the `OPS-KNOWHOW-LOG`, not as scientific failures. Follow
  [operational-knowhow-lifecycle.md](operational-knowhow-lifecycle.md) to group
  signatures, reuse or patch an existing helper, transfer verified guards to
  the owning skill, and quarantine completed receipts.
- Write experiment commands and submit scripts to files, with recorded
  hashes, before execution — always, not only when quoting is fragile.
  (Read-only queries and hash checks are exempt.)
- Any transformation of a validated script (sed derivation, manual edit,
  template substitution) invalidates its validation; re-run the preflight
  validator on the derived file before submission. Observed failure modes:
  unexpanded variables in sed-derived wrappers, and stale positional
  arguments surviving a partial substitution.
- Capture raw logs during diagnosis; narrow filters can hide errors.
- Register every command-line option in the parser.
- Investigate empty results through raw logs and job journals; do not assume
  cached data are non-empty.
- Audit PBC graph saturation and numerical convergence explicitly.
- Treat GPU JIT/library failures separately from model correctness; a CPU
  forward smoke can isolate environment from architecture.
- Separate production-code commits from experiment/analysis documentation when
  practical. Commit only when authorized.

## 7. Completion, Convergence, And Downstream Permission

For every monitored compute lane, render and record distinct state columns;
never collapse them into one green/complete label:

```text
scheduler: PENDING | RUNNING | COMPLETED | FAILED | CANCELLED | TIMEOUT
science:   ELECTRONIC-CONVERGED | ARTIFACT-READY | SET-READY | GEOMETRY-PASS
permission: DOWNSTREAM-PERMITTED | BLOCKED
gate:      MECHANICS-PASS | PHYSICS-PASS (both required; mechanics never implies physics)
```

- Define the convergence metric from the exact input and the code's own
  stopping rule as documented by the code-specific skill (for DFT codes,
  `$dft-skills` and its children own those rules); retain other residuals as
  diagnostic traces only. Preserve the metric name, value, gate, and
  normal-finish marker in machine-readable evidence.
- Make a direction-level source ready only after formal electronic convergence,
  normal completion, required method flags, and a nonempty downstream artifact.
  Make a multi-direction DMI/Jx set ready only after every required direction
  passes. Make it downstream-permitted only after the declared geometry and
  provenance gates also pass.
- Treat a log-declared artifact path as authoritative when legacy wrappers
  write outside an immutable attempt directory; record that path explicitly.
  Do not discover artifacts through broad sibling searches or silently borrow
  a sibling attempt's output.
- Before retrying, recover the parent state and inspect active/pending sibling
  jobs. Never duplicate `RUNNING` or `PENDING` work. Submit an immutable
  child only after a named terminal failure, timeout, missing artifact, or
  formal convergence failure; record parent job/path/hash, unchanged contract,
  changed controls, and the next gate.
- For dashboards, lead with the research question and a readiness matrix that
  separately shows scheduler state, electronic convergence, artifact,
  direction/set readiness, geometry gate, and downstream permission. A plot or
  scheduler `COMPLETED` status is operational evidence, never acceptance.
