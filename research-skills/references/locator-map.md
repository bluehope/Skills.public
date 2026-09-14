# LOCATOR-MAP (`PATH_MAP.md`) — experimental capability

Maturity: `EXPERIMENTAL` (global form; promotion requires reuse by a second
project). The originating pilot record with its project evidence lives in the
pilot project's `research_organization/policies/`, not in this skill.

A LOCATOR-MAP is one file per mission or campaign that owns *where* things
are: builds, original versus modified source/runtime, checkpoints, physical
inputs, result roots as arm × method, execution environment in load order, and
known asymmetries. It never owns a number, PASS/FAIL, claim, or verdict; the
immutable result audit owns those, and the state capsule owns direction and
next gate. Use [assets/path-map-template.md](../assets/path-map-template.md).

Rules:

1. Create one only when the state capsule's authorities table would need ≥5
   server roots, ≥2 hosts, a name denoting ≥2 objects, a multi-step execution
   environment, or a recorded repeat of "where is X?". Below that, the capsule
   table suffices.
2. Every row: role, absolute path, identifier (sha256-16 / git HEAD / version),
   consuming stage, `verified_on` = date checked on the actual host.
3. Hard gate on creation: linked from the mission SSOT or state capsule, the
   project STATE, and the project Hub. A handoff missing any link is not READY.
4. Other documents say "see PATH_MAP"; they never restate a path with its hash.
   Include the map in the packet's `SHA256SUMS`.
5. Moved or rebuilt objects get a new row; old rows go to *Superseded rows*
   with `SUPERSEDED BY`, date, reason. Never delete.
6. One mission, one map; freeze it under the archive index at closure and let a
   successor inherit by link. Shared infrastructure gets a project-level
   `INFRA_PATH_MAP.md` only when a second mission shares ≥3 rows.
7. A result-root row records the actual consumer/assembler and its own input,
   geometry, and build/runtime identities; a directory name is not a substitute.

States: `PARTIAL` (unverified cells) → verify on host; `BLOCKED` (object not
found/hashable) → recover or supersede; `READY` (all verified, three links,
in SHA256SUMS); `REJECTED` (carries verdicts or duplicates an owner) → strip.

