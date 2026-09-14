# Registration Checklist

Maturity: `EXPERIMENTAL` automation over active evidence/provenance principles.
Projects opt in through `registration_receipts`; a mechanical PASS does not
promote a claim or waive human scientific review.

Use this contract immediately before a RESULT/EVIDENCE artifact, catalog
entry, portfolio row conclusion, or research-figure registry entry becomes an
accepted source for downstream work. Copy
`assets/registration-checklist-template.md` into the project and complete its
frontmatter; do not copy this prose into each registration template.

## Deterministic gate

The project document-audit policy lists completed receipts under
`registration_receipts` and, when references are used, names one
`stable_id_registry` created from `assets/stable-id-registry-template.json`.
The core validator blocks registration when:

- a declared `reference_id` is blank, equals `candidate_id`, or is absent from
  the stable-ID registry;
- core field `candidate_id`, `consumer_id`, or `condition_fingerprint` is
  blank;
- `condition_fingerprint` is not `sha256:<64 hexadecimal characters>`;
- a reference is declared and its `reference_litmus`, `observable_id`, or
  `unit_id` is blank;
- the reference-litmus path does not exist;
- the receipt's observable or unit conflicts with a value declared for the
  reference registry entry;
- a checklist field is absent or carries a failing value.

Workflow-specific profiles may additionally require fields such as shape,
cell identity, Slurm job ID, or artifact path. A profile requirement is a
mechanical gate only when the project policy declares that profile.

## Human boundary

Code verifies declarations, exact identifiers, paths, and fingerprints. A
person decides whether differently named observables are scientifically
equivalent, whether a threshold is physically justified, and how to interpret
a new failure. Record those as `SEMANTIC-WARN` candidates; an LLM or person may
not convert a mechanical BLOCK into PASS without correcting the receipt or its
source evidence.

The human-readable five-line checklist is a view over the structured
frontmatter. The validator reads the fields, not prose or Markdown table
semantics.
