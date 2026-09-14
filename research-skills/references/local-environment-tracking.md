# Local Environment Tracking

Capture enough local runtime state to explain reproducibility changes without
dumping credentials, personal environment variables, or machine-specific
package URLs.

## Snapshot contract

The bundled tracker records:

- OS, architecture, processor, and NVIDIA GPU/driver/memory identity;
- Python implementation, version, sanitized executable, and conda/venv label;
- installed package count and a normalized `name/version` SHA-256;
- selected scientific package versions;
- versions and availability of Git, search, document, Node, and GPU tools;
- Git commit and dirty state for the target project;
- an allowlisted set of numerical/runtime controls.

It does not record the hostname, username, full `PATH`, arbitrary environment
variables, tokens, package download URLs, or full filesystem paths. Paths under
the project and home directory become `$PROJECT` and `~`; unrelated executable
paths retain only the final filename.

## Capture and compare

Write immutable timestamped snapshots to a project-owned evidence directory or
an explicitly chosen per-machine operations directory:

```bash
python <research-skills>/scripts/capture_local_environment.py \
  --project-root PROJECT \
  --output PROJECT/reports/environment/environment-YYYYMMDDTHHMMSSZ.json
```

Compare a later state with an accepted baseline:

```bash
python <research-skills>/scripts/capture_local_environment.py \
  --project-root PROJECT \
  --compare PROJECT/reports/environment/environment-BASELINE.json \
  --output PROJECT/reports/environment/environment-CURRENT.json
```

Use `--include-packages` only when a complete package name/version inventory is
required. The default stores its hash and core versions, which is smaller and
avoids accidental overcollection.

## Interpretation

- `fingerprint_sha256` identifies the normalized captured environment, not the
  scientific condition by itself.
- `comparison.match=true` means all captured fields match. It does not prove
  hardware nondeterminism, external services, datasets, or remote scheduler
  state are equivalent.
- A dirty Git tree is descriptive, not automatically invalid. Preserve the
  exact patch or commit before accepting a result.
- A changed package hash requires inspection of named differences through a
  controlled full inventory or environment manager lockfile.
- Never cite a mutable `latest.json` as evidence. Link the timestamped snapshot
  and its hash from the run receipt or immutable artifact.

Keep dependency lockfiles or container recipes as stronger reconstructive
owners. Use this snapshot as an observed-state witness and drift detector.
