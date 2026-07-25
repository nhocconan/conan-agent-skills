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

**Picking the accent trio — check the gradient midpoint, not just the endpoints.**
`--grad` paints headline text via `background-clip:text`, so any desaturated
zone in the ramp shows up as dull grey letters in the middle of the wordmark.
Two accents on roughly opposite hues interpolate through neutral: cyan `#0ea5e9`
→ amber `#f59e0b` passed through olive and washed out `Engin**eer**ing` in the
loop theme (fixed 2026-07-25 by moving `--accent-3` to emerald `#10b981`, which
keeps chroma the whole way). Render the wordmark and look before committing a trio.

**Accent ≠ text colour.** A vivid accent used for `.sidebar-brand-title em`
often fails AA against white: amber `#f59e0b` on `#fff` is ~2.1:1. Keep a
separate `--brand-em` token (dark in light mode, light in dark mode) for accent
text, and measure it — 17px/800 is not "large text" under WCAG.

**Callout icons are masked SVG, never emoji.** `.callout::before` is a 17×17
box with `background-color:currentColor` and the glyph applied as a
`mask`/`-webkit-mask` data-URI; each variant sets `color:var(--info|--warning|
--success|--danger|--accent-2)`. This inherits the semantic token in both colour
modes and renders identically on every platform, which emoji do not. The
`insight` icon is the same spark path as the Takeaway eyebrow — reuse it.

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
- **Arrowheads — two failure modes that render silently wrong** (both shipped
  to production 2026-07; audit with `scripts/audit-svg-arrows.py`):
  1. **One connector per `<path>`.** SVG paints `marker-end` on the LAST vertex
     of the whole path element, so `d="M0 0h20 M0 40h20"` draws exactly ONE
     arrowhead — the other branch silently loses its head. A fan-out to three
     boxes needs three `<path>` elements, not one path with three subpaths.
     (Decorative rails that are not connectors carry no marker at all.)
  2. **The final segment IS the arrow direction.** With `orient="auto"` the
     marker rotates to the last segment, so a trailing jog like `…v60h-4`
     points the head backwards, out of the box it should enter. Route the
     connector *outside* the target box, then enter it with a final segment
     that travels INTO the box.
  3. **The final segment must be LONGER than the head's backward reach.**
     `markerUnits` defaults to `strokeWidth`, so a `refX="7"` head on a
     `stroke-width="2"` path reaches **14 user units back** from its tip. Land
     that on a 4-unit jog and the head spills across the corner onto the
     previous segment — on screen it is a detached blob, not an arrow.
     Rule of thumb: give every connector an approach run of at least
     `refX × stroke-width`, and turn *earlier* rather than shrinking the head.

     Fixing 2 by adding a tiny jog is what causes 3. Both were shipped from
     this file: an earlier revision held up `M238 65 H246 V127 H250` as the
     model answer, and that exact path rendered the blob a reader reported in
     `ai-agent-operational-training` Hình 2.3 (07/2026). The correct shape for
     that step is a plain elbow with a real runway — exit the source box, turn
     once, and run into the target edge:
     `M238 65 H270 V96` (target box spans x 254–466, top edge y=96 → a 31-unit
     final approach for a 14-unit head).
  Sanity check when drawing: for every arrow, name the box it enters, confirm
  the last command in `d` moves toward that box, and confirm that last command
  is longer than the head that sits on it. Then **look at the rendered figure** —
  `scripts/audit-svg-arrows.py` in the courses repo checks all three classes,
  but a passing audit only means nothing is provably broken, not that the
  diagram reads right.
- **Pick the diagram FORM from the relationship** (decision tree + worked
  contrast in `examples.md §6`): flow → boxes+arrows; contrast → two-panel;
  model correspondence → parallel rows + dashed mapping lines; hierarchy →
  nested boxes; threshold → axis with shaded zones; feedback → loop with one
  labeled return arrow. Three boxes restating the headings is decoration.
- **Information test:** the picture must carry ≥2 facts that are NOT in its
  caption; otherwise delete or redraw.
- **Mobile legibility:** at `viewBox` width ≥ 700, text below `font-size:9`
  is unreadable on a 375px phone (the validator warns). Fewer, bigger labels;
  detail goes in the caption.
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

**The coherence triangle (per lesson, non-negotiable).** Every lesson has ONE
core idea, stated in one sentence in its curriculum brief. The felt problem
dramatizes it, the takeaway states it, the quiz forces a decision that hinges
on it — three exposures of the same idea at three depths. A quiz that tests a
side detail, or a takeaway that summarizes a different point than the opening
raised, is a structural bug even if each piece reads well alone
(`examples.md §4`).

**Concept budget.** L1–L2 lessons introduce **≤3 new terms** each (working
memory is the constraint); every new term gets a first-use plain-language
explanation and a glossary row. If a brief needs 5 new terms, it's two lessons.

