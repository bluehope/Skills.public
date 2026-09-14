# Research Monitor And Dashboard Contract

## Contents

1. Purpose and authority
2. Information architecture
3. Status and gate semantics
4. Metrics and visual evidence
5. Provenance and safety
6. Generation and validation
7. Handoff checklist

## 1. Purpose And Authority

Use this contract for live computational-research monitors, recurring status
reports, and local HTML dashboards. Optimize the artifact for answering:

```text
What scientific question is active?
What evidence exists now?
What prevents the next decision?
What exact event will make the work ready?
```

Do not make a scheduler table the primary narrative. A job is an attempt; it
becomes scientific evidence only after its declared contract is validated.

Keep document ownership explicit:

- `LIVE-MONITOR` owns current jobs, freshness, blockers, and next gates.
- `EXPERIMENT-LEDGER` owns attempt and decision history.
- `EVIDENCE-ARTIFACT` owns reproducible metrics and pass/fail results.
- `DESIGN-SSOT` or `DECISION-RESEARCH` owns the scientific adoption rule.
- The dashboard is a rendered view over these authorities, not a new source of
  truth.

Keep current-state monitoring distinct from historical reasoning. When a human
needs to understand how many iterations led to the current direction, embed or
link the research trail defined in
`research-history-and-loop-visualization.md`; do not expand the scheduler table
into an improvised decision history.

## 2. Information Architecture

Present information in this order:

1. Current research objective, strongest supported conclusion, exact next
   decision, and claim ceiling.
2. Active frontier with mechanism verdict, promotion verdict, branch
   disposition, closure basis, blocker, and next gate kept separate.
3. A top-to-bottom chronological research trail or a link to the frozen trail.
4. One card or panel per research track, comparison family, or structure
   family.
5. The stage chain for each track, such as:

   ```text
   structure provenance -> relaxation -> electronic ground state
   -> perturbation/directional calculations -> derived observable -> decision
   ```

6. Current metric, target, distance or ratio to target, blocker, and next gate.
7. Evidence links: structures, force or convergence figures, logs, immutable
   artifacts, report, ledger, and source snapshot.
8. Decision log and then operational/scheduler log at the bottom.

Use low-cardinality filters that reflect scientific navigation, normally
research track, code/method, and scheduler state. Avoid filters that merely
expose incidental filenames or create dozens of one-item categories.

For each track, state an adoption rule before showing detailed status. Examples
include a matched comparison, a convergence threshold, a force criterion, or a
required downstream artifact. Keep project-specific thresholds in project
configuration or the design authority; do not hard-code them into this global
skill.

## 3. Status And Gate Semantics

Model operational and scientific states separately.

```text
operational: planned -> submitted -> pending -> running -> completed/failed
scientific:  unverified -> contract-valid -> gate-pass -> ready -> accepted
```

Within scientific state, do not collapse mechanism, promotion, and branch
disposition into one badge. A promotion failure may coexist with a supported
mechanism and an active or paused branch. Display `HARD-CLOSED` only when a
linked mathematical derivation or exact physical-law argument states its
assumptions and scope. Display intuition-led avoidance as
disposition `DEPRIORITIZED` with closure basis `HEURISTIC`, never as a permanent
prohibition.

Never infer `ready` from `COMPLETED`. A completed process can still have an
empty output, unconverged state, mismatched structure, stale restart, or failed
post-processing.

Every readiness claim must expose:

```text
metric identity / current value / target / comparator
pass rule / verified_at / source path / lineage or matched provenance
```

When an application exposes both an internal stopping criterion and an
independent scientific convergence metric, display and name both. Do not label
one as the other. For example, an electronic-energy stopping condition and a
density-residual acceptance gate are separate claims even when both are called
"SCF convergence" informally.

For a derived-observable stage, require all declared upstream gates. A typical
electronic-structure readiness contract may require:

```text
independent convergence gate passed
AND normal completion marker present
AND required binary/output artifact is nonempty
AND structure, method, spin/SOC, direction, and restart lineage match
```

For relaxation, evaluate the latest force on atoms allowed to move against the
force target defined by the actual input. Record fixed/free degrees of freedom
and whether the system has one or multiple periodic interfaces. Do not silently
include fixed atoms in the relaxation gate or assume a slab has only one
interface.

Use explicit reasons for `blocked`, `stalled`, `failed`, and `unknown`. Absence
of a recent log is not itself convergence failure; report it as freshness or
observability evidence with the applicable time window.

## 4. Metrics And Visual Evidence

Prefer small, decision-bearing figures over decorative plots.

- Plot iterative residuals against iteration on a logarithmic axis when the
  metric spans orders of magnitude. Draw and label the acceptance gate.
- Show latest value and target next to the plot; do not make the reader estimate
  readiness from a curve alone.
- For relaxation, show energy change and maximum movable-atom force. Add force
  vectors or highlight high-force atoms when that helps diagnose the next
  structural change.
- Link initial, selected/best, and latest structures when geometry lineage is
  material. Display fixed and free regions or degrees of freedom.
- When several methods have incompatible absolute reference energies, separate
  their panels. Compare within-method deltas or trends, not cross-code absolute
  energy per atom.
- Label proxy metrics as proxies and state what they cannot establish.

