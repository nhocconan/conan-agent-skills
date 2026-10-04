# Text that does not use its width

The defect: a description or paragraph wraps to a second line while empty space sits beside it.
It recurs because a review checklist only catches the instance in front of the reviewer. Prevent
the class: fix the shared component, then add both checks below so the next page cannot ship it.

## 1. Root causes to look for in source

Search the shared header, card, empty-state and section components first; one capped component
reproduces the defect on every page that uses it.

| Shape | Synthetic example | Fix |
|---|---|---|
| Width cap on a text element inside a wide container | `<p class="max-w-[90ch]">`, `max-w-prose`, `max-w-xl`/`2xl`, `max-width: 60ch` | Remove the cap; the container sets the measure |
| Cap documented as an exception in the design spec | "Descriptions cap at 90ch" | Delete the exception with the cap, or the next agent restores it |
| Flex child that does not grow | `<div class="flex"><div><h1/><p/></div><Actions/></div>` | `min-w-0 flex-1` on the text column |
| Description sharing a row with actions that wrap | Header `flex-wrap` where actions drop below and leave the text at its basis | Text column `flex-1 basis-0`/`min-w-0`; actions `shrink-0` |
| Fixed width on a text block | `w-96`, `width: 420px` on a `p` or caption | `w-full` or no width |
| Grid track sized to content | `grid-cols-[auto_1fr]` with the text in the `auto` track | Put the text in the `1fr` track |
| `text-balance` on body copy | `p { text-wrap: balance }` | `balance` for headings only; `pretty` for body copy |
| `inline-block`/`w-fit` wrapper around prose | `<span class="inline-block">long text</span>` | `block` |

A measure cap on long-form reading text (an article column) is legitimate when the whole column is
narrow and centred. A cap on one paragraph inside a wide header, card or panel is not.

Grep, then confirm each hit in the rendered page:

```bash
rg -n 'max-w-(prose|xs|sm|md|lg|xl|[2-7]xl|\[[0-9.]+(ch|rem|em|px)\])|max-width:\s*[0-9.]+(ch|rem|em|px)' \
   --glob '*.{tsx,jsx,vue,svelte,html,css,scss}'
```

## 2. Rendered probe

[`../scripts/narrow-wrap-probe.js`](../scripts/narrow-wrap-probe.js) flags every visible leaf text
block that wraps to ≥ 2 lines while its effective column is under 85% of its container's content
width (and the gap is ≥ 96px) with no sibling beside it. It climbs from the text to the outermost
ancestor no wider than the text, so a capped wrapper is measured, not just the `p`.

- Use 0.85, not 0.7: a `90ch` cap at 14px in a 1440px layout measures 69–75%, and a 0.7 threshold
  misses the most common real case.
- Run it at the real breakpoints (at least 1440×900 and 390×844) and in both themes.
- Checked on synthetic fixtures: capped `p`, non-growing flex child (flagged); full width, text
  beside actions, three-column grid, centred column, `data-narrow-ok` (not flagged).
- Prove the probe on the broken page before trusting it on the fixed one: it must report the
  defect the user showed.

```ts
import { readFileSync } from 'node:fs';
const probe = readFileSync('scripts/narrow-wrap-probe.js', 'utf8'); // copied into the repo
const problems: string[] = await page.evaluate(`${probe}\nnarrowWrapProbe()`);
expect(problems).toEqual([]);
```

## 3. Make it a repo check

Follow [`bug-class-audits`](../../bug-class-audits/SKILL.md): fix every site, then add both halves.

1. **Runtime gate.** Add the probe to the project's existing Playwright route sweep (the one that
   already checks horizontal scroll, axe or touch targets) as one more check per route, viewport and
   theme. Add any route the sweep is missing, the reported page first. No sweep yet: one spec that
   visits the main routes and asserts `[]`.
2. **Static rule.** An audit that fails on width caps on text tags (`p`, `li`, headings, `label`,
   card descriptions), arbitrary values included. Unit-test it with a failing example and a
   legitimate counter-case (`max-w-full`, a percentage on a chat bubble, a centred page column).
3. **Exceptions are explicit.** `data-narrow-ok="<reason>"` on the element for the probe; a same-line
   `audit-ok-<rule>: <reason>` marker for the static rule.
4. **Update the design spec** in the same change: the rule, both check names, and no exception left
   that permits the old cap.
