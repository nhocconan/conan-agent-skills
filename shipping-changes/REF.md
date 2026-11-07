---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:ship/SKILL.md
version: 1.0.0
fingerprint: sha256:b785363fea9ed6999863ab50d24128899e60fd811936d4b121e473a695cf3cef
reviewed: 2026-10-02
---

# Provenance

Wraps gstack's `ship` (1005 lines on 2026-11-05, 15 on-demand sections).
Upstream markdown is fetched into `.vendor/gstack/` by `refsync.py ensure` (gitignored,
files only, never a gstack install); the skill reads it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Upstream's flow requires a feature branch and opens a PR, and its commit step adds a `Co-Authored-By: Claude` trailer; house rules follow the repository's branch policy and the operator's commit identity. Its description now routes, so the wrap earns itself through overrides 1-4, not triggering.

## Overrides that MUST survive an upgrade

1. follow the repository's branch and review policy; never delete branches as cleanup
2. operator commit identity, no assistant attribution (upstream still adds a co-author trailer, ship/SKILL.md Step 15)
3. hooks must pass, never --no-verify
4. capture each gate's exit status before filtering its output
5. upstream Steps 4–11 are not run: no TESTING.md / CLAUDE.md `## Testing` writes, no
   coverage-driven test generation, no header-comment value cards (effective-development
   LEAN-SUITE, global Tests/Comments lines)

## Upstream sections this depends on

- "Section index"
- "sections/changelog.md"
- "sections/pr-body.md"

Override 3 (hooks) has no upstream counterpart to contradict; it stays as a house rule.

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.
