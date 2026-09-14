# Structured Experiment Campaigns

## Contents

1. Scope and authority
2. Separate campaign concerns
3. Lock the experiment contract
4. Resolve the campaign plan before execution
5. Track coverage, not only jobs
6. Preserve metric identity and result origin
7. Promote only reproduced experiments to a catalog
8. Explicitly excluded patterns
9. Pilot and handoff criteria

## 1. Scope And Authority

Use this workflow for repeated, comparable experiments whose inputs and outputs
can be described by a stable schema. Typical cases include parameter sweeps,
seed studies, benchmark matrices, repeated evaluators, ablations, and external
campaigns imported from Slurm or another execution path.

Do not impose it on one-off calculations, early exploratory work whose contract
changes after nearly every run, or workflows dominated by bespoke large
artifacts and tightly coupled checkpoints. Start with the ordinary research
contract and introduce campaign structure only when it reduces ambiguity,
duplicate work, or manual comparison.

The living `DESIGN-SSOT` owns scientific definitions and gates. Immutable
evidence artifacts own computed values. Campaign files coordinate repeated
measurement; they do not become a second scientific authority.

## 2. Separate Campaign Concerns

Represent the campaign as distinct, linked objects:

```text
research question
-> candidate space
-> measurement contract
-> selection policy
-> execution operation
-> evidence artifact
-> scientific gate
```

- **Candidate space**: the entities or parameter combinations that may be
  measured, including domains and exclusions.
- **Measurement contract**: required and optional inputs, defaults, outputs,
  units, metric definitions, stochastic behavior, validity checks, and failure
  semantics.
- **Selection policy**: why the next point or batch is chosen. Keep this
  swappable across grid, random, optimization, information-gain, or manual
  discriminator policies.
- **Execution operation**: one concrete attempt under a scheduler, local
  runner, laboratory procedure, or external source.
- **Scientific gate**: the independent rule that determines what the result may
  support.

Do not let one run script silently own all these meanings. Version each changed
contract or policy and link it from operations and artifacts.

## 3. Lock The Experiment Contract

For a repeated campaign, instantiate
`assets/structured-experiment-contract-template.yaml` and record:

- stable experiment identifier and version;
- implementation path, code commit, and content hash;
- required inputs and their domains;
- optional inputs, domains, and defaults;
- scientific target properties;
- method-specific observed properties, namespaced by evaluator or experiment;
- units, aggregation, metric definition, masks, split, and tolerance;
- stochasticity, seed policy, deterministic flags, and replica policy;
- known-answer anchors, preconditions, failure semantics, limitations, and
  permitted non-claims.

A target property names the scientific quantity of interest. An observed
property names that quantity as produced by a specific protocol. Never compare
two values merely because their targets share a short label.

```text
target: force_error
observed: force-evaluator-v2:force_rmse_per_atom
```

Changing an evaluator, implementation, aggregation, unit, mask, split, or
tolerance changes the observed-property identity and usually the experiment
contract version.

## 4. Resolve The Campaign Plan Before Execution

Instantiate `assets/campaign-plan-template.yaml`, then produce a resolved
`assets/plan-receipt-template.yaml` before an expensive or multi-run launch.
The receipt records what the plan expands to, rather than only preserving an
editable template.

Resolve and verify:

```text
point and replica count
expanded point-manifest path and hash
DIRECT / REUSED-EXACT / EXTERNAL / MATCHED counts
blocked, invalid, and to-run counts
estimated CPU/GPU time, memory, walltime, and storage
dependencies and exact input hashes
execution backend, packetization, and immutable output namespaces
preflight result, unresolved assumptions, and stop conditions
```

Treat a dry-run that only parses syntax as insufficient. A campaign is ready to
launch only when the resolved receipt exposes cardinality, reuse decisions,
cost, outputs, and blocking conditions. Do not submit a large campaign while
the receipt is incomplete or its preflight gate fails.

## 5. Track Coverage, Not Only Jobs

Use `assets/campaign-coverage-template.tsv` when the candidate space has many
comparable points. Keep one row per condition fingerprint and update it from
verified artifacts or scheduler state, never from memory.

Use these point states:

| State | Meaning |
|---|---|
| `UNSEEN` | Defined by the candidate space but not selected |
| `PLANNED` | Selected and included in a resolved plan |
| `REQUESTED` | Submitted or handed to an execution path |
| `DIRECT` | Measured under the current contract |
| `FAILED` | Attempted but operationally or scientifically failed |
| `REUSED-EXACT` | Reused after full condition-fingerprint equality |
| `EXTERNAL-VERIFIED` | Imported source passed manifest, fingerprint, and artifact validation |
| `MATCHED-ONLY` | Similar result found; locator only, not accepted evidence |
| `INVALID` | Point violates the experiment contract or candidate domain |

