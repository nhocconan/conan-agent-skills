---
name: frontend-design
description: Mandatory loop for ANY change a user will see in a web UI - a new or restructured page, component, layout, form, table, dialog, empty state, header, top bar, nav, sidebar, menu, panel, launcher, icon, theme or spacing tweak, help or docs page, landing page, redesign. Use before editing markup, .tsx/.jsx/.vue or CSS that renders, including "small" chrome changes ("thêm nút", "sửa header", "đổi icon", "làm trang mới", "sửa giao diện", "chỉnh layout", "làm lại top bar", "trang help", "UI/UX", "đẹp hơn", "nhìn xấu quá làm lại", "landing page", "dashboard layout").
---

# Frontend design

The build loop for anything a user sees. Reviewing a page someone complained about is `design-qa`;
this skill runs before and while the change is built, and it ends in that review. Small is not an
exemption: chrome tweaks (a toggle, an icon, a menu) are where unreviewed defects ship most.

## Who does what

| Need | Owner |
|---|---|
| The loop, evidence, and the gate below | this skill |
| The taste bar: plain copy, one system, no captions under visuals, equal edges, icon-only controls, metadata is not content | [sections/taste-gate.md](sections/taste-gate.md) (taste-skill, vendored in `upstream/taste-skill/`) - on demand: a new design or redesign, a UI or design review, or when the operator asks for it |
| Counted critique of rendered screens, defect fixing | `design-qa` (its `sections/rubric.md`, `scripts/layout-probe.js`) |
| UX plan for a new surface; heuristic critique; polish, layout, typeset, clarify, adapt, harden passes; DESIGN.md from code | `impeccable` commands `shape`, `critique`, `polish`, `layout`, `typeset`, `clarify`, `adapt`, `harden`, `document` |
| Mechanical tells (gradient text, glow, contrast, side-tab, cramped padding) | impeccable's detector: the edit hook scans source; `impeccable detect <url>` scans the rendered DOM. Neither judges composition: a lone boxed flag, tiny spread-out icons or a bare-list panel pass it |
| WCAG, speed, admin baseline, charts | `a11y-audit`, `web-perf-audit`, `admin-crud-standards`, `dataviz` / project chart package |

Precedence: operator's words > project design system and DESIGN.md > this skill > impeccable and
upstream style rules. The Anthropic plugin `frontend-design:frontend-design` may also load: this loop wins on conflict; the plugin supplies marketing aesthetic only. Never add a font, colour, size or radius the system does not own. The taste gate runs only for a new design or redesign, a UI or design review, or when the operator asks for it; other UI changes skip it.

## The loop - every step leaves an artifact

1. **Ground.** Read DESIGN.md (and PRODUCT.md if present), the tokens, and the components already
   used for this job. When the taste gate applies, read [sections/taste-gate.md](sections/taste-gate.md). Shoot the current screen and two siblings ("before"). Write down the
   neighbours' numbers: control height, icon size, gap, radius, type sizes. New elements match
   them unless the plan says why not.
2. **Plan** (10 lines, shown before code): the surface's one job and mode (work screen, reading
   page, persuasion page); what changes and which existing components carry it; the inherited
   sizes; the states (empty, loading, error, long Vietnamese text, one item, many, no permission);
   the single place emphasis goes. Check the plan against the tells in `design-qa`'s rubric and
   [sections/anti-slop.md](sections/anti-slop.md); revise any hit. When the taste gate applies, add a "Taste" line: T1-T9 hits and fixes.
3. **Build** with the system: kit components, tokens, icon set, i18n catalog. Paths:
   [sections/app-pages.md](sections/app-pages.md) for work screens,
   [sections/landing-page.md](sections/landing-page.md) +
   [sections/motion.md](sections/motion.md) for marketing pages.
4. **Shoot** per [sections/screenshots.md](sections/screenshots.md): 1440×900 and 390×844, light
   and dark, every open state touched, one edge state; run `layout-probe.js` on each.
5. **Critique by a second reader.** A fresh subagent (or `impeccable critique`) gets the shots,
   probe output and siblings, not the builder's verdict, and scores `design-qa`'s 12-criterion
   rubric (plus taste rows T1-T9 when the gate applies) with counts. The builder's own PASS does not count: builders pass their own pages.
6. **Iterate.** Fix every FAIL, shared component first; re-shoot what changed; up to three rounds,
   then report what is still open and why.
7. **Report**: plan, before/after paths per viewport and theme, the rubric line with counts, gates
   run (`a11y-audit` always for new controls; `web-perf-audit` for motion, media or heavy charts;
   `anti-slop-review` for copy), and what was skipped.

Trivial change (one string, one token value, no layout change): steps 4, 5 and 7 at the affected
viewport. Anything that adds, moves or resizes an element runs the full loop.

## Delegating UI work

A worker brief carries the loop as acceptance, not as advice: "return before/after screenshot
paths (1440/390, light/dark) and the rubric line from a reader other than you". "Use the design
skills if available" gets skipped. The lead reads the shots before accepting.

[REF.md](REF.md) holds provenance, the overrides that survive upgrades and the decision log.
