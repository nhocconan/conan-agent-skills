---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@44170d67916dc80a008803f7b3f7cbf7dbe32ea7:ship/SKILL.md
tracking_source: github:garrytan/gstack@main:ship/SKILL.md
version: 1.0.1
fingerprint: sha256:a91073b4dda543940b0a1a213d2d3826e9d5cb38c43e856eadb5463be26d1b5f
reviewed: 2026-11-18
---

# Provenance

Wraps gstack's `ship` (976 lines at the pinned source).
Upstream markdown is fetched into `.vendor/gstack/` by `refsync.py ensure` (gitignored,
files only, never a gstack install); the skill reads it by path, so its bulk loads only
when the skill actually fires.

## Why this exists

Upstream's flow requires a feature branch and opens a PR, and its commit step adds a `Co-Authored-By: Claude` trailer; house rules follow the repository's branch policy and the operator's commit identity. Its description now routes, so the wrap earns itself through overrides 1-4, not triggering.

## Overrides that MUST survive an upgrade

1. follow the repository's branch and review policy; never delete branches as cleanup
2. operator commit identity, no assistant attribution (upstream Step 15 delegates the trailer to Step 16's release helper)
3. hooks must pass, never --no-verify
4. capture each gate's exit status before filtering its output
5. upstream ship orchestration/helpers are not run: no TESTING.md / CLAUDE.md `## Testing` writes, no
   coverage-driven test generation, no header-comment value cards (effective-development
   LEAN-SUITE, global Tests/Comments lines)

## Upstream sections this depends on

- "Section index"
- "sections/changelog.md"
- "sections/pr-body.md"

Override 3 (hooks) has no upstream counterpart to contradict; it stays as a house rule.

If `refsync.py status` reports one of these has vanished, the wrapper's routing
instructions are stale and must be re-pointed before the skill is trusted again.

## Accepted source review — 2026-11-07

Pinned source and markdown cache use the commit in `source`; this is a frozen
compatibility baseline; `tracking_source` separately checks the moving branch.
Reviewed entrypoint/section changes against the previous cache; local runtime,
evidence, authority and repository gates take precedence over upstream helpers.
