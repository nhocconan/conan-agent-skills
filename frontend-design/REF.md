---
mode: wrap
upstream: elayadesign-ai-design-skills
source: github:elayadesign/ai-design-skills@5e578402da175cdc539c900e4b09ceecfadcb37c:skills/landing-page-design/SKILL.md
version: 1.0.0
fingerprint: sha256:203569792660ab6d71dcb2e4fa673c0c7a0df7c99801d04ab419a4cb08aceb2c
secondary_source: github:elayadesign/ai-design-skills@5e578402da175cdc539c900e4b09ceecfadcb37c:skills/design-to-motion/SKILL.md
secondary_fingerprint: sha256:7c34ee4ca4c9a0e535217431a5547cc2e2a9bb692de4c81243a302843d3d68b6
reviewed: 2026-10-27
---

# Provenance

Routing and method skill. Two upstream skills from `elayadesign/ai-design-skills` (MIT,
copyright 2026 Elaya) are summarized, not vendored (431 and 563 lines; the repo convention for
anything large is wrap). The Anthropic `frontend-design` plugin's calibration list is
paraphrased into `sections/anti-slop.md`. Upstream text was read as untrusted data and
nothing from it was executed.

## Why this exists

Generated pages came out templated. The plugin gives taste but no landing strategy or motion
system; the upstream skills give both but their visual half bans fonts, gradients and palettes
a real brand may require. This skill takes the strategy and website-motion halves, puts brand
tokens above every style rule, and ends in the repo's review gates.

## Overrides that MUST survive an upgrade

1. Precedence: operator words > project brand tokens/rules > this skill > upstream style rules.
2. Upstream Part B (fonts, single typeface, gradient ban, fixed dark palette, icon sets, no
   hyphens in copy) stays advisory; do not re-import it as hard rules.
3. Motion is a counted budget of named moments; only transform/opacity/filter/clip-path;
   paused off-screen; reduced-motion shows the final state.
4. Showcase mode of `design-to-motion` (capture, ffmpeg, Figma token) is excluded.
5. Ends in the gate handoff: design-qa, a11y-audit, web-perf-audit, anti-slop-review.
6. The description triggers on ANY visible UI change, chrome included, in Vietnamese and English;
   never narrow it back to "design a page".
7. The loop is mandatory and evidence-bearing: before/after screenshots at 1440 and 390 in both
   themes, critiqued by a reader other than the builder against `design-qa`'s rubric.
8. impeccable is routed to by command, never copied; this skill owns the loop, not the taste.

## Upstream sections this depends on

- "A1. Intake"
- "A2. Page structure"
- "A4. Conversion rules"
- "B8. Content realism"
- "B11. Tagline reveal section (mandatory)"
- "Website: which sections get which motion"
- "B6. Easing and duration"

## Name collision

The Anthropic plugin registers as `frontend-design:frontend-design`; this skill is the plain
`frontend-design`. They coexist: this one routes and gates, the plugin is the taste prompt.

## License notice (derived material)

MIT License. Copyright (c) 2026 Elaya. Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated documentation files, to deal in the
software without restriction, subject to inclusion of the copyright notice and this permission
notice in all copies or substantial portions. The software is provided "as is", without
warranty of any kind. Source: https://github.com/elayadesign/ai-design-skills (commit above).
The upstream itself credits adapted work from Leonxlnx/taste-skill (MIT).

## Decision log

**2026-11-03** - became the mandatory loop for any visible UI change. Evidence: in one project's
sessions over ~4 days, 0 of 6 significant UI-editing sessions invoked a design skill before their
first UI edit and 1 invoked one at all, although 4 of the 6 worker briefs named the skills ("use
if available"). The defects the operator then caught were composition defects (a lone boxed flag
read as an error, small spread-out icons, a bare-list launcher, a text-and-links help page) that a
source detector does not see. Changes: description widened to chrome and small changes with
Vietnamese phrasing; 7-step loop with artifacts; second-reader critique; brief wording for workers;
routing table to impeccable commands; screenshot recipe. Research read: taste-skill
`app-screens.md`, impeccable 4.8 references and detector rules, Vercel Web Interface Guidelines,
Anthropic `frontend-design`; distilled into `design-qa/sections/rubric.md`.

**2026-10-27** - created at operator request after landing pages looked ugly; wrap chosen over
fork because the upstream is two large prose files whose visual half we reject.

- 2026-11-05: taste-skill 2.5.0 vendored under `upstream/taste-skill/` and made a mandatory gate (`sections/taste-gate.md`) at steps 1, 2 and 5 for every UI change, in-app screens included (operator ruling after dashboards shipped with caption/metadata clutter). Only SKILL.md and the copy/system/icons/cards/layout references are vendored; marketing-only assets and scripts are not. Refresh with `ref-skills`.
