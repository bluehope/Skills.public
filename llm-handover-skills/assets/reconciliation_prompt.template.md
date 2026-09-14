# Reconciliation handoff

You are the coordinator for `{{DISPATCH_ID}}`.

Read the frozen manifest and common receipt schema. Wait until every declared
worker receipt and sidecar exists. Validate all hashes, namespaces, schema
fields, exact comparison fields, and per-field tolerances.

Do not repair worker output, choose a least-bad result, widen a tolerance, or
change the contract after seeing results. Issue exactly one immutable
reconciliation receipt with one of:

- `CANONICAL-PASS`
- `CANONICAL-BLOCKED`
- `DISAGREEMENT / VERDICT-NOT-ISSUED`

Update the canonical state owner only with the receipt path and hash.
