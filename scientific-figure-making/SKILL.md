---
name: scientific-figure-making
description: "Route mixed scientific figure workflows or unresolved figure-production choices. A known static, trajectory or plot-style task uses its specialist directly."
metadata:
  version: "2026.09.14.1"
---

# Scientific figure coordination

EXPERIMENTAL umbrella: own selection and handoff, not generators or evidence.
Use $atom-visualize for structures, $atom-trajectory-visualize for movies and
$figures4papers-style for Matplotlib style. Do not activate this umbrella merely
to call its runtime doctor, or make a known leaf return here before working.

## Find the existing owner

The stable capability IDs and owners are in
[capability-map.json](references/capability-map.json). Query a known ID without
preloading all prose; for ambiguous selection or multi-step production read
[capability-map.md](references/capability-map.md). Example from this skill root:

```bash
python -c 'import json; d=json.load(open("references/capability-map.json")); print(next(x for x in d["capabilities"] if x["id"]=="atomic-structure"))'
```

Search the project for a validated generator/input map first:
SEARCH → VERIFY → REUSE → PATCH → EXTEND → NEW. Select only the needed owners.
Extraction, crop, redraw, rendering, animation and QA remain distinct operations;
do not rebuild specialist code or create a parallel registry.

## Shared contract

Lock purpose/audience/medium, data/units/transforms/uncertainty, source rights,
structure/frame identity and output formats before styling. Preserve generator,
inputs, command, runtime, hashes and output settings in the existing manifest.
Research registration applies only for authorized durable evidence work, not
every plot preview. Publication styling cannot change scientific values or
exclusions; rendering cannot promote an unconverged state or qualitative movie.

For an unverified/changed stack read [runtime-baseline.md](references/runtime-baseline.md)
and run only the selected profile:

```bash
python <skill-root>/scripts/figure_runtime_doctor.py --profile publication --smoke
```

Profiles: core, publication, trajectory, plotly, ovito; all is for full environment
audits, not a routine figure. Reuse same-environment readiness; rerun after relevant
changes/failure. Conda codex is recommended, not mandatory. Missing optional
dependencies are UNAVAILABLE for that renderer, not a whole-skill failure.
Do not install packages without authorization; isolate ABI-sensitive viewers.

Read selected references fully. Inspect output at intended size/medium:
fixture success is not project layout, source-rights or scientific acceptance.
External style code needs explicit pinned provenance/license/scope.
For release apply the project's actual gates; this umbrella cannot grant release.
After changing the map run [routing_smoke_test.py](tests/routing_smoke_test.py).
Edit the verified canonical library, not an installed projection; use
$skill-librarian only for library management/sync. Keep dependencies/links outside sync.
