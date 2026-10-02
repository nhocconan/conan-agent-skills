---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:browse/SKILL.md
version: 2.0.0
fingerprint: sha256:6b3efbf1b38fab4349e5bbca7baec9a67b6d20bbc2f8c5b2b5a75bcfb6b9ebb3
reviewed: 2026-10-02
---

# Provenance

Wraps gstack's `browse` (457 lines on 2026-10-02, binary-backed).
Upstream markdown is fetched into `.vendor/gstack/` by `refsync.py ensure` (gitignored,
files only, never a gstack install); the skill reads it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Binary-backed (compiled browse + daemon) so it can only ever be wrapped, never forked. Upstream's description omits the two standing rules that cause real failures here.

## Overrides that MUST survive an upgrade

1. never the Chrome MCP (Claude in Chrome); on a host without a desktop the Playwright CLI loop in `sections/headless-server.md` is the default, and `browse` covers it where installed
2. do not stop to re-confirm an already-open logged-in session (upstream Rule 3's non-local mutation confirm still applies)
3. never trigger a modal dialog
4. bulk collection goes to resilient-data-harvest

## Locally owned, not upstream

`sections/headless-server.md` is this checkout's own content — upstream `browse`
covers driving a browser, not verifying a page from a desktop-less host. It must
survive any upgrade untouched. Its load-bearing facts, verified 2026-09-22 against
a `playwright run-server` on 1.62.1: the `connect()` rule is **major.minor must
match, patch may skew** (clients 1.62.0 and 1.62.1 accepted; 1.61.0 and 1.63.0
refused with `428 Precondition Required`), matching the documented "1.2.3 → is
compatible with 1.2.x"; and a headless launch on a host with no `DISPLAY`, no X
socket and a non-root user renders a full page with no `xvfb`. Re-check the version
rule at <https://playwright.dev/docs/api/class-browsertype> when Playwright moves.

## Upstream sections this depends on

- "BROWSER SETUP"
- "Rules for driving a real browser"
- "Browser fallback: gstack's own headless browser"
- "Translate the Aside scripts step by step"
- "Cookbook"
- "sections/command-list.md"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
