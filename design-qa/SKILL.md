---
name: design-qa
description: Reviews a rendered UI with a designer's eye — spacing and alignment, visual hierarchy, inconsistent components, text that wraps or overflows, charts and tables that collide, and AI-slop layout patterns — then fixes what it finds. Use when the user says "nhìn xấu", "nhìn stupid", "layout bị lỗi", "rớt hàng", "chữ bị đè", "wrap không full width", "AI slop", "check giao diện", "does this look right", "design polish", or points at a screenshot of something that renders but looks wrong. Functional QA passes these defects — this is the lens that catches them.
---

# Design QA

Wrapper over gstack's `design-review`. Upstream owns the audit procedure; this file exists
because upstream's description lists only *what* it does, so it never fires on the language
actually used to report a visual defect.

## The recurring defects — check these every time

These come from real reports on this operator's own projects, and they repeat:

1. **Text that wraps or drops a line** — headings breaking to 4 lines, a subtitle wrapping
   mid-phrase, a card title clipped mid-glyph. Check at the real breakpoints, not just the
   width your browser happens to be.
2. **Content not using its width** — a block wrapping to a narrow column while empty space
   sits beside it.
3. **Collisions** — chart labels over chart, text over a circle, a toast covering the
   button the user needs, a filter row colliding with a date picker.
4. **Layout imbalance** — everything pushed left with dead space right; controls eating a
   third of the screen while the actual content gets a sliver.
5. **Inconsistency across pages** — same component, different padding/size/placement; page
   titles that don't follow one naming pattern.
6. **AI-slop layout** — a subtitle that restates the title, decorative boxes with no
   information, a section header for one sentence of content.

## Rules

- **Look at the rendered thing, not the source.** A visual defect is a fact about pixels.
  Capture a screenshot; that is the evidence and the before/after proof.
- **Check both themes and the small breakpoint.** Light and dark, and 375px wide. Most
  reported defects here were found on a phone or in the theme nobody tested.
- **Fixing is in scope for this skill** (unlike `web-qa`, which reports by default) — but
  the `shipping-changes` house rules still apply: main only, operator identity, hooks pass,
  atomic commits with a re-render check after each.
- **Do not "improve" adjacent design** that nobody complained about. Fix the defect.

For the audit procedure, checklist and screenshot mechanics, read
`~/.shared-ai-skills/design-review/SKILL.md` — its **"When to invoke this skill"** and
**"Skill routing"** sections.

## Sibling lenses

`web-qa` — does it *work* (this skill asks: does it *look right*).
`a11y-audit` — contrast, focus, touch targets: correctness, not taste.
`anti-slop-review` — slop in the *words*; this covers slop in the *layout*.
`interactive-course-builder` — for course pages, its design system is the authority.
