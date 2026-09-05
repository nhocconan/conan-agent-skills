---
name: browsing-web
description: >-
  Drives a real browser for anything on the web — opening pages, QA-testing a running app,
  filling forms, capturing screenshots, reading console and network output, and pulling data
  from logged-in sites. Use for every web interaction: "mở web", "check trang này", "test cái
  site", "chụp màn hình", "lấy data từ trang", "console log", or verifying a UI change
  actually renders. This is the only sanctioned browser path on this machine — the Chrome MCP
  tools must never be used.
---

# Browsing the web

Thin wrapper over gstack's `browse` procedure (markdown only — fetched into
`.vendor/gstack/`, not a gstack install). Upstream owns the commands; this file owns
the standing rules. If the compiled `browse` binary is not on this machine, still
never use the Chrome MCP; drive the browser with the tools this harness has.

## Standing rules

1. **`browse` is the only browser path.** Never use `mcp__claude-in-chrome__*` tools —
   this is a global instruction, not a preference.
2. **The operator's browser is usually already open and logged in.** When they say so,
   proceed — do not stop to re-confirm or ask for credentials. Halting mid-run to ask for
   something already provided wastes their time and tokens.
   *("tao mở sẵn browser cài sẵn chrome extension và mở sẵn kalodata rồi như mọi lần sao
   mày lại cứ dừng rồi hỏi làm tốn token tao.")*
3. **Session/profile matters.** If a task needs a specific browser profile, say so up
   front rather than failing ten minutes in.
4. **Never trigger a modal dialog** (`alert`, `confirm`, native prompt) — it blocks the
   automation channel and the session has to be rescued by hand.

## Getting the commands

Read `~/.conan-agent-skills/.vendor/gstack/browse/SKILL.md` — its **"SETUP (run this check BEFORE any
browse command)"** section first, then **"Most-Used Commands"**. Skip the binary setup
check when `browse` is not installed; the house rules above still apply.

For any command or snapshot flag beyond that table, read
`~/.conan-agent-skills/.vendor/gstack/browse/sections/command-list.md`. Upstream carved the full
command reference out of SKILL.md (v1.71), so it no longer arrives with the skill body —
read it rather than working from memory of the old inline list. `refsync.py ensure`
fetches both files.

## When the task is bulk data collection

Stop and use `resilient-data-harvest` instead. Anything paginated or long-running needs
per-item checkpointing, human-paced request rhythm and drift detection — a plain browse
loop will get the account rate-limited or throw away four hours of work on one dropped
connection.

## When the task is verifying a UI change

Capture the evidence, don't just assert. A screenshot or the console output is what makes
"it renders correctly" a fact instead of a claim. For visual quality judgements pair with
`a11y-audit` (correctness) and the frontend design skills (aesthetics).
