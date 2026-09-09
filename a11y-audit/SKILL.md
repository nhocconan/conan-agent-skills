---
name: a11y-audit
description: Audit and fix web UI for accessibility against WCAG 2.2 AA — keyboard navigation, visible focus, ARIA correctness, color contrast, labeled inputs, touch-target size, reduced-motion, semantic HTML, heading order. Use when building or reviewing any web component, page, form, table, modal, or dashboard, when the user says "accessibility", "a11y", "WCAG", "screen reader", "keyboard", or before shipping any UI.
---

# Accessibility Audit (WCAG 2.2 AA)

Target WCAG 2.2 AA across keyboard, screen-reader, low-vision, and motor access.
Separate mandatory criteria from additional house conventions.

## How to run an audit
1. **Automated first pass** (partial coverage): run an axe-core scan on the rendered page. With a browser driver available: inject `axe-core` (`@axe-core/playwright` or the CDN build) and dump violations. Or use Lighthouse's accessibility category. Treat these as a floor, never the whole audit.
2. **Manual keyboard pass** (catches what automation can't): unplug the mouse. `Tab` through the whole page — every interactive element must be reachable, in a logical order, with a **visible focus ring**; `Enter`/`Space` activate; `Esc` closes overlays; focus is trapped inside open modals and returns to the trigger on close.
3. **Structure/semantics pass**: read the accessibility tree (browser devtools → Accessibility panel) and confirm names/roles/states match what's on screen.
4. Report each finding as: WCAG criterion → element/selector → what's wrong → concrete fix. Apply fixes only when requested; an audit alone is report-only.

## The checklist (verify every item)

### Keyboard & focus
- Every interactive control is reachable and operable by keyboard alone; no keyboard traps (2.1.1, 2.1.2).
- Focus indicator is clearly visible and not obscured by sticky headers/footers (2.4.7, **2.4.11 new in 2.2**).
- Logical focus/tab order matches visual order (2.4.3). No positive `tabindex`.
- Modal dialogs: move focus in, contain it while modal, and restore it on close. Nonmodal menus/drawers follow their own keyboard pattern; do not trap focus indiscriminately.

### Semantic HTML & ARIA
- Use native elements first: `<button>` for actions, `<a href>` for navigation, `<label>` for inputs, `<table>` for tabular data. A `<div onClick>` is a bug.
- Headings express the content hierarchy (1.3.1); one `<h1>` is a house convention, not a WCAG requirement. Landmarks (`<main>`, `<nav>`, `<header>`) present.
- ARIA only to fill gaps native HTML can't — and then correct: valid role, required states (`aria-expanded`, `aria-selected`, `aria-current`), and `aria-live` for async updates (toasts, validation, loaded data).
- Icon-only buttons have an accessible name (`aria-label` or visually-hidden text). Decorative images `alt=""`; meaningful images have real `alt` (1.1.1).

### Forms
- Every input has a programmatically-associated `<label>` (placeholder is NOT a label) (1.3.1, 3.3.2).
- Errors are announced and tied to the field (`aria-describedby`, `aria-invalid`), text not color-only, and say how to fix (3.3.1, 3.3.3).
- Don't force re-entering info already provided in the same flow (**3.3.7 Redundant Entry, new in 2.2**); don't block paste into password/OTP fields (**3.3.8 Accessible Authentication, new in 2.2**).

### Visual / low-vision
- Text contrast ≥ 4.5:1 (≥ 3:1 for ≥24px/19px-bold); UI components & focus indicators ≥ 3:1 (1.4.3, 1.4.11). This is the #1 thing aesthetic-only review misses — verify actual computed colors, in BOTH light and dark themes.
- Never convey meaning by color alone — add icon/text/pattern (chart series, status, required fields) (1.4.1).
- Layout survives 200% zoom and 320px width with no loss of content/function (1.4.10); test reflow at 400% browser zoom where applicable (text resize is 200%, 1.4.4).

### Motor & touch
- Interactive targets ≥ **24×24 CSS px** (**2.5.8 new in 2.2**); aim 44×44 for primary mobile actions. Account for the spacing and other exceptions in 2.5.8.
- Any drag interaction has a single-pointer/keyboard alternative (**2.5.7 Dragging Movements, new in 2.2**).

### Motion & timing
- Honor reduced-motion preferences; interaction-animation criterion 2.3.3 is AAA, an additional house target beyond AA. No content flashing > 3×/sec (2.3.1).
- Auto-playing/looping/marquee content can be paused; time limits are adjustable (2.2.1, 2.2.2).

### Help & consistency
- Help affordances (contact, docs) appear in a consistent location across pages (**3.2.6 Consistent Help, new in 2.2**).

Reference: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Report tested pages, states, browsers, assistive technology, and untested criteria; a clean scanner is not a conformance certification.

## Definition of done
Automated scan is clean, full keyboard pass works, contrast verified in both themes, and every fix is re-checked. Report what failed, what was fixed, and any item that needs a design decision from the user.
