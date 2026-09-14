# Local retrieval contract

## Tier selection

| Need | Tier | Example |
|---|---|---|
| filename, ID, DOI, symbol, exact wording | `rg` | `rg -n -m 20 "D4N-F07B" .` |
| repeated regex in a measured-large codebase | `tgrep` | `tgrep -n -m 20 --index-path INDEX "CallGraph" .` |
| text inside PDF, EPUB, DOCX, archive | `rga` | `rga -n -m 20 "latent map" sources/` |
| unknown file, known terminology | QMD BM25 | `qmd search "latent map" -c project -n 5` |
| paraphrase, cross-language, unknown terminology | QMD semantic | `qmd vsearch "숫자 생성 공간" -c project -n 5` |
| broad intent requiring combined recall | QMD hybrid | `qmd query "how generation becomes controllable" -c project -n 5` |

Do not use semantic or hybrid retrieval for a plain identifier that exact search can answer.
Do not create a tgrep index for a one-off query that `rg` answers cheaply.

## Bounded reading

- Return about five candidates initially.
- Read roughly 20–60 lines around each match.
- Use `-m`, `-n`, file globs, and directory scope to avoid output floods.
- Read a whole file only after it is selected for final verification.
- Search filenames before bodies when the query names an artifact type or ID.

## Evidence boundary

- A ranked hit, snippet, staged copy, derived PDF text, or model summary is a locator.
- Verify dates, quantitative values, citations, equations, captions, and status against the canonical file or original source.
- Prefer the live filesystem for freshness; indexes can lag edits.
- Record disagreements between duplicates instead of silently choosing the convenient copy.
- Search zero-result means “not found in this query/scope/tier,” not “does not exist.”

## Failure classification

Classify a miss before escalating:

- `QUERY`: wrong term, language, spelling, or identifier;
- `SCOPE`: wrong folder, collection, mask, or exclusion;
- `ADAPTER`: binary extractor unavailable or incompatible;
- `TEXT-LAYER`: scanned/image-only source;
- `INDEX`: collection missing, stale, or unhealthy;
- `EMBEDDING`: vectors missing or model changed;
- `AUTHORITY`: hit exists only in a stale/derived source;
- `ZERO-RESULT`: supported query completed with no adequate candidate.

Change one dimension at a time. Do not brute-force every tier and dump all output into model context.

## Two-witness rule

For consequential claims, require a current canonical project record plus the original/immutable source or another independent authority. Model recall can suggest queries but is not documentary evidence.

For consequential status labels, collect four context classes when available:

```text
definition / current usage / terminal artifact / correction or history
```

Use `scripts/local_search_tools.py claim-bundle PROJECT TERM` as a bounded
locator generator. Its role classification is heuristic; reopen the selected
canonical files and apply the project's authority order before resolving a
contradiction.

Verdict:

```text
agree → cite canonical source and proceed
contradict → correct or record discrepancy
no support → mark unverified
unclear after bounded probes → report the conflict
```
