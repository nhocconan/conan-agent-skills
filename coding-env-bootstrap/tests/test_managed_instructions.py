import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "managed_harness", Path(__file__).resolve().parents[1] / "harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class ManagedInstructionsTests(unittest.TestCase):
    def test_verify_rejects_agy_skill_from_an_unmanaged_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            active = home / ".gemini/config/skills"
            active.mkdir(parents=True)
            (home / ".gemini/AGENTS.md").write_text(harness.managed_instructions_block())
            other = home / "other-checkout"
            other.mkdir()
            (other / "SKILL.md").write_text("outdated instructions")
            link = active / "agent-orchestration"
            link.symlink_to(other)
            with patch.object(harness, "HOME", home), \
                 patch.object(harness, "desired_names", return_value=["agent-orchestration"]):
                self.assertTrue(harness.verify_target("agy", "agy-dev"))
                link.unlink()
                link.symlink_to(harness.REPO / "agent-orchestration")
                self.assertEqual(harness.verify_target("agy", "agy-dev"), [])

    def test_preserves_outside_text_and_refreshes_stale_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.md"
            path.write_text(f"before\n{harness.START}\nstale\n{harness.END}\nafter\n")
            self.assertTrue(harness.install_managed_instructions(path))
            self.assertEqual(path.read_text(),
                             f"before\n{harness.managed_instructions_block()}\nafter\n")
            self.assertFalse(harness.install_managed_instructions(path))

    def test_refuses_malformed_markers_without_writes(self):
        for content in (harness.START, harness.END,
                        harness.END + harness.START,
                        harness.START * 2 + harness.END):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "rules.md"
                path.write_text(content)
                with self.assertRaises(ValueError):
                    harness.install_managed_instructions(path)
                self.assertEqual(path.read_text(), content)

    def test_marker_validation(self):
        self.assertTrue(harness.valid_managed_markers(harness.managed_instructions_block()))
        self.assertFalse(harness.valid_managed_markers(""))

    def test_verify_rejects_stale_content_with_valid_markers(self):
        for target, directory in (("codex", ".codex"), ("agy", ".gemini")):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                config = home / directory
                config.mkdir()
                if target == "codex":
                    (config / "production.config.toml").write_text("")
                rules = config / "AGENTS.md"
                with patch.object(harness, "HOME", home), patch.object(harness, "desired_names", return_value=[]):
                    rules.write_text(f"{harness.START}\nstale\n{harness.END}")
                    self.assertTrue(harness.verify_target(target, "core"))
                    rules.write_text(harness.managed_instructions_block())
                    self.assertEqual(harness.verify_target(target, "core"), [])
