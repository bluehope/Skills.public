"""Missing optional dependencies affect the selected profile only; no installs."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

p = Path(__file__).resolve().parents[1] / "scripts/figure_runtime_doctor.py"
spec = importlib.util.spec_from_file_location("runtime_doctor", p)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)

class Profiles(unittest.TestCase):
    def test_missing_optional_is_scoped(self):
        def importer(name):
            if name == "ovito": raise ImportError("fixture: unavailable")
            return object()
        for profile, expected in [("core", 0), ("ovito", 1)]:
            out = io.StringIO()
            with patch.object(sys, "argv", ["doctor", "--profile", profile, "--smoke"]), patch.object(doctor.importlib, "import_module", side_effect=importer), patch.object(doctor.importlib.metadata, "version", return_value="fixture"), patch.object(doctor, "smoke") as smoke, contextlib.redirect_stdout(out):
                self.assertEqual(doctor.main(), expected)
                self.assertEqual(smoke.called, expected == 0)
            report = json.loads(out.getvalue())
            self.assertEqual(report["ready"], expected == 0)

if __name__ == "__main__": unittest.main()
