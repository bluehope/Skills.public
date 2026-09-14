# Research Loop And Stop Rules

## Contents

1. Bounded loop contract
2. Research lanes
3. Gate orthogonality and informative failure
4. Experiment selection
5. Scientific posture
6. Doubt checkpoint
7. Exit and escalation
8. Recover before recompute
9. Preflight expensive transformations

## 1. Bounded Loop Contract

Before a multi-step research loop, record:

```text
central question and competing explanations
frozen comparator and condition fingerprint
allowed claim level and explicit non-claims
loop and compute budget
possible outcomes and decision branches
stop rule and human-review boundary
```

Each iteration ends with:

```text
evidence -> verdict -> remaining uncertainty -> one next hard gate
```

Do not let a renderer, monitor, or report job automatically open a new
scientific branch. Separate compute, validate, and decide stages when a wrong
continuation would be costly.

## 2. Research Lanes

Every active packet declares one lane:

| Lane | Purpose | Contract | Allowed conclusion |
|---|---|---|---|
| `EXPLORATORY` | generate, narrow, or distinguish hypotheses | conditions and provenance recorded; adaptation allowed | diagnostic or scoped hypothesis update |
| `CONFIRMATORY` | test a frozen prediction or discriminator | comparator, metric, threshold, split, outcomes, and stop rule preregistered; applicability premise verified | pass/fail for the declared gate |
| `PROMOTION` | raise the claim or make a workflow canonical | previous rung passed; reproducibility, external/independent evidence, documentation, and activation closure | claim only at the newly passed rung |

Changing the metric, comparator, threshold, split, source, or principal
hypothesis during a confirmatory run moves the work back to `EXPLORATORY`.
Post-hoc analysis may explain a failed confirmation, but it does not retroactively
change the confirmatory verdict.

Freezing a threshold does not validate its premise. Before freezing, answer
one question in writing: *what verified fact defines the domain where this
gate applies* (for example, what the production consumer actually enumerates
— file-level evidence beats an assumption). If that premise is later shown
false, record **`PREMISE-VOID`**: the gate dissolves — this is neither a
failed confirmation nor a post-hoc relaxation, and the frozen text is
preserved with the void reason. A void requires the same evidence standard
as the original premise claim; a void without concrete counter-evidence is
invalid.

A promotion packet must state which evidence rung is being entered and which
claims remain forbidden. Operational completion alone is not promotion.

## 2a. Tiered Goal Ladders And Intermediate Deliverables

An all-or-nothing promotion gate can starve a long campaign of every
intermediate deliverable: repeated code-valid work produces only FAIL verdicts
and nothing citable. When that pattern appears (see the doubt checkpoint),
restructure the goal into a tiered ladder instead of loosening the promotion
gate itself.

- Order property targets by physical sensitivity, cheapest-forgiving first.
  For derivative-style targets this is typically
  `integral/value -> first derivative -> second derivative`
  (for example band -> force -> phonon); evaluate the harshest target last.
- Split evaluation into two lanes with different verdict vocabularies:
  a **diagnostic trend lane** (fixed checkpoint, preregistered, majority-based
  loosened thresholds, verdict `TREND-PASS`/`TREND-FAIL`) and the unchanged
  **promotion lane**. A trend verdict never converts into a promotion rung and
  its thresholds must never be reused as promotion thresholds.
- Loosen only *before* running, by preregistration (for example
  "at least 70% of items within a floor-capped tolerance"), and record who
  approved the loosening and why. Loosening after seeing results moves the
  packet back to `EXPLORATORY`.
- Scope, do not repeal, existing stop rules when opening a diagnostic lane:
  record the direction change, keep closed sweeps closed, and keep the failed
  promotion verdict standing.
- Each tier's failure must name which cheaper diagnostic (sensitivity kernel,
  alignment audit, oracle control) allocates the error before any new
  representation or capacity change is proposed.

## 3. Gate Orthogonality And Informative Failure

Treat these as distinct transitions:

```text
FAILS-GATE != FALSIFIES-HYPOTHESIS != CLOSES-BRANCH
```

A gate failure falsifies a hypothesis only when the gate was preregistered as
a branch-specific falsifier, the condition fingerprint matches, the metric
directly measures that mechanism, and the contract states the failure
propagation. A promotion metric or guardrail may block promotion while leaving
the mechanism supported or unresolved.

Declare each metric role before use:

| Role | Purpose | Default effect of failure |
|---|---|---|
| `PRIMARY-PROMOTION` | raise the headline claim | block promotion |
| `MECHANISM-DIAGNOSTIC` | identify direction, sensitivity, or cause | update only that mechanism |
| `GUARDRAIL` | protect worst-case, symmetry, safety, or validity | block promotion; do not automatically refute mechanism |
| `SANITY-CONTROL` | validate null, sign, routing, or implementation | invalidate the affected result when required |

Before closing a branch after a failed gate, record the failed claim, surviving
claim, closure basis, closure scope, contrary evidence, and revisit trigger.
Only an explicit mathematical derivation or exact physical-law argument may
produce `HARD-CLOSED`. Use `BLOCKED` for a contract proof, `PAUSED` for scoped
empirical failure, `DEPRIORITIZED` with closure basis `HEURISTIC` for
intuition-led avoidance, and `PREMISE-VOID` when a preregistered gate's
applicability premise is disproven (see section 2 — the gate dissolves
without a pass/fail verdict).

