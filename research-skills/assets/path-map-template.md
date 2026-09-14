<!--
role: LOCATOR-MAP
status: DRAFT | READY | SUPERSEDED
policy: research-skills/references/locator-map.md
verified_on: YYYY-MM-DD TZ via <host(s)> (existence, sha256 prefix, versions)
parent_map: <INFRA_PATH_MAP.md path, or none>
authority: locations and environment identity only. Numbers, PASS/FAIL, and
  claims stay with the linked immutable result audits. Re-verify on disk before
  citing; this map is a locator, not evidence.
-->

# Key paths for <mission / campaign name>

Shorthand roots used below: `A=<server attempts root>`, `W=<server workspace root>`,
local packet root `<repo-relative path>`. Hash prefixes are the first 16 hex of sha256.

## Builds and binaries

| role | path | identifier (sha16 / git HEAD / version) | used by | verified |
|---|---|---|---|---|

## Source and runtimes (original vs modified — keep separate rows)

| role | path | identifier | modification scope (files, lines, patch source) | used by |
|---|---|---|---|---|

## Model checkpoints and physical inputs

| family / role | path | sha16 | companion inputs (PP, cards, conf) |
|---|---|---|---|

## Result roots (arm × method)

| arm | consumer/assembler identity | consumer's own PP/input identity | geometry/cell identity | build/runtime identity | server root (attempt namespace, job ids) | local immutable output (path, sha16) |
|---|---|---|---|---|---|---|

## Execution environment (order = what a script must do first)

| item | value | used by |
|---|---|---|
| profile / modules to source before `set -u` |  |  |
| launcher (MPI ranks, srun/mpirun form) |  |  |
| interpreter envs (conda env path, version, key packages) |  |  |
| language runtimes and depots (Julia, node, …) |  |  |
| scheduler partitions per stage |  |  |
| SSH form |  |  |
| preflight validators |  |  |

Envs that exist on the host but are bound to no accepted receipt: list them and
forbid substitution without a new hash-bound receipt.

## Known asymmetries and P0-relevant gaps

- <a path/route fact that the next hard gate depends on>

## Superseded rows

| old path | superseded by | date | reason |
|---|---|---|---|
