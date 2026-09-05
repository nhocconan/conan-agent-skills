---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:browse/SKILL.md
version: 1.60.1.0
fingerprint: sha256:88fc9376988d8d1bd5e2b913a36d0b4f7ba536de6a7c19984b535b7428ffe199
reviewed: 2026-08-28
---

# Provenance

Wraps gstack's `browse` (1022 lines, binary-backed).
Upstream is **not** vendored — this skill points at it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Binary-backed (compiled browse + daemon) so it can only ever be wrapped, never forked. Upstream's description omits the two standing rules that cause real failures here.

## Overrides that MUST survive an upgrade

1. browse is the only browser path — never the Chrome MCP
2. do not stop to re-confirm an already-open logged-in session
3. never trigger a modal dialog
4. bulk collection goes to resilient-data-harvest

## Upstream sections this depends on

- "SETUP (run this check BEFORE any browse command)"
- "Most-Used Commands"
- carved file: `browse/sections/command-list.md` (v1.71) — the full command reference

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
