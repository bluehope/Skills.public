# Temporary Policy Lifecycle

## Contents

1. Why temporary policies exist
2. Two separate state machines
3. Pilot operation
4. Promotion gate
5. Promotion procedure
6. Archive procedure
7. Rejection and later revision

## 1. Why Temporary Policies Exist

Create a project-local temporary policy when a repeated workflow needs a
written contract but evidence is insufficient for a global rule. Its purpose
is to reduce memory dependence while allowing controlled revision.

Do not confuse a project-local skill with a temporary policy. A project-local
skill can be the permanent, first-class canonical owner for behavior whose
correct scope is one project. It does not need global promotion to become
complete or legitimate; promote only when cross-project generalization is a
separate demonstrated benefit.

Examples include structure/data intake, report organization, evaluator choice,
job monitoring, and artifact naming. Do not hide an unresolved scientific
decision inside a procedural policy.

## 2. Two Separate State Machines

Research packet status:

| State | Meaning |
|---|---|
| `PARTIAL` | useful information exists; declared fields or gates are missing |
| `BLOCKED` | exact external decision/resource is required before progress |
| `READY` | packet satisfies its declared downstream gate |
| `REJECTED` | unsuitable for the declared purpose; reason and provenance retained |

Policy lifecycle:

| State | Meaning |
|---|---|
| `DRAFT` | proposed, not yet governing work |
| `PILOT-ACTIVE` | project-local rule currently used |
| `PILOT-REVISED` | evidence forced a recorded policy change |
| `PROMOTION-CANDIDATE` | generalization gates pass; awaiting owner approval |
| `PROMOTED` | generalized rule landed in the global skill |
| `ARCHIVED` | frozen pilot and promotion record stored; old live path is a pointer |
| `REJECTED` | policy did not generalize; evidence preserved |

A packet becoming `READY` does not automatically promote its governing policy.

## 3. Pilot Operation

The temporary policy records:

- policy ID, owner, creation/verification date, scope, canonical path;
- problem and reason a global rule is premature;
- included/excluded objects and forbidden interpretations;
- packet status definitions and hard gates;
- source/evidence locations and negative evidence;
- iteration ledger: change, evidence, verdict, missing fact, next gate;
- intended global target and archive location.

Keep the policy close to the project hub or input owner. Do not store it as a
chat summary or in a results directory.

## 4. Promotion Gate

Mark `PROMOTION-CANDIDATE` only when all are true:

1. The policy was used in at least two independent packets/campaigns, or one
   repeated high-risk workflow with a written justification.
2. At least one realistic failure, rejection, or revision tested the status and
   correction rules; a frictionless toy pass is insufficient.
3. Every state has an operational definition and an exact next gate.
4. Canonical ownership, provenance, link, and archive behavior worked without
   relying on chat memory.
5. Project-specific names, paths, chemistry, hardware, and thresholds can be
   removed while preserving the useful rule.
6. Exceptions and non-goals are known.
7. A second reader or fresh session can resume from files alone.
8. The policy owner approves mutation of the global skill.
9. If canonical and runtime-installed skill copies differ, the activation
   target and synchronization method are declared before promotion closure.

If these do not pass, keep the policy project-local and record the missing gate.

## 5. Promotion Procedure

1. Freeze the pilot's evidence cutoff and final iteration verdict.
2. Extract the smallest general rule; keep project examples in references, not
   the core workflow, unless they are indispensable.
3. Update the global skill's `SKILL.md`, relevant reference, and template.
4. Validate the skill and forward-test it on a fresh realistic task when safe.
5. When a separate runtime-installed copy exists, synchronize it from the
   canonical source, record both paths and hashes, validate both trees, and
   verify discovery in a fresh runtime.
6. Create a promotion record containing old/new paths, evidence, exclusions,
   approver, date, canonical/installed hashes, activation result, and
   validation debt.
7. Update project links and retain project-specific exceptions in the living
   project design document.
8. Mark the temporary policy `PROMOTED`, then archive it.

## 6. Archive Procedure

Use a recoverable project path such as:

```text
archive/policies/<policy-id>/<YYYY-MM-DD>/
```

Archive the final policy, iteration ledger, promotion record, relevant hashes,
and link map. Do not duplicate large evidence; link immutable artifacts.

At the old live path, leave a thin pointer containing:

```text
PROMOTED TO: <global skill path and section>
ARCHIVED AT: <frozen project snapshot>
PROJECT EXCEPTIONS: <living project owner>
PROMOTED/ARCHIVED: <date and approver>
```

The archived copy is read-only. Never silently continue editing it. A new
policy revision gets a new version/ID and explicit lineage.

Do not delete rejected sources, failed attempts, correction history, or the
reason the policy changed. Archive means preserved and inactive, not disposable.

## 7. Rejection And Later Revision

If the pilot does not generalize:

- mark `REJECTED` with reason and evidence;
- leave the global skill unchanged;
- archive the rejected policy or retain it as a project-specific exception;
- create a new policy ID if a materially different approach is tried.

If a promoted rule later fails, correct the global rule in place, cite the new
evidence, and supersede rather than rewrite the archived pilot history.
