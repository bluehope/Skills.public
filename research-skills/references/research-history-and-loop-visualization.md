# Research History And Loop Visualization

## Contents

1. Purpose and authority
2. Three-level history model
3. Define a unit experiment
4. Trigger aggregation and human review
5. Build the decision view
6. Verdict and closure semantics
7. Track expectation and surprise
8. Plot and table contracts
9. Refresh, validate, and hand off

## 1. Purpose And Authority

Use this workflow when a research question accumulates enough iterations that a
human can no longer reconstruct the important direction changes, comparisons,
and anomalies from the experiment ledger alone. The output is a compact
**research trail**: a decision-oriented history of what was tried, why it was
tried, what happened, and what changed next.

The trail is a rendered view, not a new scientific source of truth:

- `EXPERIMENT-LEDGER` owns attempt intent, interpretation, and decisions.
- `EVIDENCE-ARTIFACT` owns computed values and pass/fail evidence.
- `DESIGN-SSOT` owns metric definitions, comparators, and scientific gates.
- hypothesis and direction-change records own branch topology and pivots.
- a normalized history snapshot and its plots/tables are regenerated one-way
  from those authorities at a declared evidence cutoff.

Never hand-edit a rendered summary to repair the underlying history. Correct
the canonical owner, regenerate the snapshot, and render again.

## 2. Three-Level History Model

Keep three levels distinct:

```text
attempt/run -> unit experiment -> research direction
```

- **Attempt/run**: one execution or observation with an immutable artifact.
- **Unit experiment**: a scientifically comparable group of attempts that
  answer one bounded question under one measurement contract.
- **Research direction**: a sequence or graph of unit experiments connected by
  hypothesis, decision, blocker, and pivot edges.

Schedulers and run folders expose attempts. They do not define unit
experiments. Calendar weeks and arbitrary chunks of 10 or 20 runs are also not
scientific groups unless a recorded contract change happened at that boundary.

Assign every attempt to at most one primary unit experiment for aggregation.
Secondary tags may support search, but must not double-count the attempt in
summary statistics.

## 3. Define A Unit Experiment

Create or close a unit experiment around a stable tuple:

```text
question and competing expectation
test case or cohort
baseline/comparator identity
measurement and metric contract
intervention family or factor being varied
research lane and claim ceiling
aggregation and decision rule
```

Give it a stable `unit_id`. Split the unit when the target, evaluator, split,
mask, aggregation, unit, comparator, test case meaning, or principal question
changes. A code change need not split the unit when it is the declared
intervention and the measurement contract remains comparable; record the exact
code identity on every attempt.

Before running, record the expected relation to the comparator:

```text
BETTER | WORSE | NO-CHANGE | UNCERTAIN
```

Also record what each possible outcome would change. `UNCERTAIN` is legitimate
for exploration, but it cannot later be rewritten as a directional prediction.

At closure, summarize:

```text
attempt count and eligible count
coverage and failed/invalid regions
median or preregistered aggregate
best result with condition fingerprint
delta from the frozen comparator
expected versus observed relation
representative supporting and contradicting artifacts
verdict, remaining uncertainty, and next decision
```

The summary links raw evidence; it does not copy or replace it.

## 4. Trigger Aggregation And Human Review

Start a research trail before history becomes expensive to understand. Use any
of these triggers:

- roughly 30 comparable attempts exist under one question;
- the attempt ledger no longer fits a compact review screen;
- the same test case or metric has been revisited across three unit
  experiments;
- a major pivot, contract change, or comparator change occurs;
- a human asks which changes actually helped or hurt.

At 100 or more attempts under one active research question, require all of the
following before another large batch:

1. group attempts into unit experiments;
2. regenerate the research trail at a frozen evidence cutoff;
3. review metric trends, coverage, failed regions, and surprises;
4. record a human decision: `CONTINUE`, `FOCUS`, `PIVOT`, `PAUSE`, or `CLOSE`;
5. name the next unit experiment and its expected information gain.

Do not reset this threshold by renaming the campaign or opening a cosmetic new
branch. Count all condition-relevant attempts since the current question was
opened, including failed and superseded attempts.

## 5. Build The Decision View

Render coordinated views in this order. The top answers "what is true now?";
the vertical trail answers "how did we get here?"; detailed logs stay below
the scientific reasoning.

