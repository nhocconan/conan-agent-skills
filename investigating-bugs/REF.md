---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:investigate/SKILL.md
version: 1.0.0
fingerprint: sha256:2257118effdc9afcd0cd2a688e2342e99f6b681dea6aa7e836b17ac4871938bc
reviewed: 2026-10-02
---

# Provenance

Wraps gstack's `investigate` (719 lines on 2026-10-02, binary-backed).
Upstream markdown is fetched into `.vendor/gstack/` by `refsync.py ensure` (gitignored,
files only, never a gstack install); the skill reads it by path, so its bulk loads only
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
