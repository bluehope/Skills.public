# Research Figure Reproducibility

## Contents

1. Purpose and authority
2. Figure lifecycle
3. Registry contract
4. Plot contract
5. Dashboard integration
6. Audit and handoff

## 1. Purpose And Authority

Use this contract when creating, recovering, comparing, or publishing research
figures. A figure is a rendered view over evidence, not a replacement for the
source artifact, experiment ledger, or design authority.

Keep the editable generator and structured inputs separate from rendered PNG,
SVG, or PDF outputs. Link to canonical evidence rather than copying scientific
definitions into captions or dashboard code.

When a task spans publication styling, atomic rendering, trajectory movies,
source extraction, cropping, or visual QA, compose with the sibling
`scientific-figure-making` umbrella. This document remains the owner of metric,
provenance, reproducibility, and claim-ceiling requirements.

## 2. Figure Lifecycle

Assign one status to every expected figure:

```text
REPRODUCIBLE
PRESERVED-ONLY
MISSING
```

- `REPRODUCIBLE`: retain the exact generator, command pattern, required input
  paths or immutable artifacts, metric contract, and current output hash.
- `PRESERVED-ONLY`: retain an authentic historical output when the exact
  command or complete input fingerprint is unavailable. Display it with that
  limitation; do not imply that it can be regenerated.
- `MISSING`: no verified contract-matched figure exists. State the absence and
  do not substitute a nearby model, split, metric, source, or stale image.

Do not upgrade a figure from `PRESERVED-ONLY` merely because a plausible
plotting script exists. Reproduction requires the condition-equivalent inputs
and command contract.

## 2b. Rendered-Format Contract

A rendered figure has a format contract in addition to its plot contract, and it
must be checked in the environment where the figure will be **consumed**.

- **Dependency closure**: the file references nothing outside itself (no remote
  scripts, styles, fonts or images).
- **Envelope completeness**: the file carries the structure its standalone
  consumer requires. An HTML figure opened from `file://` needs its own
  document declaration, encoding declaration and document containers; a page
  published into a host that supplies those is a fragment and is not
  interchangeable with the standalone file.

These are separate properties and passing one does not imply the other. Report
them separately: "self-contained" is not "standalone". When the same figure is
delivered through two channels, record which envelope each carries and which one
is canonical.

For a text-bearing figure, verify the encoding declaration explicitly — a
missing one degrades silently and only for non-ASCII labels.

## 3. Registry Contract

For each figure record at least:

```text
stable figure id
material/cohort and model or attempt identity
rendered path and expected SHA-256
reproducibility status and limitation reason
rendered-format contract result (dependency closure, envelope completeness)
generator and command pattern
required structured inputs
predicted quantity and units
x/y or panel semantics
split/mask/aggregation
claim ceiling
dashboard or report placement requirement
```

Before a figure registry entry supports a RESULT/EVIDENCE claim, complete the
shared [registration checklist](registration-checklist.md). A preserved-only
display that is not used as evidence does not require this promotion gate.

Keep project-specific thresholds, sign conventions, shell identities, target
names, and paths in the project registry or design owner. Do not promote them
into this shared contract.

## 4. Plot Contract

Lock the metric identity before plotting:

- declare the predicted object and any transform;
- convert units exactly once at a named boundary;
- distinguish geometry coordinates from transform indices or lattice labels;
- separate train, development diagnostic, validation, and true holdout;
- use signed linear parity with equal limits and an identity reference when
  sign and calibration matter;
- label proxy metrics and state what they cannot establish;
- combine models on one numeric axis only when source, target, split, mask,
  units, aggregation, and comparator contracts match.

Prefer a small decision-bearing figure. Put gate lines, target values, units,
and relevant uncertainty or shell annotations on the visual rather than asking
the reader to infer them from prose.

## 5. Dashboard Integration

For dense historical collections, use progressive disclosure such as
`material -> model -> figure`. Keep the first view compact and useful.

- Show a thumbnail, concise contract-aware caption, and original-file link.
- Use native keyboard-accessible controls where possible.
- Load large historical images lazily, but scroll through the rendered page
  during QA so every image is actually requested and decoded.
- Keep incompatible figure families in separate panels.
- Preserve explicit `PRESERVED-ONLY` and `MISSING` labels.
- Do not issue remote compute or data requests from browser JavaScript.

## 6. Audit And Handoff

Use a deterministic project-local audit before handoff. Fail closed on:

```text
missing output or source
hash mismatch
duplicate figure identity
path escaping the project root
missing metric-contract fields
REPRODUCIBLE without generator, command, or inputs
PRESERVED-ONLY without a limitation reason
required dashboard figure without a valid link
```

Treat the audit `project_root` as the namespace root against which registry
paths were authored, not automatically as the Git repository root. Before the
full audit, resolve one known registry path against that root as a sentinel;
abort with an invocation/root error if it does not exist. Do not misclassify a
bad audit root as dozens of missing scientific artifacts.

Test at least one accepted registry and one deliberately corrupted fixture.
The negative fixture must fail with a nonzero exit and a specific finding.

Then serve the report on loopback and verify wide and narrow layouts, console
errors, broken requests, image decoding after lazy loading, and original-file
click targets. Record the audit receipt and output hashes. Mechanical audit
success does not validate scientific truth or promote the evidence rung.
