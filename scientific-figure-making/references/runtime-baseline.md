# Scientific Figure Runtime Baseline

Verified on 2026-09-05 in conda environment `codex` with CPython 3.14.7.

| Capability | Packages verified |
|---|---|
| core static | NumPy 2.5.2, Matplotlib 3.11.1, Pillow 12.3.0, ASE 3.29.0 |
| publication | Seaborn 0.13.2 |
| trajectory | ImageIO 2.37.4, imageio-ffmpeg 0.6.0 |
| interactive/static export | Plotly 7.0.0, Kaleido 1.4.0 |
| atomistic 3D | OVITO 3.16.0, Traits 7.1.0, PySide6 Essentials 6.10.3 |

The optional packages in this historical snapshot were installed through the
environment's own Python; these are provenance commands, not a reinstall recipe:

```bash
python -m pip install \
  seaborn imageio imageio-ffmpeg 'plotly==7.0.0' 'kaleido==1.4.0'
python -m pip install 'ovito==3.16.0'
```

Validate the environment rather than trusting this dated snapshot. Resolve the
runtime doctor from this skill root. Select the needed profile for ordinary work;
the all-profile audit below is only for a requested full environment check:

```bash
python -m pip check
python scripts/figure_runtime_doctor.py --profile all --smoke
```

The smoke test verifies Matplotlib PNG/PDF, ImageIO/FFmpeg MP4, Plotly/Kaleido
PNG export, and the ASE/OVITO structure round-trip plus headless Tachyon PNG in
a temporary directory. It does not validate scientific content or final layout.

Later OVITO installation/recovery guidance is owned by atom-visualize's
`references/runtime-and-renderers.md` (2026-09-07 official conda record).
Resolve that skill root; do not layer the old wheel over an installed conda
package. Inspect this machine's package source before choosing any change.

At the historical snapshot above, the PyPI OVITO wheel imported and rendered successfully on macOS ARM64 with
CPython 3.14.7. OVITO itself warns that a pip installation inside conda can
conflict with existing Qt libraries. Treat this as a verified-but-monitored
exception: do not suppress the warning, and rerun the `ovito` smoke profile
after Python, Qt, NumPy, or OVITO changes. If it regresses, prefer OVITO's
official conda channel or a dedicated environment instead of patching around a
Qt conflict.
Use OVITO's [official installation guide](https://www.ovito.org/docs/current/python/introduction/installation.html)
as the authority when changing installation route.

pymatgen, Crystal Toolkit, and Dash remain outside the shared baseline. Use a
dedicated compatibility environment when one of those stacks is required, and
record its Python ABI and package versions.
