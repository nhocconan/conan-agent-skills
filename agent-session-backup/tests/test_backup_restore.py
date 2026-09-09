"""Isolated round-trip tests for the light Cowork backup format."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load_script(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


backup = load_script("agent_session_backup_backup", "backup.py")
restore = load_script("agent_session_backup_restore", "restore.py")


class CoworkRoundTripTests(unittest.TestCase):
    def make_source_session(self, root: Path, cwd: Path) -> tuple[Path, Path]:
        space = root / "account" / "space"
        space.mkdir(parents=True)
        metadata = space / "local_session.json"
        metadata.write_text(json.dumps({"cwd": str(cwd)}), encoding="utf-8")
        transcript = space / "local_session"
        transcript.mkdir()
        (transcript / "conversation.jsonl").write_text("history\n", encoding="utf-8")
        return metadata, transcript

    def test_backup_and_restore_preserve_paired_transcript_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            cowork_source = root / "live-source"
            _, transcript = self.make_source_session(cowork_source, project)
            destination = root / "backup"

            old_trees, old_code = backup.COWORK_TREES, backup.CODE_SRC
            backup.COWORK_TREES = [(str(cowork_source), "Claude-Cowork-Local")]
            backup.CODE_SRC = str(root / "no-claude-code")
            try:
                with patch.object(sys, "argv", ["backup.py", str(destination)]):
                    backup.main()
            finally:
                backup.COWORK_TREES, backup.CODE_SRC = old_trees, old_code

            archived = destination / "Claude-Cowork-Local" / "account" / "space"
            self.assertEqual((archived / "local_session.json").read_text(encoding="utf-8"),
                             json.dumps({"cwd": str(project)}))
            self.assertEqual((archived / "local_session" / "conversation.jsonl").read_text(),
                             "history\n")

            live_target = root / "live-target"
            existing = live_target / "account" / "space" / "local_session" / "conversation.jsonl"
            existing.parent.mkdir(parents=True)
            existing.write_text("live history\n", encoding="utf-8")
            # A second transcript file proves directory contents merge rather than skip wholesale.
            (archived / "local_session" / "events.jsonl").write_text("events\n", encoding="utf-8")

            copied, skipped = restore.restore_tree(destination / "Claude-Cowork-Local", live_target, False, False)
            self.assertGreaterEqual(copied, 2)  # metadata + newly introduced transcript file
            self.assertGreaterEqual(skipped, 1)
            self.assertEqual(existing.read_text(encoding="utf-8"), "live history\n")
            self.assertEqual((existing.parent / "events.jsonl").read_text(encoding="utf-8"), "events\n")

    def test_restore_dry_run_does_not_create_paired_transcript_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "backup" / "account" / "space"
            source.mkdir(parents=True)
            (source / "local_session.json").write_text("{}", encoding="utf-8")
            transcript = source / "local_session"
            transcript.mkdir()
            (transcript / "conversation.jsonl").write_text("history\n", encoding="utf-8")
            target = root / "live"

            copied, skipped = restore.restore_tree(root / "backup", target, True, False)
            self.assertEqual((copied, skipped), (2, 0))
            self.assertFalse(target.exists())

    def test_backup_skips_transcript_symlinks_without_following_cycles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            source = root / "live-source"
            _, transcript = self.make_source_session(source, project)
            outside_secret = root / "outside-secret.txt"
            outside_secret.write_text("do not export\n", encoding="utf-8")
            (transcript / "outside-secret").symlink_to(outside_secret)
            (transcript / "cycle").symlink_to(transcript, target_is_directory=True)
            destination = root / "backup"

            old_trees, old_code = backup.COWORK_TREES, backup.CODE_SRC
            backup.COWORK_TREES = [(str(source), "Claude-Cowork-Local")]
            backup.CODE_SRC = str(root / "no-claude-code")
            try:
                with patch.object(sys, "argv", ["backup.py", str(destination)]):
                    backup.main()
            finally:
                backup.COWORK_TREES, backup.CODE_SRC = old_trees, old_code

            archived = destination / "Claude-Cowork-Local" / "account" / "space" / "local_session"
            self.assertEqual((archived / "conversation.jsonl").read_text(), "history\n")
            self.assertFalse((archived / "outside-secret").exists())
            self.assertFalse((archived / "cycle").exists())
            manifest = (destination / "MANIFEST.txt").read_text(encoding="utf-8")
            self.assertIn("ignored 2 transcript symlink(s)", manifest)
            self.assertNotIn("do not export", manifest)

    def test_restore_refuses_symlink_source_root_without_writing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            (source / "account").mkdir(parents=True)
            (source / "account" / "session.json").write_text("history\n", encoding="utf-8")
            source_link = root / "source-link"
            source_link.symlink_to(source, target_is_directory=True)
            target = root / "live"

            with self.assertRaisesRegex(restore.RestoreSafetyError, "source root"):
                restore.restore_tree(source_link, target, False, False)
            self.assertFalse(target.exists())

    def test_restore_refuses_symlink_destination_parent_without_outside_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            (source / "account" / "space").mkdir(parents=True)
            (source / "account" / "space" / "session.json").write_text(
                "history\n", encoding="utf-8"
            )
            target = root / "live"
            target.mkdir()
            outside = root / "outside"
            outside.mkdir()
            (target / "account").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(restore.RestoreSafetyError, "destination parent"):
                restore.restore_tree(source, target, False, False)
            self.assertFalse((outside / "space" / "session.json").exists())

    def test_restore_refuses_dangling_destination_file_symlink_without_outside_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            (source / "account").mkdir(parents=True)
            (source / "account" / "session.json").write_text("history\n", encoding="utf-8")
            target = root / "live"
            destination_parent = target / "account"
            destination_parent.mkdir(parents=True)
            outside_file = root / "outside" / "escaped.json"
            (destination_parent / "session.json").symlink_to(outside_file)

            with self.assertRaisesRegex(restore.RestoreSafetyError, "destination file"):
                restore.restore_tree(source, target, False, False)
            self.assertFalse(outside_file.exists())

    def test_restore_refuses_directory_destination_file_even_with_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            (source / "account").mkdir(parents=True)
            (source / "account" / "session.json").write_text("history\n", encoding="utf-8")
            target = root / "live"
            destination_file = target / "account" / "session.json"
            destination_file.mkdir(parents=True)

            with self.assertRaisesRegex(restore.RestoreSafetyError, "non-regular"):
                restore.restore_tree(source, target, False, True)
            self.assertFalse((destination_file / "session.json").exists())


if __name__ == "__main__":
    unittest.main()
