---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:ship/SKILL.md
version: 1.0.0
fingerprint: sha256:b785363fea9ed6999863ab50d24128899e60fd811936d4b121e473a695cf3cef
reviewed: 2026-10-02
---

# Provenance

Wraps gstack's `ship` (1212 lines on 2026-10-02, binary-backed).
Upstream markdown is fetched into `.vendor/gstack/` by `refsync.py ensure` (gitignored,
files only, never a gstack install); the skill reads it by path, so its bulk loads only
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
