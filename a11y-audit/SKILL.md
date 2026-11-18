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

Report WCAG 2.2 AA findings separately from house conventions.

## How to run an audit
1. **Automated first pass** (partial coverage): scan the rendered page with local axe-core or Lighthouse. Record the violations and affected states.
2. **Manual keyboard pass** (catches what automation can't): use Tab, Shift+Tab and widget-specific keys. Check visible focus, activation and dismissal. Check modal focus containment and restoration.
3. **Screen-reader pass**: use a browser and screen-reader pair on representative flows. Check announced names, roles, states, errors and updates. Record where only the accessibility tree could be inspected.
4. Report each finding as: WCAG criterion → element/selector → what's wrong → concrete fix. Apply fixes only when requested; an audit alone is report-only.

## The checklist (verify every item)

### Keyboard & focus
- Every interactive control is reachable and operable by keyboard alone; no keyboard traps (2.1.1, 2.1.2).
- Focused element is not entirely hidden by sticky headers/footers or banners (**2.4.11 AA new in 2.2**; fully unobscured is AAA 2.4.12); focus indicator visible (2.4.7).
- Sequential focus order preserves meaning and operability (2.4.3). Avoid positive `tabindex`.
- Modal dialogs: move focus in, contain it while modal, and restore it on close. Nonmodal menus/drawers follow their own keyboard pattern; do not trap focus indiscriminately.

### Semantic HTML & ARIA
- Headings express the hierarchy and describe their section (1.3.1, 2.4.6). House style uses one main heading. Check the page title (2.4.2), document language (3.1.1) and a way to bypass repeated blocks (2.4.1).
- ARIA only to fill gaps native HTML can't — and then correct: valid role, required states (`aria-expanded`, `aria-selected`, `aria-current`), and `aria-live` for async updates (toasts, validation, loaded data).
- Icon-only buttons have an accessible name (`aria-label` or visually-hidden text). Decorative images `alt=""`; meaningful images have real `alt` (1.1.1).
- Status messages reach AT without focus: `role=status`/`alert`/`aria-live` (4.1.3). Visible label text is contained in the accessible name (2.5.3).
- Authored hover/focus content stays available while needed and accepts pointer hover. Provide dismissal without moving focus or the pointer when it obscures content, except for input errors (1.4.13).

### Forms
- Provide visible labels or instructions and programmatically identify each input. Prefer a native `<label>` for form fields (1.3.1, 3.3.2, 4.1.2). Identify supported personal data purposes (1.3.5).
- Errors are announced and tied to the field (`aria-describedby`, `aria-invalid`), text not color-only, and say how to fix (3.3.1, 3.3.3).
- Don't force re-entering info already provided in the same flow (**3.3.7 Redundant Entry, new in 2.2**); no cognitive-function test (memorize, transcribe, solve a puzzle) at login without an alternative — allowing paste and password managers is the usual fix (**3.3.8 Accessible Authentication (Minimum), new in 2.2**).

### Visual / low-vision
- Check text contrast at 4.5:1, or 3:1 for large text (18pt regular or 14pt bold). Required visual cues for authored controls, states and graphics need 3:1 against adjacent colors. Apply the criteria’s exceptions, including inactive controls. Test each supported theme (1.4.3, 1.4.11).
- Check reflow at 320 CSS px wide for vertical content or 256 CSS px high for horizontal content. Parts requiring two-dimensional layout, such as maps, are exempt (1.4.10). Enlarge text to 200% and check for loss of content or functionality (1.4.4).
- Text still works with line-height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em (1.4.12).

### Motor & touch
- Interactive targets ≥ **24×24 CSS px** (**2.5.8 new in 2.2**, mind its exceptions); 44×44 is best practice for touch-first, not AA. Other skills link here.
- Test a click or tap alternative to dragging (2.5.7), except for essential dragging or unmodified user-agent behavior. Test keyboard access separately (2.1.1).

### Motion & timing
- Honor reduced-motion preferences; interaction-animation criterion 2.3.3 is AAA, an additional house target beyond AA. Check flashes against the frequency or general/red flash thresholds (2.3.1).

### Help & consistency
- Repeated help mechanisms keep the same order relative to other content unless the user changes it (3.2.6).

Reference: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Report tested pages, states, browsers, assistive technology, and untested criteria; a clean scanner is not a conformance certification.

## Definition of done
Deliver the findings, coverage and unresolved criteria. For requested fixes, repeat the checks that exposed each defect.
