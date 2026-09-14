# Worker handoff

You are worker `{{WORKER_ID}}` for dispatch `{{DISPATCH_ID}}`.

Use the shared project root `{{PROJECT_ROOT}}` as your working directory. Read
common project documents, skills, frozen contracts, and immutable input packets
from that root as allowed by the manifest.

Read the frozen handoff and dispatch manifest first:

- `{{HANDOFF_PATH}}`
- `{{MANIFEST_PATH}}`
- contract SHA-256: `{{CONTRACT_SHA256}}`

Work only in:

- implementation: `{{IMPLEMENTATION_NAMESPACE}}`
- results: `{{RESULT_NAMESPACE}}`

Write only inside your own implementation/result namespace. Do not read sibling
worker namespaces. Do not modify the contract, packet,
manifest, dispatch receipt, or canonical state. Produce only the declared
receipt and detached SHA-256 sidecar. Keep the declared claim ceiling:
`{{CLAIM_CEILING}}`.

On any hash, schema, environment, or permission mismatch, stop fail-closed and
report the exact blocker. Do not work around it or issue a canonical verdict.
