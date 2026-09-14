# Figure extraction and generation skill collection

This directory is a collection, not a single skill. Invoke the narrowest child skill that owns the requested action.
Use the sibling `scientific-figure-making` umbrella when the request also
requires publication styling, atomic/trajectory rendering, or research figure
registration; this collection continues to own extraction, crop, generation,
and asset-QA operations listed below.

| Need | Skill |
|---|---|
| compare candidates and record adoption | `select-figure-evidence` |
| render a PDF source page or extract embedded raster assets | `extract-source-figures` |
| make an unmodified rectangular panel crop | `crop-figure-panels` |
| prove crop identity and inspect a review sheet | `qa-figure-assets` |
| create a code-native plot, diagram, redraw, or teaching illustration | `generate-lecture-figures` |

Use them as a transaction when needed:

```text
state claim
→ select source/candidate
→ extract source page or embedded asset
→ crop only when a panel boundary is needed
→ QA exact identity and rendered readability
→ generate/redraw only when transformation or a new visual is required
→ promote through the target project's canonical registry/build
```

## Artifact roles

Keep these roles distinct:

```text
originals      immutable acquired files
source_pages   rendered evidence of source context
extracted      unmodified embedded assets
crops          unmodified rectangular regions
generated      code-native plots, diagrams, redraws, illustrations
review         contact sheets and decision packets
release        assets promoted through the target project's build
```

The collection does not own a project's figure registry, release status, or final folder layout. Project-local skills remain the operational authority for those items.

Use `computational-lecture-workflow` before code-reproduced figures that depend
on a native scientific stack or trained checkpoint. Use
`rehearse-lecture-delivery` for actual projector/back-of-room proof; a source-
resolution or contact-sheet inspection is not a classroom rehearsal.

## Validation calibration

Every bundled validator must pass a known-good fixture and reject a known-bad
fixture for the invariant it claims to enforce. The collection smoke test
exercises selection schema, overwrite protection, crop bounds, exact-rectangle
identity, and generated-figure trace failures. Run it after changing any child
script:

```bash
python -B tests/smoke_test.py
```

## Codex discovery

Each child is a valid Codex skill and includes `agents/openai.yaml`. Place or link each child directory in a configured Codex skills root when automatic discovery is required. Codex-specific tool guidance is under `## Codex execution` in every `SKILL.md`.

## Claude discovery

Claude Code discovers filesystem skills from `~/.claude/skills/` or a project's `.claude/skills/`. Place or link each child directory there; the shared `SKILL.md`, references, assets, and scripts are portable. `agents/openai.yaml` is Codex metadata and may be ignored. Claude-specific guidance is under `## Claude execution`.

Claude API/claude.ai uploads must package one child skill at a time. Their sandbox may have no network or runtime package installation, so use bundled inputs and verify required Python packages before promising execution.

## Runtime baseline

- Python 3.10+
- Pillow and NumPy for crop and image QA
- Poppler commands `pdftocairo` and `pdfimages` for PDF extraction

Run the portable collection smoke test after installation:

```bash
python -B tests/smoke_test.py
```

The test creates its fixtures in the operating system's temporary directory and removes them automatically.
