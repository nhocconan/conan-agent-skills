"""Every skill in this repository is reachable by some load-out, and the
browser probe counts a driver-managed browser.

TWO DEFECTS THIS PINS, both found 2026-09-09 when `design-qa` was installed and
no agent could see it.

1. COVERAGE. `loadouts/*.txt` is the per-profile directory, but `loadout.txt`
   is still the workstation Claude list, and `loadout_path()` falls back to it
   only for `claude-dev`. Six skills — autonomous-loops, browsing-web,
   design-qa, investigating-bugs, shipping-changes, web-qa — appeared in NO
   file under `loadouts/`, so any reading of that directory said they did not
   exist. A skill that is in the repository and in no load-out cannot be
   installed by the documented command on any machine, and nothing said so.

2. THE BROWSER PROBE. `auto` downgrades a host to `core` when it finds no
   "real browser", and it looked only at PATH executables, macOS app bundles,
   and `$DISPLAY`. Playwright and Puppeteer install their own Chromium in a
   per-user cache, outside PATH, and run it headless — which is how visual QA
   is done on a Linux server, and precisely what the browser/design skills
   drive. A host driving headless Chromium against production all day resolved
   to `core` and silently lost 37 skills.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "ref-skills"))

import refsync  # noqa: E402

# Directories in the repo root that are not skills.
NOT_SKILLS = {".git", ".github", ".vendor", "__pycache__"}
# A skill deliberately absent from every load-out states so here, with the
# reason. Empty on purpose: today every skill belongs somewhere.
INACTIVE: dict[str, str] = {}


def repo_skills() -> set[str]:
    return {
        path.name
        for path in REPO.iterdir()
        if path.is_dir()
        and path.name not in NOT_SKILLS
        and not path.name.startswith(".")
        and (path / "SKILL.md").is_file()
    }


def loadout_names() -> set[str]:
    names: set[str] = set()
    paths = list((REPO / "ref-skills" / "loadouts").glob("*.txt"))
    paths.append(REPO / "ref-skills" / "loadout.txt")
    for path in paths:
        if path.is_file():
            for line in path.read_text().splitlines():
                line = line.split("#")[0].strip()
                if line:
                    names.add(line)
    return names


class LoadoutCoverage(unittest.TestCase):
    def test_every_skill_is_in_a_loadout(self) -> None:
        orphans = sorted(repo_skills() - loadout_names() - set(INACTIVE))
        self.assertEqual(
            orphans,
            [],
            "these skills are in the repository but in no load-out, so the "
            "documented install can never place them; add each to a profile "
            "or to INACTIVE with a reason: " + ", ".join(orphans),
        )

    def test_no_owned_skill_is_promised_but_absent(self) -> None:
        # An entry naming a directory this repo owns must actually resolve;
        # third-party entries are allowed to be missing on a given host.
        owned_but_missing = sorted(
            name
            for name in loadout_names()
            if (REPO / name).is_dir() and refsync.resolve(name) is None
        )
        self.assertEqual(owned_but_missing, [])

    def test_profile_directory_covers_the_documented_profiles(self) -> None:
        # README documents claude-dev / codex-dev / agy-dev / core. Each must
        # resolve to a file that exists, whether directly or by the legacy
        # fallback, or `--profile <name>` silently installs nothing.
        for profile in ("claude-dev", "codex-dev", "agy-dev", "core"):
            path = refsync.loadout_path(profile)
            self.assertTrue(
                path.is_file(),
                f"profile {profile!r} resolves to {path}, which does not exist",
            )
            self.assertTrue(refsync.read_loadout(profile), f"{profile} is empty")


class BrowserProbe(unittest.TestCase):
    def test_managed_browser_is_a_real_browser(self) -> None:
        managed = refsync.managed_browser_path()
        if managed is None:
            self.skipTest("no driver-managed browser on this host")
        self.assertTrue(managed.is_file())
        saved = dict(os.environ)
        try:
            for key in (
                "CONAN_AGENT_BROWSER",
                "CONAN_AGENT_HEADLESS",
                "DISPLAY",
                "WAYLAND_DISPLAY",
            ):
                os.environ.pop(key, None)
            # No display server: the managed browser alone must decide.
            self.assertTrue(
                refsync.real_browser_available(),
                "a driver-managed Chromium must count as a browser without $DISPLAY",
            )
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_explicit_override_still_wins(self) -> None:
        saved = dict(os.environ)
        try:
            os.environ["CONAN_AGENT_BROWSER"] = "0"
            self.assertFalse(refsync.real_browser_available())
            os.environ["CONAN_AGENT_BROWSER"] = "1"
            self.assertTrue(refsync.real_browser_available())
        finally:
            os.environ.clear()
            os.environ.update(saved)


if __name__ == "__main__":
    unittest.main()
