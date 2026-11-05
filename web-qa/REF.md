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
`qa-only` (342 lines on 2026-11-05, report) and
`qa` (530 lines on 2026-11-05, fix).
Both are fetched into `.vendor/gstack/`; this skill routes to them by path. Upstream qa-only now also forbids invoking /qa itself, which matches override 1: a fix is a separate, requested run.

`refsync.py` fingerprints both: `status` flags a changed `secondary_source`, and
`upgrade` writes it to `.upstream-preview-secondary.md` for review before `--accept`.

## Why this exists

Upstream's descriptions are one-liners ("Fix browser/API/CLI/job/worker/webhook bugs. (gstack)",
"Report ... bugs."). Neither names the phrasings actually used ("test cái này",
"check xem chạy được không"), so both under-trigger.

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

- "Section index" (qa-only, qa)
- "Browser Setup (conditional)" (qa-only)
- "sections/browser-setup.md" (qa)

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