**Quiz distractor standard.** Distractors are *misconceptions a smart reader
could hold*, written confidently — never jokes, non-sequiturs, or obviously
absurd fillers. Procedure and worked GOLD/FAIL pair: `examples.md §2`. The
`data-explain` must teach why the wrong options are wrong, not just praise
the right one. Vary the correct-answer position across lessons.

**Analogy standard (the `insight` callout).** An analogy must map the
*mechanism* (not the vibe) and *state where it breaks* — the break is what
stops learners over-extending it (`examples.md §5`).

**Callbacks (spaced retrieval).** From module 2 on, each module makes ≥1
explicit callback to an earlier lesson's concept ("bạn đã gặp shape này ở bài
2.1 — đây là nó dưới ràng buộc mới"). The recap's synthesis quiz must span
concepts from ≥3 different modules.

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
  Padding alone does **not** get you there — measure. `.mobile-toggle` and
  `.mode-toggle` both need explicit `min-width:44px;min-height:44px`; a
  `padding:9px` hamburger renders 40×43 and a `min-height:34px` mode toggle
  renders 44×34. Audited 2026-07-25: 12 of 14 shipped courses were failing this.
- **Keyboard-only affordances are hidden on touch widths.** The `← → chuyển bài`
  hint carries `class="mono kbd-hint"`, and the `max-width:1024px` block carries
  `.kbd-hint{display:none}` — arrow keys don't exist on a phone, and leaving the
  hint in truncates the breadcrumb next to it.
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

- **`COURSE_TITLE` is not the sidebar wordmark.** The template used to run
  `sidebar-brand-title.innerHTML = COURSE_TITLE.replace(/(\S+)$/,'<em>$1</em>')`,
  which overwrote the short hand-authored brand with the full title *and*
  accent-coloured whatever word happened to land last — shipping a 3-line
  sidebar header ending in a stray red "ship" / "IDSS" / "liệu". Removed from the
  template and from 6 shipped courses on 2026-07-25. The brand stays **static
  markup**: `<div class="sidebar-brand-title">Short <em>Name</em></div>`.
  `COURSE_TITLE` is for `<title>` and the LMS payload only.
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

**Public-course data rules (hard — a real leak taught these).** A course
whose distribution is PUBLIC must contain **no** client/shop names, real
revenue or operational metrics, internal repo/product/component names, or
internal doc citations. Real systems appear only as *anonymized illustrative
examples* ("một hệ ví dụ"), with a disclaimer callout on the overview pane
stating that names/numbers are example values. Anonymize at **digest** time
(PLAYBOOK Phase 1's distribution gate) — scrubbing the assembled file while
the digests/fragments stay dirty re-leaks on the next re-assembly. Keep
`sensitive-terms.txt` beside the digests; run
`validate_course.py <file> --sensitive sensitive-terms.txt` on every build
and review.

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
- [ ] Coherence triangle holds: felt problem, takeaway and quiz serve the same core idea.
- [ ] Distractors are plausible misconceptions; `data-explain` teaches why they're wrong.
- [ ] ≤3 new terms (L1–L2); each explained at first use + in the glossary.

**Public courses only**
- [ ] `--sensitive` pass clean (no client names, real figures, internal identifiers).
- [ ] Example system framed as illustrative; disclaimer callout present on overview.

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

---

## 12 · Pipeline & mechanical gates (model-agnostic builds)

The full build pipeline lives in **`PLAYBOOK.md`** (source digests →
curriculum contract → fragments → scripted assembly → scripted validation →
human pass). Rules from it that are part of the standard itself:

- **Source-digest discipline.** Facts enter a course only via a digest file
  produced from the primary source (definitions/formulas, figures-to-redraw,
  worked examples with verbatim numbers, relevance hooks). Authors never
  write from memory; reviewers verify against digests, not recollection.
- **SVG id prefixing.** Every internal SVG id (marker/gradient/clipPath) is
  prefixed with its lesson id (`m2l1-arrow`). Merged fragments with generic
  ids (`#ah`, `#arrow`) collide silently — first definition wins and other
  diagrams' arrowheads render with the wrong color or not at all.
- **Chrome localization.** For a non-English course, every visible template +
  engine string must be localized ("Mark complete", "← Previous", the
  `Overview`/`Complete` crumbs, quiz "✓ Correct."…). The canonical list is
  the `VI_CHROME` table in `scripts/assemble_course.py`; the validator flags
  leftovers when `<html lang>` ≠ en. The sidebar part-label regex must also
  strip the localized part prefix (e.g. `Phần I · `).
- **Decorative vs content SVG.** Diagrams (inside `<figure>`) carry
  `role="img"` + `aria-label` + `viewBox`; decorative icons (e.g. the
  takeaway star) carry `aria-hidden="true" focusable="false"`.
- **Mechanical gates before taste.** `scripts/validate_course.py` must report
  0 errors before any human review time is spent; `scripts/assemble_course.py`
  is the only way multi-fragment builds become a file. Legacy pre-template
  courses fail these gates structurally — bring them onto the template when
  next touched, don't chase individual checks.