### A. Current decision and active frontier

Lead with the current question, strongest supported conclusion, failed or open
promotion gate, active or revisit-able branches, and one next decision. Show
mechanism, promotion, branch disposition, and closure basis as separate text
fields. Do not fill the top with scheduler counts or historical attempts.

Select the current unit from an explicit state-capsule pointer supplied as
`--current-unit-id`. Without one, infer current only when exactly one unit's
latest event is `ACTIVE`, and label that selection `INFERRED`. With zero or
multiple active units, render `CURRENT UNKNOWN`. Never use the last event or
last unit as a current-state fallback.

### B. Top-to-bottom research timeline

Show only decision-bearing nodes:

```text
question -> hypothesis -> unit experiment -> evidence verdict -> decision/pivot
```

Collapse individual attempts inside their unit. Render unit experiments in
chronological order from top to bottom so scroll direction matches causal
reading. The current conclusion may be repeated in the top summary, but do not
reverse the scientific timeline merely to place the newest event first.

Use vertical swimlanes only when two or three branches materially diverge and
rejoin. Mark branches as `ACTIVE`, `PAUSED`, `DEPRIORITIZED`, `MERGED`,
`BLOCKED`, `HARD-CLOSED`, or `HISTORICAL-SCOPED`, and link every evidence node
to its canonical artifact or ledger span. Collapse old linear spans and keep
attempt-level and operational logs below the route.

Use explicit edge semantics. `BLOCKS-PROMOTION` must not look like
`FALSIFIES-WITHIN-SCOPE`; `DEPRIORITIZES` must not look like a hard closure.
Do not rely on color alone: pair text with line style, border style, or an
accessible symbol.

For the single-parent snapshot contract, require `parent_event_id` and
`edge_type` together. Reject missing parents, self-edges, and parents whose
sequence is not earlier than the child. Render the parent, child, and edge type
as accessible text in addition to visual styling. Use a separate edge table if
the project later needs multiple parents per event.

### C. Metric history

Plot eligible attempt-level values against stable sequence number or evidence
time. Include:

- comparator and gate lines;
- unit-experiment boundaries and major pivot markers;
- stable colors for intervention families;
- distinct status marks for accepted, diagnostic, failed, and invalid points;
- uncertainty or replica summaries when defined by the contract;
- tooltips or links to the immutable artifact.

Create separate panels when metric identities, contracts, or comparators are
incompatible. Treat comparator identity as a fail-safe panel boundary even if a
project mistakenly left the contract version unchanged.
Never draw a continuous line across a comparator, evaluator, unit, split,
aggregation, or target-definition change without an explicit comparability
receipt.

### D. Unit-experiment scorecard

Use one row per unit experiment. At minimum show:

```text
unit / question / test case / intervention family
attempts and eligible attempts / comparator
aggregate and best value / direction-aware delta
expected relation / observed relation / surprise count
coverage or failed region / verdict / next decision / evidence links
```

Include mechanism verdict, promotion verdict, branch disposition, closure
basis, and failed gate as distinct columns. A single `REJECTED` column is not
sufficient.

Rank only within a compatible metric family. A global leaderboard that mixes
test cases, contracts, or claim levels is forbidden.

### E. Surprise and anomaly table

Surface, rather than average away:

- improvements where degradation was expected;
- degradation where improvement or invariance was expected;
- factor interactions or non-monotonic regions;
- failures clustered by condition;
- results that change sign across test cases or seeds;
- operational anomalies that could counterfeit a scientific trend.

Every row states whether it is scientific, diagnostic, operational, or still
unresolved, plus the cheapest useful follow-up.

### F. Decision and operational logs

Put decision history and operational history below the route, scorecard, and
surprises. Decision logs may be newest-first for rapid inspection. Keep
scheduler and runtime failures in a separate operational section so they do
not visually imply scientific rejection.

## 6. Verdict And Closure Semantics

Every decision-bearing node carries four independent fields:

```text
mechanism verdict / promotion verdict / branch disposition / closure basis
```

Render `FORMAL-DERIVATION` and `EXACT-PHYSICAL-LAW` as scoped hard closures
only when the node links its proposition, assumptions, domain, and derivation
or evidence. Render `CONTRACT-PROOF` as blocked under the current contract,
`SCOPED-EMPIRICAL` as paused or historical-scoped, `HEURISTIC` as
deprioritized and revisit-able, and `OPERATIONAL` outside the scientific
closure lane.

