# Evidence And Validation

## Contents

1. Epistemic discipline
2. Contract and claim levels
3. Four-axis verification
4. Preflight and evaluation hygiene
5. Failure diagnosis
6. Result-use states, closure basis, and NO-GO classes

## 1. Epistemic Discipline

- Read the file before editing it, the implementation before describing it,
  and the log/artifact before judging a run.
- Pin sign rules, units, schemas, irreps, cutoffs, and constants to the actual
  definition. Do not reconstruct them from memory.
- Treat code reading as a behavior hypothesis. Confirm input-to-output routing
  with a minimal forward or intervention test.
- Search for existing helpers and harnesses before writing new machinery.
- Record unverified assumptions as assumptions; store `unknown` with a reason.
- Unexpected results are investigation targets. Isolate them using source
  comparison, code history, parameter sweeps, and representative failures.

Authority order for behavior and numbers:

```text
immutable artifact + executed code > current code inspection > living prose
> frozen report > chat memory
```

## 2. Contract And Claim Levels

Freeze target and representation contracts before training:

```text
target: source field, physical meaning, unit, sign/reference, transform id
label: measured/converged/teacher-forced/generated provenance
mask: included sites/pairs/examples
aggregation: per-site/per-atom/per-cell/micro/macro/group
representation: cell, cutoff, periodic images, neighbor cap, grid, canonical map
split: train/validation/test and leakage controls
```

Do not conflate auxiliary scores, model-internal potentials, DFT energies,
response-derived quantities, or evaluator outputs. Give each an allowed claim.

Claim ladder:

| Level | Evidence |
|---|---|
| `DESIGN` | equation, architecture, or hypothesis proposed |
| `CODE-PASS` | smoke/unit/integration/contract test passed |
| `FIT-PASS` | fitted cases reproduced; not generalization |
| `HOLDOUT-PASS` | disjoint case/cell/material/seed predicted |
| `COVERAGE-PASS` | unfitted intervention verified correct over the declared consumer-enumerated domain (custody bounds, not improvement thresholds); replaces `HOLDOUT-PASS` when the intervention has no fitted parameters |
| `PHYSICS-PASS` | independent simulator, DFT, experiment, or physical cross-check |

Every headline metric must include its protocol and claim level.

A reference row or cell compared with itself is rendered as `—`, never `0`,
and is not evidence that the reference is valid. Reference validity requires a
separate receipt. Apply [registration-checklist.md](registration-checklist.md)
before registering RESULT/EVIDENCE.

## 2a. Coverage And Applicability

- Declare the **consumption domain** in the contract: the exact index set,
  loop, or enumeration the production consumer executes, with file-level
  evidence (a source line beats an assumption). Distinguish three levels:
  *defined* (mathematically well-posed) ≠ *supported* (the pipeline is
  validated there) ≠ *required* (the consumer enumerates it).
- Known-answer coverage **is** claim coverage: a defect outside every KA is
  invisible for exactly as long as no consumer steps there. When a domain
  axis is likely to expand (more k-points, cells, species), plant one
  **coverage sentinel** KA outside the current-use subset on that axis.
- Tests of unfitted interventions over a wider domain are coverage-custody
  gates (correctness bounds), not holdouts (improvement thresholds); see
  the `COVERAGE` rung.

## 3. Four-Axis Verification

### Theory

- known-answer or analytic limit;
- exact round-trip for paired transforms;
- identity/sum-rule checks;
- dimensional and scale sanity;
- behavior at boundaries and special cases.

### Physics

- symmetry invariance/equivariance: time reversal, O(3), translation,
  permutation, gauge, and pair reciprocity as applicable;
- conservation and sum rules;
- primitive/supercell or equivalent-input size consistency;
- `DIFFER`: intended variable changes output;
- `EQUAL`: symmetry-equivalent or matched control remains equal;
- before designing confound experiments, list what is exactly invariant
  under the intervention (gauge, basis, ordering); an analytic invariance
  plus one numerical `EQUAL` control eliminates a confound family at
  near-zero cost.

### Mechanics

- load, forward, backward, save/reload;
- finite loss and nonzero expected gradients;
- deterministic behavior within declared tolerance;
- feature-off/default-off no-regression;
- active-path audit: feature norm, parameter norm, gradient norm, output norm.

### Generalization

- disjoint held-out cases;
- ablation against controlled baselines;
- transfer/OOD protocol;
- repeated seeds or uncertainty larger than numerical noise.

