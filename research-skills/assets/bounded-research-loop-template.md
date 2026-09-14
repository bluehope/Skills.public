# Bounded Research Loop: `<id>`

## Contract

- Central question:
- Research lane: `EXPLORATORY | CONFIRMATORY | PROMOTION`
- Competing explanations:
- Condition fingerprint:
- Comparator:
- Claim ceiling and non-claims:
- Loop/compute budget:
- Human-review boundary:
- Stop rule:

## Metric Roles And Failure Propagation

| Metric | Role | Gate | Failure blocks | Failure does not imply |
|---|---|---|---|---|
|  | `PRIMARY-PROMOTION \| MECHANISM-DIAGNOSTIC \| GUARDRAIL \| SANITY-CONTROL` |  |  |  |

## Verdict Vector

- Mechanism verdict: `SUPPORTED | CONTRADICTED | MIXED | UNRESOLVED`
- Promotion verdict: `PASSED | FAILED | NOT-TESTED`
- Branch disposition: `ACTIVE | PAUSED | DEPRIORITIZED | BLOCKED | HARD-CLOSED`
- Closure basis: `FORMAL-DERIVATION | EXACT-PHYSICAL-LAW | CONTRACT-PROOF | SCOPED-EMPIRICAL | HEURISTIC | OPERATIONAL`
- Closure scope and argument locator:
- Failed gate and surviving claim:
- Revisit trigger:

## Active Frontier

| Branch | Mechanism | Promotion | Disposition | Closure basis | Supporting evidence | Contradicting evidence | One next hard gate |
|---|---|---|---|---|---|---|---|
|  | `UNRESOLVED` | `NOT-TESTED` | `ACTIVE` |  |  |  |  |

## Outcome Branches

| Possible result | Interpretation | Allowed next action | Forbidden inference |
|---|---|---|---|
|  |  |  |  |

## Lane Integrity

- Which fields are frozen in this lane?
- Which change would return the work to `EXPLORATORY`?
- What evidence rung is eligible after a pass?
- What remains forbidden even after a pass?

## Iterations

| Loop | Action | Hypotheses distinguished | Cost | Result | Verdict | Next gate |
|---:|---|---|---:|---|---|---|
| 1 |  |  |  |  |  |  |

## Doubt Checkpoint

- Are we still answering the original question?
- Is the metric directly tied to the target?
- Did source, comparator, condition, or code change?
- Are recent runs conditionally dependent?
- Is a cheaper oracle, counterexample, or formal check available?
- Should a branch be paused, merged, or closed?
- Is the failed gate a branch-specific falsifier or only a promotion/guardrail gate?
- Is any avoidance decision formal, empirical, contractual, operational, or heuristic?
- Did an informative failure release one bounded diagnostic continuation?

## Exit

`PROMOTE | CONTINUE-WITH-ONE-GATE | PAUSE-FOR-HUMAN-REVIEW |
CLOSE-SCOPED-NO-GO | BLOCKED-BY-CONTRACT | REPLAN`
