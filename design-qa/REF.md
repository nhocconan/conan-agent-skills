---
mode: wrap
upstream: gstack
source: local:~/.shared-ai-skills/design-review/SKILL.md
version: 1.60.1.0
fingerprint: sha256:8a74c2068bea907e66f4d08facb5648e3cde52f2488b11b9037f40c97b4c2c37
reviewed: 2026-08-28
---

# Provenance

Wraps gstack's `design-review` (1994 lines,
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

## Upstream sections this depends on

- "When to invoke this skill"
- "Phases 1-6: Design Audit Baseline"
- "Design Critique Format"

## Decision log

**2026-07-25** — activated unwrapped, then wrapped within the hour after
`validate_skills.py` flagged the description as stating no WHEN. The mechanical check
outranked the eyeball judgment.
