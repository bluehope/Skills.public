---
name: local-search
description: "Resolve broad, conflicting or binary local-source retrieval; manage requested indexes and search diagnostics. Plain known-path or filename lookup uses direct reads/rg."
metadata:
  version: "2026.09.14.1"
---

# Local Search

Find a trustworthy local source span when scope, file format, authority or retrieval tier needs more than one exact lookup. A known path/ID or ordinary filename search uses direct reading or scoped `rg` without activating this workflow.

## Retrieve only what is needed

Use live `rg --files` / `rg` first, then stop once the requested locator or evidence is established. Escalate only for a diagnosed gap:

- Repeated scans of a measured-large codebase: tgrep indexed regex; retain live-file freshness checks. AST/LSP may suit structural code questions.
- Binary documents: rga; text-layer PDF fallback `pdfgrep` or bounded PDF text extraction. Scans need OCR with provenance.
- Unknown file / terminology: existing QMD BM25, then semantic or hybrid only when lexical retrieval is insufficient. Retrieve only ranked candidates with bounded get/multi-get.
- Structured fields from already located text: [langextract.md](references/langextract.md), never as a search engine or factual authority.

Read [retrieval_contract.md](references/retrieval_contract.md) for broad, ambiguous or consequential lookups. Start with about five candidates and relevant 20–60-line spans. Default ordinary tool output is at most 2,000 tokens. Inspect file type first; parse selected JSONL fields instead of printing conversation logs, and never print executables as text. Read selected instruction files completely. Re-read an unchanged source only for a new decision or missing context.

## Verify at the requested stakes

Search hits, summaries and indexes are locators. Reopen the canonical source; citations point there, not to staged copies. Consequential claims require the canonical record plus original/immutable source or another independent authority. Model memory is not a second witness. Simple filename lookup needs neither a second document nor a ledger.

For conflicting status/terms, `scripts/local_search_tools.py claim-bundle PROJECT TERM` gathers bounded definition/current/terminal/history locators, not a verdict. Follow declared authority and disclose conflicts. `ZERO-RESULT` means missing coverage in this query/scope, not scientific absence. Change query/scope/tier after a miss; do not repeat an unchanged failed query.

## Optional operations

- Corpus creation or maintenance requested: [corpus-management.md](references/corpus-management.md). Reuse existing policy; no automatic hub tour, policy, receipt or index creation for ordinary retrieval.
- Create/start tgrep: [tgrep.md](references/tgrep.md).
- Create/embed/move/repair QMD: [qmd_operations.md](references/qmd_operations.md).
- Needed tier missing, stale or failing: [search-diagnostics.md](references/search-diagnostics.md). Check only that tier; do not run all doctors or latest-release checks at task start.
- Authorized tool setup/platform migration: [installation.md](references/installation.md). Optional-tool absence does not block plain `rg`.

Keep indexes, staged corpora, caches and extracted restricted data per-machine outside synced folders and deliverables. Honor source/restricted-data policy; logs excluded from indexing may still be read directly within scope. No links/junctions/hard links/mounts inside synced trees.

For restricted extraction use a verified local provider; cloud use requires explicit provider and source-scope authorization. Never inspect credentials/cookies. Carbonyl is public-page visual inspection only, not authenticated acquisition or a structured extractor; prefer current browser/API tools for that work.

Return locators (`path:line`) and short relevant context. Write search receipts only when consequential decisions belong to authorized durable work. Retrieval alone does not trigger research registration, SSH or document production.
