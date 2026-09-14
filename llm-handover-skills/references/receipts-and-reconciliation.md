# Receipt validation and reconciliation

Read to accept/reject a worker receipt, continue from a prerequisite, or issue a
coordinator verdict. Reuse the existing dispatch; do not create a new task merely
to read a receipt. Permission to observe is not permission to stop workers.

### 5. Monitor by receipts

The coordinator watches for immutable result receipts, not conversational
claims or process completion alone. On receipt:

1. verify schema and every declared hash;
2. verify worker identity, namespace, input contract, and forbidden-action log;
3. classify `VALID`, `DIAGNOSTIC-ONLY`, `INVALID-FOR-ACCEPTANCE`, or
   `BLOCKED`;
4. preserve the raw log and sidecar;
5. continue only when the frozen prerequisite is satisfied.

If a worker reports a contract defect, stop acceptance/dispatch. Stop affected
workers only within the owner's authorized scope (otherwise request direction),
preserve their logs, and issue a versioned repair bundle. Do not let one worker silently patch
the shared contract.

### 6. Reconcile once

After all required worker receipts freeze, perform one distinct coordinator
reconciliation. Use the existing coordinator unless a new task is authorized.
Compare exact identity fields first, then per-field numerical tolerances. Use
the following outcome mapping:

```text
all valid + compatible + gate pass    -> canonical PASS/selection
all valid + compatible + gate failure -> scoped canonical BLOCKED
any invalid receipt                   -> VERDICT-NOT-ISSUED
any same-condition disagreement      -> DISAGREEMENT / counterexample needed
```

Never choose the least-bad result, widen tolerances after seeing results, or
re-run only the worker whose output is inconvenient.

## Automation boundary

Safe to automate:

- search, hash, schema, link, and namespace audits;
- staging-only code and local synthetic tests;
- bounded login-CPU tests explicitly allowed by the contract;
- receipt validation, deterministic comparison, and status rendering;
- continuation after a frozen prerequisite receipt within the authorized task;
  a new task still needs the product's task-creation authority.

Keep human-gated:

- contract, threshold, candidate, source, split, or claim changes;
- production-source edits and checkpoint promotion;
- Slurm/GPU/DFT/fit submission;
- sealed holdout release;
- canonical scientific promotion or branch reopening.

## Close and hand off

Before finishing, verify all paths and hashes from disk, update only the
canonical state owner, record the claim ceiling and exact next gate, and leave
the newest dispatch/status pointer at the top of the handoff. Keep historical
bundles and failed receipts immutable and linked as superseded or blocked.
