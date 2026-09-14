# Literature Management

Use this reference when external papers, standards, databases, or technical
notes are being collected, searched, compared, or mapped into a research
design.

## 1. One Workspace-Level Library

Keep one literature root above individual projects when several projects share
the same scientific domain:

```text
<workspace>/papers/
  README.md
  REFERENCE_REGISTER.md
  inbox/
  topics/
  sources/SRC-YYYY-FIRSTAUTHOR-SHORTKEY/
    SOURCE.md
    paper.pdf       # optional mirror
    notes.ko.md     # optional interpretation
  templates/
  archive/
```

Projects link source cards. Do not duplicate PDFs or long paper summaries in
project folders. DOI, publisher, standards body, database, or arXiv remains
canonical; a local file is a mirror.

## 2. Stable Source Identity

Assign immutable IDs of the form `SRC-YYYY-FIRSTAUTHOR-SHORTKEY`. Each accepted
source owns one `SOURCE.md`. Human aliases are navigation only; reproducible
citations use the exact ID and canonical URI.

Minimum source-card fields:

```text
src_id / status / title / authors / year / source_type
doi / canonical_url / verified_at
topics / projects
local_pdf / local_notes / mirror hash when needed
verified claim / exact source location / project use / limitation or non-claim
```

Copy `assets/source-card-template.md` when starting a new source card.

## 3. Lifecycle And Claim Ceiling

```text
inbox -> metadata-verified -> primary-source-verified
      -> synthesized -> design-linked -> superseded/rejected
```

- Search result, abstract, citation graph, and model recall are locators.
- A scientific claim becomes citable only after checking the primary source.
- Record section/equation/figure/page for consequential claims when practical.
- A paper can support `DESIGN`; it cannot establish `CODE-PASS`, `FIT-PASS`,
  `HOLDOUT-PASS`, or `PHYSICS-PASS` for the local implementation.
- Preserve rejected papers and failed analogies as negative evidence with a
  reason; do not silently erase them.

## 4. Document Ownership

| information | canonical owner |
|---|---|
| bibliographic identity and source-specific claims | source card |
| PDF/supplement mirror | source folder |
| cross-paper landscape and disagreement | `LITERATURE-SYNTHESIS` topic page |
| candidate recommendation | project `DECISION-RESEARCH` |
| implementation contract and gates | project `DESIGN-SSOT` |
| computed result and pass/fail | immutable artifact and experiment ledger |

Do not copy a literature table into several design/status documents. Link the
topic/source owner and record only the project decision it caused.

## 5. Search Order

Apply the sibling `$local-search` skill and this
skill's [research adapter](local-search.md). The shared skill owns exact,
binary, BM25, semantic, and hybrid tier selection; do not reproduce or override
that ladder here.

Within the selected retrieval tier, preserve this research authority order:

1. Search the register, topic pages, and source cards before acquiring another
   copy of a paper.
2. Read the matching source card, status, verified claims, and limitations.
3. Open a registered local PDF only when the card is insufficient.
4. Open the primary publication/database/standard for final verification,
   version-sensitive metadata, or a missing local mirror.
5. Register newly accepted material before adding it to a reusable corpus.

Recommended corpus policy:

```text
always small: papers/README.md, REFERENCE_REGISTER.md, active topic page
search on demand: SOURCE.md cards and project design/ledger
binary on demand: PDFs and supplements via rga
excluded from index: duplicate PDFs, logs, generated outputs, temp downloads
```

For a consequential claim, the source card/index locates the claim and the
original paper confirms it. Two summaries derived from the same abstract are
not independent witnesses. Record the lookup using the shared search receipt
when it changes a design choice or claim ceiling.

## 6. Literature-To-Experiment Gate

For each design-relevant paper, write an evidence card in the decision note:

```text
question
source IDs and exact claims
what transfers to the current representation/physics
what does not transfer
cheapest discriminating oracle or smoke
go/no-go rule
claim ceiling before and after the test
```

Competing physical explanations must remain separate. For example, improvement
from a pair-centred term proves that additional representational freedom helped;
it does not by itself prove that the pair centre is the unique physical answer.

## 7. Validation

After modifying a literature library:

1. verify every register link resolves;
2. verify every registered ID has one source card;
3. run the local-search smoke cases appropriate to the enabled tiers: one exact
   DOI, one SRC-ID, and one conceptual phrase when ranked retrieval is enabled;
4. verify a registered PDF query when the binary tier is enabled;
5. ensure project documents cite source cards rather than stale PDF paths;
6. record tier-unavailable, `ZERO-RESULT`, broken-link, or incomplete-source
   status instead of hiding it.
