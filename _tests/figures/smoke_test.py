from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def run(*parts: object) -> None:
    command = [sys.executable, *(str(part) for part in parts)]
    subprocess.run(command, check=True)


def run_fail(*parts: object) -> str:
    command = [sys.executable, *(str(part) for part in parts)]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode == 0:
        raise AssertionError(f"known-bad fixture unexpectedly passed: {command}")
    return completed.stdout + completed.stderr


def make_image(path: Path) -> None:
    y, x = np.mgrid[0:120, 0:180]
    pixels = np.zeros((120, 180, 3), dtype=np.uint8)
    pixels[..., 0] = (x * 3) % 255
    pixels[..., 1] = (y * 5) % 255
    pixels[..., 2] = ((x + y) * 2) % 255
    Image.fromarray(pixels, "RGB").save(path)


def make_pdf(path: Path, image: Path) -> None:
    page = Image.new("RGB", (400, 300), "white")
    with Image.open(image) as source:
        resized = source.resize((240, 160))
        page.paste(resized, (80, 70))
    page.save(path, "PDF", resolution=72)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="figure-skill-smoke-") as temp_name:
        temp = Path(temp_name)
        original = temp / "original.png"
        pdf = temp / "source.pdf"
        make_image(original)
        make_pdf(pdf, original)

        selection = temp / "selection.csv"
        with selection.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "candidate_id",
                    "claim",
                    "visible_action",
                    "source",
                    "rights",
                    "status",
                    "decision_reason",
                ]
            )
            writer.writerow(["C01", "Gradient varies in two directions", "compare", pdf, "test-only", "KEEP", "Exact fixture"])
        run(ROOT / "select-figure-evidence/scripts/validate_selection_ledger.py", selection)
        bad_selection = temp / "selection_bad.csv"
        bad_selection.write_text(
            selection.read_text(encoding="utf-8").replace(",KEEP,", ",INVALID,"),
            encoding="utf-8",
        )
        if "invalid status" not in run_fail(
            ROOT / "select-figure-evidence/scripts/validate_selection_ledger.py",
            bad_selection,
        ):
            raise AssertionError("selection negative fixture failed for the wrong reason")

        page_png = temp / "source_pages/p001.png"
        run(
            ROOT / "extract-source-figures/scripts/extract_pdf_assets.py",
            "render-page",
            "--pdf",
            pdf,
            "--page",
            1,
            "--output",
            page_png,
            "--receipt",
            temp / "source_pages/p001.json",
        )
        if "use --overwrite deliberately" not in run_fail(
            ROOT / "extract-source-figures/scripts/extract_pdf_assets.py",
            "render-page",
            "--pdf",
            pdf,
            "--page",
            1,
            "--output",
            page_png,
        ):
            raise AssertionError("extraction overwrite fixture failed for the wrong reason")
        run(
            ROOT / "extract-source-figures/scripts/extract_pdf_assets.py",
            "extract-images",
            "--pdf",
            pdf,
            "--page",
            1,
            "--output-dir",
            temp / "extracted",
            "--receipt",
            temp / "extracted/receipt.json",
        )
        extraction_receipt = json.loads((temp / "extracted/receipt.json").read_text(encoding="utf-8"))
        if extraction_receipt["count"] < 1:
            raise AssertionError("fixture PDF produced no embedded raster extraction")

        crop = temp / "crops/F01.png"
        run(
            ROOT / "crop-figure-panels/scripts/crop_figure_panel.py",
            "--source",
            page_png,
            "--box",
            "100,100,500,380",
            "--output",
            crop,
            "--receipt",
            temp / "crops/F01.json",
        )
        if "outside source bounds" not in run_fail(
            ROOT / "crop-figure-panels/scripts/crop_figure_panel.py",
            "--source",
            page_png,
            "--box",
            "0,0,99999,99999",
            "--output",
            temp / "crops/bad.png",
        ):
            raise AssertionError("crop bounds fixture failed for the wrong reason")

        inventory = temp / "inventory.csv"
        with inventory.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["figure_id", "source_page", "crop"])
            writer.writerow(["F01", page_png, crop])
        run(
            ROOT / "qa-figure-assets/scripts/qa_figure_assets.py",
            "validate",
            "--inventory",
            inventory,
            "--root",
            temp,
            "--report",
            temp / "validation/crop_qa.json",
        )
        bad_crop = temp / "crops/F01_bad.png"
        Image.new("RGB", (16, 16), (255, 0, 255)).save(bad_crop)
        bad_inventory = temp / "inventory_bad.csv"
        with bad_inventory.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["figure_id", "source_page", "crop"])
            writer.writerow(["F01-BAD", page_png, bad_crop])
        if "not an exact source-page rectangle" not in run_fail(
            ROOT / "qa-figure-assets/scripts/qa_figure_assets.py",
            "validate",
            "--inventory",
            bad_inventory,
            "--root",
            temp,
        ):
            raise AssertionError("crop identity fixture failed for the wrong reason")
        run(
            ROOT / "qa-figure-assets/scripts/qa_figure_assets.py",
            "contact-sheet",
            "--inventory",
            inventory,
            "--root",
            temp,
            "--output",
            temp / "validation/contact_sheet.png",
        )

        generator = temp / "build_figure.py"
        generator.write_text("# deterministic smoke-test generator\n", encoding="utf-8")
        output = temp / "generated/F99.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        make_image(output)
        manifest = temp / "figure_manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "figure_id": "F99",
                    "claim": "A deterministic gradient has two coordinate directions.",
                    "visible_action": "compare",
                    "source_type": "CODE_NATIVE_DIAGRAM",
                    "generator": generator.name,
                    "output": str(output.relative_to(temp)),
                    "rights": "self-generated",
                    "parameters": {"fixture": True},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        run(ROOT / "generate-lecture-figures/scripts/validate_generated_figure.py", manifest)
        bad_manifest = temp / "figure_manifest_bad.json"
        bad_manifest.write_text(
            json.dumps(
                {
                    "figure_id": "F98",
                    "claim": "Unsupported quantitative result",
                    "visible_action": "compare",
                    "source_type": "CODE_REPRODUCED",
                    "generator": generator.name,
                    "output": str(output.relative_to(temp)),
                    "rights": "self-generated",
                    "parameters": {},
                }
            ),
            encoding="utf-8",
        )
        if "CODE_REPRODUCED requires source_data" not in run_fail(
            ROOT / "generate-lecture-figures/scripts/validate_generated_figure.py",
            bad_manifest,
        ):
            raise AssertionError("generated-figure trace fixture failed for the wrong reason")

    print("OK figure_extrac_gen smoke test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
