---
name: web-platform-baseline
description: >-
  Use when writing or reviewing the code behind a web UI (forms, inputs, focus, dialogs,
  touch, motion, loading states, theme, images), when asked to apply "modern web
  guidance", "web interface guidelines", "chuẩn web", "baseline", or to retrofit a
  codebase to it, and when refreshing this standard from its upstreams. Cross-project
  platform rules distilled from Chrome's Modern Web Guidance and Vercel's Web Interface
  Guidelines. Not how it looks (design-qa) or a WCAG audit (a11y-audit).
---

# Web platform baseline

Rules for the code behind any web UI, in any project. A project's own rulebook and design system
outrank them: where a project rule says otherwise it wins, and the report names the difference.
Provenance, pins and the adopt/reject verdicts: [REF.md](REF.md).

- **Building or changing UI:** apply the rules below to what the change adds or touches
  (`frontend-design` step 3 routes here) and add one line to the report:
  `baseline: <rules applied> · conflicts with project rules: <none or list>`. Rendered checks
  stay with `design-qa`; WCAG conformance with `a11y-audit`; measured speed with `web-perf-audit`.
- **Retrofitting a codebase:** [sections/retrofit.md](sections/retrofit.md).
- **Upstreams moved:** [sections/refresh.md](sections/refresh.md). Never fetch upstream text
  while doing product work.

## Browser support

- A project states its support policy once in its rulebook. With none stated, use this default
  and say so: a feature that is Baseline Widely available needs no fallback; a Newly available
  or limited feature ships behind feature detection (`@supports`, `in`, `HTMLElement.prototype`)
  with a fallback that keeps the task possible.
- Reach for the platform before a library when the support policy allows it: `<dialog>`,
  Popover, `inert`, `:focus-visible`, `accent-color`, container queries, `text-wrap: balance`.
  In a project with a component kit, adopt them inside the kit, never per page.

## Input and forms

- A custom Enter handler ignores composition: `if (e.isComposing || e.keyCode === 229) return`.
  Vietnamese, Japanese, Chinese and Korean input all compose; without the check a half-typed
  word submits.
- Give the keyboard a hint: `inputmode`, `enterkeyhint`, the right `type` and `autocomplete`
  token. Identifiers, codes and OTPs are `type="text"` with `inputmode`, never `type="number"`;
  turn `spellcheck`, `autocapitalize` and `autocorrect` off for them.
- A button inside a form states its `type`. No nested forms. Never block paste.
- Keep the submit enabled until the request starts; validate on blur and on submit, and move
  focus to the first invalid field.
- A screen that can lose typed work warns before navigation.

## Focus, pointer and touch

- Focus rings use `:focus-visible`, an `outline-offset`, and survive forced colours
  (`@media (forced-colors: active)`); `outline: none` never ships without a replacement.
- A control whose visual is under the target size gets its hit area extended; numbers:
  [a11y-audit](../a11y-audit/SKILL.md#motor--touch).
- Controls set `touch-action: manipulation`; a modal, drawer or sheet sets
  `overscroll-behavior: contain` so the page behind does not scroll.
- An open modal makes the rest of the page `inert` (or uses `showModal()`), keeps a visible
  close control, closes on Esc and returns focus to its trigger.

## Motion and loading

- Never `transition: all` (Tailwind `transition-all`): name the properties, and animate only
  `transform`, `opacity`, `filter`, `clip-path`. Honour `prefers-reduced-motion`.
- A loader waits about 150-300 ms before showing and then stays at least 300-500 ms; a known
  layout loads as a skeleton of that layout.
- One polite and one assertive live region per page; "Loading" is not announced, the result is.

## Theme and document

- `color-scheme` is set on the root for each theme so native controls, scrollbars and
  autofill match; `<meta name="theme-color">` follows the theme.
- Anchored headings carry `scroll-margin-top` for a sticky header. Brand names and code tokens
  that must not be machine-translated carry `translate="no"`.

## Performance at build time

- The largest above-the-fold image is never lazy-loaded and gets `fetchpriority="high"`;
  below-the-fold media is lazy with explicit dimensions.
- Preconnect to the origins a first render needs; preload only the fonts that render it.
- A handler that can run longer than 50 ms yields (`scheduler.yield()` where supported, else a
  task break); scroll and resize handlers are throttled; layout reads are batched before writes.

## Not adopted (do not re-import)

Curly quotes and Title Case as rules (copy style is the project's); URL-as-state where a
project rule keeps that state elsewhere; APCA as the conformance gate (WCAG 2.2 AA stays
the gate); a mandatory disclosure block in replies; fetching guidance from a remote `main` or an
`npx` CLI while the agent works.
