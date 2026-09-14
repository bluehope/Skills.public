# Scientific Figure Capability Map

Use the narrowest owner. The machine-readable companion
[`capability-map.json`](capability-map.json) is validated by the umbrella smoke
test.

| Need | Owning skill | Maturity | Runtime profile | Boundary |
|---|---|---|---|---|
| Publication Matplotlib style and vector export | `figures4papers-style` | `EXPERIMENTAL` | `publication` | follow the adapter's pinned-source license contract; do not vendor implicitly |
| Atomic structures, slabs, spins, and static viewers | `atom-visualize` | `ACTIVE` | `core` / `ovito` | geometry and magnetic provenance remain mandatory |
| MD/trajectory frames and movies | `atom-trajectory-visualize` | `EXPERIMENTAL` | `trajectory` | movies are qualitative unless a separate quantitative analysis supports the claim |
| Select visual evidence and rights state | `select-figure-evidence` | `ACTIVE` | `core` | selection is not release |
| Render PDF pages or extract embedded assets | `extract-source-figures` | `ACTIVE` | `core` | extraction does not prove completeness |
| Make an unmodified rectangular panel crop | `crop-figure-panels` | `ACTIVE` | `core` | any annotation or relabeling becomes a redraw |
| Prove crop identity and build review sheets | `qa-figure-assets` | `ACTIVE` | `core` | pixel identity is not scientific correctness |
| Generate lecture plots, diagrams, and redraws | `generate-lecture-figures` | `ACTIVE` | `publication` | teaching artifact classes retain distinct claim ceilings |
| Research figure evidence and reproducibility | `research-skills` | `ACTIVE` | `core` | owns metric contract, provenance, registry, and claim ceiling |

Do not route interactive dashboards, GIS, dominant 3D scientific rendering, or
bitmap illustration to a Matplotlib style adapter merely because the output is
a figure. Use the corresponding specialist or image-generation workflow.

## Executable entry points

Resolve each named skill root from the active installation; do not assume
adjacent directories. Commands below are preflights, not project generators.

| Input / purpose | Existing command under owning skill root | Output / check | Unavailable route |
|---|---|---|---|
| Numeric arrays, publication plot | scientific-figure-making: `python scripts/figure_runtime_doctor.py --profile publication --smoke` | JSON readiness; temporary PNG/PDF export | retain data and generator; report unavailable profile, select an approved working renderer |
| ASE-readable static structure | atom-visualize: `python tests/ovito_structure_smoke_test.py` | identity round-trip and nonblank PNG fixture | use the static renderer table; do not label a fallback as OVITO |
| Selected trajectory frames | scientific-figure-making: `python scripts/figure_runtime_doctor.py --profile trajectory --smoke` | two-frame codec export/decode; frame count/dimensions | keep frames; report movie encoding unavailable |

Use the project's existing generator for actual inputs. Attach its command,
input hashes, renderer/version, camera/style/frame settings, output paths and
hashes to the existing artifact manifest; do not create a parallel registry.
A missing optional package blocks only its selected profile, not unrelated
capabilities. A successful fixture proves mechanics, not scientific acceptance.
