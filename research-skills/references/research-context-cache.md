# Research Context Cache

## Contents

1. Purpose and authority
2. Working-set states
3. Cache keys and admission
4. Invalidation and retrieval
5. Health and token efficiency

## 1. Purpose And Authority

The cache reduces repeated retrieval and stale-memory errors. It stores scoped
claims and canonical locators, not copied evidence tables, raw numerical
artifacts, or a second decision history.
It is optional for projects with repeated costly retrieval, not a required
state machine for every session. Routine known-ID access needs no cache record.

Authority remains:

```text
immutable artifact + executed code > living owner > frozen report > cache
```

A cache hit is a routing success, not independent evidence. Reopen the
canonical witness before a consequential claim or mutation.

## 2. Working-Set States

```text
PINNED
RECENT-ONCE
RECURRENT
GHOST
COLD
```

- `PINNED`: compact current state and locators to the living design, active
  question, next gate and latest accepted artifact, not all their full texts.
- `RECENT-ONCE`: newly retrieved candidate not yet proven reusable.
- `RECURRENT`: repeatedly useful locator or high-cost scoped claim.
- `GHOST`: path, claim key, and status only; rehydrate on a declared trigger.
- `COLD`: searchable corpus and archives loaded only on demand.

This borrows from 2Q/LRU cache design without pretending research context is a
pure recency problem. Authority, condition validity, and error cost outrank
recency.

Use soft capacity rather than universal fixed counts:

- `PINNED` should fit in one short session-start read and contain only the
  active direction, question, gate, blocker, and latest accepted evidence.
- `RECURRENT` should contain only condition-valid items reused by the current
  research frontier.
- Demote inactive, superseded, or rarely reused entries to `GHOST`; move
  unneeded history to the cold searchable corpus.
- Review capacity at a major pivot, handoff, promotion, or whenever session
  startup becomes a historical reading exercise.

## 3. Cache Keys And Admission

A condition-aware cache key includes the fields relevant to the claim, such as:

```text
topic
material, structure, cohort, or population
source and producer profile
target and preprocessing policy
code commit, executable, and runtime
split, checkpoint, or comparator
metric identity and threshold
evidence cutoff
```

Admit an entry when at least one is true:

- it was retrieved in more than one distinct task;
- a stale or wrong retrieval would be expensive;
- it directly controls the next hard gate;
- the user repeatedly asks for it;
- it is essential for file-only handoff.

Do not admit transient scheduler status, one-off logs, duplicated tables, or
unverified chat summaries.

## 4. Invalidation And Retrieval

Demote, invalidate, or reverify after:

- source, producer, profile, geometry, cohort, split, or target changes;
- code, executable, environment, or metric changes;
- a direction pivot or superseding canonical owner;
- contradictory evidence or a correction;
- evidence cutoff expiry for time-sensitive state.

A stale hit triggers a contradiction audit before the cached claim can be used
again. Record the stale key, cause, affected decision, corrected authority,
and whether the entry was refreshed, demoted, invalidated, or removed. Do not
silently overwrite it.

Retrieval order:

1. Read `PINNED`.
2. Use a condition-matched `RECURRENT` entry when available.
3. Rehydrate `GHOST` only when its trigger fires.
4. Run bounded exact local search.
5. Escalate to broader or semantic search only if needed.
6. Verify the canonical witness.
7. Update cache state and record consequential stale or zero-result events.

## 5. Health And Token Efficiency

Track softly:

```text
context hit
indexed/local-search hit
search miss
stale hit
repeated wide search
entry promoted, demoted, or invalidated
```

Do not impose a strict hit-ratio target. Optimize in this order:

1. zero stale hits;
2. bounded search scope;
3. fewer repeated wide searches;
4. useful recurrent hit rate.

Practical rules:

- Start with the needed state capsule and locators; reopen only the relevant
  design or artifact rather than preload all three.
- Stop at the first sufficient search tier.
- Promote a repeated locator instead of rewriting the same summary.
- Convert a repeated deterministic analysis into code before its third manual
  implementation.
- Generate prose and tables one-way from machine-readable evidence.
- Keep current state in the state capsule and history in ledgers or archives.

Use `assets/research-context-cache-template.md` for a project cache. Keep the
top of the file small enough to serve as the session working set.
