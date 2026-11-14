---
name: a11y-audit
description: >-
  Use when accessibility is the explicit ask ("accessibility", "a11y", "WCAG", "screen
  reader", "keyboard navigation", "focus ring", "contrast", "axe", "ARIA", "alt text",
  "trợ năng"), or when another skill hands off to the accessibility gate before a UI
  ships. Audits web UI against WCAG 2.2 AA (report-only; fix when asked): keyboard,
  focus, ARIA, contrast, labels, target size, motion, semantics. Not for explaining one
  attribute.
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
- Focused element is not entirely hidden by sticky headers/footers or banners (**2.4.11 AA new in 2.2**; fully unobscured is AAA 2.4.12); focus indicator visible (2.4.7).
- Logical focus/tab order matches visual order (2.4.3). No positive `tabindex`.
- Modal dialogs: move focus in, contain it while modal, and restore it on close. Nonmodal menus/drawers follow their own keyboard pattern; do not trap focus indiscriminately.

### Semantic HTML & ARIA
- One `<h1>`, headings nest without skipping levels and describe their section (1.3.1, 2.4.6); landmarks (`main`, `nav`) present; `<title>` per page (2.4.2); `<html lang>` set (3.1.1); a skip link or landmarks to bypass repeated blocks (2.4.1).
- ARIA only to fill gaps native HTML can't — and then correct: valid role, required states (`aria-expanded`, `aria-selected`, `aria-current`), and `aria-live` for async updates (toasts, validation, loaded data).
- Icon-only buttons have an accessible name (`aria-label` or visually-hidden text). Decorative images `alt=""`; meaningful images have real `alt` (1.1.1).
- Status messages reach AT without focus: `role=status`/`alert`/`aria-live` (4.1.3). Visible label text is contained in the accessible name (2.5.3).
- Hover/focus popups (tooltips, menus) are dismissible with Esc, hoverable, persistent (1.4.13).

### Forms
- Every input has a programmatically-associated `<label>` (placeholder is NOT a label) (1.3.1, 3.3.2); personal-data fields carry the right `autocomplete` token (1.3.5).
- Errors are announced and tied to the field (`aria-describedby`, `aria-invalid`), text not color-only, and say how to fix (3.3.1, 3.3.3).
- Don't force re-entering info already provided in the same flow (**3.3.7 Redundant Entry, new in 2.2**); no cognitive-function test (memorize, transcribe, solve a puzzle) at login without an alternative — allowing paste and password managers is the usual fix (**3.3.8 Accessible Authentication (Minimum), new in 2.2**).

### Visual / low-vision
- Text contrast ≥ 4.5:1 (≥ 3:1 for large text: ≥24px, or ≥18.66px bold — 18pt / 14pt bold); UI components & focus indicators ≥ 3:1 (1.4.3, 1.4.11). This is the #1 thing aesthetic-only review misses — verify actual computed colors, in BOTH light and dark themes.
- No two-dimensional scroll at 320 CSS px wide (= 400% zoom from 1280 px) (1.4.10); text enlarges to 200% without loss (1.4.4).
- Text still works with line-height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em (1.4.12).

### Motor & touch
- Interactive targets ≥ **24×24 CSS px** (**2.5.8 new in 2.2**, mind its exceptions); 44×44 is best practice for touch-first, not AA. Other skills link here.
- Any drag interaction has a single-pointer/keyboard alternative (**2.5.7 Dragging Movements, new in 2.2**).

### Motion & timing
- Honor reduced-motion preferences; interaction-animation criterion 2.3.3 is AAA, an additional house target beyond AA. No content flashing > 3×/sec (2.3.1).

### Help & consistency
- Help affordances (contact, docs) appear in a consistent location across pages (**3.2.6 Consistent Help, new in 2.2**).

Reference: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Report tested pages, states, browsers, assistive technology, and untested criteria; a clean scanner is not a conformance certification.

## Definition of done
Automated scan is clean, full keyboard pass works, contrast verified in both themes, and every fix is re-checked. Report what failed, what was fixed, and any item that needs a design decision from the user.
