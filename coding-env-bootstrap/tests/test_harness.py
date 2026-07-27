from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
HARNESS = REPO / "coding-env-bootstrap" / "harness.py"
REFSYNC = REPO / "ref-skills" / "refsync.py"
CORE_COUNT = len([
    line for line in (REPO / "ref-skills/loadouts/core.txt").read_text().splitlines()
    if line.split("#", 1)[0].strip()
])


def invoke(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["HOME"] = str(home)
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
    )


class HarnessTests(unittest.TestCase):
    def test_clean_home_apply_is_idempotent_for_both_agents(self):
        with tempfile.TemporaryDirectory() as raw_home:
            home = Path(raw_home)
            command = [
                str(HARNESS), "apply",
                "--target", "both",
                "--profile", "core",
            ]
            first = invoke(home, *command)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            second = invoke(home, *command)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("already current", second.stdout)

            for active in (home / ".claude/skills", home / ".agents/skills"):
                self.assertEqual(len(list(active.iterdir())), CORE_COUNT)
                self.assertTrue(all(path.is_symlink() for path in active.iterdir()))

            strict = invoke(
                home,
                "-c",
                "import tomllib,pathlib;"
                "tomllib.loads((pathlib.Path.home()/'.codex/production.config.toml').read_text())",
            )
            self.assertEqual(strict.returncode, 0, strict.stdout + strict.stderr)

    def test_claude_merge_preserves_custom_keys_but_removes_dangerous_bypass(self):
        with tempfile.TemporaryDirectory() as raw_home:
            home = Path(raw_home)
            settings = home / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(
                '{"customSetting": "keep-me", '
                '"skipDangerousModePermissionPrompt": true}\n'
            )

            result = invoke(
                home,
                str(HARNESS), "apply",
                "--target", "claude",
                "--profile", "core",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            import json
            installed = json.loads(settings.read_text())
            self.assertEqual(installed["customSetting"], "keep-me")
            self.assertNotIn("skipDangerousModePermissionPrompt", installed)

    def test_legacy_claude_symlink_is_backed_up_then_replaced(self):
        with tempfile.TemporaryDirectory() as raw_home:
            home = Path(raw_home)
            claude = home / ".claude"
            shared = home / ".shared-ai-skills"
            claude.mkdir()
            shared.mkdir()
            (claude / "skills").symlink_to(shared)

            result = invoke(
                home,
                str(REFSYNC), "loadout",
                "--target", "claude",
                "--profile", "core",
                "--migrate",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((claude / "skills").is_dir())
            self.assertFalse((claude / "skills").is_symlink())
            self.assertEqual(
                len(list(claude.glob("skills.symlink-backup-*"))),
                1,
            )

    def test_codex_preserves_external_skills_and_prunes_only_repo_links(self):
        with tempfile.TemporaryDirectory() as raw_home:
            home = Path(raw_home)
            active = home / ".agents/skills"
            external = active / "external-suite"
            external.mkdir(parents=True)
            (active / "skill-miner").symlink_to(REPO / "skill-miner")

            result = invoke(
                home,
                str(REFSYNC), "loadout",
                "--target", "codex",
                "--profile", "core",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(external.is_dir())
            self.assertFalse((active / "skill-miner").exists())

    def test_codex_refuses_same_name_external_skill_collision(self):
        with tempfile.TemporaryDirectory() as raw_home:
            home = Path(raw_home)
            collision = home / ".agents/skills/a11y-audit"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text(
                "---\nname: a11y-audit\ndescription: collision\n---\n"
            )

            result = invoke(
                home,
                str(REFSYNC), "loadout",
                "--target", "codex",
                "--profile", "core",
                "--apply",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stdout)
            self.assertFalse(collision.is_symlink())


if __name__ == "__main__":
    unittest.main()
