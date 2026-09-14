---
name: llm-handover-skills
description: "Prepare hash-bound multi-worker dispatches or reconcile independent LLM receipts; not ordinary handoff notes or single-session summaries."
metadata:
  version: "2026.09.14.1"
---

# Bounded LLM delegation

Own dispatch contracts and receipt reconciliation, not transport or schedulers.
No dispatcher executable is bundled: use available authorized task tools,
verified CLI and existing project validators. A normal handoff summary can use
the current project documents without creating workers or loading this workflow.

## Core contract

- One coordinator owns frozen inputs/contract, shared state and canonical verdict.
  Each worker has a unique namespace, role, output prefix and receipt path.
- Freeze dependency hashes, schema, seed, comparisons/tolerances and forbidden
  actions before dispatch. Never edit a consumed bundle; issue a successor.
- Sibling implementations/results and hidden evaluation data remain unreadable
  to independent workers until all required receipts freeze. A shared filesystem
  is not isolation: enforce read/write boundaries before writes, failing closed.
- A worker owns local metrics/flags, never scientific promotion. Process exit,
  valid receipt and scientific acceptance are separate. Missing/stale observations
  stay unknown with their observation time.
- Treat results as DIAGNOSTIC-ONLY until schema, provenance, hashes and declared
  gate pass. Preserve failed/invalid/superseded receipts; no least-bad selection,
  post-hoc tolerance widening or rerunning only an inconvenient witness.
- Delegation cannot enlarge authority: no production edits, Slurm/GPU/DFT runs,
  installs, cancellations or new tasks unless the user/product permits them.
  A contract alone cannot grant those permissions.

## Choose only the needed procedure

Start at the known bundle/receipt or compact state locator, not every project
document. Reopen/hash declared inputs; selected instruction files are read fully.

| Request | Read / reuse |
|---|---|
| New/revised dispatch, backend selection, namespace validation | [dispatch.md](references/dispatch.md); existing manifest and worker templates |
| Validate a returned receipt, continuation or final comparison | [receipts-and-reconciliation.md](references/receipts-and-reconciliation.md); existing reconciliation template |
| Inspect one worker's current state | named task/receipt, bounded status tools; no new dispatch |

Use separate durable tasks only when requested/permitted and needed for
independent context/resumption. Claude CLI requires verified installation/auth,
bounded turns and tools. Short-lived subagents are side checks, not independent
blind scientific witnesses. Do not install a missing CLI without authorization.

Shared `project_root` is read context; `worker_write_root` is the write boundary.
Use worktrees/copies only when needed for isolation without hiding required
documents. Preserve same-project read access in non-Git Dropbox projects; keep
KIAS's common read-only mirror and per-worker temporary namespaces. Do not make
links inside synced trees.

Assets are templates, not executable validators:
[dispatch manifest](assets/dispatch_manifest.template.json),
[worker prompt](assets/worker_prompt.template.md),
[reconciliation prompt](assets/reconciliation_prompt.template.md).
A template's illustrative hash is not a validated dependency. Reuse project
schema/hash/namespace checks and positive/negative fixtures before dispatch.

Compose $ssh-skills only for transport and $hpc-skills only for scheduler work.
Their names do not require reading both for a local receipt review.
For consequential handoff failures reuse project `ops_knowhow/incidents.tsv`,
actual skill versions and bounded evidence; resolve via the existing project
helper, not a new registry or automatic promotion. Update only changed canonical
state pointers when closing; keep the exact next gate and newest receipt visible.
