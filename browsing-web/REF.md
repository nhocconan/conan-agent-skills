---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:browse/SKILL.md
version: 2.0.0
fingerprint: sha256:851aab576c9c2bd38561117323add4458f72521f18939955f22c28b77e254c44
reviewed: 2026-09-12
---

# Provenance

Wraps gstack's `browse` (443 lines, binary-backed).
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

- "BROWSER SETUP"
- "Rules for driving a real browser"
- "Browser fallback: gstack's own headless browser"
- "Translate the Aside scripts step by step"
- "Cookbook"
- "sections/command-list.md"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
