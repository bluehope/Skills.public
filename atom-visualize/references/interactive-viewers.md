# Interactive viewers and VESTA export

Read for Crystal Toolkit/Dash, VESTA vectors or HTML/3Dmol production. Use the
selected route; do not install all viewers. Examples resolve actual skill roots.

## Crystal Toolkit/Dash workflow

1. Convert each selected `POSCAR`/`CONTCAR` to `pymatgen.Structure`.
2. Attach relaxed `magmom` as a site property only when sourced from the final OUTCAR.
3. Instantiate `crystal_toolkit.components.StructureMoleculeComponent` with VESTA colors, unit cell, controls, export, and a declared bonding strategy.
4. Use a manifest/table as the single selector source for structure identity,
   state, stage, source path, selected metadata, and remote provenance.
5. Register the component with `ctc.register_crystal_toolkit(app, layout=...)` and use Dash callbacks to replace the component data.
6. For production, cache expensive graph generation and run behind Gunicorn; for local work, `python app.py` is sufficient.

Crystal Toolkit is optional and may require a dedicated environment. Do not add
`StructureGraph.with_*`/`from_*` aliases speculatively: reproduce the failing
call, record versions, and keep any necessary alias local to the affected app.
Consult [runtime and renderer compatibility](runtime-and-renderers.md)
for the dated tested recipe and upgrade rules.

Crystal Toolkit accepts scalar or vector `site_properties["magmom"]`; use the
vector form for spin arrows when the source is a collinear final OUTCAR. This
viewer capability does not expand the scientific claim to noncollinear order,
and Materials Project magnetic-property records should still be treated as
collinear/scalar database evidence. Retain a static, provenance-labelled
matplotlib/VESTA/3Dmol artifact for reports and archival handoff.

## VESTA workflow

- Write fractional coordinates in `STRUC` and Cartesian spin vectors in `VECTR`.
- Emit `VECTT` styles for each vector and include cell, atom display, and scene sections.
- Keep one `.vesta` per structure/state; do not overwrite distinct magnetic-state files.
- Validate that vector count equals the number of moments above threshold and that atom indices are 1-based.

## HTML/3Dmol and MP-style workflow

- Inline CIF/XYZ data or reference a controlled local asset; use 3Dmol.js spheres, sticks, unit cell, and `addArrow` for spins.
- Add only filters backed by the manifest, such as structure family, layer
  count, spin order, reference status, and stage.
- Keep a static HTML hub for sharing and a Dash app for callbacks/data updates; a Dash app cannot become a fully offline static HTML without replacing its callbacks.
- Use a fixed camera, element color scheme, and atom radii across comparison panels.
