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


class OnDemandMeasureTests(unittest.TestCase):
    def test_measure_sums_referenced_files_transitively(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(
                root, "alpha",
                "# Alpha\n[section](sections/one.md)\n",
            )
            sections = skill / "sections"
            sections.mkdir()
            (sections / "one.md").write_text(
                "# One\n[deeper](nested/two.md)\n", encoding="utf-8",
            )
            (sections / "nested").mkdir()
            (sections / "nested" / "two.md").write_text("# Two\n", encoding="utf-8")

            on_demand = context_budget.measure_on_demand(skill)

            expected = (sections / "one.md").stat().st_size + \
                (sections / "nested" / "two.md").stat().st_size
            self.assertEqual(on_demand, expected)

    def test_measure_excludes_the_private_projects_tree(self):
        # Mirrors validate_skills.py's carve-out: senior-operator/projects/ is
        # gitignored, per-repo, per-project data and must never be pulled into
        # a committed context-budget.json ceiling.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(
                root, "senior-operator",
                "# Senior Operator\n[index](projects/INDEX.md)\n",
            )
            projects = skill / "projects"
            projects.mkdir()
            (projects / "INDEX.md").write_text(
                "secret internal project map\n" * 200, encoding="utf-8",
            )

            on_demand = context_budget.measure_on_demand(skill)

            self.assertEqual(on_demand, 0)

    def test_measure_ignores_a_reference_outside_the_skill(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(
                root, "alpha", "# Alpha\n[other](../beta/SKILL.md)\n",
            )
            beta = write_skill(root, "beta", "# Beta\nSome body.\n")

            on_demand = context_budget.measure_on_demand(skill)

            self.assertEqual(on_demand, 0)

    def test_on_demand_over_ceiling_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(root, "alpha", "# Alpha\n[section](sections/one.md)\n")
            sections = skill / "sections"
            sections.mkdir()
            (sections / "one.md").write_text("x" * 5000, encoding="utf-8")
            ceilings = Path(raw) / "context-budget.json"
            measured = context_budget.measure(skill)
            assert measured
            ceilings.write_text(
                json.dumps({
                    "alpha": {
                        "always_on": context_budget.cap(measured["always_on"]) + 1000,
                        "eager": context_budget.cap(measured["eager"]) + 1000,
                        "on_demand": 100,  # far below the real ~5000 B on-demand content
                    }
                }) + "\n",
                encoding="utf-8",
            )

            result, output = run_budget(root, ceilings, "--no-ratchet")

            self.assertEqual(result, 1)
            self.assertIn("OVER      alpha.on_demand:", output)
            self.assertIn("nowhere further to be carved", output)

    def test_on_demand_within_ceiling_passes_the_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(root, "alpha", "# Alpha\n[section](sections/one.md)\n")
            sections = skill / "sections"
            sections.mkdir()
            (sections / "one.md").write_text("x" * 100, encoding="utf-8")
            ceilings = Path(raw) / "context-budget.json"
            measured = context_budget.measure(skill)
            assert measured
            ceilings.write_text(
                json.dumps({"alpha": {k: context_budget.cap(v) for k, v in measured.items()}}) + "\n",
                encoding="utf-8",
            )

            result, output = run_budget(root, ceilings, "--no-ratchet")

            self.assertEqual(result, 0)
            self.assertNotIn("OVER", output)

    def test_seeding_on_demand_does_not_disturb_existing_eager_ceiling(self):
        # A skill that already had an eager/always_on ceiling but no on_demand
        # key yet (every skill in this repo, before this change) gets
        # on_demand captured as a new key — eager/always_on must not move.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skills"
            root.mkdir()
            skill = write_skill(root, "alpha", "# Alpha\n[section](sections/one.md)\n")
            sections = skill / "sections"
            sections.mkdir()
            (sections / "one.md").write_text("x" * 200, encoding="utf-8")
            ceilings = Path(raw) / "context-budget.json"
            measured = context_budget.measure(skill)
            assert measured
            # Ceilings set to exactly the current cap: neither over (triggers
            # OVER) nor above it (triggers a shrink-ratchet) — isolating the
            # one thing under test: adding the missing on_demand key.
            fixed_always_on = context_budget.cap(measured["always_on"])
            fixed_eager = context_budget.cap(measured["eager"])
            ceilings.write_text(
                json.dumps({"alpha": {"always_on": fixed_always_on, "eager": fixed_eager}}) + "\n",
                encoding="utf-8",
            )

            result, output = run_budget(root, ceilings)  # default: writes
            updated = json.loads(ceilings.read_text(encoding="utf-8"))

            self.assertEqual(result, 0)
            self.assertEqual(updated["alpha"]["always_on"], fixed_always_on)
            self.assertEqual(updated["alpha"]["eager"], fixed_eager)
            self.assertEqual(updated["alpha"]["on_demand"], context_budget.cap(measured["on_demand"]))
            self.assertIn("added alpha.on_demand:", output)


if __name__ == "__main__":
    unittest.main()
