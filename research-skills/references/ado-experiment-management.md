# Optional ado Experiment Management

## Contents

1. Role and recommendation gate
2. Choose an adoption mode
3. Initialize the project workspace
4. Preserve authority and evidence boundaries
5. Control result reuse
6. Operate and hand off safely

Apply
[structured-experiment-campaigns.md](structured-experiment-campaigns.md) first;
it owns the ado-independent experiment contract, resolved plan, coverage,
metric identity, result-origin vocabulary, and verified-catalog promotion gate.
This reference owns only ado suitability, workspace, storage, and integration
constraints.

## 1. Role And Recommendation Gate

Treat IBM `ado` as an optional experiment registry, query layer, and campaign
orchestrator. Do not make it a prerequisite for research-skills and do not
recommend it merely because a task contains experiments.

Assess ado when a campaign has several of these properties:

- the same stable experiment interface will be applied to many parameter
  points, entities, seeds, structures, checkpoints, or datasets;
- inputs and outputs fit a durable typed schema;
- runs are mostly independent or can be imported as independent measurements;
- cross-run queries, comparisons, or result sharing are recurring needs;
- avoiding condition-equivalent recomputation has material value;
- multiple people or agents need a shared, queryable campaign view.

As a heuristic, recommend ado when at least four properties apply or when one
property has exceptional value, such as avoiding very expensive duplicate
measurements. A campaign with roughly 20 or more comparable points is a useful
signal, not a hard threshold.

Prefer the existing research-skills workflow without ado for one-off bespoke
calculations, rapidly changing experiment contracts, large binary artifacts,
checkpoint-heavy Slurm DAGs, or campaigns where scientific gatekeeping matters
more than repeated querying.

When recommending ado, tell the user:

1. which concrete campaign property makes ado useful;
2. which adoption mode is proposed;
3. what ado will and will not own;
4. the setup, database, migration, and maintenance cost;
5. the smallest reversible pilot.

Do not install ado, provision a database, create a context, initialize the
project workspace, or import results until the user accepts the recommendation.

## 2. Choose An Adoption Mode

Choose the least expansive mode that provides the benefit.

| Mode | Use | Execution owner | ado role |
|---|---|---|---|
| `catalog` | Existing or planned external runs | Slurm, `hpc-skills`, or another runner | Import/replay, query, comparison |
| `local-active` | Single-user structured campaign | Local ado operator/actuator where suitable | Registry, execution, Sample Store |
| `shared` | Multi-user or remote-agent campaign | Shared ado-compatible infrastructure | Shared MySQL metastore and Sample Store |

Default the first pilot to `catalog`. Keep Slurm as the execution authority and
import small structured results into ado. Do not replace a working scheduler or
production workflow merely to adopt ado.

## 3. Initialize The Project Workspace

After the user accepts ado for a project, initialize the workspace with:

```bash
python <research-skills>/scripts/init_ado_workspace.py <project-root> \
  --mode catalog
```

Use `--ado-project` and `--context-name` only when their values are known. The
initializer creates missing files and directories but never overwrites an
existing file. If `<project>/ado/` already exists, inspect its manifest and
receipts before adding or changing anything.

Use this project-local layout:

```text
<project>/ado/
  ADO.md
  ado-project.yaml
  .gitignore
  configs/
    actuators/
    operations/
    samplestores/
    spaces/
  imports/
  exports/
  receipts/
    RECEIPT-TEMPLATE.yaml
```

- `ADO.md`: navigation, decision status, authority boundary, and current use.
- `ado-project.yaml`: secret-free ado mode, project/context locator, storage
  policy, Sample Store, reuse rule, and canonical artifact pointers.
- `configs/`: exact reviewed YAML inputs. Use stable names or immutable IDs;
  do not cite a mutable `latest` configuration.
- `imports/`: replay/import mappings and source manifests with hashes. Keep
  large source data at its canonical artifact location.
- `exports/`: timestamped resource, measurement, and relationship exports plus
  checksums. Treat exports as recovery snapshots, not a second editable truth.
- `receipts/`: commands, versions, resource IDs, fingerprints, result origins,
  artifact links, and scientific disposition.

Do not put context credentials, tokens, live SQLite databases, caches, or
temporary execution files in this directory. In particular, keep live SQLite
outside Dropbox or another synchronized tree.

## 4. Preserve Authority And Evidence Boundaries

Keep the following ownership split:

```text
research-skills: hypothesis, contract, claim ceiling, gate, acceptance
ado: structured experiment definition, operation, measurement index, query
immutable artifacts: raw outputs, logs, configs, hashes, accepted metrics
```

An ado operation with `success` is operationally complete, not scientifically
accepted. Do not promote a claim from an ado status alone. Keep `STATE.md`, the
living `DESIGN-SSOT`, the `EXPERIMENT-LEDGER`, and immutable evidence artifacts
canonical; link to them from `ado/ADO.md` and receipts.

Do not make the ado database the sole copy of evidence. Before accepting an
ado-managed result, export or otherwise preserve the exact operation and space
definitions, measurements, resource relationships, ado-core/plugin versions,
and links to hash-bound raw artifacts.

Store scalar metrics, small tables, identifiers, and artifact locators in ado.
Keep checkpoints, trajectories, wavefunctions, raw logs, and other large
artifacts in their existing immutable storage.

## 5. Control Result Reuse

Classify every consumed result as one of:

```text
DIRECT         measured by the current accepted operation
REUSED-EXACT   reused after full condition-fingerprint equality
MATCHED        found by ado similarity or looser memoization
EXTERNAL       imported from a non-ado execution path
```

`DIRECT` and verified `REUSED-EXACT` may enter a confirmatory or promotion gate
without remeasurement. `EXTERNAL` may enter only after its source manifest,
condition fingerprint, immutable output, and original execution receipt pass
the same contract. `MATCHED` is a candidate locator, not accepted evidence.

Do not infer exact reuse from an experiment name, resource ID, `latest`, or
major semantic version. Compare at least:

```text
experiment implementation and code commit
ado-core and plugin versions
input data/artifact hashes
fully resolved configuration and representation contract
environment/container and numerical flags
seed policy, split, metric identity, tolerance, and evidence cutoff
```

Disable memoization for confirmatory and promotion work unless this full
fingerprint has been demonstrated equivalent and recorded in the receipt.

## 6. Operate And Hand Off Safely

- Prefer one shared Sample Store within a coherent reuse/trust boundary.
  Separate stores only for incompatible ontology, access, retention, or trust
  policies; creating a store per Discovery Space prevents useful sharing.
- Use SQLite for a local reversible pilot and MySQL for genuine shared access.
  Keep the context secret outside the repository and record only its local
  context name or secret-free locator.
- Back up the database and test restore before upgrades. Preserve timestamped,
  hash-recorded exports because ado resource and Sample Store formats may
  evolve.
- Never delete failed or negative scientific evidence through ado maintenance.
  Reconcile ado cleanup with the experiment ledger and archive policy first.
- At handoff, state the ado mode, context name, database owner, Sample Store ID,
  last verified export, unresolved fingerprint mismatches, and the exact next
  scientific gate.
