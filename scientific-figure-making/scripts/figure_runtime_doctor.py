#!/usr/bin/env python3
"""Audit and smoke-test Python capabilities used by scientific figure skills."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import tempfile


PROFILES = {
    "core": {"numpy": "numpy", "matplotlib": "matplotlib", "pillow": "PIL", "ase": "ase"},
    "publication": {"seaborn": "seaborn"},
    "trajectory": {"imageio": "imageio", "imageio-ffmpeg": "imageio_ffmpeg"},
    "plotly": {"plotly": "plotly", "kaleido": "kaleido"},
    "ovito": {"ovito": "ovito"},
}


def required_packages(profile: str) -> dict[str, str]:
    selected = dict(PROFILES["core"])
    if profile == "all":
        for name in ("publication", "trajectory", "plotly", "ovito"):
            selected.update(PROFILES[name])
    elif profile != "core":
        selected.update(PROFILES[profile])
    return selected


def smoke(profile: str, findings: list[dict[str, str]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    with tempfile.TemporaryDirectory(prefix="scientific-figure-doctor-") as name:
        root = Path(name)
        x = np.linspace(0.0, 1.0, 8)
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.plot(x, x**2)
        for suffix in ("png", "pdf"):
            target = root / f"smoke.{suffix}"
            fig.savefig(target, dpi=120)
            if not target.is_file() or target.stat().st_size == 0:
                findings.append({"severity": "BLOCK", "code": "MATPLOTLIB_EXPORT", "message": suffix})
        plt.close(fig)

        if profile in {"trajectory", "all"}:
            import imageio.v2 as imageio
            import imageio_ffmpeg
            from ase import Atoms
            from ase.io import read, write

            imageio_ffmpeg.get_ffmpeg_exe()
            atoms = Atoms("H2", positions=[[0, 0, 0], [0.74, 0, 0]])
            moved = atoms.copy(); moved.positions[1, 0] = 0.9
            trajectory = root / "fixture.extxyz"
            write(trajectory, [atoms, moved])
            restored = read(trajectory, index=":")
            if len(restored) != 2 or any(a.get_chemical_symbols() != ["H", "H"] for a in restored) or not np.allclose(restored[-1].positions, moved.positions):
                findings.append({"severity": "BLOCK", "code": "TRAJECTORY_IDENTITY", "message": "frame/atom identity mismatch"})
            frames = []
            for index, frame in enumerate(restored):
                figure, axes = plt.subplots(figsize=(1, 1), dpi=32)
                axes.scatter(frame.positions[:, 0], frame.positions[:, 1])
                axes.set(xlim=(-0.3, 1.2), ylim=(-0.5, 0.5)); axes.axis("off")
                png = root / f"frame-{index}.png"; figure.savefig(png); plt.close(figure)
                frames.append(imageio.imread(png)[:, :, :3])
            target = root / "smoke.mp4"
            imageio.mimsave(target, frames, fps=2, macro_block_size=1)
            if not target.is_file() or target.stat().st_size == 0:
                findings.append({"severity": "BLOCK", "code": "TRAJECTORY_EXPORT", "message": "mp4"})
            else:
                decoded = imageio.mimread(target)
                if len(decoded) != len(frames) or any(frame.shape[:2] != (32, 32) for frame in decoded):
                    findings.append({"severity": "BLOCK", "code": "TRAJECTORY_DECODE", "message": "frame count/dimensions mismatch"})

        if profile in {"plotly", "all"}:
            import plotly.graph_objects as go

            target = root / "plotly-smoke.png"
            try:
                go.Figure(go.Scatter(x=[0, 1], y=[0, 1])).write_image(target)
            except Exception as exc:  # runtime/browser failures vary by platform
                findings.append({"severity": "BLOCK", "code": "PLOTLY_EXPORT", "message": str(exc)})
            else:
                if not target.is_file() or target.stat().st_size == 0:
                    findings.append({"severity": "BLOCK", "code": "PLOTLY_EXPORT", "message": "empty PNG"})

        if profile in {"ovito", "all"}:
            from ase.build import bulk
            from ovito.io.ase import ase_to_ovito, ovito_to_ase
            from ovito.pipeline import Pipeline, StaticSource
            from ovito.vis import TachyonRenderer, Viewport

            atoms = bulk("NaCl", "rocksalt", a=5.64, cubic=True)
            pipeline = Pipeline(source=StaticSource(data=ase_to_ovito(atoms)))
            try:
                data = pipeline.compute()
                restored = ovito_to_ase(data)
                identity_ok = (
                    data.particles.count == len(atoms)
                    and restored.get_chemical_symbols() == atoms.get_chemical_symbols()
                    and np.allclose(restored.positions, atoms.positions)
                    and np.allclose(restored.cell.array, atoms.cell.array)
                )
                if not identity_ok:
                    findings.append({
                        "severity": "BLOCK",
                        "code": "OVITO_STRUCTURE_IDENTITY",
                        "message": "ASE/OVITO round-trip changed count, species, positions, or cell",
                    })

                target = root / "ovito-smoke.png"
                viewport = Viewport(type=Viewport.Type.Ortho, camera_dir=(1, 1, -1))
                pipeline.add_to_scene()
                viewport.zoom_all()
                viewport.render_image(
                    filename=str(target),
                    size=(640, 480),
                    background=(1.0, 1.0, 1.0),
                    renderer=TachyonRenderer(ambient_occlusion=False, shadows=False),
                )
                if not target.is_file() or target.stat().st_size == 0:
                    findings.append({"severity": "BLOCK", "code": "OVITO_RENDER", "message": "empty PNG"})
            except Exception as exc:  # Qt and renderer failures vary by platform
                findings.append({"severity": "BLOCK", "code": "OVITO_RENDER", "message": str(exc)})
            finally:
                pipeline.remove_from_scene()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=[*PROFILES, "all"], default="core")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    findings: list[dict[str, str]] = []
    packages: dict[str, dict[str, str | bool]] = {}
    for distribution, module in required_packages(args.profile).items():
        try:
            importlib.import_module(module)
            version = importlib.metadata.version(distribution)
            packages[distribution] = {"available": True, "version": version}
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            packages[distribution] = {"available": False, "error": str(exc)}
            findings.append({"severity": "BLOCK", "code": "MISSING_PACKAGE", "message": distribution})

    if args.smoke and not findings:
        smoke(args.profile, findings)

    report = {
        "profile": args.profile,
        "runtime": {"python": platform.python_version(), "executable": sys.executable},
        "packages": packages,
        "findings": findings,
        "ready": not findings,
        "non_claim": "Runtime readiness does not validate scientific content or release status.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
