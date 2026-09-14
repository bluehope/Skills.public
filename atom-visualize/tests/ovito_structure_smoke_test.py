#!/usr/bin/env python3
"""Verify ASE/OVITO structure identity and a headless Tachyon PNG render."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile

import numpy as np
from ase.build import bulk
from ovito.io.ase import ase_to_ovito, ovito_to_ase
from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import TachyonRenderer, Viewport
from PIL import Image, ImageStat


def main() -> int:
    atoms = bulk("NaCl", "rocksalt", a=5.64, cubic=True)
    pipeline = Pipeline(source=StaticSource(data=ase_to_ovito(atoms)))
    try:
        data = pipeline.compute()
        restored = ovito_to_ase(data)
        assert data.particles.count == len(atoms)
        assert restored.get_chemical_symbols() == atoms.get_chemical_symbols()
        assert np.allclose(restored.positions, atoms.positions)
        assert np.allclose(restored.cell.array, atoms.cell.array)

        with tempfile.TemporaryDirectory(prefix="ovito-structure-smoke-") as name:
            target = Path(name) / "nacl-ovito-tachyon.png"
            viewport = Viewport(type=Viewport.Type.Ortho, camera_dir=(1, 1, -1))
            pipeline.add_to_scene()
            viewport.zoom_all()
            viewport.render_image(
                filename=str(target),
                size=(640, 480),
                background=(1.0, 1.0, 1.0),
                renderer=TachyonRenderer(ambient_occlusion=False, shadows=False),
            )
            assert target.is_file() and target.stat().st_size > 0
            with Image.open(target) as image:
                extrema = ImageStat.Stat(image.convert("RGB")).extrema
            assert any(low != high for low, high in extrema), "rendered PNG is blank"
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
    finally:
        pipeline.remove_from_scene()

    print(f"OVITO structure smoke test: PASS particles={len(atoms)} image_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
