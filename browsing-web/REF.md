---
mode: wrap
upstream: gstack
source: local:~/.shared-ai-skills/browse/SKILL.md
version: 1.60.1.0
fingerprint: sha256:a33632d9948aa65e207fcdcf6bd6c39d46fee8a4028cafc56a472481609d106f
reviewed: 2026-07-25
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
- "Skill routing"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
