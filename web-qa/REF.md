---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@5862765a20cd751b73e54fe85ffebd9e4da01e30:qa-only/SKILL.md
tracking_source: github:garrytan/gstack@main:qa-only/SKILL.md
version: 1.0.1
fingerprint: sha256:1130fd5a80b02eea003d5cd8370e8eab524f2a6bf14a8caf262650ce64606c26
reviewed: 2026-11-07
secondary_source: github:garrytan/gstack@5862765a20cd751b73e54fe85ffebd9e4da01e30:qa/SKILL.md
secondary_tracking_source: github:garrytan/gstack@main:qa/SKILL.md
secondary_fingerprint: sha256:1cda78da8e01d074966334d1ff3c3103f1a78732f6d7ecf797df5b8cbf6ce540
---

# Provenance

Wraps **two** upstream skills that are one skill with a mode switch:
`qa-only` (report) and `qa` (fix), at the same pinned commit.
Both are fetched into `.vendor/gstack/`; this skill routes to them by path. Upstream qa-only now also forbids invoking /qa itself, which matches override 1: a fix is a separate, requested run.

`refsync.py` fingerprints both: `status` flags a changed `secondary_source`, and
`upgrade` writes it to `.upstream-preview-secondary.md` for review before `--accept`.

## Why this exists

Upstream now has task-oriented descriptions; the wrapper preserves local phrases
("test cái này", "check xem chạy được không") and makes repair authority explicit.

Splitting one job across two ~1,000-line skills is upstream's packaging, not a real
distinction. The distinction that IS real — *am I allowed to change your code* — was
invisible in the descriptions and is now the first decision this skill makes.

## Overrides that MUST survive an upgrade

1. **Report-only is the default.** Fix only when fixing was explicitly requested.
2. In fix mode, `shipping-changes` house rules apply (repository branch policy,
   operator identity, hooks pass); commit/push only when authorized.
3. Every finding carries an artifact; nothing is reported unreproduced.
4. State the scope actually covered and the tier actually run.
5. Use the user-selected or project-approved available browser; `browsing-web` owns
   session and evidence discipline.
6. Fix-mode regression tests follow `effective-development/LEAN-SUITE.md`; upstream's 8a.5
   attribution comment block is not written into code (2026-11-07: it cites ids and dates,
   which the global comment rule and `slop_audit.py` W7 reject). Nor are
   `sections/test-bootstrap.md`'s TESTING.md / CLAUDE.md `## Testing` writes (:29, :84): the
   test command is one `AGENTS.md` line, with no coverage target.

## Upstream sections this depends on

- "Section index" (qa-only, qa)
- "sections/exploratory.md" (qa-only, qa)
- "sections/reporting.md" (qa-only)
- "sections/scope.md" and "sections/qa-patterns.md" (qa)

## Decision log

Entries below predate `design-qa` (2026-07-25, later the same day); where they say
design-review runs unwrapped, `design-qa` supersedes them.

**2026-07-25 — `dogfood` dropped.** It is the same job as `qa-only` (functional QA,
report-only) but runs on `agent-browser` (homebrew) instead of gstack `browse`. Two
browser stacks is two things to debug, and the global rulebook already mandates browse.
Revealed preference decided it: browse 56 invocations, dogfood 0 with a symlink broken
for a month and never missed. Its only real edge was repro *video*; browse can capture
that. Source remains at `~/.agents/skills/dogfood` if the decision is ever revisited.

**2026-07-25 — `design-review` activated unwrapped.** Different lens (visual, not
functional), and its 152-char description already states what and when. A wrapper would
be maintenance tax with no triggering gain — a wrap must earn itself.

Shared host: one browser, a context per tab/test, production build: [SHARED-HOST](../effective-development/SHARED-HOST.md).

## Accepted source review — 2026-11-07

Pinned source and markdown cache use the commit in `source`; this is a frozen
compatibility baseline; `tracking_source` separately checks the moving branch.
Reviewed entrypoint/section changes against the previous cache; local runtime,
evidence, authority and repository gates take precedence over upstream helpers.
