---
name: design-qa
description: >-
  Use when critiquing a UI after any change, or when the user says "nhìn xấu", "nhìn
  stupid", "không hài hoà", "lố", "nhìn như lỗi", "icon nhỏ quá", "rớt hàng", "chữ bị
  đè", "lệch", "AI slop", "check giao diện", "does this look right", "design review",
  "design polish", or shows a screenshot that looks wrong. Counts defects in a rendered
  UI with a designer's eye (spacing, alignment, mixed-size controls/icons, a lone boxed
  element, overflow, collisions, dark-mode/phone issues, AI-slop layout), then fixes
  them.
---

# Design QA

The critique lens for rendered screens. It answers "does this look right", with counts. It is
step 5 of `frontend-design`'s loop and the whole job when someone complains about a screen.

## Procedure

1. **Evidence first.** Screenshots at 1440×900 and 390×844, light and dark, plus each open state
   (menu, panel, dialog) involved. Recipe: `frontend-design` `sections/screenshots.md`.
2. **Probe.** Run [scripts/layout-probe.js](scripts/layout-probe.js) on each shot's page. It
   counts mixed control heights and icon sizes per bar, uneven gaps, small glyphs, lone styled
   controls, type and icon scale sprawl, overflow and cut text, prose walls, link farms and
   ungrouped panels. Each finding is a lead; confirm it on the screenshot.
3. **Score** the 12-criterion rubric and the product-UI tells in
   [sections/rubric.md](sections/rubric.md). Measure neighbours before judging a new element.
   On a requested UI review, also score [taste rows T1-T9](../frontend-design/sections/taste-gate.md).
   Report counts, never adjectives.
4. **Fix or report.** Review-only requests produce findings. When fixes are requested, fix the
   shared component before the page, re-shoot, re-probe. Commit and push need authorization.

## The recurring defects — check these every time

The [rubric](sections/rubric.md) owns most of them: mismatched controls (row 5), the odd one out
(6), bare-list panels (4), prose walls (10), AI-slop copy (9), imbalance (3, 8) and cross-page
inconsistency (step 2, neighbours first). Three defects the rubric lacks:

1. **Text that wraps or drops a line**: headings breaking to 4 lines, a title clipped mid-glyph.
2. **Content not using its width**: a block wrapping to a narrow column beside empty space. Fix
   the shared component, then add the source rule and rendered probe from
   [sections/text-width.md](sections/text-width.md).
3. **Collisions**: chart labels over the chart, a toast over the button the user needs.

## Rules

- **Look at the rendered thing.** A visual defect is a fact about pixels; the screenshot is
  the proof.
- **Both themes, both widths, every open state.** Most defects surface on a phone, in the untested
  theme, or inside a panel nobody opened.
- **The builder does not grade their own screen.** Run this as a fresh reader given the shots and
  the rubric, not the builder's verdict.
- **Do not "improve" adjacent design** nobody asked about; list it as a finding.

## Neighbours

`frontend-design` owns the build loop. `impeccable critique` adds heuristic scoring; `impeccable
polish`, `layout`, `typeset` are deeper fix passes. `web-qa`: does it work. `a11y-audit`: WCAG.
`anti-slop-review`: slop in the words. Optional depth: `../.vendor/gstack/design-review/SKILL.md`, **"Phases 1-6"** through
**"Design Critique Format"** ([REF.md](REF.md)). Capture/score/fix locally; skip startup,
helpers, installs, outside voices, bootstrap and auto-commit/revert.
