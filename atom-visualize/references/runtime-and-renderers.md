# Runtime and Renderer Compatibility

Read this reference only when installing or changing visualization packages,
choosing an optional renderer, or diagnosing runtime/export failures. Shared
package versions are recorded in `$scientific-figure-making`'s
`references/runtime-baseline.md`; do not duplicate that full inventory here.

## Environment policy

Dated runtime records may describe different machines with the same environment
name. Verify interpreter, ABI and package source here before reusing a recipe;
a shared Dropbox note is not proof of this machine's pip/conda installation.

- Recommend conda environment `codex` for supported common work. Python 3.12,
  3.13, and 3.14 are acceptable when the selected packages pass their smoke
  tests; a version number alone is not proof of compatibility.
- Before installing, run the applicable runtime-doctor profile and inspect the
  existing environment. Do not reinstall a package that already passes.
- Invoke pip through the target interpreter:
  `python -m pip ...`. Do not rely on an unqualified `pip`.
- For a proposed pip change, prefer `pip install --dry-run ...` first. Pin the
  direct package being introduced, record the command and versions, then run
  `python -m pip check` and the applicable smoke test.
- Do not mix pip and conda builds of the same renderer in one environment. Do
  not repair a shared environment by layering a second distribution on top.
- A successful import is insufficient. Verify a representative conversion and
  a real nonblank export before declaring the renderer ready.

## Function to code index

| Function | Canonical implementation | Invocation |
|---|---|---|
| Core ASE/Matplotlib readiness | this skill's `scripts/figure_runtime_doctor.py` (shared implementation) | `--profile core --smoke` |
| OVITO import, structure identity, and render | same runtime doctor | `--profile ovito --smoke` |
| Atom-specific ASE↔OVITO round-trip | `tests/ovito_structure_smoke_test.py` | run with conda `codex` |
| Trajectory frames and movies | `$atom-trajectory-visualize` | follow its runtime contract |

If project code already wraps one of these functions, inspect whether it adds a
real project-specific contract before creating another wrapper.

## Core static route

ASE and Matplotlib in conda `codex` are the default for structure inspection and
batch side views. Verify them with:

```bash
python \
  <atom-visualize>/scripts/figure_runtime_doctor.py --profile core --smoke
```

Use VESTA or 3Dmol.js when the requested interaction or spin-vector format makes
them the narrower fit. These routes do not justify installing Crystal Toolkit.

## OVITO

As verified on 2026-09-07, conda `codex` uses standard CPython 3.14.7 (`cp314`)
with the official `conda.ovito.org` package `ovito==3.16.0`. The installation
also provides `ospray_ovito` and `anari_ovito`; Qt/PySide dependencies remain on
conda-forge. ASE↔OVITO identity and headless Tachyon PNG rendering pass.

The environment was previously free-threaded (`cp314t`). Installing the official
OVITO conda package normalized it to standard CPython 3.14 because the solver
selected the supported binary ABI. Record this as an environment mutation and
rerun both smoke tests after any future Python/NumPy/Qt/OVITO change. Run:

```bash
python \
  <atom-visualize>/tests/ovito_structure_smoke_test.py
python \
  <atom-visualize>/scripts/figure_runtime_doctor.py --profile ovito --smoke
```

For a fresh conda/Miniforge environment or recovery after regression, the
official OVITO route is:

```bash
conda install --strict-channel-priority \
  -c https://conda.ovito.org -c conda-forge ovito=3.16.0
```

The similarly named conda-forge-only package is OVITO Basic and does not provide
the Python module. Confirm the source channel with `conda list`. Do not layer a
PyPI OVITO wheel over this conda installation. Use pip only when the user
explicitly requests that route or a separate non-conda interpreter must be
supported:

```bash
conda run -n <env> python -m pip install --dry-run 'ovito==3.16.0'
conda run -n <env> python -m pip install 'ovito==3.16.0'
conda run -n <env> python -m pip check
```

After Python, NumPy, Qt/PySide, or OVITO changes, rerun both OVITO smoke tests.
On failure, do not hide warnings or add ad hoc Qt pins. Capture the error and
installed versions, then replace the installation cleanly with the official
conda package or move OVITO to a dedicated environment. Follow the
[official installation guide](https://www.ovito.org/docs/current/python/introduction/installation.html)
for current commands.

## Crystal Toolkit / Dash

Treat this as an optional interactive stack, not part of common conda `codex`.
A previously tested compatibility recipe used standard CPython 3.13 in
`codex-ct`, Crystal Toolkit 2026.7.20, pymatgen 2026.5.4,
`pymatgen-core==2026.4.16`, Dash 3.4.0, and Flask-Caching 2.5.0. This is a dated
recipe, not evidence that the environment still exists or remains current.

Before reuse, verify imports and instantiate one
`StructureMoleculeComponent` with vector `magmom`. If the installed Crystal
Toolkit expects `StructureGraph.with_*` while pymatgen exposes only `from_*`,
prefer a known-compatible version pair. Add a narrowly scoped startup alias only
when pinning is impractical and the exact failing call has been reproduced.

## Change receipt

For any runtime mutation, retain:

- environment name, Python version and ABI;
- package manager, exact command, direct package version and source channel;
- `pip check` or conda consistency result;
- applicable smoke-test command and result;
- unresolved warnings and the recovery route.

Runtime readiness proves only that the toolchain executes. It does not validate
structure identity, magnetic provenance, scientific interpretation, or final
figure quality beyond the explicit smoke-test assertions.
