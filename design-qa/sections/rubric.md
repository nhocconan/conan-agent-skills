# Critique rubric for a rendered screen

## Contents
- How to run it
- The rubric (12 criteria)
- Product-UI tells
- Report format

Applied by a reader who did not build the screen, to screenshots at 1440×900 and 390×844 in
light and dark, plus every open state (menu, panel, dialog) the change touched. Each criterion is a
pass/fail check with a count. "Looks clean" is not a result; "3 control heights in one bar" is.

## How to run it

1. Collect the evidence: the screenshots, the `layout-probe.js` output for each
   (`../scripts/layout-probe.js`), and two sibling screens of the same product for comparison.
2. Measure the neighbours first. A new element passes only if it matches what already sits next to
   it: same control height, same icon size, same gap, same radius, same type role.
3. Walk the 12 criteria in order. Mark each PASS, FAIL (with the count and the element) or N/A.
4. Run the tells list. Each hit is FAIL unless the brief or the design system names it as a choice.
5. Squint test last: blur the 1440 shot (or view it at 25%). Name the first thing the eye lands on.
   If it is not the screen's primary answer or action, hierarchy fails.

## The rubric (12 criteria)

| # | Criterion | FAIL when (count it) |
|---|---|---|
| 1 | **Spacing rhythm** | a gap not on the spacing scale; two gutter values in one grid (12 and 16); space inside a group ≥ space between groups; less space above a heading than below it |
| 2 | **Alignment** | more than 3 distinct text left edges in a column; cards in one row with ragged bottom edges; baselines in one row that differ; figures not right-aligned with tabular digits |
| 3 | **Hierarchy** | the squint test lands on chrome, decoration or a secondary action, or shows more than 3 masses; the figure that answers the page title is not the largest (≥1.3× its siblings); a title and its subtitle at one weight |
| 4 | **Grouping** | a list of 9+ items with no group label or separator; related controls split across the screen; unrelated controls touching |
| 5 | **Control consistency** | more than one control height in one row or bar (desktop range 28-40px); more than one icon size per bar; nav icons outside 16-20px or inline icons outside 12-14px; an icon-only glyph under ~40% of its hit box; icon-to-label gap outside ~8-10px; mixed icon sets or stroke weights; hit boxes under 24px (WCAG 2.5.8) or under the project's touch floor on phones |
| 6 | **Odd one out** | a single element in a row styled unlike its siblings (a boxed flag, a filled pill, a red dot) that is not the primary action or a real alert. Users read a lone emphasized element as a status or an error |
| 7 | **States** | empty, loading, error, long text, one item, many, no-permission not designed; a zero shown as a dash or a missing value shown as 0; an empty block that loses its frame or says nothing about the next step; loading that shifts the layout or flashes for under ~300ms; an error that replaces the page instead of staying in its block with a retry; a delta coloured by direction rather than good/bad, or coloured at zero |
| 8 | **Density** | the first viewport at 1440 shows less than one task unit (a table needs rows, a report its first numbers); a blank band over ~40px inside a card; a short list or narrow table stretched across the full canvas instead of paired with a neighbour; or the opposite, groups with no air between them |
| 9 | **Copy** | a label that is not the user's word; mixed languages in chrome; a subtitle restating the title; a button without a verb; truncation that hides the distinguishing part of a label |
| 10 | **Prose pages** | a help or docs page with a run of ≥160 words and no heading, figure, list or table; more links than sentences; a how-to with no picture of the screen it describes |
| 11 | **Theme parity** | in dark: a hard-coded white or black surface, a shadow that turns into a smudge, a border that disappears, contrast that passes light only |
| 12 | **Narrow width** | at 390: horizontal scroll, a bar whose controls wrap to two rows, a table that hides its key column, a tap target under the touch floor, text cut mid-word |

A screen ships with zero FAIL on 3, 5, 6, 11, 12 and an explicit, named reason for any other FAIL
left open. The ranges are defaults measured on well-regarded product screens; the project's tokens
and DESIGN.md override them. Type: 4-9 sizes and about 3 weights per screen is the normal band.

## Product-UI tells

The look a generated app screen converges on. Each is a default to remove or a choice to justify.

- One control in a bar boxed or filled while its neighbours are bare (a flag in a bordered box, a
  lone pill): reads as an error badge.
- Icon glyphs small inside large hit boxes, spread with wide gaps: the bar looks empty and the
  icons look broken. Cluster related controls; size glyph to box.
- Mixed icon families or stroke widths in one view; emoji or flags used as icons.
- Panels and launchers that are a bare text list: no icons, no group headings, no description,
  every row the same weight.
- Help or docs pages that are paragraphs and links: no screenshot, no steps, no "what you see".
- Identical cards in a grid each holding one sentence; a card per field.
- A badge, chip or dot on everything, so nothing reads as a status.
- Gray text on a colored surface; low-contrast placeholder used as the label.
- A section header for one line of content; a subtitle that restates the title.
- Everything centred on a work screen; a hero banner on an app page.
- Gradient text, glow shadows, glassmorphism with no depth reason, a colored side border on cards.
- Tracked all-caps eyebrows over every heading; middle-dot meta strings; numbered sections that
  are not steps.
- Spinners where the layout is known; fade-up on every block; hover lift on every card; entrance
  animation on dashboard blocks (on work screens motion is feedback: press, hover, open).
- A tinted icon chip on every KPI, card or row; a sparkline and a green "+x%" pill on every KPI;
  KPI values at 36px+ in brand colour.
- Border and shadow together on resting cards; cards nested in cards; more than 3 radii.
- Four or more font sizes inside one card; bold used for emphasis in every row.
- English chrome labels on a screen localized to another language.

## Sources

Numbers and tells distilled from: taste-skill `references/app-screens.md` (measured ranges for
icons, controls, gutters, KPIs, states; github.com/Leonxlnx/taste-skill), impeccable's detector rules
and critique reference (github.com/pbakaus/impeccable), Vercel Web Interface Guidelines (loader
timing, focus/hover contrast; github.com/vercel-labs/web-interface-guidelines), and the Anthropic
`frontend-design` skill's slop clusters. Read 2026-11-03; paraphrased, not vendored.

## Report format

```
Screen: <route> · shots: <paths> · probe: <findings count>
Rubric: 1 PASS · 2 FAIL (3 stray left edges in filter row) · ... · 12 PASS
Tells: <hits with element>
Squint: lands on <element> (expected <element>)
Fixes, in order: <shared component first, then page>
```
