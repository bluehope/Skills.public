"""Check review-case locators and report static reading size, not model behavior."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/progressive_loading_cases.json"


class ReadingCases(unittest.TestCase):
    def test_cases_are_available_without_reference_chains(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        body = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        direct = set(re.findall(r"\]\((references/[^)#]+)(?:#[^)]*)?\)", body))
        seen = set()
        reports = []
        for case in data["cases"]:
            self.assertNotIn(case["id"], seen)
            seen.add(case["id"])
            self.assertTrue(case["request"] and case["expected_behavior"])
            paths = case["instruction_files"]
            self.assertEqual(paths[0], "SKILL.md")
            self.assertEqual(len(paths), len(set(paths)))
            characters = 0
            for name in paths:
                path = (ROOT / name).resolve()
                self.assertIn(ROOT, path.parents)
                self.assertTrue(path.is_file(), name)
                if name != "SKILL.md":
                    self.assertIn(name, direct, "mode must be directly discoverable")
                characters += len(path.read_text(encoding="utf-8"))
            reports.append({"case": case["id"], "files": len(paths),
                            "characters_this_skill_only": characters,
                            "additional_skills_not_measured": case["additional_skill_ids"]})
        print(json.dumps({"measurement": "static expected reading, not actual tokens",
                          "cases": reports}, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
