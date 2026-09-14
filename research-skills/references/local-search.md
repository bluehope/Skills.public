# Research Local-Search Adapter

This reference adds scientific-project constraints to the sibling
`$local-search` skill. The sibling skill is the
authority for installation, retrieval tiers, bounded reading, corpus-policy
generation, staging, and QMD operations.

This adapter is for broad discovery or authority conflicts, not every direct
ID/path read. Use `research_state.py show/find` or scoped `rg` first when
sufficient; no index or optional-tool preflight is needed for these operations.
Before first relying on an unverified QMD environment or changed capabilities,
run the sibling `doctor` and `qmd-capabilities`
commands, then read `qmd skills get qmd --full` for guidance matching the
installed QMD release. Do not assume a flag is portable merely because it
works on one machine.

## Research corpus roles

Always context:

- the compact current `STATE` or equivalent decision capsule, when current
  project context is needed; use its locators rather than preload their targets.

Applicable project instructions still govern. "Always context" is not a command
to read STATE for an isolated known-source question or maintain a new cache.

Search on demand:

- the design source of truth, experiment ledger and artifact/provenance map;
- living method notes, evidence cards, verified report claims, and source maps;
- registered paper metadata and derived text with explicit provenance;
- code-adjacent Markdown needed to interpret an experiment or result.

Exclude:

- generated reports used only as derivatives, logs, build output, and caches;
- duplicate raw mirrors, temporary exports, unregistered paper extracts, and
  large code/data dumps;
- credentials, personal data, hidden evaluation truth, and restricted material.

For consequential scientific claims, a search hit is only a locator. Verify the
claim in the canonical project record and in an immutable artifact or original
source. Model recollection is not an independent witness.
Index exclusions are not prohibitions on direct raw-log inspection for a
specific failed attempt; restricted/private material still requires its scope.

## Reconcile Contradictions Before Updating State

When chat memory, prose, code, and artifacts disagree, first compare their
condition fingerprints and classify the disagreement:

```text
STALE-DOC
MODEL-MEMORY-ERROR
CONDITION-CHANGED
SEMANTIC-DRIFT
INVALID-ARTIFACT
TRUE-OPEN-CONTRADICTION
```

- `STALE-DOC`: an older document still points to a superseded live state.
- `MODEL-MEMORY-ERROR`: recalled context has no verified file witness.
- `CONDITION-CHANGED`: both claims may be true under different source,
  geometry, split, code, runtime, target, or metric conditions.
- `SEMANTIC-DRIFT`: a label or metric name changed meaning.
- `INVALID-ARTIFACT`: a contract, provenance, or validation failure prevents
  acceptance.
- `TRUE-OPEN-CONTRADICTION`: trusted evidence conflicts under the same
  condition fingerprint.

Use `assets/contradiction-audit-template.md` for consequential cases. Scope both
claims when conditions differ. For a true open contradiction, stop promotion
and design the cheapest discriminating check.

## Activate it from a research task

Compose with local-search when scoped ID/path/rg retrieval is insufficient:
for example, broad recovery of prior work, locating literature already stored
locally, reconciling conflicting versions, or tracing an unclear claim back to
code/data/artifacts. A known source can still be inspected directly.

```text
research question
  -> local-search candidate retrieval
  -> canonical-path verification
  -> research authority/claim-level decision
  -> answer, or authorized ledger/design/evidence update
```

Do not create or modify a corpus policy during an answer-only audit. Search the
live filesystem in a bounded scope and report missing coverage. For a requested
workspace setup or reusable workflow, use the shared `init-policy` command to
seed a policy, then review it before staging.

## Research policy additions

Extend the shared policy with project-specific declarations for:

- `authority_order`: code/data/artifact, living design/decision, frozen report,
  mirror, and chat-memory precedence;
- `always_context`: the compact state capsule; keep hub/design/ledger/artifact
  register as on-demand locators unless the project justifies a small exception;
