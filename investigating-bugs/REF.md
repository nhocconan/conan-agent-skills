---
mode: wrap
upstream: gstack
source: local:~/.shared-ai-skills/investigate/SKILL.md
version: 1.60.1.0
fingerprint: sha256:6296d2cedc1dda85d55044f68a52bce2f6dbf867e770e255a9d3bb2b67dec747
reviewed: 2026-07-25
---

# Provenance

Wraps gstack's `investigate` (1074 lines, binary-backed).
Upstream is **not** vendored — this skill points at it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Upstream's description does not state when to fire, so it under-triggers on the phrasings actually used ("sao lại lỗi", "lại bị nữa"). The reproduce-before-editing discipline and the fix-the-class handoff are local additions.

## Overrides that MUST survive an upgrade

1. reproduce before editing — never edit to test a theory
2. verify the presupposition first
3. verify by re-deriving, not recognising
4. escalate a repeated shape to bug-class-audits

## Upstream sections this depends on

- "Skill routing"
- "Confusion Protocol"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