Use restrained scientific styling, readable units, stable colors for the same
state, and visible timestamps. A single overview figure may summarize the whole
campaign, but it must link to inspectable evidence for anomalous or blocking
cases.

## 5. Provenance And Safety

Build the report from a reviewed local snapshot or structured sidecar generated
from canonical sources. Include:

```text
snapshot time / remote host and absolute canonical path
job id and scheduler evidence / input and output paths
structure and restart lineage / parser or generator version
known omissions / freshness and collection failures
```

Do not issue live remote requests from browser JavaScript and do not embed
credentials, tokens, private keys, or environment secrets. Keep server-specific
binary paths, modules, queues, and launch commands in server profiles rather
than global dashboard rules.

Unless the user explicitly authorizes mutations, monitoring and report
generation are read-only with respect to remote compute: do not submit, cancel,
restart, rename, or edit remote jobs or files. Local snapshot, report, plot, and
HTML regeneration are allowed when they are the requested monitoring outputs.

Serve local dashboards on loopback by default. Do not publish or expose them to
the network without explicit authorization.

## 6. Generation And Validation

### Bundled local snapshot adapter

`research_state.py --project PROJECT refresh --observation observation.json
--dashboard` builds STATE, link/context/timeline lists and
`research_dashboard/views/index.html`. Without --dashboard it refreshes an
existing dashboard only. Plain `render` also refreshes an existing dashboard
from its last observation; it does not claim a fresh collection.

The existing project monitor/parser supplies a redacted JSON file, not a new
remote command runner. Top-level fields: `observed_at` (UTC ISO timestamp) and
`items`. Each item requires a registered `id`; optional fields are
`operational_status`, `scientific_status`, `adoption_status`, `blocker`,
`next_gate`, `metric`, `value`, `target`, `comparator`, `evidence`.
Absent values remain unknown. Labels are attributed adapter observations,
not automatic registry promotion. Unknown fields and obvious secret patterns
are rejected; this is not a guarantee of complete secret detection. Redact
before export and do not supply raw command output or credentials.

Example: `{"observed_at":"2026-09-12T10:00:00Z","items":[{"id":"A-1",
"operational_status":"COMPLETED","scientific_status":"UNVERIFIED"}]}`.
`refresh --collection-error` records a generic failure and retains the last
successful values and timestamp. Failed refresh inputs do not replace a valid
snapshot. Observation history is stored under research_dashboard/observations/.

Project schema `project` may contain `objective`, `supported_conclusion` and
`next_decision` for the dashboard; the project owner supplies these statements.
`monitor.poll_seconds` defaults to 300 and `stale_after_seconds` to three
intervals. The page reloads the local HTML every 60 seconds and ages its
freshness label locally; it never fetches remote scheduler state.

Refresh emits `notifications`, `continue_polling`, and `poll_seconds` for an
existing runtime scheduler/notification adapter. Schedule only when continuous
monitoring is requested; the command does not install timers or send messages.
Notify only terminal transitions, blocker/next-gate/science-state changes;
unchanged observations are quiet. Stop when continue_polling is false; null
means collection failed without enough state to decide, requiring review.
Existing RUNNING/PENDING work retains polling through collection failure.
Do not resubmit jobs or grant scientific acceptance automatically.

Serve via loopback (for example `python -m http.server --bind 127.0.0.1` from
the project root) and review the rendered page. Manifest hashes bind rendered
sources. Generated HTML and lists are not editable authorities.

Make generation reproducible and idempotent:

```text
collect/read authority -> normalize snapshot -> render report and figures
-> build static artifact -> browser QA -> record verified_at
```

For a file-safe or archival dashboard, render a second one-way static view from
the reviewed local snapshot after building the live view. Embed the displayed
values in a self-contained `index.html`; do not fetch remote state or rely on
browser-side module routing. Write a manifest with generator, source
path/hash, evidence cutoff, artifact hash, and the fact that the static page
is frozen. Rebuild it from the ordinary monitor command. Preserve unavailable
metrics as `unknown` or `—`, never zero, and keep scheduler state distinct from
scientific acceptance.

Integrate snapshot and dashboard regeneration into the existing read-only
monitor update when practical. Preserve historical rows in an append-only
history or immutable snapshots; do not cite a mutable `latest` file as evidence.

Before handoff:

1. Run the generator from a clean or explicitly recorded environment.
2. Verify structured data schema, timestamps, units, missing-value behavior,
   and links.
3. Build the production/static artifact, not only a development view.
4. Serve it locally and inspect the rendered page.
5. Check the title, research question, adoption rules, key counts, blocker
   paths, plots, filters, track tabs, and evidence links.
6. Check browser console errors and broken asset requests.
7. Confirm that an unavailable source becomes `unknown` or `collection-error`,
   never a fabricated zero, success, or stale current value.

## 7. Handoff Checklist

Report:

- the local dashboard/report path and loopback URL, if running;
- the command that refreshes data and the command that opens or serves it;
- the evidence cutoff and last verified timestamp;
- the most important current blocker and exact next gate;
- validation performed and any known limitations;
- whether the operation was read-only and whether anything remains running
  locally.

Promote a project-specific reporting policy into this global contract only
after it survives repeated use, has a stable scientific meaning across projects,
and removes rather than introduces hidden assumptions. Keep code-specific
parsers, thresholds, server paths, and campaign names in the relevant project,
DFT-code, or server skill.
