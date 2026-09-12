---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:ship/SKILL.md
version: 1.0.0
fingerprint: sha256:c357e51351d21639a6d368a87acf4b721a9c7aeda2abe7692b74a0dd699f641e
reviewed: 2026-09-12
---

# Provenance

Wraps gstack's `ship` (1122 lines, binary-backed).
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

- "Section index"
- "Completeness Principle"
- "sections/changelog.md"
- "sections/pr-body.md"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
