# Capability To Code Map

Search this map before writing a new helper. Prefer
`SEARCH -> VERIFY -> REUSE -> PATCH -> EXTEND -> NEW`; record the named
incompatibility before choosing `NEW`. Bundled Python helpers recommend conda
`codex`:

```bash
python <script> --help
```

Python 3.12, 3.13, and 3.14 are supported after dependencies pass preflight;
the conda `codex` environment remains the recommended default. Record the
actual executable, version, and environment identity in the run receipt. Do
not silently fall back to Python 3.11 or older.

| Function | Code | Usage owner | Input/template | Test |
|---|---|---|---|---|
| Register and revise documents, capability locators, views and observation snapshots | `scripts/research_records.py` | `references/project-records-and-views.md` | `research_state.py document/view/refresh` | `tests/project_records_test.py` |
| Stage writes, detect conflicts and recover interrupted commits | `scripts/research_transaction.py` | `references/project-records-and-views.md` | `research_state.py recover` | `tests/project_records_test.py` |
| Classify the request type and detect request/state mismatch before acting | judgment, no script | `references/request-classification.md` | — | — |
| Keep one verified LOCATOR-MAP per mission (EXPERIMENTAL) | none | `references/locator-map.md` | `assets/path-map-template.md` | — |
| Read project state by stable id, lint registries, bounded find, repeat guard; adopt an unmanaged project | `scripts/research_state.py` | `references/state-registry-api.md` | `<project>/research_state_schema.json` (`init-schema`/`adopt`), `assets/conversation-intake-template.md` | `tests/research_state_smoke_test.py` |
| Static fail-closed preflight of a short Bash/sbatch stage wrapper | `scripts/validate_stage_script.py` | `references/operational-knowhow-lifecycle.md` | the wrapper script | `tests/validate_stage_script_test.py` |
| Audit living research documents and registrations | `scripts/audit_research_docs.py` | `references/research-document-audit.md` | `assets/research-doc-audit-policy-template.json`, `assets/registration-checklist-template.md`, `assets/stable-id-registry-template.json` | `tests/smoke_test.py` |
| Render a decision-oriented research history | `scripts/build_research_history_view.py` | `references/research-history-and-loop-visualization.md` | `assets/research-history-snapshot-template.tsv` | `tests/research_history_view_smoke_test.py` |
| Capture and compare a redacted local environment | `scripts/capture_local_environment.py` | `references/local-environment-tracking.md` | project-owned JSON output | `tests/local_environment_smoke_test.py` |
| Initialize the optional ado workspace | `scripts/init_ado_workspace.py` | `references/ado-experiment-management.md` | `assets/ado-project-template/` | `tests/ado_workspace_smoke_test.py` |
| Look up operational errors by ID/signature/skill; log or resolve one incident | `scripts/operational_knowhow.py` (`lookup`, `log`, `resolve`) | `references/operational-error-recording.md` | `assets/operational-incident-record-template.json` | `tests/operational_knowhow_smoke_test.py` |
| Review recurrence or transfer a verified prevention | `scripts/operational_knowhow.py` (`analyze`, `mark-transferred`) | `references/operational-knowhow-lifecycle.md` | `assets/knowhow-transfer-receipt-template.json` | `tests/operational_knowhow_smoke_test.py` |
| Stage and index this skill's local-search corpus | `scripts/setup_local_search.py` | `references/local-search.md` | `local_search_policy.json` | `tests/local_search_integration_smoke_test.py` |

Graphify is an external experimental navigator rather than a bundled helper;
its runtime and rollback contract are owned by
`references/graphify-integration.md`. Templates without executable helpers
remain owned by the reference that links them. Do not invent a script merely
to fill an empty code column.
