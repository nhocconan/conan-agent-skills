"""A wrap's `secondary_source` must be fingerprinted, not just recorded.

THE DEFECT THIS PINS, found 2026-10-02 while accepting gstack wrap upstreams.

web-qa routes to two upstream skills: `qa-only` (primary) and `qa` (secondary).
refsync compared only the primary's fingerprint, so `qa` shrank from 960 to 817
lines and gained a sections/ index while `status` kept printing "up to date".
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "ref-skills"))

import refsync  # noqa: E402

SRC = "github:example/upstream@main:qa/SKILL.md"


class StaleSecondaryTest(unittest.TestCase):
    def test_no_secondary_is_never_stale(self):
        self.assertIsNone(refsync.stale_secondary({"fingerprint": "sha256:x"}))

    def test_matching_fingerprint_is_current(self):
        fm = {"secondary_source": SRC, "secondary_fingerprint": refsync.sha256("body")}
        with mock.patch.object(refsync, "read_source", return_value="body"):
            self.assertIsNone(refsync.stale_secondary(fm))

    def test_changed_text_is_reported_with_new_text(self):
        fm = {"secondary_source": SRC, "secondary_fingerprint": refsync.sha256("old")}
        with mock.patch.object(refsync, "read_source", return_value="new"):
            self.assertEqual(refsync.stale_secondary(fm), (SRC, "new"))

    def test_unreachable_secondary_is_reported(self):
        fm = {"secondary_source": SRC, "secondary_fingerprint": refsync.sha256("old")}
        with mock.patch.object(refsync, "read_source", return_value=None):
            self.assertEqual(refsync.stale_secondary(fm), (SRC, None))


class BumpSecondaryTest(unittest.TestCase):
    def test_rewrites_only_the_secondary_fingerprint(self):
        with TemporaryDirectory() as td:
            ref = Path(td) / "REF.md"
            ref.write_text(
                "---\nfingerprint: sha256:primary\n"
                f"secondary_source: {SRC}\nsecondary_fingerprint: sha256:old\n---\nbody\n"
            )
            refsync.bump_secondary(ref, "sha256:new")
            text = ref.read_text()
            self.assertIn("secondary_fingerprint: sha256:new", text)
            self.assertIn("fingerprint: sha256:primary", text)
            self.assertNotIn("sha256:old", text)


if __name__ == "__main__":
    unittest.main()
