from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "context_budget.py"
SPEC = importlib.util.spec_from_file_location("context_budget", MODULE_PATH)
assert SPEC and SPEC.loader
context_budget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context_budget)


def write_skill(root: Path, name: str, body: str = "# Fixture\n") -> Path:
    skill = root / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Fixture skill. Use when testing.\n---\n{body}",
        encoding="utf-8",
    )
    return skill


def run_budget(root: Path, ceilings: Path, *flags: str) -> tuple[int, str]:
    output = io.StringIO()
    argv = [str(MODULE_PATH), str(root), *flags]
    with patch.object(context_budget, "CEILINGS", ceilings), patch.object(
        sys, "argv", argv
    ), redirect_stdout(output):
        result = context_budget.main()
    return result, output.getvalue()


class ContextBudgetTests(unittest.TestCase):
    def test_report_is_read_only_and_labels_new_ceiling_as_proposal(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            write_skill(root, "alpha")
            ceilings = Path(raw) / "context-budget.json"
            ceilings.write_text("{}\n", encoding="utf-8")

            before = ceilings.read_bytes()
            result, output = run_budget(root, ceilings, "--report")

            self.assertEqual(result, 0)
            self.assertEqual(ceilings.read_bytes(), before)
            self.assertIn("proposals (read-only; not written):", output)
            self.assertIn("would capture alpha", output)
            self.assertIn("context budget: 1 skills within ceilings (read-only)", output)

    def test_no_ratchet_is_read_only_and_labels_shrink_as_proposal(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            write_skill(root, "alpha", "# Short\n")
            ceilings = Path(raw) / "context-budget.json"
            measured = context_budget.measure(root / "alpha")
            assert measured
            ceilings.write_text(
                json.dumps(
                    {
                        "alpha": {
                            "always_on": context_budget.cap(measured["always_on"]) + 1000,
                            "eager": context_budget.cap(measured["eager"]) + 1000,
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            before = ceilings.read_bytes()
            result, output = run_budget(root, ceilings, "--no-ratchet")

            self.assertEqual(result, 0)
            self.assertEqual(ceilings.read_bytes(), before)
            self.assertIn("proposals (read-only; not written):", output)
            self.assertIn("would ratchet alpha.", output)
            self.assertNotIn("ratcheted alpha.", output)

    def test_default_grade_persists_a_shrink(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            write_skill(root, "alpha", "# Short\n")
            ceilings = Path(raw) / "context-budget.json"
            measured = context_budget.measure(root / "alpha")
            assert measured
            ceilings.write_text(
                json.dumps(
                    {
                        "alpha": {
                            "always_on": context_budget.cap(measured["always_on"]) + 1000,
                            "eager": context_budget.cap(measured["eager"]) + 1000,
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result, output = run_budget(root, ceilings)
            updated = json.loads(ceilings.read_text(encoding="utf-8"))

            self.assertEqual(result, 0)
            self.assertEqual(updated["alpha"], {
                key: context_budget.cap(value) for key, value in measured.items()
            })
            self.assertIn("ratcheted alpha.", output)
            self.assertNotIn("would ratchet", output)

    def test_no_ratchet_does_not_create_missing_ceiling_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            write_skill(root, "alpha")
            ceilings = Path(raw) / "missing-context-budget.json"

            result, output = run_budget(root, ceilings, "--no-ratchet")

            self.assertEqual(result, 0)
            self.assertFalse(ceilings.exists())
            self.assertIn("would capture alpha", output)


if __name__ == "__main__":
    unittest.main()
