---
mode: wrap
upstream: gstack
source: local:~/.shared-ai-skills/ship/SKILL.md
version: 1.60.1.0
fingerprint: sha256:fad896a79f2b4e527fb0a908de90d2fceed3bd0351d2d1a035b8450006ff262f
reviewed: 2026-08-28
---

# Provenance

Wraps gstack's `ship` (1417 lines, binary-backed).
Upstream is **not** vendored — this skill points at it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Upstream's description is 31 chars ("Pre-landing PR review."-class) and cannot route. Its default flow creates a feature branch and a PR; the house rule is main-only with the operator's own commit identity.

## Overrides that MUST survive an upgrade

1. main only — never create a feature branch
2. operator commit identity, no assistant attribution
3. hooks must pass, never --no-verify
4. never pipe the gate through tail/head/grep

## Upstream sections this depends on

- "Section index — Read each section when its situation applies"
- "Completeness Principle"
- carved files: `ship/sections/changelog.md`, `ship/sections/pr-body.md` (v1.71)

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
