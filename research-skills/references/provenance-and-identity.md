# Provenance And Identity

## Contents

1. Status labels are claims, not evidence
2. Three failure classes: data, label, pointer
3. Resolve identity by content, never by name
4. Verify in the consumption context
5. Derived-artifact reproducibility (pointer to the canonical owner)
6. Harness reuse: inherit and patch, do not reimplement

## 1. Status Labels Are Claims, Not Evidence

The authority order (`immutable artifact + executed code > living decision >
frozen report > context cache > chat memory`) ranks *artifacts*. A status
marker — `DEPRECATED.md`, `SUPERSEDED`, `DO-NOT-USE`, a `status:` field — is
not an artifact in that ladder. It is a **claim about** an artifact, written by
someone at some time for some purpose.

On meeting a status label:

1. **Measure what it asserts.** If it says "imaginary modes, +14% at Γ", read
   the array and check. A label whose claims verify is trustworthy about *what
   it measured*; one whose claims fail is stale or misfiled.
2. **Look for its scope.** Which uses does it forbid? A label without a scope
   is under-specified, and neither obeying nor ignoring it is defensible.
   Resolve by measurement, not by deference.
3. **Do not oscillate.** Blocking on an unread label and then unblocking under
   push-back are the same error twice: both substitute a posture for a
   measurement.

When *writing* a label, always record the scope and the evidence:

```text
SCOPE: invalid for <use A>; valid for <use B>. Basis: <measurement, date>.
```

An artifact can be simultaneously unfit for one role and canonical for another.
"Deprecated" without a role is not a decidable statement.

## 2. Three Failure Classes: Data, Label, Pointer

When a record and reality disagree, enumerate all three before repairing any:

| Class | Meaning | Repair target |
|---|---|---|
| **Data error** | the artifact itself is wrong | the artifact / a rerun |
| **Label error** | the marker's claims do not verify | the marker |
| **Pointer error** | data and label are both correct, but a ledger/index/card **names the wrong artifact** | the pointer |

Pointer errors are the easiest to misdiagnose, because the symptom (a document
disagreeing with a measurement) is identical in all three classes. A campaign
can run correctly for weeks while its own ledger names a discarded lineage.

Rule: **do not edit anything until the class is decided.** Deciding requires
measuring the artifact the pointer names *and* the artifact actually consumed,
and comparing both to the record.

## 3. Resolve Identity By Content, Never By Name

File names, directory names and run labels are mnemonics. They are written by
hand, copied, and reused; they drift from what they contain.

- Establish identity from **content**: a hash, a coordinate, a header field, a
  reproduced anchor value.
- Treat `<thing>_q9/` or `run_v3_final/` as a hint for *where to look*, never as
  the key itself.
- Record identity in documents as **hash first, path second**: paths are how
  you reach it, hashes are what it is. When copies are byte-identical, say so
  and designate one path as a pointer.

This is distinct from the context-cache fingerprint rule (which keys *claims*
by their conditions). This rule governs **reference resolution**: deciding which
object a name denotes.

## 4. Verify In The Consumption Context

An artifact's format contract must be checked in the environment where it will
be **consumed**, not where it was produced. A file that renders correctly inside
one host may be malformed on its own.

Check separately:

- **Dependency closure** — does it reference anything outside itself?
- **Envelope completeness** — does it carry the structure its standalone consumer
  requires (declarations, encoding, containers), or does a host supply that?

These are different properties and passing one does not imply the other.
Name them separately in reports; "self-contained" is not "standalone".

When the same content is delivered through two channels, record which envelope
each carries and which one is canonical.

## 5. Derived-Artifact Reproducibility

The lifecycle vocabulary for derived artifacts (`REPRODUCIBLE` /
`PRESERVED-ONLY` / `MISSING`), the registry fields, and the rule that a status
is never upgraded merely because a plausible script exists are owned by
[research-figure-reproducibility.md](research-figure-reproducibility.md).
Use that vocabulary verbatim; do not coin synonyms such as "regenerable".

Two points this document adds, because they are provenance rather than plotting:

- **Persist the generator at creation.** Retrofitting one to an existing
  artifact usually fails, and a reconstructed generator produces a different
  artifact — which is why a status is not upgraded on the strength of a
  plausible script.
- **Cite by status.** A `PRESERVED-ONLY` artifact may be shown but not cited as
  reproduced evidence; cite its structured inputs instead.

## 6. Harness Reuse: Inherit And Patch, Do Not Reimplement

When extending a validated computation, **inherit the accepted harness verbatim
and apply the smallest possible patch**, rather than reimplementing its logic.

```text
inherit lines 1..N of the accepted source   (the harness boundary)
apply the minimal diff (parameterize, expose, widen)
append your own driver
```

Two properties follow, and both are load-bearing:

1. **Known anchors reproduce bit-exactly.** Any documented value the harness
   already produced must come back identical. This is a far stronger check than
   agreement to a tolerance.
2. **Failure to reproduce becomes a detector.** If an anchor misses by a small
   but non-floor amount, the cause is a changed *condition* — a different input
   lineage, a rebuilt payload — not a coding difference. A reimplementation
   would have absorbed that signal into its own approximation noise.

Record the harness source hash, the exact patch, and the anchor comparison in
the result document. State the harness boundary (which lines were inherited) so
the patch is auditable.

Verify anchors **before** interpreting any new value the extension produces.
An extension whose anchors do not reproduce is not evidence about anything.

## Domain Vocabulary

When discussing where a method or pipeline "works", distinguish three levels
and name the one you mean: **defined** (mathematically well-posed there) ≠
**supported** (the pipeline is validated there) ≠ **required** (the
production consumer enumerates it). Claims inherit the narrowest applicable
level; see evidence-and-validation §2a for the contract fields.
