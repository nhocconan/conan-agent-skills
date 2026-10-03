---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:qa-only/SKILL.md
version: 1.0.0
fingerprint: sha256:ee78c0215c2d476a0a1ab736b24b6d8fd852439f57a0ec112111c9071076ce99
reviewed: 2026-10-02
secondary_source: github:garrytan/gstack@main:qa/SKILL.md
secondary_fingerprint: sha256:d303cda3491d56ed7202cdd290214316e29506b4a116e8bcc4bb66c0bde75ae9
---

# Provenance

Wraps **two** upstream skills that are one skill with a mode switch:
`qa-only` (621 lines on 2026-10-02, report) and
`qa` (817 lines on 2026-10-02, fix).
Neither is vendored — this skill routes to them by path.

`refsync.py` fingerprints both: `status` flags a changed `secondary_source`, and
`upgrade` writes it to `.upstream-preview-secondary.md` for review before `--accept`.

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
- "Browser Setup (conditional)"

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
