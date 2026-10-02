"""`prune_dead_hooks` drops only hook entries whose absolute command no longer exists.

Written as unittest cases: AGENTS.md runs these with `python3 -m unittest discover`,
which does not collect pytest-style module functions, so a pytest-only file here
passes CI by never running.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refsync  # noqa: E402


def _settings(tmp_path: Path, cmd: str) -> Path:
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({
        "model": "x",
        "hooks": {"Stop": [{"hooks": [{"type": "command", "command": cmd, "timeout": 5}]}]},
    }))
    return p


class PruneDeadHooks(unittest.TestCase):
    def test_removes_hook_whose_script_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            p = _settings(tmp_path, str(tmp_path / "nope" / "timeline-stop-hook"))
            removed = refsync.prune_dead_hooks(p)
            self.assertEqual(len(removed), 1)
            data = json.loads(p.read_text())
            self.assertNotIn("hooks", data)
            self.assertEqual(data["model"], "x")
            self.assertTrue((tmp_path / "settings.json.bak-dead-hooks").exists())

    def test_keeps_hook_whose_script_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script = tmp_path / "hook"
            script.write_text("#!/bin/sh\nexit 0\n")
            p = _settings(tmp_path, str(script))
            self.assertEqual(refsync.prune_dead_hooks(p), [])
            self.assertIn("hooks", json.loads(p.read_text()))

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            p = _settings(tmp_path, str(tmp_path / "missing"))
            before = p.read_text()
            self.assertTrue(refsync.prune_dead_hooks(p, dry_run=True))
            self.assertEqual(p.read_text(), before)


if __name__ == "__main__":
    unittest.main()
