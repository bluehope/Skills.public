---
name: atom-trajectory-visualize
description: "Render multi-frame atomic trajectories and comparison movies with matched identity, provenance and camera; not static-only views or quantitative physics claims."
metadata:
  version: "2026.09.14.1"
---

# Atom Trajectory Visualization

Status: `EXPERIMENTAL`. This skill owns frame and movie rendering. The
trajectory producer and quantitative analysis remain authoritative for physics.

Find the project generator by trajectory ID or exact input path before writing
one. Reuse its manifest for frame selection, render settings and output hashes.
If encoding is unavailable, retain frames and report UNAVAILABLE; do not claim
a delivered movie from a successful structure import or PNG alone.

## Contract

Record the trajectory path/hash, format, frame count, timestep and units when
known, atom ordering, cell/PBC, species map, selected frame indices, camera,
colors, radii, dimensions, FPS, renderer/runtime, and output hash. Keep raw
trajectories immutable and write frames and movies to a declared generated
directory.

## Choose the route

- Use ASE for format inspection, frame selection, and lightweight static
  rendering.
- Use the OVITO Python API for bonds, modifiers, periodic images, and higher
  quality atomistic scenes when its environment passes a smoke test.
- Use ImageIO with its verified FFmpeg executable for MP4 encoding.
- Render compared systems independently with the same camera, frame selection,
  colors, dimensions, and FPS, then compose them. Do not compare videos made
  under unmatched visualization contracts.

For a new/unverified or changed environment, run this skill's thin entrypoint
to the unchanged shared doctor, using only the trajectory profile below. Reuse recorded same-environment readiness; conda
codex is recommended, not required:

```bash
python <atom-trajectory-visualize-root>/scripts/figure_runtime_doctor.py --profile trajectory --smoke
```

OVITO is optional. For a new/changed OVITO stack run the same doctor with
`--profile ovito --smoke`; do not assume an old pip/conda snapshot describes this
machine. For installation or Qt failures resolve $atom-visualize's
`references/runtime-and-renderers.md`. Keep warnings visible, use the recorded
package source and obtain authorization before changing the environment.

## Scientific boundary and QA

- Keep element colors and camera fixed across a comparison.
- Show the cell when periodicity or escape matters; state whether coordinates
  are wrapped or unwrapped.
- Label accelerated-temperature movies as stress tests.
- A short movie may show motion or rearrangement qualitatively. Diffusion,
  melting, stability, and kinetics require separate quantitative metrics,
  adequate duration, and replicate/ensemble evidence.
- Verify first/last frames, atom count and identity, missing frames, playback
  duration, codec decoding, labels, and final dimensions before handoff.

Compose with `$atom-visualize` only for an additional static/spin artifact,
not every trajectory. Research registration uses the project's existing contract
when requested as evidence; a preview alone creates no research registry.
Consequential failures reuse project ops_knowhow records and actual skill/version.
