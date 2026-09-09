from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "coding-env-bootstrap" / "project_rules.py"
ADAPTER_CONTENT = "@AGENTS.md\n"


def invoke(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--root", str(root)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


class ProjectRulesTests(unittest.TestCase):
    def make_project(self, parent: Path) -> Path:
        project = parent / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Canonical rules\n", encoding="utf-8")
        return project

    def test_apply_creates_exact_adapters_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))

            first = invoke(project, "apply")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            for name in ("CLAUDE.md", "GEMINI.md"):
                self.assertEqual((project / name).read_text(encoding="utf-8"), ADAPTER_CONTENT)

            second = invoke(project, "apply")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("already match", second.stdout)
            checked = invoke(project)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_check_reports_missing_adapters_without_writing(self):
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))

            result = invoke(project)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing adapter", result.stdout)
            self.assertFalse((project / "CLAUDE.md").exists())
            self.assertFalse((project / "GEMINI.md").exists())

    def test_apply_refuses_empty_or_whitespace_canonical_rules(self):
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            (project / "AGENTS.md").write_text(" \n\t", encoding="utf-8")

            result = invoke(project, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty or whitespace", result.stdout)
            self.assertFalse((project / "CLAUDE.md").exists())
            self.assertFalse((project / "GEMINI.md").exists())

    def test_apply_refuses_drift_without_partial_writes(self):
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            (project / "GEMINI.md").write_text("# user rules\n", encoding="utf-8")

            result = invoke(project, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stdout)
            self.assertFalse((project / "CLAUDE.md").exists())
            self.assertEqual((project / "GEMINI.md").read_text(encoding="utf-8"), "# user rules\n")

    def test_apply_refuses_nonempty_codex_override_without_partial_writes(self):
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            (project / "AGENTS.override.md").write_text("# shadow rules\n", encoding="utf-8")

            result = invoke(project, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("shadows canonical", result.stdout)
            self.assertFalse((project / "CLAUDE.md").exists())
            self.assertFalse((project / "GEMINI.md").exists())

    def test_refuses_symlinked_canonical_or_adapter(self):
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            canonical_target = parent / "canonical-source.md"
            canonical_target.write_text("# rules\n", encoding="utf-8")
            project = parent / "canonical-link-project"
            project.mkdir()
            (project / "AGENTS.md").symlink_to(canonical_target)

            canonical_result = invoke(project, "apply")
            self.assertNotEqual(canonical_result.returncode, 0)
            self.assertIn("non-symlink canonical", canonical_result.stdout)
            self.assertFalse((project / "CLAUDE.md").exists())

            safe_project = self.make_project(parent)
            adapter_target = parent / "adapter-source.md"
            adapter_target.write_text(ADAPTER_CONTENT, encoding="utf-8")
            (safe_project / "CLAUDE.md").symlink_to(adapter_target)
            adapter_result = invoke(safe_project, "apply")
            self.assertNotEqual(adapter_result.returncode, 0)
            self.assertIn("non-symlink adapter", adapter_result.stdout)
            self.assertFalse((safe_project / "GEMINI.md").exists())

    def test_apply_supports_one_explicit_scoped_directory_only(self):
        with tempfile.TemporaryDirectory() as raw:
            parent = Path(raw)
            project = self.make_project(parent)
            nested = self.make_project(project)

            result = invoke(nested, "apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((nested / "CLAUDE.md").is_file())
            self.assertFalse((project / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
