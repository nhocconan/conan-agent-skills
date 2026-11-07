---
name: web-qa
description: >-
  Use when the user says "qa", "test cái này", "test site", "find bugs", "check xem
  chạy được không", "does this work", "kiểm tra e2e", or says a feature is ready for
  testing. Tests a running web app for functional defects — broken flows, dead
  buttons, failing forms, console errors, layout breakage; REPORT-ONLY with
  reproduction evidence unless fixing was requested. Runs the app; for reviewing a
  diff use Claude Code's /code-review, for how it looks use design-qa.
---

# Web QA

Wrapper over gstack's `qa` (fix mode) and `qa-only` (report mode). Upstream owns the test
procedure; this file owns which mode to pick and what counts as evidence.
Paths below are relative to this skill's real directory in the repo checkout
(`~/.conan-agent-skills` by default — resolve the symlink first). `refsync.py ensure`
fetches the vendored upstream files; if one is absent, say so and apply the rules in
this file instead of guessing upstream's content.

Use upstream's exploration and reporting procedure only. Skip Claude startup,
preambles, telemetry, hooks and gstack helper commands; drive the available browser
through `browsing-web`. Missing upstream browser setup does not block an available
driver. Preserve functional, accessibility and evidence checks. For a diff review,
use the active harness's review tool or inspect the diff directly.

Before upstream reads, follow [portable routes and helper replacements](sections/portable-upstream.md).

## Pick the mode first

| The user said | Mode | Read |
| --- | --- | --- |
| "test này", "check xem chạy không", "find bugs", "qa" | **report-only** | `../.vendor/gstack/qa-only/SKILL.md` |
| "test and fix", "sửa luôn đi", "fix what's broken" | **fix** | `../.vendor/gstack/qa/SKILL.md` |

**Default to report-only.** A QA pass that
silently rewrites source is not a QA pass. If the request is ambiguous, report first and
offer to fix.

In fix mode, implement and re-verify scoped repairs. Commit/push only when authorized,
following repository controls and `shipping-changes` if shipping was requested. Regression
tests follow [LEAN-SUITE](../effective-development/LEAN-SUITE.md); skip upstream's 8a.5
attribution comment and test-bootstrap's TESTING.md / CLAUDE.md `## Testing` writes (the test
command is one `AGENTS.md` line, no coverage target).

## Evidence, or it didn't happen

Every reported defect carries: the URL/route, the exact steps, what was expected, what
happened, and an artifact — screenshot, console output, or HTTP status. A finding without
an artifact is a guess.

Equally: **do not report a defect you have not reproduced.** Re-run it once before writing
it down. Console noise from an unrelated extension is not a bug in the app.

## Scope honestly

State up front which routes and flows you covered and which you did not. Name the depth you actually ran; in fix mode also the fix tier (quick / standard /
exhaustive — which severities get fixed).

## Sibling lenses — different jobs, don't substitute

- **Visual/aesthetic defects** (spacing, hierarchy, heading wrap, chart overlap, layout
  slop) → `design-qa`. Functional QA does not catch "it works but looks broken".
- **Accessibility correctness** → `a11y-audit`.
- **Displayed numbers being wrong** → `metric-integrity`. A page that renders perfectly
  while showing a fabricated KPI passes web QA and is still badly broken.
- **Driving the browser directly** for a one-off check → `browsing-web`.

## Browser stack

Use the user-selected or project-approved available browser. Follow its current tool
instructions; `browsing-web` describes session and evidence discipline. If no approved
driver is available, mark browser probes blocked and continue functional probes.
