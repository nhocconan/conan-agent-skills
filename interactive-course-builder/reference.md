# Interactive Course Standard — Reference Spec

> The complete, authoritative spec for **every** interactive HTML training
> course the owner ships (LMS-embedded or standalone). `template.html` is the
> executable embodiment of everything here; `SKILL.md` is the short loader.
> When this doc and the template disagree, **the template wins** (it's tested)
> — fix this doc.
>
> **Design philosophy in one line:** *unify the system, theme the surface.*
> One structure, one component kit, one engine, one accessibility bar across
> every course — a per-course accent (`data-theme`) is the only thing that
> changes, so each course stands alone yet clearly belongs to the family.

## The owner's style contract (applies to EVERY course, always)

1. **Modern & clean UI** — generous whitespace, card-based lessons, semantic
   tokens, restrained accent use. No visual clutter, no decoration that
   carries no information.
2. **Responsive** — flawless from 375px phones to wide desktops; sidebar
   collapses, tables scroll, nothing overflows horizontally.
3. **Light AND dark, light first** — light mode is ALWAYS the default; dark is
   a persisted topbar toggle, never `prefers-color-scheme`. Both modes must be
   fully readable.
4. **Rich with examples, images, and diagrams** — ≥1 visual per lesson, ≥2
   concrete cross-domain examples per concept, diagrams doing work text can't.
   Walls of text fail the standard.

---

## 0 · Provenance & non-goals

- **Provenance.** The system is extracted from `courses/ai-practical-playbook.html`
  (the reference implementation the client blessed): navy-led brand, Inter +
  IBM Plex Mono, card-based lessons, single-lesson pagination, localStorage +
  `window.storage` LMS bridge, `postMessage` progress reporting.
- **Reframed as a design system.** Raw hex from the playbook is lifted into
  **semantic tokens** so themes and dark mode work without touching components.
- **Non-goals.** No build step. No framework runtime. No external JS libs
  (no Tailwind CDN, no Mermaid runtime, no chart libs). A course is **one HTML
  file that opens offline** — that is what "stands alone" means here.
- **Fonts are the ONE permitted external request** (Google Fonts link with
  `display=swap`). The stacks in `--font-body`/`--font-mono` must keep their
  system fallbacks so the file still reads perfectly offline. Everything else
  (JS, CSS, diagrams, images) lives inside the file.
- **Works without an LMS.** The `postMessage` calls and `window.storage`
  bridge are no-ops when no shell is listening — the same file is correct in
  the portal iframe, opened from disk, or hosted anywhere.

---

## 1 · Anatomy of a course

```
Course
├── Overview pane (#overview)      hero + curriculum grid  ← landing
├── Part I … Part N                grouping only (sidebar labels)
│   └── Module 1 … M               module-header + its lessons
│       └── Lesson 1.1 … 1.k       the atomic learning unit (a card)
└── Completion pane (#complete)    celebration + next step
```

- **Lesson = the atom.** Everything the engine tracks (progress, nav, resume,
  completion) is keyed on lesson `id` of the form `m<MOD>-l<N>` (`m3-l2`).
- **Part** is a *sidebar grouping label only* — it has no pane. It maps to the
  **skill level band** (see §4). Modules live inside parts.
- **One `LESSONS` array** at the bottom of the file is the single source of
  truth. Sidebar, TOC cards, pagination, progress %, prev/next footers and the
  completion trigger all derive from it. **Never hand-maintain navigation.**

Course length guide: 12–28 lessons. Under 12 → probably an article, not a
course. Over ~30 → split it (see §11).

---

## 2 · Design tokens (the contract)

Components **only** read tokens. If you type a raw hex outside the `:root`
blocks in `template.html`, you have introduced a bug.

| Group | Tokens | Notes |
|---|---|---|
| Brand (immutable) | `--brand-navy/-deep/-sky/-coral/-gold/-red` | never themed |
| Accent trio | `--accent`, `--accent-2`, `--accent-3` | the course identity; set by `[data-theme]` |
| Gradient | `--grad`, `--grad-bar` | derived from accents; used on hero, lesson head, takeaway |
| Surfaces | `--bg`, `--surface`, `--surface-2/-3`, `--border`, `--border-strong` | flip in dark mode |
| Ink | `--ink`, `--ink-2`, `--ink-3`, `--on-accent` | text hierarchy |
| Status | `--success/-bg`, `--warning/-bg`, `--danger/-bg`, `--info/-bg` | callouts, quiz |
| Type | `--font-body` (Inter), `--font-mono` (IBM Plex Mono) | + system fallbacks |
| Rhythm | `--radius(-sm/-lg)`, `--shadow-sm/-md/-lg`, `--sidebar-w`, `--maxw`, `--focus` | |

**Themes** (approved, standalone identities — pick one per course):
`navy` (canonical/default) · `midnight` (navy family, coral kicker) · `indigo` ·
`teal` · `plum` · `slate`.
A new theme = one line: `[data-theme="x"]{--accent;--accent-2;--accent-3}` +
a dark-mode `--accent` override for contrast. Nothing else.

**Dark mode is toggle-only (house rule).** Light is ALWAYS the default —
never `prefers-color-scheme`. The topbar 🌙/☀️ button sets
`data-mode="dark"` on `<body>` and the engine persists the choice per course
(`MODE_KEY`). The dark block only flips surfaces + ink; accents lighten just
enough to stay legible (per-theme one-line overrides under
`body[data-mode="dark"]`). Author in light; dark is free *if* you never
hardcode color — then verify both modes before shipping.

---

## 3 · Component vocabulary

Every component lives in `template.html` behind a `COMPONENT:` comment. Copy the
block; don't reinvent. The kit (and when to reach for each):

| Component | Use it for | Rule |
|---|---|---|
| **Lesson card** | the container for one lesson | gradient head (level badge + title) + body |
| **Level badge** | show L1–L5 at a glance | filled gold dots = level; see §4 |
| **Objectives** | "by the end you can…" | 2–4 verb-first, testable outcomes |
| **Callout** ×5 | `info` `warn` `success` `danger` `insight` | one idea each; `insight` = mental model |
| **Comparison** | anti-pattern vs better; novice vs pro | left-border red/green, parallel bullets |
| **Concept box** | name & define the load-bearing idea | after the felt problem, never before |
| **Figure + SVG** | show a *relationship* words make you hold in your head | inline SVG only, uses `dgm-*` classes, has `<figcaption>` + `role="img"` + `aria-label` |
| **Prompt card** | copy-and-adapt prompts | has working Copy button |
| **Code card** | code the reader reads (not copies-to-run) | monospace, optional `tok-*` highlight spans |
| **Accordion** | "apply it" per audience; optional depth | progressive disclosure, not core content |
| **Steps** | ordered process / rhythm | numbered rail; ≤7 steps |
| **Table** | compare ≥3 things on ≥2 axes | wrapped in `.table-wrap` for mobile scroll |
| **Takeaway** ⭐ | the one sentence to remember | **mandatory, once per lesson**, gradient, gold highlight on the key phrase |
| **Quiz** ⭐ | check understanding | **mandatory, once per lesson**, scenario-based, `data-explain` reinforces the takeaway |
| **Lesson-nav** | prev / complete / next | auto-generated — leave the placeholder empty |

**Visual-density mandate.** "Nhiều diagram thay vì chỉ text." Target **≥1
figure/comparison/steps/table per lesson**, and no more than ~2 screens of
unbroken prose before a visual, callout, or interactive element. Text walls fail
the standard.

### SVG diagram rules (this is where courses win or look cheap)
- **Inline `<svg>` only.** No Mermaid/D3/image files — keeps the file standalone
  and themeable. Use `viewBox` (never fixed width/height on the `<svg>` — let it
  be fluid), `role="img"`, and a descriptive `aria-label`.
- **Color via `dgm-*` classes** (`dgm-box`, `dgm-accent`, `dgm-warn`, `dgm-ink`,
  `dgm-ink2`, `dgm-line`, `dgm-flow`) so diagrams theme + dark-mode for free.
  Never hardcode fills.
- Label nodes in mono; keep to ≤ ~9 nodes; one clear left-to-right or
  top-to-down flow; arrowheads via a `<marker>`.
- Every figure earns a **`<figcaption>`** that states the takeaway of the
  picture — a diagram without a caption is decoration.

### Raster images (screenshots/photos — allowed, but SVG first)
- **Default to inline SVG** for anything conceptual (flows, architectures,
  comparisons) — it themes, dark-modes, and scales for free.
- Real **screenshots/photos** may be embedded as `<img>` inside the same
  `.figure` component (the CSS already handles it): optimized WebP/PNG,
  **data-URI** so the file stays standalone, meaningful `alt`, and a
  `figcaption` like any other figure. Never a screenshot of text you could
  write as HTML.
- **Size budget:** ≤ ~200 KB per embedded image, and the whole course file
  ≤ ~3 MB. If screenshots push past that, cut or downscale them — a slow
  first paint fails the "it respected me" bar.

---

## 4 · Pedagogy — levels, structure, rigor

**Level bands (L1→L5)** map to Parts and to the gold dots on each lesson badge:

| Level | Band | Learner leaves able to… | Dots |
|---|---|---|---|
| **L1** | Foundations | name the concept, recognise it in the wild | ●○○○○ |
| **L2** | Working knowledge | apply it to a guided example | ●●○○○ |
| **L3** | Practitioner | choose between options under real constraints | ●●●○○ |
| **L4** | Advanced | combine patterns; handle failure modes | ●●●●○ |
| **L5** | Expert / lead | design systems & teach others; know when *not* to | ●●●●● |

Difficulty must be **monotonic**: a later lesson never assumes less than an
earlier one, and never depends on a *later* one. State prerequisites in the
module header when a jump is real.

**Learner-tooling additions (proven in the 2026-07 review round — include in new courses):**
- **Reading-time chip** on every lesson head (`<span class="level-badge">⏱ ~N phút</span>`,
  N ≈ words/220, min 3) — learners plan before they click.
- **Recap chapter** ("Tổng kết · Cheat sheet 1 trang") as the final lesson: a
  table distilling every chapter's takeaway to one line + an action checklist +
  one cross-chapter synthesis quiz. Own part label (e.g. `Tổng kết`).
- **Glossary table** on the overview pane (~12–15 EN terms, one-line meanings
  as used in this course) — essential for VI-language courses.
- **Keyboard ←/→ navigation** (built into the template engine) + a small
  `← → chuyển bài` hint in the topbar.
- Keep any single lesson **under ~1,800 words** (≈8 min); split into `mX-l2`
  when it exceeds that — the engine supports multiple lessons per module.

**Lesson skeleton (the reliable rhythm):**
1. **Felt problem** — a concrete scenario the reader recognises (not a definition).
2. **Name it** — the concept/term, in a concept box.
3. **Show it** — a figure, comparison, or worked example (the visual mandate).
4. **Apply it** — accordions per audience / a prompt card / steps.
5. **Takeaway** — one memorable sentence (mandatory).
6. **Quiz** — one scenario question that *tests the takeaway* (mandatory).

**Examples must be concrete and role-plural.** Show the same principle in ≥2
domains (e.g. backend + data, or sales + research) — the repetition across
contexts is what makes it transfer. Prefer real numbers, real tool names, real
before/after over hand-waving.

---

## 5 · Accessibility (WCAG 2.2 AA — non-negotiable)

- Skip-link first in `<body>`; `#main` target present.
- Landmarks: `<aside aria-label>`, `<main id="main">`, `<nav aria-label>`.
- **Contrast** ≥ 4.5:1 body, ≥ 3:1 large text & UI — tokens are pre-checked;
  keep body text on `--surface`/`--bg`, never colored text on colored bg except
  the pre-approved takeaway/quiz states.
- **Keyboard**: everything reachable & operable; `:focus-visible` ring on every
  interactive element (built into tokens). Accordions are native `<details>`.
  Quiz options are real `<button>`s.
- **Touch targets** ≥ 44px (lesson-nav min-height 62px; buttons padded).
- `prefers-reduced-motion` disables animations (built in).
- Every `<svg>` diagram: `role="img"` + `aria-label`. Every control has a
  discernible name (text or `aria-label`).
- Never signal correct/incorrect by **color alone** — quiz also uses ✓/✗ glyphs.
- Built into the template engine (keep intact when extending): active nav link
  carries `aria-current="page"`; the sidebar progress track is a
  `role="progressbar"` with live `aria-valuenow`; quiz feedback is a
  `role="status"` live region; on lesson change, focus moves to `#main`
  (`tabindex="-1"`) so screen readers announce from the top; the mode toggle
  exposes `aria-pressed` + a mode-specific `aria-label`.

---

## 6 · Interactivity engine & LMS contract

The engine (bottom `<script>`) is framework-free and course-agnostic. Configure
three constants + the `LESSONS` array; touch nothing else unless extending.

- **Storage**: `window.storage` (the LMS bridge) first, `localStorage` fallback.
  Keys namespaced `ai-course:<slug>:<lessonId>`. Never write to `window.storage`
  directly from lesson HTML.
- **Progress → LMS** via `postMessage`:
  - `{type:'lms:progress', course, percent, done, total}` on every change — this
    is the one the portal **consumes today** (`CourseContent.tsx` reads
    `e.data.percent`; it also has a scroll-based fallback if no message arrives).
    Keep this shape stable.
  - `{type:'lms:lesson-change', course, lessonId}` on navigation — currently
    **forward-compatible / not yet consumed** by the shell; emit it anyway so a
    future shell can scroll the iframe to top on lesson change. Harmless if ignored.
- **Resume**: last lesson + within-lesson scroll offset are restored on load.
- **Color mode**: `MODE_KEY` persists the light/dark choice per course; the
  engine applies it on load (default `light`, always).
- **Completion**: marking the last lesson done routes to `#complete`.
- Hash routing (`#m2-l3`) drives pagination — every lesson is deep-linkable.

**Do not** add analytics beacons, external fetches, or anything that phones home.
Courses are content, served in a signed-in iframe. Privacy by construction.

---

## 7 · Content voice & anti-slop

- **Bilingual-aware.** Match the course's language (the playbook ships `vi` +
  `.en` mirror). Keep technical terms in English where that's the industry norm.
