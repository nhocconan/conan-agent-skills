---
name: design-qa
description: Reviews a rendered UI with a designer's eye and counts what is wrong — spacing and alignment, hierarchy, controls and icons of mixed sizes, a lone boxed element that reads as an error, ungrouped list panels, walls of text, wrapping and overflow, collisions, dark-mode and phone defects, AI-slop layout — then fixes what it finds. Use as the critique step after any UI change, and when the user says "nhìn xấu", "nhìn stupid", "không hài hoà", "lố", "nhìn như lỗi", "icon nhỏ quá", "rớt hàng", "chữ bị đè", "lệch", "AI slop", "check giao diện", "does this look right", "design review", "design polish", or points at a screenshot of something that renders but looks wrong. Functional QA passes these defects — this is the lens that catches them.
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
   Report counts, never adjectives.
4. **Fix or report.** Review-only requests produce findings. When fixes are requested, fix the
   shared component before the page, re-shoot, re-probe. Commit and push need authorization.

## The recurring defects — check these every time

1. **Text that wraps or drops a line**: headings breaking to 4 lines, a title clipped mid-glyph.
2. **Content not using its width**: a block wrapping to a narrow column beside empty space. Fix
   the shared component, then add the source rule and rendered probe from
   [sections/text-width.md](sections/text-width.md).
3. **Collisions**: chart labels over the chart, a toast over the button the user needs.
4. **Layout imbalance**: controls eating a third of the screen while content gets a sliver.
5. **Inconsistency across pages**: same component, different padding, size or placement; page
   headers built three ways.
6. **AI-slop layout**: subtitle restating the title, decorative boxes with no information, a
   section header for one sentence.
7. **A bar of mismatched controls**: heights, icon sizes and gaps that differ inside one top bar
   or toolbar; glyphs small in big hit boxes. One height, one glyph size, one gap per cluster.
8. **The odd one out**: one element boxed, filled or coloured unlike its siblings (a flag in a
   bordered box, a lone pill). Users read it as a status or an error.
9. **Bare-list panels**: launchers, menus and drawers that list many items with no icons, group
   headings or descriptions.
10. **Prose walls and link farms**: help and docs pages that are paragraphs and links with no
    picture of the screen, no steps, no headings.

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
`anti-slop-review`: slop in the words. Optional deeper procedure: gstack `design-review` ([REF.md](REF.md)).
