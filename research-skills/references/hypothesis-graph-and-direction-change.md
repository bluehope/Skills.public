# Hypothesis Graph And Direction Change

## Contents

1. Linear spine and nonlinear graph
2. Question and branch contracts
3. Direction-change protocol
4. Contradictions and branch reopening
5. Handoff and visualization

## 1. Linear Spine And Nonlinear Graph

Research rarely follows its initial plan linearly. Keep rigor through a linear
evidence spine while allowing nonlinear hypothesis search inside each rung:

```text
SOURCE -> CODE -> FIT -> HOLDOUT -> PHYSICS
```

Graph nodes may be:

```text
QUESTION | HYPOTHESIS | EVIDENCE | EXPERIMENT | DECISION | BLOCKER
```

Use explicit edge labels:

```text
SUPPORTS-MECHANISM | CONTRADICTS | FALSIFIES-WITHIN-SCOPE |
BLOCKS-PROMOTION | DEPRIORITIZES | REQUIRES | REOPENS |
SUPERSEDES | OUT-OF-SCOPE
```

The graph is a decision aid, not a second evidence store. Nodes link to
canonical documents and immutable artifacts rather than copying their
contents.

## 2. Question And Branch Contracts

Each active question records:

```text
question / why it matters / current belief
at least two competing explanations
condition fingerprint and claim ceiling
canonical supporting and contradicting evidence
cheapest useful discriminator
cost, risk, and expected decision change
status and revisit trigger
```

Keep four verdict axes independent:

```text
mechanism verdict / promotion verdict / branch disposition / closure basis
```

Do not infer one axis from another. In particular, a failed promotion or
guardrail does not close a mechanism branch, and an operational failure does
not update the mechanism verdict.

Use branch states:

```text
ACTIVE | PAUSED | DEPRIORITIZED | MERGED | BLOCKED | HARD-CLOSED |
HISTORICAL-SCOPED
```

Use `HARD-CLOSED` only with an explicit mathematical derivation or exact
physical-law argument whose assumptions, scope, and evidence locator are
recorded. Use `DEPRIORITIZED` with closure basis `HEURISTIC` when a direction
is avoided by intuition, cost, analogy, or incomplete experience.

Keep at most two active scientific branches plus one contract/debug branch by
default. Opening another branch requires pausing, closing, or merging one, or
recording why the exception is worth the added cognitive and compute cost.

Do not confuse a large tree of possible experiments with progress. A branch is
active only when it has one exact next gate.

## 3. Direction-Change Protocol

A pivot is a normal research operation. Use
`assets/direction-change-template.md` and record:

1. Triggering evidence and its condition fingerprint.
2. The old and new central questions.
3. `KEEP`, `PAUSE`, `CLOSE`, `MERGE`, and `OPEN` decisions.
4. Which historical claims remain valid in their original scope.
5. Which live claims are superseded.
6. The new comparator, claim ceiling, first hard gate, and non-claims.
7. Forbidden carry-over assumptions from the previous branch.
8. Which gate failed, which claim it actually blocks, and which mechanism
   claims survive.
9. Closure basis and scope, or why the old branch remains revisit-able.

Never erase a failed or superseded branch. Preserve it as negative or scoped
evidence and leave a locator in the ledger or ghost cache.

## 4. Contradictions And Branch Reopening

Before treating two statements as a scientific contradiction, compare their
condition fingerprints and classify the disagreement using the local-search
adapter:

```text
STALE-DOC
MODEL-MEMORY-ERROR
CONDITION-CHANGED
SEMANTIC-DRIFT
INVALID-ARTIFACT
TRUE-OPEN-CONTRADICTION
```

If conditions differ, scope both claims. If conditions match and trusted
evidence conflicts, stop downstream promotion and design the smallest
discriminator.

Reopen a paused, blocked, or deprioritized branch when a declared revisit
trigger fires: new evidence, changed contract, improved measurement, an oracle
success, a cheaper discriminator, cross-branch contradiction, formal
correction, or a new downstream requirement. Curiosity alone may open an
exploratory note, but not an expensive active branch. A `HARD-CLOSED` branch
reopens only when an assumption, scope boundary, or proof is invalidated.

## 5. Handoff And Visualization

For a long campaign, maintain:

- one compact active-frontier table;
- a question register created from `assets/question-register-template.md`;
- a direction-change record for each major pivot;
- a graph or decision tree only when it clarifies dependencies;
- links from graph nodes to canonical evidence.

For long human-facing views, put the current decision and active frontier at
the top, then render decision-bearing unit experiments on a top-to-bottom
chronological timeline. Use vertical swimlanes only for a small number of
scientific branches. Keep detailed decision and operational logs below the
scientific route.

When the graph contains many repeated attempts, collapse them into unit
experiment nodes and render the decision-oriented route, metric histories,
scorecard, and surprises using
`research-history-and-loop-visualization.md`. Keep the graph readable; the
attempt-level evidence remains linked rather than copied into each node.

A fresh reader should be able to answer from files:

```text
What is the current question?
Which branches are active, paused, or closed?
Why did the direction change?
What evidence remains valid?
What exact result would change the next decision?
```
