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


class CrossReferenceCheckTests(unittest.TestCase):
    def test_skill_md_citation_with_no_heading_in_skill_md_is_an_error(self):
        # The real bug this check was built for: TEMPLATES.md cites "SKILL.md
        # §5.6" while SKILL.md itself has zero § headings (they live in
        # sections/ instead).
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "orchestration",
                "name: orchestration\ndescription: A fixture. Use when testing § citations.",
                "## Start\nSee [routing](sections/routing.md).\n",
            )
            (skill / "sections").mkdir()
            (skill / "sections" / "routing.md").write_text(
                "## §5. Routing\nBody.\n", encoding="utf-8",
            )
            (skill / "TEMPLATES.md").write_text(
                "Escalate now (`SKILL.md` §5.6).\n", encoding="utf-8",
            )

            errors, _ = validate_skills.check(skill)

            self.assertTrue(any(
                "TEMPLATES.md" in e and "SKILL.md §5" in e and "no matching" in e
                for e in errors
            ), errors)

    def test_bare_citation_matching_a_real_heading_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "orchestration",
                "name: orchestration\ndescription: A fixture. Use when testing § citations.",
                "## §5. Quality gate\nRe-run the gate at §5 before handing off.\n",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_plain_numbered_heading_without_glyph_resolves_a_bare_citation(self):
        # coding-env-bootstrap / ref-skills style: "## 7. Secrets" with no §
        # glyph in the heading, cited elsewhere as bare "§7".
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "bootstrap",
                "name: bootstrap\ndescription: A fixture. Use when testing plain headings.",
                "## 7. Secrets and identity\nBody.\n",
            )
            (skill / "AUDIT.md").write_text(
                "Ask the operator only for the items in §7.\n", encoding="utf-8",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_dangling_named_file_citation_within_the_skill_is_an_error(self):
        # A citation that names a REAL file in this skill, but a number that
        # file doesn't have — e.g. AUDIT.md → BOOTSTRAP.md §4b when
        # BOOTSTRAP.md only has "3b" and "4".
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "bootstrap",
                "name: bootstrap\ndescription: A fixture. Use when testing dangling refs.",
            )
            (skill / "BOOTSTRAP.md").write_text(
                "### 3b. Third-party\nBody.\n## 4. Settings\nBody.\n", encoding="utf-8",
            )
            (skill / "AUDIT.md").write_text(
                "`BOOTSTRAP.md` §4b replaces it.\n", encoding="utf-8",
            )

            errors, _ = validate_skills.check(skill)

            self.assertTrue(any("BOOTSTRAP.md §4b" in e for e in errors), errors)

    def test_citation_naming_a_file_outside_the_skill_is_skipped(self):
        # investigating-bugs cites "`senior-operator` OPERATING-MANUAL §4" —
        # a real, valid reference to a DIFFERENT skill this check cannot
        # verify from here, so it must be skipped, never errored. The
        # citation is also split across a soft line-wrap, as it is for real.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "investigating-bugs",
                "name: investigating-bugs\ndescription: A fixture. Use when testing external refs.",
                "A pattern that looks familiar — see `senior-operator`\n"
                "OPERATING-MANUAL §4.\n",
            )
            # The sibling skill that actually owns the named document.
            (root / "senior-operator").mkdir()
            (root / "senior-operator" / "OPERATING-MANUAL.md").write_text(
                "## 4. Verify by re-derivation\n", encoding="utf-8",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_capitalised_word_before_a_citation_is_not_a_filename(self):
        # "MUST §9" / "EVERY §5.2": an ALL-CAPS word that is not any skill's
        # document must not be mistaken for a file miss and skipped — the
        # citation is bare and has to resolve against this skill's headings.
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "shouty",
                "name: shouty\ndescription: A fixture. Use when testing capitalised prose.",
                "## 1. Intro\nYou MUST §9 comply.\n",
            )

            errors, _ = validate_skills.check(skill)

            self.assertTrue(any("§9" in e and "no matching heading" in e for e in errors), errors)

    def test_citation_inside_fenced_code_block_is_skipped(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "templated",
                "name: templated\ndescription: A fixture. Use when testing fenced examples.",
                "```markdown\nKNOWN TRAPS: §41 example trap; §35 another.\n```\n",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_citation_inside_quotes_is_skipped(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "audits",
                "name: audits\ndescription: A fixture. Use when testing quoted examples.",
                'Numbered rules are citable ("§33") and become memory.\n',
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_literal_n_placeholder_is_skipped(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "placeholder",
                "name: placeholder\ndescription: A fixture. Use when testing the N placeholder.",
                "No internal doc citations (§N), and no internal names.\n",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])

    def test_lint_allow_marker_skips_the_line(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            skill = write_skill(
                root, "marked",
                "name: marked\ndescription: A fixture. Use when testing the opt-out marker.",
                "See SKILL.md §9 for the deliberately unresolved case. lint-allow\n",
            )

            errors, _ = validate_skills.check(skill)

            self.assertEqual(errors, [])


class BannedWordsCheckTests(unittest.TestCase):
    def test_clean_content_has_no_warnings(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = write_skill(
                Path(raw), "clean",
                "name: clean\ndescription: A fixture. Use when testing clean copy.",
                "The build finished in 4.2s and 12 tests passed.\n",
            )

            warns = validate_skills.check_banned_words(skill, banned_terms=("successfully", "robust"))

            self.assertEqual(warns, [])

    def test_unquoted_banned_term_is_a_warning(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = write_skill(
                Path(raw), "sloppy",
                "name: sloppy\ndescription: A fixture. Use when testing slop detection.",
                "The migration was successfully completed.\n",
            )

            warns = validate_skills.check_banned_words(skill, banned_terms=("successfully", "robust"))

            self.assertTrue(any("successfully" in w for w in warns), warns)

    def test_quoted_user_trigger_phrase_is_skipped(self):
        with tempfile.TemporaryDirectory() as raw:
            # A single-quoted YAML scalar lets the trigger phrase carry plain
            # double quotes with no backslash-escaping, matching how a real
            # frontmatter `description` quotes a user's own words.
            skill = write_skill(
                Path(raw), "trigger",
                "name: trigger\n"
                'description: \'Use when the user asks for a "robust" solution.\'',
                "",
            )

            warns = validate_skills.check_banned_words(skill, banned_terms=("robust",))

            self.assertEqual(warns, [])


class ModelIdContainmentCheckTests(unittest.TestCase):
    def _fixture_root(self, raw: str, routing_body: str) -> Path:
        root = Path(raw)
        routing = root / "agent-orchestration" / "sections"
        routing.mkdir(parents=True)
        (routing / "routing.md").write_text(routing_body, encoding="utf-8")
        return root

    def test_id_absent_from_routing_is_no_violation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "canonical policy, no model IDs here\n")
            other = root / "some-skill"
            other.mkdir()
            (other / "SKILL.md").write_text("Just prose, no model IDs.\n", encoding="utf-8")

            errors = validate_skills.check_model_id_containment(root)

            self.assertEqual(errors, [])

    def test_private_projects_tree_is_not_scanned(self):
        # senior-operator/projects/ is gitignored, per-project data; scanning it
        # would make the gate's result differ between a checkout and CI.
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "| Terra | `gpt-5.6-terra` | ... |\n")
            projects = root / "senior-operator" / "projects"
            projects.mkdir(parents=True)
            (projects / "map.md").write_text("lead: gpt-5.6-terra\n", encoding="utf-8")

            errors = validate_skills.check_model_id_containment(root)

            self.assertEqual(errors, [])

    def test_duplicated_model_id_outside_routing_is_an_error(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "| Terra | `gpt-5.6-terra` | ... |\n")
            other = root / "some-skill"
            other.mkdir()
            (other / "TEMPLATES.md").write_text(
                "in progress (gpt-5.6-terra, medium)\n", encoding="utf-8",
            )

            errors = validate_skills.check_model_id_containment(root)

            self.assertTrue(any(
                "gpt-5.6-terra" in e and "TEMPLATES.md" in e for e in errors
            ), errors)

    def test_undocumented_model_id_outside_routing_is_also_an_error(self):
        # store-screenshots' real case: gpt-4o-mini-tts is a real API model the
        # code calls, but routing.md (an orchestration-tier policy) has never
        # heard of it — that is flagged too, just with a different message,
        # since an ID absent from the canonical policy is not "in containment"
        # either; the fix is either an opt-out marker or adding it to policy.
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "| Terra | `gpt-5.6-terra` | ... |\n")
            other = root / "some-skill"
            other.mkdir()
            (other / "preview_core.py").write_text(
                'model = "gpt-4o-mini-tts"\n', encoding="utf-8",
            )

            errors = validate_skills.check_model_id_containment(root)

            self.assertTrue(any(
                "gpt-4o-mini-tts" in e and "not in" in e for e in errors
            ), errors)

    def test_model_id_allow_marker_skips_the_line(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "| Terra | `gpt-5.6-terra` | ... |\n")
            other = root / "some-skill"
            other.mkdir()
            (other / "config.toml") .write_text(
                'model = "gpt-6-astra"  # model-id-allow: routing.md is the source of truth\n',
                encoding="utf-8",
            )

            errors = validate_skills.check_model_id_containment(root)

            self.assertEqual(errors, [])

    def test_routing_md_itself_is_never_flagged(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(
                raw, "| Terra | `gpt-5.6-terra` | | Astra | `gpt-6-astra` |\n",
            )

            errors = validate_skills.check_model_id_containment(root)

            self.assertEqual(errors, [])

    def test_vendored_upstream_preview_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as raw:
            root = self._fixture_root(raw, "| Terra | `gpt-5.6-terra` | ... |\n")
            other = root / "some-skill"
            other.mkdir()
            (other / ".upstream-preview.md").write_text(
                "some other project's own gpt-5.6-terra mention\n", encoding="utf-8",
            )

            errors = validate_skills.check_model_id_containment(root)

            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
