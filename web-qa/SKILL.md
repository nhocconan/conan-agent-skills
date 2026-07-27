---
name: web-qa
description: Tests a running web application for functional defects — broken flows, dead buttons, failing forms, console errors, layout breakage — and either reports them with reproduction evidence or fixes them, depending on which the user asked for. Use when the user says "qa", "test cái này", "test site", "find bugs", "check xem chạy được không", "does this work", "kiểm tra e2e", or says a feature is ready for testing. Default is REPORT-ONLY; only fix when fixing was actually requested.
---

# Web QA

Wrapper over gstack's `qa` (fix mode) and `qa-only` (report mode). Upstream owns the test
procedure; this file owns which mode to pick and what counts as evidence.

## Pick the mode first — this is the whole point

| The user said | Mode | Read |
| --- | --- | --- |
| "test này", "check xem chạy không", "find bugs", "qa" | **report-only** | `~/.shared-ai-skills/qa-only/SKILL.md` |
| "test and fix", "sửa luôn đi", "fix what's broken" | **fix** | `~/.shared-ai-skills/qa/SKILL.md` |

**Default to report-only.** Fixing is a bigger action than testing, and a QA pass that
silently rewrites source is not a QA pass. If the request is ambiguous, report first and
offer to fix — that costs one message; an unwanted commit costs trust.

In fix mode the `shipping-changes` house rules apply in full: main only, operator's commit
identity, hooks must pass, one atomic commit per fix with re-verification after each.

## Evidence, or it didn't happen

Every reported defect carries: the URL/route, the exact steps, what was expected, what
happened, and an artifact — screenshot, console output, or HTTP status. A finding without
an artifact is a guess, and the operator will find out at the worst moment.

Equally: **do not report a defect you have not reproduced.** Re-run it once before writing
it down. Console noise from an unrelated extension is not a bug in the app.

## Scope honestly

State up front which routes and flows you covered and which you did not. "Tested the app"
when you clicked three pages is the failure mode that makes a green QA report worthless.
Upstream's tiers (quick / standard / exhaustive) are a useful frame — name the tier you
actually ran.

## Sibling lenses — different jobs, don't substitute

- **Visual/aesthetic defects** (spacing, hierarchy, heading wrap, chart overlap, layout
  slop) → `design-review`. Functional QA does not catch "it works but looks broken".
- **Accessibility correctness** → `a11y-audit`.
- **Displayed numbers being wrong** → `metric-integrity`. A page that renders perfectly
  while showing a fabricated KPI passes web QA and is still badly broken.
- **Writing reusable automation** rather than running a pass → `playwright-skill`.
- **Driving the browser directly** for a one-off check → `browsing-web`.

## Browser stack

One stack only: gstack's `browse`. Never the Chrome MCP, and not `agent-browser` — a
second browser stack is a second thing to debug for no gain.
