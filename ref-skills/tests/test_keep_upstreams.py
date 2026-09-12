"""A `keep` upstream must actually land on every harness this repo targets,
and `ensure` must not call it green when it did not.

THE DEFECT THIS PINS, found 2026-09-12 while upgrading after a pull.

`ensure_npx` treated the installer's exit code as proof of installation. It is
not. `npx impeccable install --global` picks its own harness list by
auto-detection, which finds `.claude/`, `.agents/` and `.cursor/` but never
agy: agy reads `~/.gemini/config/skills`, and impeccable knows that harness
only by the name `antigravity`, only when asked for it explicitly.

So on every run `_keep_missing_targets` reported impeccable missing on agy, the
installer ran, wrote nothing for agy, exited 0, and refsync printed
"impeccable: installed". The skill was absent from agy for as long as that
lasted, and each upgrade reasserted that it was fine — a green that measured
the subprocess instead of the outcome.

Two pins, because the bug needed both halves to stay fixed:
  1. the providers list names every harness in TARGET_DIRS, and
  2. a success exit with the skill still missing is a failure, out loud.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "ref-skills"))

import refsync  # noqa: E402

# Harness name in TARGET_DIRS -> the name its installer answers to. Only needed
# where the two differ; impeccable calls agy's harness "antigravity".
PROVIDER_ALIASES = {"agy": "antigravity"}


class ProvidersCoverEveryTarget(unittest.TestCase):
    def test_impeccable_install_names_every_target_harness(self) -> None:
        spec = refsync.read_upstreams().get("impeccable")
        self.assertIsNotNone(spec, "impeccable dropped out of upstreams.ini")
        named = " ".join(shlex.split(spec.install))
        for target in refsync.TARGET_DIRS:
            provider = PROVIDER_ALIASES.get(target, target)
            self.assertIn(
                provider,
                named,
                f"`install` does not name {provider!r}, so the {target!r} harness "
                f"is left to auto-detection, which skips it: {spec.install}",
            )


class SuccessExitIsNotProof(unittest.TestCase):
    """ensure_npx must verify the outcome, not the return code."""

    def _spec(self) -> refsync.Upstream:
        return refsync.Upstream(
            name="fixture-skill",
            kind="npx",
            install="true",  # exits 0 and writes nothing, like the real gap
            keep=True,
        )

    def _run_against(self, targets: dict[str, Path]) -> tuple[int, str]:
        saved_dirs = refsync.TARGET_DIRS
        saved_run = refsync._run_logged
        calls: list[list[str]] = []

        def fake_run(command, *, cwd=None):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, "", "")

        refsync.TARGET_DIRS = targets
        refsync._run_logged = fake_run
        try:
            import contextlib
            import io

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = refsync.ensure_npx(self._spec())
            return code, buf.getvalue()
        finally:
            refsync.TARGET_DIRS = saved_dirs
            refsync._run_logged = saved_run

    def test_unreached_target_fails_and_says_which(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            reached = root / "claude" / "skills"
            (reached / "fixture-skill").mkdir(parents=True)
            (reached / "fixture-skill" / "SKILL.md").write_text("x")
            unreached = root / "agy" / "skills"
            unreached.mkdir(parents=True)

            code, out = self._run_against({"claude": reached, "agy": unreached})

        self.assertEqual(code, 1, "a target the installer never wrote must fail")
        self.assertIn("agy", out, "the failure must name the harness that is missing")
        self.assertNotIn(
            "fixture-skill: installed",
            out,
            "refsync must not report success while the skill is absent",
        )

    def test_every_target_reached_still_succeeds(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            targets = {}
            for name in ("claude", "agy"):
                d = root / name / "skills"
                (d / "fixture-skill").mkdir(parents=True)
                (d / "fixture-skill" / "SKILL.md").write_text("x")
                targets[name] = d

            code, out = self._run_against(targets)

        self.assertEqual(code, 0, out)
        self.assertIn("fixture-skill: updated", out)


if __name__ == "__main__":
    unittest.main()
