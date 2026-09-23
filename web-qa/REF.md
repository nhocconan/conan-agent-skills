---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:qa-only/SKILL.md
version: 1.0.0
fingerprint: sha256:b309d22f376a1620dd022989a1e212e0713ee0ba82a81696a8e3c62d00b10102
reviewed: 2026-09-23
secondary_source: github:garrytan/gstack@main:qa/SKILL.md
secondary_fingerprint: sha256:dd68e0d4d65e51f319199d2c4c1ef15624a2e9d13d7cb45ffca5a5837e727779
---

# Provenance

Wraps **two** upstream skills that are one skill with a mode switch:
`qa-only` (984 lines, report) and
`qa` (960 lines, fix).
Neither is vendored — this skill routes to them by path.

`refsync.py` fingerprints the primary (`qa-only`) only. The secondary is recorded here for
manual review; if `qa`'s procedure changes materially, re-check this wrapper by hand.

## Why this exists

Upstream's descriptions cannot route: `qa` is 69 chars, `qa-only` is 32
("Report-only QA testing. (gstack)"). Neither says when to fire, so both under-trigger on
the phrasings actually used ("test cái này", "check xem chạy được không").

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

## Upstream sections this depends on

- "When to invoke this skill"
- "Preamble (run first)"

## Decision log

**2026-07-25 — `dogfood` dropped.** It is the same job as `qa-only` (functional QA,
report-only) but runs on `agent-browser` (homebrew) instead of gstack `browse`. Two
browser stacks is two things to debug, and the global rulebook already mandates browse.
Revealed preference decided it: browse 56 invocations, dogfood 0 with a symlink broken
for a month and never missed. Its only real edge was repro *video*; browse can capture
that. Source remains at `~/.agents/skills/dogfood` if the decision is ever revisited.

**2026-07-25 — `design-review` activated unwrapped.** Different lens (visual, not
functional), and its 152-char description already states what and when. A wrapper would
be maintenance tax with no triggering gain — a wrap must earn itself.
