# Request Classification

Use the full request and recent context, not isolated keywords, to determine
the permitted work. No fixed announcement is needed for an obvious narrow
request. State ambiguous boundaries or material scope changes; required
substeps of an authorized task do not need repeated approval. A workflow label
never authorizes additional external actions.

## Type table

| type | user is asking for | allowed side effects | mandatory steps from this skill |
|---|---|---|---|
| `understand` | explanation, reading, "파악", "이해만", what does X mean | none | direct relevant evidence; no compulsory status/reference tour |
| `analyze` | diagnosis, comparison, verdict on existing evidence, "분석", "검토", "판정" | no durable writes; reversible diagnostics only | evidence recovery; claim ceiling stated; two-witness rule for consequential claims |
| `organize` | restructure or clean documents, "정리", "재구성", rename, dedupe | requested owner documents and their necessary path/index updates; no new scientific claims | preserve IDs, history and links; no unrequested evidence moves/deletion |
| `record` | persist a decision or result, "저장", "기록", "등록", update state | STATE capsule, ledger, registry, milestone, receipts | registration invariants; registration checklist; claim ceiling; next gate |
| `implement` | write or extend code/scripts/templates, "구현", "만들어" | requested source, tests and necessary documentation in the declared namespace | scientific contract for scientific changes; relevant preflight, not every experiment ritual for an ordinary edit |
| `fix` | correct a defect, "고쳐", "버그를 수정" | diagnosis/reproduction and minimal fix with relevant tests | reproduce first; smallest change; re-run the failing check; preserve consequential failures |
| `execute` | run jobs or measurements, "돌려", "제출", "실행" | only the requested execution scope; not blanket scheduler access | scientific runs require the applicable contract/gates and immutable attempts; a local lint is not a scientific run |
| `handoff` | freeze for another session, "인계", "handoff", close out | necessary receipts, capsule changes and evidence locators | update only changed owners; no compulsory regeneration of every view |

Adjacency groups that never need clarification: {plan, think, understand,
design, sketch, brainstorm} → `understand`; {summarize, list, inventory} →
`analyze` when no persistence is asked, `record` when it is.

## Signal words

Korean: 이해만·파악·생각해보자·기획·구상 → `understand`; 분석·검토·비교·판정·왜 →
`analyze`; 정리·재구성·묶자 → `organize`; 저장·기록·등록·반영·남겨두자 →
`record`; 구현·작성·만들자 → `implement`; 고쳐·수정·버그 → `fix`; 돌려·제출·
실행·실제로 해보자 → `execute`; 인계·마무리·넘기자 → `handoff`.
English equivalents: explain/understand, analyze/diagnose/compare, tidy/
reorganize, save/log/register, implement/build, fix/debug, run/submit/launch,
hand off/close.

These are hints, not a keyword classifier. "왜 안 되지?" without a request
to repair means diagnose, not permission to edit. "기획안을 저장" authorizes
the plan document, not the planned implementation. "계속" inherits the active
scope unless new words change it. Resolve a material ambiguity; otherwise use
the least expansive reading that satisfies the request.

## Mismatch tests

Check material mismatches before acting. State the evidence and fitting
alternative; wait only when missing authority or a meaningful user choice
prevents safe continuation. Offer at most two proposals; never repeat questions
just to relabel normal substeps. A user's decision cannot bypass a hard
permission boundary or turn an unmet scientific criterion into PASS.

| requested | conflict evidence | propose |
|---|---|---|
| `analyze` results | the unit has no terminal attempt; required arm or EQUAL control missing | `execute` the missing arm, or `analyze` explicitly labeled PARTIAL |
| `organize`/`record` "final" results | unit verdict is open, gate not passed, or reproduction pending | `record` as interim with claim ceiling, or wait |
| `fix` | defect not yet reproduced | reproduce/diagnose within the authorized fix; ask only if a new target or risky action is needed |
| `execute` | contract not locked, hard gate open, or budget/coverage plan absent | `implement`/`record` the contract, then execute |
| `record` a milestone as achievement | any ACHIEVEMENT condition unmet (unit closed, gate passed, controls, provenance, claim ceiling, reproduction) | `record` as NEGATIVE-FINDING/METHOD/DECISION or defer |
| `understand` | user's premise contradicts the canonical record (wrong owner, superseded number) | answer, and flag the contradiction in one line |

Near-miss requests are not mismatches: asking to "plan" when the project is
mid-execution, or to "think through" a closed unit, is legitimate. Only act
on conflicts that would make the output misleading or destructive.
