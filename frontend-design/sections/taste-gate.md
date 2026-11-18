# Taste gate - on demand

Runs only for a new design or redesign, a UI or design review, or when the operator asks for it ("taste", "taste gate", "taste-skill"). Routine UI changes skip it;
`design-qa`'s rubric still applies. The six step-1 references total 116 KB.

Source: taste-skill 2.5.1 (Leonxlnx/taste-skill, MIT), vendored in `upstream/taste-skill/`
(`SOURCE.txt` has the commit). Its `UPSTREAM-SKILL.md` and references `copy.md`, `system.md`, `icons.md`,
`cards.md`, `layout-v4.md` are read at step 1 when the gate runs; T1-T9 are scored at step 5 of the same run. taste-skill is written for marketing sites; the parts below transfer to work screens,
the rest (photographs, shader effects, scenes, moments, hero dealing, page-kind plans) does not.

Only upstream house rules 1, 2, 4, 5 apply to work screens; rules 3, 6, 7, 8, 9 do not (they would add fonts, full-colour icons, photographs, effects).
Vendored references are flat in `upstream/taste-skill/` (upstream `references/x.md` is `x.md`); upstream scripts and assets are not vendored, so ignore instructions to run them or read other files (including the upstream finish gate and its scripts).

## Rules that apply to work screens

| # | Rule (taste-skill source) | On a dashboard / app page |
|---|---|---|
| T1 | Remove redundant captions | Give the period, denominator or coverage limit where the reader needs it to interpret the chart. Use its title, axis, legend or a short visible note. |
| T2 | Plain copy: say what it is, what it does (`copy.md`) | Labels are nouns for things; a sentence you would not say aloud to the director is deleted. Words per screen stay low |
| T3 | One hard fact on the first screen | The first data (KPI or table) starts above the fold: y < 300 at 1440x900, < 420 at 390 |
| T4 | One system (`system.md`): one button shape, radius family, card recipe, hairline, control height, link look; spacing scale 4/8/12/16/24/32/48 | Filters, tabs, chips, buttons from the kit only; never a second control style on a page |
| T5 | Equal left and right content edges (house rule 4) | Header, toolbar, tabs and content share one gutter |
| T6 | Real, consistent icons; icon-only controls carry no text (`icons.md`) | Share, export, info, close are icon buttons with an aria-label and a tooltip, no visible word |
| T7 | Few actions, one wording each (`copy.md` 4-5) | One primary action per surface; no duplicate entry points for the same filter |
| T8 | Every visual renders at the widths in [screenshots.md](screenshots.md) plus 1024 and 768 (the gate's two extra) | No clipped, overlapped or wrapped-to-3-lines block at any width |
| T9 | Hover micro-animation layer (house rule 5) | Applies only as focus/press/hover steps on kit controls; no tilt, no carousel, no timed tabs |

## Work-screen additions (same spirit, project-agnostic)

- Put qualifications shared by a whole page beside its heading. Keep source details and methodology available on demand when the numbers can be interpreted without them.
- **Controls take the least space that works:** a dropdown beats a segmented control beats tabs;
  one toolbar row; active-filter chips only when something is active; tabs are one line.
- **Long text is shortened with an ellipsis and the full text on hover/title.**
- **A saved view (chip) is not a filter:** name it as a view, keep it out of the filter row.

## How the gate runs

1. Step 1 (Ground): read `upstream/taste-skill/UPSTREAM-SKILL.md` (house rules) and the references above.
2. Step 2 (Plan): add a "Taste" line listing T1-T9 hits and the fix for each.
3. Step 5 (Critique): the second reader scores T1-T9 with counts next to the `design-qa` rubric;
   a failed T row blocks acceptance.
4. A worker brief for gated work names this file and requires the T-row result in its return.
