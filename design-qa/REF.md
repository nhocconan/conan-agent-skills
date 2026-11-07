---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@5862765a20cd751b73e54fe85ffebd9e4da01e30:design-review/SKILL.md
tracking_source: github:garrytan/gstack@main:design-review/SKILL.md
version: 2.0.1
fingerprint: sha256:56c3dcd8b33a692f73c26fc7a3f01974cbf9c861b2c3b3f3cc5b66da14046b8e
reviewed: 2026-11-07
---

# Provenance

Wraps gstack's `design-review` (markdown cached in `.vendor/gstack/`, routed by path).

## Why this exists

Corrects a judgment made earlier the same day. `design-review` was first activated
unwrapped on the grounds that its 152-char description "already states what and when".
Re-reading it, that was wrong — it is entirely *what*:

> "Designer's eye QA: finds visual inconsistency, spacing issues, hierarchy problems,
> AI slop patterns, and slow interactions — then fixes them."

Its real trigger phrases ('Use when asked to "audit the design", "visual QA", "check if it
looks good"') sit in the **body**, which only loads after the skill has already fired. And
none of them match how visual defects actually get reported here — "nhìn stupid",
"rớt hàng ở heading", "lỗi UI layout AI slop à?", "chữ bị đè". Length fooled the first
review; the validator caught it.

## Overrides that MUST survive an upgrade

1. The ten recurring defect classes listed in SKILL.md — drawn from real reports on this
   operator's projects, not from upstream's checklist.
2. Always check **both themes and 390px**; most defects found here surfaced on a phone or
   in the untested theme.
3. Fixing is in scope, but under `shipping-changes` house rules.
4. Do not "improve" adjacent design nobody complained about.
5. Defect class 2 (text not using its width) is prevented mechanically, not reviewed:
   `sections/text-width.md` (root causes, probe, repo-check steps) and `scripts/narrow-wrap-probe.js`.
6. Critique is counted, not adjectival: `sections/rubric.md` (12 criteria + product-UI tells) and
   `scripts/layout-probe.js`.
7. Defect classes 7-10 (mismatched bar controls, odd one out, bare-list panels, prose walls) stay
   in SKILL.md; they are the chrome defects generated UI ships most.
8. Only upstream's "Phases 1-6" through "Design Critique Format" are read. Its
   `sections/test-bootstrap.md`, outside voices, helpers and automatic commits are skipped;
   browser capture and scoring use the local procedure.

## Upstream sections this depends on

- "Phases 1-6: Design Audit Baseline"
- "Design Critique Format"

## Decision log

**2026-11-03** - became step 5 of `frontend-design`'s loop as well as the complaint lens. Added the
counted rubric, the layout probe (synthetic good/bad fixtures: the bad page hits all 8 check
classes, the clean page returns none; 7 live product screens ran before the ragged-row check and
the icon-only glyph rule were added, so those two are fixture-tested only) and defect classes
7-10 from composition defects an operator caught after agents shipped them. Description now
triggers on "critique after any UI change" and on the complaint words used for those defects.
gstack `design-review` stays an optional deeper procedure; the skill runs without it. The wider
description is untested against real sessions: re-measure with the same transcript scan after a
week (baseline 0 of 6 significant UI sessions invoking a design skill before the first edit).

**2026-10-04** — class 2 kept recurring in one operator project after being listed here as a
review item; added root-cause table, a rendered DOM probe (threshold 0.85: a 90ch cap measured
69–75%, below the first 0.7 draft) and repo-check steps. Single-project evidence; the procedure is
framework-agnostic and the examples synthetic.

**2026-07-25** — activated unwrapped, then wrapped within the hour after
`validate_skills.py` flagged the description as stating no WHEN. The mechanical check
outranked the eyeball judgment.

## Accepted source review — 2026-11-07

The source commit pins the cache; `tracking_source` checks moving-branch freshness.
Reviewed source diffs. Local runtime, evidence, authority and gates override helpers.
