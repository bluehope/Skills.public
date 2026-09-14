# Corpus management (only for authorized index/policy work)

## Establish corpus authority

Classify project material:

- **Always context:** small hub, current state, instructions, and active decisions.
- **Search on demand:** canonical plans, source maps, evidence cards, living documents, code, and verified summaries.
- **Excluded:** generated output, logs, caches, temporary intake, duplicate mirrors, answer keys, personal data, and restricted material not required for the task.

Materialize a disposable curated corpus when the index engine cannot express the project's full authority policy. Keep staged files and indexes per-machine and out of source control, Dropbox sync, and deliverables.

Default index exclusions do not prohibit direct inspection: for a failed
attempt, open its known logs/raw output in a bounded scope. Known IDs or paths
can be queried directly without building an index or running optional-tool diagnostics.

Use these templates only for authorized corpus/index or durable search-record work, not ordinary lookup: [corpus_policy_template.json](../assets/corpus_policy_template.json), [search_receipt_template.csv](../assets/search_receipt_template.csv).

For an authorized new corpus, inspect its hub, source tree, generated outputs, restricted paths, and existing search adapters, then create a project-local policy:

```bash
python scripts/local_search_tools.py init-policy PROJECT \
  --name stable-collection-name \
  --output PROJECT/local_search_policy.json
```

Run the script from the installed skill root: on Codex this is
`$CODEX_HOME/skills/local-search/scripts/local_search_tools.py` (Windows
PowerShell: `"$env:CODEX_HOME/skills/local-search/scripts/local_search_tools.py"`);
on other runtimes use the equivalent installed or checked-out skill path.
Keep the generated policy path-relative so the project remains portable; do not
write the machine-specific skill path into the policy.

Review the proposed include/exclude sets before staging. The default records QMD as recommended but not required. Recommend QMD when ranked retrieval is repeatedly useful, the correct file is often unknown, or cross-language/semantic retrieval matters; keep `rg` as the mandatory baseline.
