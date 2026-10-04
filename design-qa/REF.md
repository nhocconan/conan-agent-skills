---
mode: wrap
upstream: gstack
source: github:garrytan/gstack@main:design-review/SKILL.md
version: 2.0.0
fingerprint: sha256:411b146216842a77d757c6483ffa1163c3e142b54c71ba1f7797f39e601fb000
reviewed: 2026-10-02
---

# Provenance

Wraps gstack's `design-review` (1897 lines in the 2026-09-05 vendored copy; 1940 upstream on 2026-10-02,
binary-backed). Not vendored — routed to by path.

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

1. The six recurring defect classes listed in SKILL.md — drawn from real reports on this
   operator's projects, not from upstream's checklist.
2. Always check **both themes and 375px**; most defects found here surfaced on a phone or
   in the untested theme.
3. Fixing is in scope, but under `shipping-changes` house rules.
4. Do not "improve" adjacent design nobody complained about.
5. Defect class 2 (text not using its width) is prevented mechanically, not reviewed:
   `sections/text-width.md` (root causes, probe, repo-check steps) and `scripts/narrow-wrap-probe.js`.

## Upstream sections this depends on

- "When to invoke this skill"
- "Phases 1-6: Design Audit Baseline"
- "Design Critique Format"

## Decision log

**2026-10-04** — class 2 kept recurring in one operator project after being listed here as a
review item; added root-cause table, a rendered DOM probe (threshold 0.85: a 90ch cap measured
69–75%, below the first 0.7 draft) and repo-check steps. Single-project evidence; the procedure is
framework-agnostic and the examples synthetic.

**2026-07-25** — activated unwrapped, then wrapped within the hour after
`validate_skills.py` flagged the description as stating no WHEN. The mechanical check
outranked the eyeball judgment.
