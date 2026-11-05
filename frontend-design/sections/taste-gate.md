# Taste gate - mandatory for every UI change

Source: taste-skill 2.5.0 (Leonxlnx/taste-skill, MIT), vendored in `upstream/taste-skill/`
(`SOURCE.txt` has the commit). Its `SKILL.md` and references `copy.md`, `system.md`, `icons.md`,
`cards.md`, `layout-v4.md` are read at step 1 of the loop for EVERY UI change, in-app screens
included. taste-skill is written for marketing sites; the parts below transfer to work screens,
the rest (photographs, shader effects, scenes, moments, hero dealing, page-kind plans) does not.
Operator ruling 2026-11-05: no frontend change ships without passing this gate.

## Rules that apply to work screens

| # | Rule (taste-skill source) | On a dashboard / app page |
|---|---|---|
| T1 | No caption or description under a visual (house rule 1) | No footnote, source line, "cận dưới"/estimate pill or explainer under a chart or table. A chart says its top-N and period in its title or axis, nothing else |
| T2 | Plain copy: say what it is, what it does (`copy.md`) | Labels are nouns for things; a sentence you would not say aloud to the director is deleted. Words per screen stay low |
| T3 | One hard fact on the first screen | The first data (KPI or table) starts above the fold: y < 300 at 1440x900, < 420 at 390 |
| T4 | One system (`system.md`): one button shape, radius family, card recipe, hairline, control height, link look; spacing scale 4/8/12/16/24/32/48 | Filters, tabs, chips, buttons from the kit only; never a second control style on a page |
| T5 | Equal left and right content edges (house rule 4) | Header, toolbar, tabs and content share one gutter |
| T6 | Real, consistent icons; icon-only controls carry no text (`icons.md`) | Share, export, info, close are icon buttons with an aria-label and a tooltip, no visible word |
| T7 | Few actions, one wording each (`copy.md` 4-5) | One primary action per surface; no duplicate entry points for the same filter |
| T8 | Every visual renders at 1440, 1024, 768, 390 (house rule 2) | No clipped, overlapped or wrapped-to-3-lines block at any of the four |
| T9 | Hover micro-animation layer (house rule 5) | Applies only as focus/press/hover steps on kit controls; no tilt, no carousel, no timed tabs |

## Work-screen additions (same spirit, project-agnostic)

- **Metadata is not content.** Updated-at, source name, "estimate" disclaimers, methodology and
  coverage notes do not appear on the page. If a fact changes how a number must be read, state it
  once in an info icon tooltip or a help page, never repeated per block. Everything on an
  estimates page is an estimate: do not say so each time.
- **Controls take the least space that works:** a dropdown beats a segmented control beats tabs;
  one toolbar row; active-filter chips only when something is active; tabs are one line.
- **Long text is shortened with an ellipsis and the full text on hover/title.**
- **A saved view (chip) is not a filter:** name it as a view, keep it out of the filter row.

## How the gate runs

1. Step 1 (Ground): read `upstream/taste-skill/SKILL.md` (house rules) and the references above.
2. Step 2 (Plan): add a "Taste" line listing T1-T9 hits and the fix for each.
3. Step 5 (Critique): the second reader scores T1-T9 with counts next to the `design-qa` rubric;
   a failed T row blocks acceptance.
4. A worker brief for UI work names this file and requires the T-row result in its return.
