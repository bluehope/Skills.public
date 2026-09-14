---
name: figures4papers-style
description: "Style and export publication Matplotlib plots using the pinned figures4papers reference, preserving data and license boundaries."
metadata:
  version: "2026.09.14.1"
---

# Figures4Papers Style

Status: `EXPERIMENTAL`. This adapter owns publication-style choices and export
checks. It does not own plotted values, scientific claims, or source rights.

Use this skill's `scripts/figure_runtime_doctor.py` thin entrypoint to the unchanged
shared implementation; no umbrella read is needed for helper access.
Its fixture tests export mechanics, not the project's
plot. Reuse the project generator and manifest rather than introducing a second
style runner or registry. Report a missing optional profile as UNAVAILABLE.

Read [upstream-source.md](references/upstream-source.md) before consulting the
external repository. Upstream is licensed CC BY-NC 4.0 (since 2026-09-06):
attribution is required and commercial use is excluded. Academic and teaching
figures are within scope; still prefer a local reimplementation of the style
contract over vendoring upstream code, and attribute the repository whenever
its code or prose is copied or adapted. Do not use it for commercial deliverables.

## Workflow

1. Search the project for an existing validated plotting module and generator.
   Prefer `SEARCH -> VERIFY -> REUSE -> PATCH -> EXTEND -> NEW`.
2. Lock data arrays, labels, units, transforms, uncertainty, exclusions,
   comparator identity, and intended output size before applying style.
3. Consult only the closest upstream demo or reference needed for layout ideas.
   Reimplement no upstream helper merely because its API is documented.
4. Use a project-owned plotting module for reusable palette, style, and export
   helpers; add a known-good render test before sharing it across projects.
5. For publication delivery generate a vector output (PDF or SVG) and review raster;
   a styling-only preview keeps the requested format. Check
   font fallback, clipping, legend collisions, grayscale/color accessibility,
   line/hatch distinction, and axis-range disclosure.
6. Record generator, input hashes, environment, command, output dimensions,
   and output hashes. Use the project's research registration only when durable
   evidence registration is requested, not for a styling-only preview.

For a new/unverified or changed environment run only the publication preflight;
reuse recorded same-environment readiness. Conda codex is recommended:

```bash
python <figures4papers-style-root>/scripts/figure_runtime_doctor.py --profile publication --smoke
```

Do not install the upstream skill under its original name: it would collide
with the local `$scientific-figure-making` umbrella. Promotion requires a clear
license, a pinned revision, a reusable local implementation with tests, and at
least two real publication figures without data or layout regression.
