---
mode: wrap
upstream: gstack
source: local:~/.shared-ai-skills/investigate/SKILL.md
version: 1.60.1.0
fingerprint: sha256:87a4dcf61b4b8a89dd82b9e62a4a0927db373a98fce2324a4d50fb4a2d955e70
reviewed: 2026-08-28
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

- "Phase 1: Root Cause Investigation"
- "Phase 2: Pattern Analysis"
- "Confusion Protocol"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