Keep scheduler status, result origin, source validation, contract validation,
and scientific status in separate columns. A completed job does not imply a
measured point; a measured point does not imply scientific acceptance.

Before selecting or launching more points, summarize missing controls, failed
regions, unsampled strata, exact reusable results, and outcome-dependent
selection. This makes campaign incompleteness and selection bias visible.

## 5a. Attribute Multi-Site Gains By Decomposition Identity

When a gain involves more than one intervention site, causal attribution
requires the factorial arm set and its decomposition identity
(for example, `BOTH − NONE = (A − NONE) + (B − NONE) + X`); report the
cross-term `X` per cell, not only in aggregate. A narrative attribution that
skips the single-site arms is not promotable — observed: a plausible
single-site story was refuted the day the missing arm was measured.

## 6. Preserve Metric Identity And Result Origin

Every reported metric records both:

```text
target property
observed property = experiment/evaluator namespace + metric definition
```

Classify the origin of every consumed result independently of scientific
status:

| Origin | Meaning | Acceptance behavior |
|---|---|---|
| `DIRECT` | Measured by the current contract and operation | Eligible after ordinary validation |
| `REUSED-EXACT` | Existing result with full fingerprint equality | Eligible after equivalence receipt |
| `MATCHED` | Similar result found through looser search | Locator only; never auto-accept |
| `EXTERNAL` | Produced outside the current execution path | Eligible only when source validation is `VERIFIED` |

Do not infer exact reuse from names, paths, tags, major versions, or `latest`.
Compare implementation, code, data, resolved configuration, representation,
environment, numerical flags, seed policy, split, metric identity, tolerance,
and evidence cutoff. Keep origin separate from result-use state such as
`VALID`, `DIAGNOSTIC-ONLY`, or `INVALID-FOR-ACCEPTANCE`.

## 7. Promote Only Reproduced Experiments To A Catalog

Treat an Experiment Catalog as a verified protocol library, not an inventory of
ideas or every attempted run. Do not create a catalog entry during initial
exploration merely because a result is promising.

Use this lifecycle:

```text
DRAFT CONTRACT
-> VALIDATED CAMPAIGN
-> ACCEPTED RESULT
-> REPRODUCTION-PASS
-> CATALOG-CANDIDATE
-> CATALOGED
```

Instantiate `assets/verified-experiment-catalog-entry-template.yaml` only after
the experiment has an accepted result and a condition-equivalent reproduction
from a clean or independently reconstructed consumption environment.
Complete one `assets/registration-checklist-template.md` receipt under the
project policy before changing the entry to `CATALOGED`.

Require before `CATALOGED`:

- frozen input/output domains and observed metric identities;
- canonical implementation and dependency closure with hashes;
- known-answer anchors and declared tolerance passing;
- reproduction command, environment, receipts, and accepted artifacts;
- stochastic seed/replica behavior demonstrated within the declared rule;
- known limitations, claim ceiling, failure semantics, and non-claims;
- explicit owner approval.

The catalog entry links canonical contracts, code, receipts, and artifacts. It
does not duplicate result data or become their owner. Use versioned entries and
retain `DEPRECATED` or `INVALIDATED` entries with scope, evidence, successor,
and revisit conditions; never silently replace or delete them.

## 8. Explicitly Excluded Patterns

Do not import these patterns from ado-like systems into the general workflow:

- making a database, dashboard, or resource registry the scientific SSOT;
- treating operational success as scientific acceptance;
- accepting `MATCHED` results or memoization hits without a full fingerprint;
- equating major semantic version or experiment name with condition equality;
- citing mutable `latest` resources as evidence;
- automatically deleting failed, negative, superseded, deprecated, or
  invalidated scientific records;
- imposing a rigid schema on early one-off exploratory work;
- coupling the research contract to Ray, MySQL, Slurm, or any one backend;
- attributing compatible external results to the current campaign without an
  explicit origin and validation receipt.

## 9. Pilot And Handoff Criteria

For the first uses, keep a project-local temporary policy and record whether
the workflow:

- prevented duplicate runs;
- exposed missing controls or unsampled strata earlier;
- caught invalid points before submission;
- reduced metric/evaluator ambiguity;
- allowed a fresh reader to reproduce coverage and reuse decisions from files;
- cost less to maintain than the errors and manual joins it replaced.

Promote refinements only under the normal temporary-policy lifecycle. At
handoff, name the contract, plan, resolved receipt, coverage ledger, latest
verified artifacts, unresolved matched/external results, and next scientific
gate.
