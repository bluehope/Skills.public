# Prepare and dispatch a bounded worker

Read for a new/revised dispatch, not to inspect a known receipt. Assets resolve
from this skill root. Task creation and process launches still require the
current product's permissions; a manifest cannot grant them.

## Shared project-root policy

When workers need the same local documents, run them from the same declared
`project_root` rather than copying the project into separate incomplete trees.
The project root is a shared read context, not a shared write context.

Declare three path classes in the manifest:

- `shared_read_roots`: project hub, current state, living design, skills,
  frozen contracts, and immutable input packets;
- `worker_write_root`: the worker's own implementation, logs, temporary files,
  and result namespace;
- `forbidden_read_roots`: sibling implementation/result namespaces and hidden
  evaluation data.

Workers may read common local documentation and frozen inputs from the same
project root. Workers may write only inside their own namespace. Canonical
documents, manifests, contracts, dashboards, and another worker's files are
read-only or forbidden according to the manifest. A path check must run before
any write and fail closed on an escape.

For a non-Git Dropbox project, prefer one shared local project root with
namespace-level write isolation. For a Git repository, a worktree can add
code-state isolation, but it must not silently omit the shared documents that
the handoff requires. On KIAS, use a common read-only source mirror plus a
separate temporary directory per worker.

## Workflow

### 1. Recover authority

Start from the named bundle/receipt or current-state capsule. Follow only the
contract, inputs and project instructions needed by this worker; the hub,
design and registry are locators, not a compulsory preload. Use bounded exact
search when a path is unknown. Verify/hash every declared dependency from disk.

### 2. Create the dispatch bundle

Create one immutable manifest containing:

- coordinator and worker IDs;
- contract, input packet, schema, and dependency paths plus hashes;
- local and remote namespace for every worker;
- exact receipt and sidecar filenames;
- allowed tools and execution environment;
- forbidden paths/actions;
- comparison fields and per-field tolerances;
- canonical verdict owner and next gate.

Use the templates in `assets/`. Do not put secrets, tokens, or mutable
`latest` paths in a scientific bundle.

### 3. Validate before dispatch

Run JSON/YAML syntax checks, dependency hash checks, namespace collision checks,
and schema satisfiability checks. For JSON Schema, verify both:

- every object's `required` key exists in that same object's `properties`;
- a full positive fixture passes and targeted negative fixtures fail.

Do not treat JSON parse success as schema validity. If a schema is impossible,
mark the dispatch `CONTRACT-BLOCKED`, preserve it, and issue a new versioned
bundle; never edit a consumed bundle in place.

### 4. Dispatch workers

For Codex, reuse an appropriate authorized task or create a new one only when
the user/product permissions allow it. Supply the worker prompt and namespace. For Claude Code, use a non-interactive invocation only after
authentication:

```bash
claude -p --output-format json --max-turns 20 \
  --permission-mode plan "$(cat worker_prompt.md)"
```

Prefer explicit `--allowedTools` and `--disallowedTools` settings. Do not use
`--dangerously-skip-permissions` for research handoffs. Store stdout, stderr,
session ID, exit status, and result receipt in the worker namespace.
Set the process working directory to the declared `project_root`; do not use a
worker result directory as the only working directory if that would hide the
common project documents.

## Codex task handoff

The coordinator prompt must name the task ID, role, handoff path, frozen bundle
hash, namespace, expected receipt, forbidden sibling paths, claim ceiling, and
the exact stop condition. Ask the task to report paths and hashes, then stop.

## Claude Code handoff

Before launch, verify `command -v claude`, `claude --version`, and
`claude doctor`. Authentication is a prerequisite, not evidence of scientific
completion. Launch from the declared project_root; use the worker namespace as the write
boundary, not as a substitute that hides shared documents. Use a prompt file, JSON output, bounded turns, and a log path.

Do not pass the sibling worker's result into the prompt. If the CLI is missing,
install it only with the user's authorization and verify the installation
before dispatch.
