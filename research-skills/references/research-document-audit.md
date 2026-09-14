# Research Document Audit

Use the bundled read-only audit when a project has several living documents,
status labels, terminal artifacts, or approval ladders.  It reduces manual
checking but does not decide scientific truth or mutate project files.

## Separation of ownership

- Global code owns generic checks only.
- A project-owned JSON policy names canonical documents, current-scope files,
  historical boundaries, ambiguous terms, and receipt locations.
- Scientific definitions remain in their canonical Markdown owner.  Do not
  duplicate equations, thresholds, or verdict definitions into the policy.
- Immutable artifact literals remain unchanged; a living owner may bind a
  narrower normalized interpretation.

## Command

Start from `assets/research-doc-audit-policy-template.json`. Prefer the conda
`codex` environment for the bundled validator:

```bash
python <research-skills>/scripts/audit_research_docs.py \
  --project-root PROJECT \
  --policy PROJECT/research_doc_audit.json \
  --output AUDIT.json
```

The audit checks document existence, local Markdown links, stale live headers,
status-definition bindings, project glossary routing, historical-boundary
markers, and search-receipt schemas.  `BLOCK` findings return exit 1; warnings
return zero unless `--strict-warnings` is requested.

When `registration_receipts` are declared, the audit also checks the core
contract in [registration-checklist.md](registration-checklist.md). A
`stable_id_registry` starts from `assets/stable-id-registry-template.json`: a
JSON object with `schema_version: 1` and an `entries` array. Each entry has an
`id` and may bind `observable_id` and `unit_id`.
Optional `registration_profiles` map a profile name to `required_fields` and
project-root-relative `path_fields`; these become BLOCK gates only when a
receipt declares that profile.

The JSON result records tool, policy, registry, document, and registration
receipt hashes; actual Python runtime identity; per-check severity; and the
final exit code. These fields make the audit itself reproducible but do not
raise a scientific claim ceiling.

## Human boundary

The tool may identify `SEMANTIC-DRIFT` candidates, but a person must decide the
normalized meaning, claim scope, scientific validity, and any destructive or
external action.  Run it after terminal transitions, before handoff, after a
canonical status-definition change, and before/after cleanup.
