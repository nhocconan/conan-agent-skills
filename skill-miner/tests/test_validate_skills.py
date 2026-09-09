from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
assert SPEC and SPEC.loader
validate_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_skills)


def write_skill(root: Path, name: str, frontmatter: str, body: str = "") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\n{frontmatter}\n---\n{body}", encoding="utf-8"
    )
    return skill


class ValidateSkillsTests(unittest.TestCase):
    def test_missing_second_level_sibling_is_reported_source_relative(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root,
                "router-skill",
                "name: router-skill\ndescription: A router fixture. Use when testing links.",
                "[router](sections/router.md#overview)\n"
                "[external](ftp://example.com/reference.md#part) [home](~/private.md)\n",
            )
            sections = skill / "sections"
            sections.mkdir()
            (sections / "router.md").write_text(
                "# Router\n\n[missing sibling](missing.md)\n", encoding="utf-8"
            )

            errors, warnings = validate_skills.check(skill)

            self.assertEqual(errors, [])
            self.assertTrue(any(
                "sections/router.md" in warning and "missing.md" in warning
                for warning in warnings
            ), warnings)
            self.assertFalse(any("nested reference" in warning for warning in warnings))

    def test_valid_nested_router_and_anchors_have_no_structural_warning(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root,
                "router-skill",
                "name: router-skill\ndescription: A router fixture. Use when testing links.",
                "[router](sections/router.md#overview)\n",
            )
            nested = skill / "sections" / "nested"
            nested.mkdir(parents=True)
            (skill / "sections" / "router.md").write_text(
                "# Router\n\n[deeper](nested/deeper.md#part)\n"
                "See `nested/deeper.md#part` for details.\n",
                encoding="utf-8",
            )
            (nested / "deeper.md").write_text("# Deeper\n", encoding="utf-8")

            errors, warnings = validate_skills.check(skill)

            self.assertEqual(errors, [])
            self.assertFalse(any("nested reference" in warning for warning in warnings))
            self.assertFalse(any("referenced file missing" in warning for warning in warnings))

    def test_private_reference_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root,
                "private-skip",
                "name: private-skip\n"
                "description: A fixture. Use when testing private paths without scanning local context.",
                "[private](private/secret.md)\n",
            )
            private = skill / "private"
            private.mkdir()
            (private / "secret.md").write_text("not a skill reference\n", encoding="utf-8")

            errors, warnings = validate_skills.check(skill)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_ignored_senior_operator_projects_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            skill = write_skill(
                parent,
                "senior-operator",
                "name: senior-operator\n"
                "description: A fixture. Use when testing ignored project maps without reading private context.",
                "[map](projects/secret.md)\n",
            )
            projects = skill / "projects"
            projects.mkdir()
            (projects / "secret.md").write_text("secret\n" * 150, encoding="utf-8")

            errors, warnings = validate_skills.check(skill)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_quoted_frontmatter_uses_yaml_scalar_values(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root,
                "quoted-name",
                'name: "quoted-name"\n'
                'description: "A quoted fixture. Use when checking frontmatter parsing."',
            )

            errors, warnings = validate_skills.check(skill)

            self.assertEqual(errors, [])
            self.assertFalse(any("must equal" in warning for warning in warnings))

    def test_quoted_frontmatter_falls_back_without_pyyaml(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root,
                "quoted-name",
                'name: "quoted-name"\n'
                'description: "A quoted fixture. Use when checking fallback parsing."',
            )

            with patch.object(validate_skills, "yaml", None):
                errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_malformed_frontmatter_delimiter_is_an_error(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = root / "bad-delimiter"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: bad-delimiter\n"
                "description: A malformed fixture. Use when testing delimiters.\n"
                "--- # trailing text is not an exact delimiter\n",
                encoding="utf-8",
            )

            errors, _ = validate_skills.check(skill)

            self.assertTrue(any("frontmatter does not open" in error for error in errors))

    def test_root_directories_without_skill_are_not_counted(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "future-docs").mkdir()
            (root / "future-docs" / "README.md").write_text("placeholder\n")
            write_skill(
                root,
                "real-skill",
                "name: real-skill\ndescription: A real fixture. Use when testing counts.",
            )
            output = io.StringIO()
            with patch.object(sys, "argv", [str(MODULE_PATH), str(root)]), redirect_stdout(output):
                result = validate_skills.main()

            self.assertEqual(result, 0)
            self.assertIn("1 skills · 0 errors", output.getvalue())
            self.assertNotIn("future-docs", output.getvalue())


if __name__ == "__main__":
    unittest.main()
