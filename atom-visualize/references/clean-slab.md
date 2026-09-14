# clean-slab — default static publication slab view

User-selected visual preset, 2026-09-07. Applies to static slab side views,
not to bulk, molecular bonding diagrams, interactive viewers or trajectories.
Explicit user preferences override it. This is a display convention, not a
scientific evidence or magnetic-state acceptance rule.

## Appearance

- OVITO + Tachyon; orthographic camera, white background, ambient occlusion on,
  shadows off. Start with +x camera and +z up for a slab normal to z (yz view).
  Adapt the camera to the actual slab normal; no perspective or coordinate shear.
- Small shaded spheres, no bonds by default. Fe #aa7546 / 0.38 Å,
  Rh #a4bec8 / 0.40 Å, C #444444 / 0.24 Å, Pt #b9a7c9 / 0.43 Å.
  For other elements choose and record a distinguishable, consistent map.
- Display lateral periodic images with fractional in-plane coordinates in
  [-0.1,1.1], inclusive tolerance 1e-12. Never repeat the slab-normal direction.
  Preserve source IDs plus integer translations; verify zero-shift coverage,
  no duplicate images and completeness against a wider translation enumeration.
  Keep original structure files unchanged; added particles are display-only.
- Gray #999999 dashed cell boundaries, 0.65 pt, dash pattern 3/3. Project actual
  lattice edges with the same camera transform as particles. For nonorthogonal
  cells, use projected corners/edges, not an orthogonal bounding rectangle.
- Main view may crop vacuum but must retain every displayed atom sphere.
  Do not place fake horizontal cell boundaries at the slab surfaces. Identify
  cropped vacuum and supply a full-cell companion when helpful/requested.
- Comparable panels share physical Å-to-pixel scale, colors, radii and camera
  direction. Fit a common field of view from the structures; do not stretch each
  raster independently. Mark any deliberately different scale.
- Quiet typography (about 7–9 pt at final size), simple panel letters, short
  structure/layer labels, shared element legend and scale bar. No decorative
  cards, gradients, large headings or software/file metadata on the figure.
  Renderer name, CONTCAR filename and pixel dimensions belong in reproduction
  records, not the scientific caption. Retain scientifically necessary reference
  conditions and limitations in the caption.
- PDF/SVG composition with vector text/lines and high-resolution raster atoms;
  PNG preview at 300 dpi or better. Do not call the atomic image fully vector.

## Structure and spins

Choose the actual structure that supports the intended comparison and record
its stage and hash. For a relaxed view prefer final CONTCAR; a POSCAR-named copy
must explicitly document that origin. Do not silently replace an explicitly
requested initial POSCAR with a final structure.

For a geometry-only view, omit arrows. If spins are requested or essential to the
task, retain the clean style but add provenance-backed vectors under the skill's
moment rules. Never interpret a lower-energy FM/AFMg label as atom-resolved spins.
Do not copy FeRh magnetic conclusions or comparison labels to another system.