The timeline must preserve informative failure. A node may simultaneously
show `mechanism=SUPPORTED`, `promotion=FAILED`, and `branch=PAUSED` or
`ACTIVE`. Do not derive branch disposition from promotion status.

## 7. Track Expectation And Surprise

Compare a preregistered expected relation with a mechanically computed observed
relation under the frozen metric direction and tolerance. Use descriptive
labels such as:

```text
AS-EXPECTED
BETTER-THAN-EXPECTED
WORSE-THAN-EXPECTED
DIRECTION-REVERSAL
NO-PRIOR
INCOMPARABLE
```

These labels prioritize review; they are not scientific verdicts. An
unexpected improvement still requires confound checks. An unexpected failure
may expose a useful boundary rather than invalidate the whole hypothesis.

Preserve the original expectation and timestamp. If a prediction was not
recorded before the result, use `NO-PRIOR`; do not infer intent from later
prose. Keep operational failure separate from an observed scientific relation.

## 8. Plot And Table Contracts

Instantiate `assets/research-history-snapshot-template.tsv` as the normalized
rendering input. Generate it from the ledger and evidence artifacts when
possible. If a project must assemble it manually, mark it as a derived snapshot
with source paths, hashes, evidence cutoff, and known omissions.

Use `scripts/build_research_history_view.py` to create:

```text
index.html          self-contained research trail with inline SVG plots
unit-summary.tsv    one derived row per unit experiment
surprises.tsv       expectation mismatches and incomparable observations
manifest.json       hashes, cutoff, counts, generator, and current-selection source
```

The renderer accepts the original snapshot columns for backward compatibility.
New snapshots should also carry metric role, mechanism verdict, promotion
verdict, branch disposition, closure basis and scope, failed gate, surviving
claim, revisit trigger, next gate, and optional parent/edge identity. Missing
new fields remain unknown; the renderer must not infer them from `FAILED`,
`REJECTED`, a scheduler state, or an earlier event. Unit-level current-state
fields come only from that unit's latest event. Immutable identity remains
subject to the unit consistency checks.

Run it from the project with an explicit frozen snapshot and output directory:

```bash
python <research-skills>/scripts/build_research_history_view.py \
  --input research-history-snapshot.tsv \
  --output-dir reports/research-trail/<cutoff-id> \
  --title "<question or campaign> Research Trail" \
  --evidence-cutoff <ISO-8601-or-artifact-id> \
  --current-unit-id <state-capsule-current-unit-id>
```

Omit `--current-unit-id` only when exactly one latest unit state is `ACTIVE`;
the renderer then labels the selection `INFERRED-SINGLE-ACTIVE`.

The normalized snapshot carries numbers for rendering convenience, but the
linked immutable artifact remains their authority. Never cite the snapshot or
HTML as if it were the original measurement.

Apply the figure reproducibility contract to every exported standalone figure.
Apply the dashboard contract when the trail is embedded in a live monitor. The
history view answers “how did we get here?”; the live monitor answers “what is
running and what blocks the next decision?”

## 9. Refresh, Validate, And Hand Off

Refresh after a unit experiment closes, a major pivot occurs, or roughly 20 new
attempts accumulate. Do not regenerate on every scheduler heartbeat.

Before human review:

1. verify unique attempt IDs and monotonic stable sequence numbers;
2. verify unit membership and compatible metric contracts;
3. reconcile eligible, failed, invalid, reused, and external counts;
4. spot-check plotted values against immutable artifacts;
5. verify comparator, gate, units, direction, and tolerance;
6. inspect the rendered route, tables, plot labels, missing-value behavior, and
   artifact links;
7. record the evidence cutoff and output hashes.
8. verify chronological top-to-bottom ordering and that current-state summary
   does not silently rewrite the historical route;
9. verify `HARD-CLOSED` nodes have a formal/exact closure basis, scope, and
   argument locator, and that heuristic avoidance remains revisit-able.

At handoff, report the active question, number of attempts and unit
experiments, best compatible result, most important surprise, current branch
decision, and exact next unit experiment. Preserve old trail snapshots at major
pivots; never use mutable `latest.html` as evidence.
