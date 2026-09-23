---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:ship/SKILL.md
version: 1.0.0
fingerprint: sha256:eb3c84ab37372374fc2bce07e1d8f57ca05b27a1a831e5092f48788b806a5854
reviewed: 2026-09-23
---

# Provenance

Wraps gstack's `ship` (1125 lines on 2026-09-23, binary-backed).
Upstream is **not** vendored — this skill points at it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Upstream's description is 31 chars ("Pre-landing PR review."-class) and cannot route. Its default flow creates a feature branch and a PR; the house rule is main-only with the operator's own commit identity.

## Overrides that MUST survive an upgrade

1. follow the repository's branch and review policy; never delete branches as cleanup
2. operator commit identity, no assistant attribution (upstream still adds a co-author trailer)
3. hooks must pass, never --no-verify
4. capture each gate's exit status before filtering its output

## Upstream sections this depends on

- "Section index"
- "Completeness Principle"
- "sections/changelog.md"
- "sections/pr-body.md"

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
