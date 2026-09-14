---
name: atom-visualize
description: "Render static/interactive atomic structures, relaxation comparisons and provenance-backed spins. Geometry-only views need no DFT or figure-umbrella workflow."
metadata:
  version: "2026.09.14.1"
---

# Atomic structure visualization

Find the existing project generator by structure ID/path before writing one.
Reuse its input mapping, settings and manifest; keep one generator per artifact,
mark successors explicitly. A smoke fixture is not a general-purpose renderer.

## Geometry, spin and artifact contract

Preserve input path/hash, structure ID/stage, atom/species order, cell/PBC,
wrapping, moment source, renderer/version, camera/projection, colors/radii,
dimensions, output path/hash and reproducible command. Display copies are not
scientific structure authority. Show initial/final side-by-side when discussing
relaxation, gaps, buckling or registry; preserve project layer/termination names.

- Keep coordinates and cell together; do not silently strip vacuum or alter it.
  For slab wrapping roll at the largest vacuum gap using an unwrapped display
  copy; do not accidentally fold positions during translation.
- Relaxed moments come from the correct final converged OUTCAR with matching
  atom order. INCAR MAGMOM is only a labeled initial/design view, never relaxed.
  Supplied arrays need their own declared provenance.
- Collinear convention: +z red/up, -z blue/down, length proportional to
  abs(moment); defaults 0.30 Å/μB and threshold 0.15 μB. Record convention,
  threshold and arrow scale in metadata/caption; no inferred magnetic state.
- Geometry-only rendering does not require new DFT/SCF checks. When labeling a
  view as relaxed/converged, verify existing state evidence or visibly mark
  unavailable/unconverged provenance; do not launch a calculation to render it.

## Select a renderer, not a stack of skills

| Need | Route / required detail |
|---|---|
| Static publication slab side view without explicit override | [clean-slab.md](references/clean-slab.md): scoped default, OVITO/Tachyon |
| Other OVITO headless or Matplotlib static view | [static-rendering.md](references/static-rendering.md) |
| VESTA spin file, HTML/3Dmol or Crystal Toolkit/Dash | [interactive-viewers.md](references/interactive-viewers.md) |
| Optional renderer selection, import/Qt/export failure or package change | [runtime-and-renderers.md](references/runtime-and-renderers.md) |

Read selected instructions fully, not every renderer. VESTA writes .vesta,
Matplotlib PNG/SVG, 3Dmol static HTML, Crystal Toolkit/Dash a local app,
Plotly Mesh3d/Kaleido PNG/HTML, and OVITO/Tachyon PNG. Use the simplest route
meeting the request; a Dash callback app is not fully offline static HTML.
The clean-slab default does not override an explicit renderer, requested spins,
bulk/molecular/interactive work or the actual surface normal.

For a known static task use this skill directly. Compose
$scientific-figure-making only for unresolved/mixed figure production or release
coordination; $atom-trajectory-visualize only for multi-frame/movie delivery.

## Existing preflight and runtime

Use this skill's thin entrypoint to the unchanged shared doctor:
`python <atom-visualize-root>/scripts/figure_runtime_doctor.py --profile ovito --smoke`
(use `--profile core` for ASE/Matplotlib). Ownership does not require loading the
umbrella. For a new/unverified or changed environment, use the selected profile;
reuse recorded readiness for the same environment on routine renders.
Recommend conda codex / Python 3.12–3.14 when compatible, not an exclusive runtime.

The local `tests/ovito_structure_smoke_test.py` checks ASE↔OVITO particle count,
species/order, positions/cell and nonblank PNG. Import alone is insufficient.
Use string output paths for the verified Qt binding. No automatic installation
or ad hoc shared-stack repair; optional failure affects only that renderer.

## Delivery audit

Verify represented atoms, moment ordering/source, scientifically correct labels,
initial/final paths, marked failed/unconverged sources, hashes/settings and
opening in the intended viewer. Mechanics cannot establish scientific validity.
Keep one existing artifact manifest; register research evidence only when the
task calls for it. Consequential errors use project ops_knowhow/incidents.tsv
and its existing helper with actual skill/version; do not create another logger.
