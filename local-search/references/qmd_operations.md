# QMD operations

QMD is an optional on-device engine for BM25, vector search, and hybrid reranking. The canonical files remain authoritative.

Set `qmd.recommended: true` and `qmd.required: false` in a new project policy by default. Recommend installation when the corpus is reused across sessions, contains many similarly named documents, the target file is often unknown, or Korean/English paraphrase search is valuable. Do not block exact or PDF search merely because QMD is absent.

## Detect the installed capability set

QMD evolves quickly. Inspect the local binary instead of assuming every machine has the same release:

```bash
python scripts/local_search_tools.py qmd-capabilities
qmd --version
qmd doctor
qmd skills get qmd --full
```

The bundled runtime skill is version-matched operational guidance. This shared skill owns corpus authority, privacy, evidence verification, and cross-platform fallbacks. Use both; do not replace the project's evidence contract with runtime help.

## Choose index scope

- Use a project-local index (`qmd init`) when the repository should carry a reviewable `.qmd/index.yml` recipe while the database remains local.
- Use `--index NAME` for separate per-machine databases that must not share collections or embedding state.
- Use the default global index only for small, intentionally shared personal corpora.

Never put a live SQLite index, model cache, or daemon state under Git, Dropbox, or another sync engine. Review the generated config and ignore runtime state before indexing restricted material.

## Create a collection

Initialize and review a project policy:

```bash
python scripts/local_search_tools.py init-policy PROJECT \
  --name project-name \
  --output PROJECT/local_search_policy.json
```

Stage only approved Markdown:

```bash
python scripts/local_search_tools.py stage-policy \
  PROJECT/local_search_policy.json STAGED_CORPUS
```

Register it. Prefer a named index when a workstation hosts several projects:

```bash
qmd --index project-name collection add STAGED_CORPUS --name project-name --mask "**/*.md"
qmd --index project-name context add qmd://project-name "Canonical project notes staged from declared sources; results are locators."
qmd --index project-name collection show project-name
qmd --index project-name update
```

Keep the staging recipe and context in the project. Keep the QMD database, models, caches, and writer logs per-machine.

Pass `--index NAME` consistently to every lifecycle and query command when using a named index. A fresh named index is also the conservative recovery path when the shared default index is corrupt: preserve the old database for diagnosis and rebuild only the reviewed project corpus. For a project-local setup, run `qmd init`, review `.qmd/index.yml`, then use QMD from that project directory. Confirm exact behavior with the installed runtime skill because config fields can change between releases.

## Query modes

```bash
qmd --index project-name search  "exact known terms" -c project-name -n 5
qmd --index project-name vsearch "semantic paraphrase" -c project-name -n 5
qmd --index project-name query   "broad intent" -c project-name -n 5
```

Use `--format json` for agent parsing, `--format files` for a file list, `--line-numbers` for inspection, `--full-path` when mapping back to canonical files, and `--no-rerank` when CPU/GPU cost is not justified. Add `--explain` to hybrid diagnostics when the installed release supports it. Pair `--all` with a deliberate `--min-score`; do not dump an unbounded corpus.

Use a structured query when lexical and semantic evidence need different wording:

```text
intent: Find the current canonical definition and its terminal evidence
lex: "NEGATIVE-COMPLETE" validator
vec: current project status and completion meaning
hyde: The canonical state file declares the status and cites an immutable validator result.
```

Every line in a structured query document must be typed (`intent:`, `lex:`, `vec:`, or `hyde:`). A single unprefixed line is an expansion query and must not be mixed with typed lines.

## Retrieve bounded evidence

After selecting candidates, retrieve only the needed spans:

```bash
qmd get qmd://project-name/docs/contract.md:120:40
qmd multi-get "qmd://project-name/docs/{STATE,contract}.md" -l 80 --max-bytes 20000
```

`get` and `multi-get` include line numbers by default in current releases. Prefer stable `qmd://` paths over ambiguous suffixes, then reopen the canonical on-disk file before citing. `multi-get` is for bounded candidate comparison, not broad corpus export.

## Search code

Use `rg`, AST tools, or LSP first for exact symbols and syntax relationships. If QMD indexes code, use `--chunk-strategy auto` when supported so compatible languages receive AST-aware chunks; fall back to `regex` for unsupported files. Search results still locate code; inspect the live source and its callers/tests before concluding behavior.

## Embeddings

BM25 does not require embeddings. Enable vectors only after collection count and BM25 smoke queries pass:

```bash
qmd --index project-name embed -c project-name
qmd --index project-name status
```

Use current memory and timeout controls shown by `qmd embed --help`; do not preserve release-specific flags in a shared contract. Current releases may expose document-count, byte-size, and timeout limits. Force re-embedding only after changing the embedding model or when vectors are known invalid:

```bash
qmd --index project-name embed -f -c project-name
```

The current default embedding model is English-oriented. For a Korean/English corpus, QMD documents `QMD_EMBED_MODEL` with a multilingual Qwen3 embedding model. Changing models requires `qmd embed -f`. Verify current model guidance in the QMD repository before pinning a model URI.

## Benchmark recurring retrieval

Create a small reviewed fixture for high-value questions and run:

```bash
qmd --index project-name bench path/to/fixture.json
```

Include representative exact terms, paraphrases, Korean/English variants, expected files, and explicit zero-result cases. Keep fixtures free of secrets. Compare BM25, vector, and hybrid quality plus latency before changing models, chunking, or reranking. A benchmark score validates retrieval locators, not the truth of the underlying documents.

## Agent integrations

`qmd mcp` exposes a stdio server; releases may also provide an HTTP daemon. Treat MCP as a transport, not an authority boundary. Keep the same collection scope, bounded retrieval, source reopening, and receipt rules. Do not start a persistent HTTP daemon unless the user requested it and its bind address, authentication, logs, and lifecycle are understood.

## Health and staleness

Before trusting semantic/hybrid results:

1. `qmd collection list` and `qmd collection show NAME`;
2. compare staged manifest count/hash with the intended corpus;
3. `qmd update` after canonical changes;
4. inspect `qmd status`;
5. run stable BM25 smoke queries;
6. verify embedding coverage before `vsearch`/`query`;
7. reopen the canonical source for final claims.

Use one writer per index. Do not put SQLite databases or live QMD config under Dropbox, Git, or another sync engine. Cross-machine equivalence means the same corpus recipe/hash and compatible smoke results, not byte-identical databases.

## Fallbacks

- QMD missing: use `rg`/`rga`; install only if ranked retrieval is worth the maintenance.
- embeddings missing: use `qmd search`.
- model download blocked: remain on BM25 and record semantic as unavailable.
- insufficient memory: use BM25 or hybrid without rerank; reduce candidate count.
- stale collection: update or rebuild the staged corpus before widening queries.
- corrupted/contended index: stop writers, preserve diagnostics, and rebuild the reviewed corpus in a fresh named index; do not delete a shared database just to recover one project.