- exact include rules for source cards, decision notes, method notes, and
  human-authored summaries;
- exact exclude rules for raw data, checkpoints, scheduler logs, generated
  reports, temporary exports, duplicate mirrors, and superseded copies;
- restricted paths for credentials, personal data, licensed/private sources,
  hidden evaluation truth, and embargoed results;
- stable collection name and a one-line context explaining that hits are
  locators, not evidence.

Keep raw numerical artifacts and large datasets outside a Markdown/QMD corpus.
Index a human-authored artifact register or evidence card, then inspect the
immutable artifact with the appropriate data/code tool.

## Search receipts and escalation

Resolve `$local-search`'s actual installed root and use its
`assets/search_receipt_template.csv` for consequential lookups within authorized
durable work. Do not assume a sibling path or write a receipt during read-only
analysis; report the needed scope/evidence in the answer instead. Record the question, tier, query, scope, result
count, selected canonical path, verification witness, verdict, and
zero-result/rejection reason.

Local `ZERO-RESULT` means no adequate result in the declared scope and tier. It
does not prove scientific absence. Check policy exclusions and source
registration, then widen deliberately or move to web/source acquisition.
Register a newly acquired source before it enters the reusable corpus.

QMD is recommended when ranked, semantic, or cross-language retrieval
repeatedly saves work; exact `rg` search remains a valid baseline and QMD is not
mandatory. Never block a research gate merely because embeddings or reranking
are unavailable; report the missing retrieval coverage separately.

For repeated scientific lookups, use a named or project-local index so corpus,
embedding, and context state do not leak across projects. Rank a bounded set
with BM25/vector/hybrid search, then retrieve only selected spans with
`qmd get FILE:FROM:COUNT` or bounded `qmd multi-get`. Prefer stable `qmd://`
paths, use `--full-path` to map back to disk, and reopen the canonical source
before citing it.

Use structured `intent:`, `lex:`, `vec:`, and `hyde:` query documents when
exact scientific vocabulary and paraphrased intent require separate channels.
Use `--explain` only as a retrieval diagnostic; score traces do not establish
scientific validity. For recurring high-stakes questions, maintain reviewed
`qmd bench` fixtures containing expected canonical files and explicit
zero-result cases.

## Install this skill's reference corpus

The canonical `research-skills` checkout includes `local_search_policy.json`.
Build its disposable corpus and dedicated index with:

```bash
python scripts/setup_local_search.py --dry-run
python scripts/setup_local_search.py
python scripts/setup_local_search.py --embed
```

The default staging path is `~/.cache/local-search/research-skills-corpus`,
outside Dropbox, and the default named index and collection are both
`research-skills`. Re-running replaces the staged corpus and updates the same
collection. `--embed` is explicit because model work can be expensive. The
script never changes canonical source files or treats indexed text as evidence.

After embedding, measure known-answer retrieval with:

```bash
qmd --index research-skills bench tests/fixtures/research_search_benchmark.json --json
```

Treat benchmark failures as retrieval regressions or fixture-review prompts,
not as scientific contradictions. The fixture names expected source owners;
the source contents and immutable artifacts still arbitrate claims.

## Coordinate Search With The Context Cache

Search and caching serve different roles:

```text
context cache -> fast condition-aware routing
local search -> candidate recovery
canonical witness -> evidence verification
```

Use this cache procedure only when the project maintains a reusable cache;
ordinary ID lookups do not require cache-state bookkeeping. Start from pinned
locators, then use recurrent entries only when their condition
fingerprint matches. Rehydrate a ghost entry only when its revisit trigger
fires. In authorized maintenance after a consequential lookup, record whether it was a context hit,
indexed/local-search hit, search miss, or stale hit.

Promote a locator to recurrent context only after repeated use, high error
cost, direct hard-gate relevance, or repeated human questions. Demote it after
a pivot, correction, source/profile change, or superseding owner. Do not use a
high hit ratio to excuse stale hits.
