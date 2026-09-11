from __future__ import annotations

import importlib.util
import io
import json
import stat
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "mine_history", Path(__file__).resolve().parents[1] / "mine_history.py")
miner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(miner)


def codex_message(text):
    return {"type": "response_item", "timestamp": "2026-01-01T00:00:00Z",
            "payload": {"role": "user", "content": [{"type": "input_text", "text": text}]}}


class MiningTests(unittest.TestCase):
    def test_short_human_correction_is_preserved(self):
        self.assertEqual(miner.classify("sai rồi"), ("prompt", "sai rồi"))
        self.assertEqual(miner.classify(""), ("noise", None))

    def test_injected_rulebook_without_directory_is_not_human_intent(self):
        injected = "# AGENTS.md instructions\n<INSTRUCTIONS>\nCheck the project rules.\n</INSTRUCTIONS>"
        self.assertEqual(miner.classify(injected), ("noise", None))
        self.assertEqual(miner.classify("Please update AGENTS.md for this project"),
                         ("prompt", "Please update AGENTS.md for this project"))

    def test_dedupe_preserves_projects_tails_and_provenance(self):
        common = "a" * 700
        def turn(cwd, text, line):
            return dict(cwd=cwd, text=text, ts="2026", path="session.jsonl",
                        session="session", line=line)
        result = miner.dedupe([
            turn("/one/app", common + "first", 1),
            turn("/one/app", common + "second", 2),
            turn("/two/app", common + "first", 3),
            turn("/one/app", common + "first", 4),
        ])
        self.assertEqual(len(result), 3)
        self.assertEqual([o["line"] for o in result[0]["occurrences"]], [1, 4])

    def test_archived_sessions_and_worker_exclusion(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive = root / "archived"
            archive.mkdir()
            (archive / "saved.jsonl").write_text(json.dumps(codex_message("please check the failure")) + "\n")
            worker = archive / "worker.jsonl"
            worker.write_text(json.dumps({"type": "session_meta", "payload": {
                "source": {"subagent": {"thread_spawn": {}}}}}) + "\n" +
                json.dumps(codex_message("worker instructions are not human intent")) + "\n")
            with patch.multiple(miner, CODEX_SESSIONS=root / "absent", CODEX_ARCHIVED=archive,
                                CLAUDE_PROJECTS=root / "claude", COWORK_DIRS=[]):
                turns, files = miner.collect("", 4000)
            self.assertEqual(files, 2)
            self.assertEqual(len(turns), 1)
            self.assertEqual(turns[0]["line"], 1)

    def test_malformed_and_unreadable_records_are_visible(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "session.jsonl"
            path.write_text("bad json\n[]\n" + json.dumps(codex_message("a real human request")) + "\n")
            errors = Counter()
            turns = list(miner.read_codex_jsonl(path, "", errors))
            self.assertEqual(errors["malformed_records"], 2)
            self.assertEqual(turns[0]["line"], 3)
            list(miner.read_codex_jsonl(path.with_name("missing"), "", errors))
            self.assertEqual(errors["unreadable_files"], 1)

    def test_unreadable_memory_is_visible(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            memory = root / "project" / "memory"
            memory.mkdir(parents=True)
            path = memory / "note.md"
            path.write_text("private memory")
            errors = Counter()
            real = Path.read_text

            def fail_read(self, *args, **kwargs):
                if self == path:
                    raise OSError("simulated read failure")
                return real(self, *args, **kwargs)

            with patch.object(miner, "CLAUDE_PROJECTS", root), \
                 patch.object(Path, "read_text", fail_read):
                self.assertEqual(miner.collect_memory("", errors), [])
            self.assertEqual(errors["unreadable_memory_files"], 1)

    def test_claude_whitespace_is_not_a_filter(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "session.jsonl"
            record = {"type": "user", "message": {"content": "please diagnose this failure"}}
            path.write_text(json.dumps(record).replace('"type": ', '"type":  ') + "\n")
            turns = list(miner.read_claude_jsonl(path, ""))
            self.assertEqual(len(turns), 1)
            self.assertEqual(turns[0]["line"], 1)

    def test_private_output_and_failed_scan_cannot_advance_watermark(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            state = root / "state" / "last-run.json"
            output = root / "digest.md"
            def failed_collect(floor, limit, errors):
                errors["malformed_records"] += 1
                return [], 1
            with patch.object(miner, "STATE_FILE", state), \
                 patch.object(miner, "collect", side_effect=failed_collect), \
                 patch.object(miner, "collect_memory", return_value=[]), \
                 patch.object(sys, "argv", ["mine", "--full", "--commit", "--out", str(output)]), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(miner.main(), 1)
            self.assertFalse(state.exists())
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertIn("capped samples", output.read_text())

    def test_memory_gap_cannot_advance_watermark(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            state = root / "state" / "last-run.json"
            output = root / "digest.md"
            def collect_ok(floor, limit, errors):
                return [], 0
            def memory_gap(floor, errors):
                errors["unreadable_memory_files"] += 1
                return []
            with patch.object(miner, "STATE_FILE", state), \
                 patch.object(miner, "collect", side_effect=collect_ok), \
                 patch.object(miner, "collect_memory", side_effect=memory_gap), \
                 patch.object(sys, "argv", ["mine", "--full", "--commit", "--out", str(output)]), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(miner.main(), 1)
            self.assertFalse(state.exists())

    def test_state_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            state = root / "state" / "last-run.json"
            state.parent.mkdir()
            target = root / "target.json"
            target.write_text("{}")
            state.symlink_to(target)
            with patch.object(miner, "STATE_FILE", state), \
                 patch.object(miner, "collect", return_value=([], 0)), \
                 patch.object(miner, "collect_memory", return_value=[]), \
                 patch.object(sys, "argv", ["mine", "--full", "--commit", "--out", str(root / "digest.md")]):
                with self.assertRaises(RuntimeError):
                    miner.main()
            self.assertEqual(target.read_text(), "{}")

    def test_committed_state_is_private(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            state = root / "state" / "last-run.json"
            output = root / "digest.md"
            with patch.object(miner, "STATE_FILE", state), \
                 patch.object(miner, "collect", return_value=([], 0)), \
                 patch.object(miner, "collect_memory", return_value=[]), \
                 patch.object(sys, "argv", ["mine", "--full", "--commit", "--out", str(output)]), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(miner.main(), 0)
            self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