Treat a failed result as informative when it shows material improvement,
endpoint overshoot, an interior optimum, smooth or non-monotonic response,
sign-control support, aggregate-versus-guardrail disagreement, or a material
frozen-state versus relaxed-state difference. Such evidence may release one
bounded exploratory continuation without changing the failed promotion
verdict. Freeze its factor, maximum points, compute budget, stop rule, and
independent validation target first. A target-fitted optimum is a mechanism
locator, not a promoted parameter; seek an independent physical measurement or
disjoint case that predicts it.

## 4. Experiment Selection

Prefer the experiment with the best qualitative information value:

```text
expected hypothesis discrimination
* downstream decision impact
* reproducibility
------------------------------------------------
compute + implementation + operational risk + branch complexity
```

This is a ranking heuristic, not a mandatory numeric score. Favor:

- known-answer, exact, oracle, or counterfeit controls;
- matched sensitivity and invariance tests;
- interventions that make competing explanations predict different outcomes;
- one new source or condition that breaks an existing degeneracy;
- validation on a genuinely disjoint case before scale-up.

Avoid runs that merely add another point to an already ambiguous sweep.

## 5. Scientific Posture

### When results look good: constructive skepticism

- Ask which confound, leakage path, gauge, alignment, or shared source could
  counterfeit the success.
- Require matched controls and a cheaper falsification test.
- State the tested condition fingerprint and claim ceiling.
- Promote only after the next evidence rung passes.

### When results look bad: disciplined optimism

- Separate source, contract, representation, learning, runtime, evaluator, and
  operational causes.
- Ask whether an exact or oracle route proves the physical target remains
  attainable.
- Turn unexplained residual behavior into competing hypotheses.
- Use the narrowest supported NO-GO class; do not call a scoped failure
  impossible.

## 6. Doubt Checkpoint

Pause the loop when any two are true:

- the same failure class appears three times;
- only hyperparameters change while the causal hypothesis stays fixed;
- recent runs do not distinguish competing explanations;
- all evidence depends on one source, split, structure, or holdout;
- current execution disagrees with the state or living design owner;
- the same analysis is being implemented for a third time;
- compute cost grows without material uncertainty reduction;
- branch count exceeds the active-frontier budget;
- resuming requires reconstructing history from chat.

At 100 condition-relevant attempts under one active question, pause even when
the ordinary two-signal rule has not fired. Group the attempts into unit
experiments, render the route, compatible metric histories, unit scorecard, and
surprise table, then require a recorded human continuation decision. Follow
`research-history-and-loop-visualization.md`; do not reset the count by renaming
the campaign.

At the checkpoint ask:

1. Is the central question still the right one?
2. Does the metric measure the desired physical or scientific outcome?
3. Did the source, comparator, condition, or code path change?
4. Is the current failure operational, representational, or scientific?
5. Is there a cheaper oracle, counterexample, or formal argument?
6. Should a branch be paused, merged, or closed before continuing?

## 7. Exit And Escalation

End a loop with one of:

```text
PROMOTE
CONTINUE-WITH-ONE-GATE
PAUSE-FOR-HUMAN-REVIEW
CLOSE-SCOPED-NO-GO
BLOCKED-BY-CONTRACT
REPLAN
```

A `FORMAL` NO-GO requires a mathematical, symmetry, rank, conservation, or
information argument. A repeated empirical failure remains
`SCOPED-EMPIRICAL` unless such an argument exists.

An intuition-led decision can reduce priority or compute allocation but cannot
create a scientific prohibition. Store disposition `DEPRIORITIZED` with closure
basis `HEURISTIC`, retain its revisit trigger, and reconsider it when new evidence, a cheaper
discriminator, a changed metric or contract, an oracle success, or a
cross-branch contradiction appears.

Use `assets/bounded-research-loop-template.md` for long or autonomous
campaigns. Do not silently reset the loop counter by renaming the experiment.

## 8. Recover Before Recompute

Before retrying or resubmitting an expensive analysis, recover the current
artifact state rather than inferring it from a failed parent job, stale
dashboard, or missing chat context. Search the bounded canonical artifact root
for completed sibling/child attempts and read their result audit first.

- Treat an earlier artifact as reusable only after comparing its condition
  fingerprint: source/config/checkpoint hashes, input data, comparator,
  split/q-set, numerical flags, and acceptance gate.
- A scheduler failure is not evidence that all logically later or independent
  artifacts failed. Verify the actual descendants and their result audits.
- If an accepted, condition-equivalent result already answers the same
  question, stop the duplicate computation. Preserve its partial logs as an
  immutable operational attempt; cite the accepted artifact as evidence.
- Reopen a computation only for a named fingerprint mismatch, a new hard gate,
  or an invalidated accepted artifact. Record that reason before submission.

## 9. Preflight Expensive Transformations

For an analysis dominated by repeated transforms, large wavefunction objects,
or independent packets, measure and bound the work before launching the full
set.

- Run one representative packet first and record elapsed time, peak memory,
  object shape/cardinality, and actual resource utilization. Estimate the full
  campaign from that measurement.
- Write each independent unit to a hash-bound checkpoint (for example by
  method, physical arm, displacement, or k-point) and merge deterministically.
  A final-only output is not an acceptable long-run design when partial work is
  independently reusable.
- Requested CPUs/GPUs are not performance evidence. Confirm thread affinity,
  actual utilization, and the algorithm's parallelism before increasing an
  allocation. If the workload is serial, allocation-only retries do not form a
  performance experiment.
- When the estimate exceeds the information value of the next decision, pause
  and redesign the packetization, checkpointing, or discriminator rather than
  extending walltime blindly.

When soliciting a second opinion (human or an independent LLM lane), frame it
adversarially: ask for refutation of named claims with confidence levels and
concrete corrections, not open-ended review. Use the llm-handover protocol
when the reviewer is an independent LLM lane.
