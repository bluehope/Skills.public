# Research Context Cache

> Cache scoped claims and canonical locators, not copied evidence tables.

| Field | Value |
|---|---|
| Owner |  |
| Last reviewed |  |
| Review trigger | pivot / handoff / promotion / oversized startup context |
| Soft capacity | `PINNED`: one short session-start read; `RECURRENT`: active-frontier reuse only |

## Pinned

| Key | Scoped claim/role | Authority | Condition fingerprint | Last verified |
|---|---|---|---|---|
| `STATE` | current direction and next gate |  |  |  |

## Recent Once

| Key | Locator | Why admitted | Last access |
|---|---|---|---|

## Recurrent

| Key | Scoped claim | Authority | Reuse count | Invalidate if |
|---|---|---|---:|---|

## Ghost

| Key | Path/ID only | Status | Rehydrate when |
|---|---|---|---|

## Cache Health

| Check | Observation |
|---|---|
| context hits |  |
| indexed/local-search hits |  |
| search misses |  |
| stale hits |  |
| repeated wide searches |  |
| entries promoted |  |
| entries demoted/invalidated |  |

## Stale-Hit Reconciliation

| Date | Cache key | Cause | Affected decision | Correct authority | Action | Contradiction audit |
|---|---|---|---|---|---|---|
