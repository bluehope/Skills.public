# Selected-tier diagnostics and client capabilities

Choose only the diagnostic for the tier in use. Reuse same-environment evidence; the command examples below are alternatives, not a startup checklist. Do not install/update or create indexes without authority.

## Codex execution

- Use `rg`/`rg --files` first and keep tool output bounded.
- Run the bundled doctor only for a missing/unverified or changed tier needed now.
- Run `tgrep-smoke` for a new or changed tgrep binary, then reuse verified readiness. Keep every
  tgrep index per-machine and outside the repository and Dropbox tree.
- For an explicitly requested version/update audit, use `scripts/install_tgrep_userspace.py --check` to compare the installed and
  latest official tgrep releases. Do not update merely because a release exists;
  review it, select an explicit tag, then rerun smoke and project queries.
- Run `qmd-capabilities` and the version-matched `qmd skills get qmd --full` guidance before relying on recently added QMD flags.
- Use project-local or named QMD indexes to prevent unrelated corpora from sharing one mutable namespace.
- Benchmark consequential recurring queries with `qmd bench`; optimize retrieval quality before adding semantic cost.
- Use `apply_patch` only for canonical policy/ledger edits; never edit a staged corpus or index.
- Prefer purpose-built PDF/document tools for final verification after search locates a page.
- Do not enter credentials or sensitive cookies into an old or unmaintained terminal-browser release. For authenticated pages, prefer a current managed browser session and obey the site's terms and access controls.
- Use LangExtract through a local provider for restricted material: Ollama or an existing localhost OpenAI-compatible server such as `llama-server` or `ds4-server`. Do not call a cloud provider unless the user explicitly authorizes that provider and source scope. Keep JSONL/HTML outputs outside synced corpora and verify every adopted item against the canonical source span.

## Claude execution

- In Claude Code, use Glob/Grep/Read for exact live-file discovery and Bash for bundled CLI diagnostics.
- Keep `SKILL.md` portable; `agents/openai.yaml` is Codex metadata and may be ignored.
- Claude Code may use the current QMD plugin/MCP, but CLI receipts and canonical-file verification remain authoritative.
- Claude API/claude.ai sandboxes may lack local filesystem, network, packages, and persistent indexes; package the bounded corpus or use Claude Code for machine-local retrieval.

## Diagnose and fall back

For the corresponding failing/unverified tier, select one command:

```bash
python scripts/local_search_tools.py doctor
python scripts/local_search_tools.py tgrep-smoke
python scripts/install_tgrep_userspace.py --check
python scripts/local_search_tools.py qmd-capabilities
```

Fallback without overstating capability:

| Missing or degraded | Fallback |
|---|---|
| `rga` | `rg` on text; `pdfgrep` for text-layer PDFs |
| `tgrep` | continue with `rg`; indexed regex is an optimization, not a correctness prerequisite |
| Office adapter | search a canonical Markdown/text mirror or convert via the document workflow |
| scanned PDF | OCR first, then search the derived text with provenance |
| QMD | exact/binary search only; do not claim ranked or semantic coverage |
| embeddings/model | QMD BM25 remains usable |
| memory/GPU | skip rerank or use bounded CPU settings |
| stale index | refresh, then verify against the live canonical file |

Report each tier independently. A working binary on `PATH` does not prove its adapter, corpus, model, or index is healthy.

Report search results as locators (`path:line` plus a one-line context);
quote full text only for the selected spans, never as bulk dumps.
