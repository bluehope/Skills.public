# Static structure rendering

Read for OVITO or Matplotlib rendering. An already verified same-environment
project generator need not repeat unrelated runtime fixtures for every image.
Recheck after an environment/renderer change or export failure.

## OVITO Python workflow

Use the verified OVITO profile in conda `codex` for headless atomistic scenes:

```bash
python <atom-visualize>/tests/ovito_structure_smoke_test.py
python <atom-visualize>/scripts/figure_runtime_doctor.py --profile ovito --smoke
```

Convert through `ovito.io.ase.ase_to_ovito` and verify particle count, species,
positions, and cell by round-tripping with `ovito_to_ase`. Prefer the Tachyon
renderer for deterministic headless PNG checks. Record camera, colors, radii,
PBC display, dimensions, OVITO version, and output hash with the artifact.

Do not infer installation health from a successful import alone. The smoke test
must also preserve structure identity and produce a nonblank PNG. Pass output
paths to OVITO as strings, not `pathlib.Path`, for the verified Qt binding.
Installation commands, the pip-in-conda warning, and recovery rules live only
in [runtime and renderer compatibility](runtime-and-renderers.md).

## matplotlib workflow

- Use element-specific colors and radii, red/blue spin arrows, and proportional arrow lengths.
- Center a slab using the maximum vacuum gap before projecting b–z or x–z.
- Label panels `[relaxed]` or `[init]`, and include a legend for every displayed
  element and spin direction.
- Save deterministic PNG/SVG with the structure ID, stage, and moment source in the filename.
