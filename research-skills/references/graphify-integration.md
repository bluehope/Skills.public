# Experimental Graphify Integration

## Status

`EXPERIMENTAL`, bounded pilot only. The active canonical owners remain the
research skill, project state capsule, decision/design owner, experiment
ledger, and immutable evidence artifacts. Graphify output is a locator and
navigation view, never evidence or a replacement for `local-search`.

## Environment

Graphify is installed in the conda environment named `codex` and must be
invoked there:

```bash
python -m graphify --version
```

The current verified package is `graphifyy==0.9.53` with Python 3.14.7. Do not
install a second runtime copy, run `graphify codex install` automatically, or
modify user/global Codex configuration as part of this pilot.

## Scope and execution

- Prefer a curated project or the `research_skills/` source tree; never scan
  the whole Dropbox workspace by default.
- Keep generated `graphify-out/`, caches, and staging directories outside
  Dropbox when possible. A staging root under `/tmp` is the default pilot
  location.
- Use the local AST path for supported code. Markdown, PDFs, and images may
  require semantic extraction; do not send restricted material to a backend
  without explicit authorization.
- TSV templates and other unsupported files are not automatically represented;
  preserve their canonical meaning in the source file and inspect them
  directly.
- Use `query`, `path`, `explain`, and graph reports to find candidate context,
  then reopen the canonical source span with `local-search` or direct bounded
  reads.

## Evidence boundary

Treat `EXTRACTED` edges as source locators and `INFERRED`/`AMBIGUOUS` edges as
hypotheses requiring verification. A graph node, community, shortest path,
report, or successful extraction does not establish a research claim, gate
pass, provenance relation, condition fingerprint, or promotion decision.

Never replace or duplicate the canonical `STATE`, `QUESTION-REGISTER`,
`DESIGN-SSOT`, `EXPERIMENT-LEDGER`, `EVIDENCE-ARTIFACT`, or Portfolio Gate
Matrix records with Graphify output. Record any adopted correction in the
canonical owner, not only in graph memory.

## Pilot exit gates

Keep this integration `EXPERIMENTAL` until a bounded pilot demonstrates:

1. the selected corpus and exclusions are reproducible;
2. graph locators lead back to canonical files without stale or ambiguous
   source identity;
3. at least one realistic false or inferred relationship is detected and
   corrected;
4. generated output stays outside the evidence authority chain; and
5. a fresh session can resume using the canonical records without Graphify.

If these gates fail, keep the feature experimental or mark the project-local
policy `TEMPORARY`/`REJECTED`; do not weaken the evidence rules.