- **Concrete over generic.** Every claim gets a mechanism, number, or example.
  Ban empty intensifiers ("powerful", "seamless", "revolutionary", "in today's
  fast-paced world"). If a sentence would survive in any course on any topic,
  cut it.
- **Facts must be true and current.** Version numbers, model names, pricing,
  feature availability — verify before shipping (dated as of the course's
  edition). Wrong facts destroy authority faster than plain prose.
- Run the `anti-slop-review` skill on prose before shipping.

---

## 8 · Authoring workflow

1. `cp template.html courses/<slug>.html`.
2. Fill `<title>`, `<meta description>`, hero, sidebar brand, footer.
3. Set `COURSE_SLUG`, `COURSE_TITLE`, and the `LESSONS` array.
4. Choose `data-theme` on `<body>` (default `navy`).
5. Outline: Parts → Modules → Lessons with level bands **before** writing prose.
6. Write each lesson to the §4 skeleton; copy components from the template.
7. Add ≥1 SVG figure or comparison per lesson (§3 visual mandate).
8. Add the mandatory Takeaway + Quiz to every lesson.
9. Run §10 checklist. Fix. Ship.

---

## 9 · Definition of "world-class" (the bar this standard is held to)

A course clears the bar only if a demanding learner would say **all** of:
- "I always knew where I was and what I'd get." (nav, objectives, levels)
- "Every screen taught me something; nothing was filler." (density, anti-slop)
- "The pictures did work the text couldn't." (real diagrams, not decoration)
- "The examples were mine — I could copy the shape into Monday." (concrete)
- "It respected me: fast, keyboard-friendly, worked on my phone, dark mode." (a11y/perf)
- "I could trust it." (facts current & correct)
- "It stood on its own — I didn't need the other courses." (self-contained)

---

## 10 · Ship checklist (run every time)

**Structure**
- [ ] `LESSONS` array matches the DOM (every `id` has a card; ids are `m*-l*`).
- [ ] Parts map to level bands; difficulty is monotonic.
- [ ] Overview hero states audience + outcome; curriculum grid renders.
- [ ] Completion pane points to a concrete next action.

**Per lesson**
- [ ] Level badge with correct dots. [ ] Objectives (2–4, verb-first).
- [ ] Opens with a felt problem. [ ] ≥1 figure/comparison/steps/table.
- [ ] No >2 screens of unbroken prose. [ ] Mandatory Takeaway. [ ] Mandatory Quiz with `data-explain`.

**System**
- [ ] `node --check` on the engine script passes; no console errors on load.
- [ ] Tags balance; single `<script>` engine; no external JS libs.
- [ ] `<html lang>` matches the course language (vi/en/…).
- [ ] No raw hex outside `:root`/theme blocks. [ ] Every SVG has `role`+`aria-label`+`figcaption`.
- [ ] Keyboard-only pass: nav, quiz, accordions, complete button all work; focus visible.
- [ ] Mobile (375px): sidebar toggles, tables scroll, no horizontal overflow.
- [ ] Color modes: loads LIGHT by default; 🌙 toggle switches + persists across
      reload; BOTH modes readable (no invisible text, no hardcoded surfaces).
- [ ] Embedded images optimized (≤ ~200 KB each, file ≤ ~3 MB total, real `alt`).
- [ ] Progress persists across reload; `postMessage` shapes intact.
- [ ] Print preview of a lesson is clean (chrome hidden — built into template).

**Content**
- [ ] anti-slop pass done. [ ] Facts/versions verified & dated.
- [ ] Standalone: no reference that only makes sense if you did another course.

---

## 11 · Splitting & course families

Split a course when it exceeds ~30 lessons **or** covers two audiences that
would never sit through each other's half. When splitting:
- Each child is a **complete standalone** course (own overview, own completion,
  own `LESSONS`, can use its own `data-theme` for identity).
- Duplicate the minimal shared foundation into each rather than cross-linking a
  hard dependency (a light "if you're new, see X first" pointer is fine).
- Keep slugs discoverable: `foo-context-engineering`, `foo-harness-engineering`.
