---
name: browsing-web
description: >-
  Drive an available browser for page interaction, screenshots, console/network
  inspection, and authenticated UI checks. Use for browser tasks such as "mở web",
  "chụp màn hình", or verifying a rendered change. Prefer the user's selected session.
---

# Browsing the web

Thin wrapper over gstack's `browse` procedure (markdown only — fetched into
`.vendor/gstack/`, not a gstack install). Upstream owns the commands; this file owns
the standing rules. Resolve paths relative to this checkout; if the optional
upstream files or binary are unavailable, use the active harness's documented browser.

## Standing rules

1. **Use the user-selected browser and project-approved tools.** Prefer an available
   purpose-built connector for data tasks; follow the active tool's instructions.
2. **The operator's browser is usually already open and logged in.** When they say so,
   proceed — do not stop to re-confirm or ask for credentials. Halting mid-run to ask for
   something already provided wastes their time and tokens.
   *("tao mở sẵn browser cài sẵn chrome extension và mở sẵn kalodata rồi như mọi lần sao
   mày lại cứ dừng rồi hỏi làm tốn token tao.")*
3. **Session/profile matters.** If a task needs a specific browser profile, say so up
   front rather than failing ten minutes in.
4. Handle dialogs through supported browser APIs. Do not inject unnecessary blocking dialogs.

## Getting the commands

Read `../.vendor/gstack/browse/SKILL.md` — its **"BROWSER SETUP"** probe, then the driver
it selects. `READY` (macOS, Aside open) → **"Rules for driving a real browser"** and the
**"Cookbook"** script shapes. `NEEDS_ASIDE` / `ASIDE_NOT_RUNNING` → **"Browser fallback:
gstack's own headless browser"** and **"Translate the Aside scripts step by step"**, which
maps every cookbook step onto a `$B` command — the normal path on Linux. Headless means no
user cookies, so standing rule 2 does not apply there: an authenticated page needs a
cookie import or `$B handoff "<why>"`.

For any command or snapshot flag beyond that table, read
`../.vendor/gstack/browse/sections/command-list.md` — the full generated reference, carved
out of SKILL.md upstream. `refsync.py ensure` fetches both files.

## When the task is bulk data collection

Stop and use `resilient-data-harvest` instead. Anything paginated or long-running needs
per-item checkpointing, human-paced request rhythm and drift detection — a plain browse
loop will get the account rate-limited or throw away four hours of work on one dropped
connection.

## When the task is verifying a UI change

Capture the evidence, don't just assert. A screenshot or the console output is what makes
"it renders correctly" a fact instead of a claim. For visual quality judgements pair with
`a11y-audit` (correctness) and the frontend design skills (aesthetics).
