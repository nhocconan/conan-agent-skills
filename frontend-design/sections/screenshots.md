# Screenshot evidence

## Contents
- The set
- Capture recipe
- Rules

The loop's evidence. A screen that was not looked at in a state did not pass in that state.

## The set

| Shot | Viewport | Why |
|---|---|---|
| before / after, light | 1440×900 | the desktop composition and the squint test |
| before / after, light | 390×844 | wrapping, tap targets, bars that wrap to two rows |
| after, dark | 1440×900 and 390×844 | the theme nobody tested is where defects ship |
| each open state the change touched | 1440 (and 390 if it differs) | menus, panels, dialogs, drawers, popovers |
| one edge state | 1440 | longest real label (Vietnamese runs ~30% longer than English), empty, error, many items |
| two sibling screens | 1440 | the comparison for consistency (criterion 5 of the rubric) |

Viewport shots (not full page) for review; one full-page shot per screen when the change is below the
fold. Device scale 1 keeps a review set small enough to read; use 2 only for a shot that ships (docs,
store, marketing).

## Capture recipe

Use the project's sanctioned browser runner and its session handling; this is the shape, not a
script to paste blind.

```js
const { chromium } = require('playwright');
const probe = fs.readFileSync(LAYOUT_PROBE, 'utf8'); // design-qa/scripts/layout-probe.js
const browser = await chromium.launch();
for (const [vp, w, h] of [['d', 1440, 900], ['m', 390, 844]])
  for (const theme of ['light', 'dark']) {
    const ctx = await browser.newContext({
      viewport: { width: w, height: h }, colorScheme: theme, storageState: SAVED_SESSION,
    });
    // Theme through the app's own storage key, set before load; never by clicking a toggle
    // that saves a user preference.
    await ctx.addInitScript((t) => localStorage.setItem(THEME_KEY, t), theme);
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `${out}/${name}-${vp}-${theme}.png` });
    const { findings } = await page.evaluate(`${probe}\nlayoutProbe()`);
    fs.writeFileSync(`${out}/${name}-${vp}-${theme}.probe.json`, JSON.stringify(findings, null, 1));
    await ctx.close();
  }
```

## Rules

- Sign in once and reuse the saved session file (chmod 600, outside the repo, deleted after);
  repeated sign-ins lock accounts.
- Open states by clicking the trigger only; never click save, apply, submit, delete or a preference
  toggle in a review run.
- Name files `<screen>-<d|m>-<light|dark>[-<state>].png` and list the paths in the report; a
  before/after pair uses the same name under `before/` and `after/`.
- Read the shots yourself before handing them to the critic. A screenshot nobody opened is not
  evidence.
- Keep review shots out of the repo unless the project stores visual baselines.
