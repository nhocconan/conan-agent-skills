from __future__ import annotations

import importlib.util
import argparse
import contextlib
import io
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    "refsync_freshness", Path(__file__).resolve().parents[1] / "refsync.py"
)
refsync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = refsync
SPEC.loader.exec_module(refsync)


class SourceFreshnessTests(unittest.TestCase):
    def test_pin_does_not_mask_tracking_branch_drift(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            pinned = root / "pinned.md"
            pinned.write_text("reviewed")
            branch = root / "branch.md"
            for secondary in (False, True):
                with self.subTest(secondary=secondary):
                    branch.write_text("changed")
                    fm = {"mode": "wrap", "source": f"local:{pinned}",
                          "fingerprint": refsync.sha256("reviewed")}
                    if secondary:
                        fm.update(secondary_source=f"local:{pinned}",
                                  secondary_tracking_source=f"local:{branch}",
                                  secondary_fingerprint=refsync.sha256("reviewed"))
                    else:
                        fm["tracking_source"] = f"local:{branch}"
                    with mock.patch.object(refsync, "ref_skills", return_value=[(root / "fixture", fm, "")]), \
                         mock.patch.object(refsync, "selected_profiles", return_value={"codex": "codex-dev"}), \
                         mock.patch.object(refsync, "read_loadout", return_value=["fixture"]), \
                         mock.patch.object(refsync, "cmd_loadout", return_value=0), \
                         contextlib.redirect_stdout(io.StringIO()):
                        args = argparse.Namespace(target="codex", profile="codex-dev")
                        self.assertEqual(refsync.cmd_status(args), 1)
                        branch.write_text("reviewed")
                        self.assertEqual(refsync.cmd_status(args), 0)

    def test_cached_fingerprint_cannot_hide_changed_or_unreachable_upstream(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            cached = root / "vendor" / "fixture" / "SKILL.md"
            cached.parent.mkdir(parents=True)
            cached.write_text("reviewed version")
            mirror = root / "mirror"
            mirror.mkdir()
            remote = mirror / "SKILL.md"
            remote.write_text("new upstream version")
            source = "github:example/fixture@main:SKILL.md"
            fm = {"mode": "wrap", "source": source,
                  "fingerprint": refsync.sha256("reviewed version")}
            with mock.patch.dict(os.environ, {
                "CONAN_AGENT_VENDOR": str(root / "vendor"),
                "CONAN_AGENT_RAW_MIRROR": str(mirror),
            }), mock.patch.object(refsync, "ref_skills", return_value=[
                (root / "fixture", fm, "")
            ]), mock.patch.object(refsync, "selected_profiles", return_value={"codex": "codex-dev"}), \
                 mock.patch.object(refsync, "read_loadout", return_value=["fixture"]), \
                 mock.patch.object(refsync, "cmd_loadout", return_value=0), \
                 contextlib.redirect_stdout(io.StringIO()):
                args = argparse.Namespace(target="codex", profile="codex-dev")
                self.assertEqual(refsync.cmd_status(args), 1)
                remote.unlink()
                self.assertEqual(refsync.cmd_status(args), 1)
                remote.write_text("reviewed version")
                self.assertEqual(refsync.cmd_status(args), 0)
                self.assertEqual(cached.read_text(), "reviewed version")