## 4. Preflight And Evaluation Hygiene

Require a machine-readable preflight artifact before expensive work:

```text
data: schema, coverage, units/sign/transforms, split
representation: graph/grid completeness and canonical mapping
physics: required symmetry, conservation, size consistency
mechanics: load/forward/backward/save and finite gradients
```

For periodic graphs, increase image range, neighbor cap, and cutoff until the
quantity of interest saturates. Do not universalize one magic value.

Every metric identity includes:

```text
(target property, observed property, experiment/evaluator contract,
 stage, representation, reference, mask, aggregation, unit, split, tolerance)
```

Treat the target property as the scientific concept and the observed property
as the namespaced value produced by one exact measurement protocol. A common
target name does not establish evaluator or metric equivalence.

Track groupwise absolute/relative loss and, when possible, gradient
contribution. A falling total loss can hide collapse of a small target.

Near-zero targets make sign accuracy misleading. Report magnitude-aware error,
tails, calibration, and uncertainty. In-sample fit is not validation.

## 5. Failure Diagnosis

When a result violates expectations:

1. Reproduce on one minimal failing sample.
2. Verify the source field and its derivation independently.
3. Audit alignment, periodic images, edge ordering, grouping, reverse maps,
   masks, units, and stale checkpoints.
4. Inspect path activity: input intervention, feature/gradient/output norms.
5. Separate data noise, representation loss, optimization failure, evaluator
   mismatch, and actual model limitation.
6. Apply the smallest guarded fix and rerun synthetic plus selected-regression
   tests before repeating a full run.

Never erase the failure. Preserve the raw artifact and add a correction or
superseding decision.

## 6. Result-Use States, Closure Basis, And NO-GO Classes

Keep operational completion separate from scientific usability. After
contract validation, classify a result as:

| State | Meaning |
|---|---|
| `VALID` | contract and declared gate pass; usable up to its claim ceiling |
| `DIAGNOSTIC-ONLY` | informative for debugging but not acceptance |
| `INVALID-FOR-ACCEPTANCE` | provenance, contract, leakage, or evaluator failure |
| `BLOCKED` | required witness or prerequisite is missing |
| `HISTORICAL-SCOPED` | valid only in a superseded or narrower recorded condition |

Use the narrowest supported NO-GO class:

| Class | Meaning |
|---|---|
| `FORMAL` | ruled out by a mathematical, symmetry, rank, conservation, or information argument |
| `CONTRACT` | current data/interface/evaluation contract cannot support the claim |
| `REPRESENTATION-CAPACITY` | tested representation cannot express the required mapping in the declared scope |
| `LEARNING` | representability remains plausible but fitting/optimization/generalization failed |
| `SCOPED-EMPIRICAL` | repeated failure in a declared finite set of conditions |
| `OPERATIONAL` | scheduler, environment, runtime, storage, or orchestration failure |

A `FORMAL` NO-GO needs an explicit argument, not many failed runs. An oracle or
exact route that succeeds usually rules out a broad physical impossibility but
does not by itself prove the learned representation is adequate. State the
condition fingerprint, retained alternatives, and revisit trigger with every
NO-GO.

Do not compress evidence strength, scientific meaning, and branch disposition
into one `REJECTED` label. Record them independently:

```text
mechanism verdict: SUPPORTED | CONTRADICTED | MIXED | UNRESOLVED
promotion verdict: PASSED | FAILED | NOT-TESTED
branch disposition: ACTIVE | PAUSED | DEPRIORITIZED | BLOCKED | HARD-CLOSED
closure basis: FORMAL-DERIVATION | EXACT-PHYSICAL-LAW | CONTRACT-PROOF |
               SCOPED-EMPIRICAL | HEURISTIC | OPERATIONAL
```

`HARD-CLOSED` is valid only with `FORMAL-DERIVATION` or
`EXACT-PHYSICAL-LAW`. Record the exact proposition, assumptions, domain,
derivation or evidence locator, independent check, and the condition that
would invalidate the closure. A contract proof blocks the current contract;
it does not establish a global physical impossibility.

Repeated finite-condition failure is `SCOPED-EMPIRICAL`. A judgment such as
"avoid this direction" based on intuition, cost, analogy, or incomplete
experience is `DEPRIORITIZED` with closure basis `HEURISTIC`; it must retain
the strongest contrary evidence, cheapest useful discriminator, and a revisit
trigger. Operational failure does not update the scientific mechanism verdict.
