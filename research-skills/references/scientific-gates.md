# Scientific gates (scientific decisions/implementation/compute only)

## Preserve The Scientific Gates

For scientific implementation or costly compute, lock the question, comparator,
source/derived targets, units/sign/reference conventions, transform/masks,
aggregation, representation/cell/input identity, split, thresholds, provenance,
claim ceiling and next hard gate. An unavailable original comparator is not
replaced by a nearby checkpoint: preregister the replacement, hash, differences
and reduced claim ceiling, then evaluate both under the same contract.
Use [evidence-and-validation.md](evidence-and-validation.md) when
defining or auditing that contract; do not impose a scientific experiment
contract on an ordinary document edit or isolated helper test.

The evidence spine is SOURCE -> CODE -> FIT -> HOLDOUT -> PHYSICS; claim levels
are DESIGN -> CODE-PASS -> FIT-PASS -> HOLDOUT-PASS -> PHYSICS-PASS. For an
intervention with no fitted parameters, replace HOLDOUT with COVERAGE (custody
of the production consumer's full domain), with COVERAGE-PASS rather than
HOLDOUT-PASS. Rungs are not skipped because a script ran successfully.

Proceed from source/known-answer checks through smoke, theory/physics audit,
preflight, small fit, holdout/ablation, production and external validation as
applicable. Pair DIFFER/EQUAL; test alignment, grouping, periodic images,
units and stale test code before reinterpreting an apparent invariant failure.
Reuse validated harnesses; verify behavior with a forward test and validate
format contracts in the consuming environment. Dependency closure and envelope
completeness are separate. Do not launch a large run with a failing preflight.
For an errexit Bash/sbatch stage wrapper, use the existing
`scripts/validate_stage_script.py` preflight before submission; retain the
ERR-trap line/command witness and do not bypass a BLOCK.

Recover Before Recompute: locate accepted artifacts by condition fingerprint
before retrying expensive analysis, and preflight a representative packet.
Choose discriminating experiments for uncertainty reduction; preregister what
outcomes would change. Declare EXPLORATORY/CONFIRMATORY/PROMOTION lanes, seek
confounds and falsification before promotion, and preserve negative findings.
Separate mechanism, promotion and branch disposition: HARD-CLOSED requires a
scoped mathematical/exact-physics argument; intuition-led avoidance is
DEPRIORITIZED with a revisit trigger. Read
[research-loop-and-stop-rules.md](research-loop-and-stop-rules.md)
for sustained loops, stopping, lane changes or expensive retries.
