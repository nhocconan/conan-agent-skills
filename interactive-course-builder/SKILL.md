---
name: interactive-course-builder
description: House standard for authoring world-class interactive HTML training courses as standalone single-file pages (LMS-embedded or independent). Use when creating, reviewing, redesigning, or unifying the style of ANY interactive/self-paced learning course, lesson, curriculum, or training module rendered as HTML. Covers the shared design system (tokens, per-course themes, light-default + dark-toggle modes), the component kit (lesson cards, SVG diagrams, images, callouts, comparisons, takeaways, quizzes), the leveled pedagogy (L1→L5, felt-problem→takeaway→quiz rhythm), WCAG 2.2 AA accessibility, the framework-free interactivity engine, and the optional LMS progress contract. Trigger on "interactive course", "training course", "make a course", "lesson HTML", "course style", "unify course design", "add takeaways/quizzes/diagrams to a course".
trigger: /interactive-course-builder
---

# Interactive Course Builder — house standard

Build (and review) interactive training courses that are **world-class,
self-contained, and visually consistent** — every course the owner ships,
whether it lives in an LMS or stands alone.

**The owner's style contract (every course, always):** modern & clean UI ·
fully responsive (375px → desktop) · **light mode default, dark via persisted
toggle** (never `prefers-color-scheme`) · rich in concrete examples, images,
and diagrams — walls of text fail the standard.

**One-line philosophy:** *unify the system, theme the surface.* One structure,
one component kit, one engine, one accessibility bar for every course — a
per-course accent (`data-theme`) is the only thing that changes, so each course
**stands alone** yet clearly belongs to the family.

## The kit (three files, same folder)

| File | Role |
|---|---|
| **`template.html`** | The executable standard. A complete, working, accessible reference course. **Start every new course by copying it.** Every reusable block is marked `COMPONENT:`. |
| **`reference.md`** | The full spec: tokens, component vocabulary, leveled pedagogy, a11y, the LMS engine contract, the "world-class" bar, the ship checklist, and splitting rules. **Read it before authoring or reviewing.** |
| `SKILL.md` | This loader. |

If template and reference ever disagree, the **template wins** (it's tested).

## When to use

- Creating a new interactive course / curriculum / training module as HTML.
- Reviewing or redesigning an existing course to the standard.
- Unifying the visual style across multiple courses.
- Adding the mandatory pieces (levels, takeaways, quizzes, SVG diagrams) a
  course is missing.

Sibling skills: `codebase-to-course` explains *a codebase* as a course;
`anti-slop-review` fact-checks the prose; `a11y-audit` deep-checks accessibility.
This skill owns the **house design system + pedagogy** those plug into.

## Non-negotiables (the short version — full detail in `reference.md`)

**System**
- Copy `template.html`. No build step, **no external JS libraries** (no Tailwind
  CDN, no Mermaid/chart runtimes). One HTML file that opens offline = "stands alone"
  (Google Fonts is the one allowed external request; system fallbacks must hold).
- All color via **semantic tokens**; raw hex only inside `:root`/theme blocks.
  **Light is the default; dark is the persisted topbar toggle** — if you never
  hardcode color, dark mode is free. Verify BOTH modes before shipping.
- Navigation, progress, pagination, resume and completion all derive from the
  single **`LESSONS`** array — never hand-maintain nav.
- Keep the LMS `postMessage` contract intact (`lms:progress`, `lms:lesson-change`).

**Pedagogy**
- Structure: Parts (= level bands L1→L5) → Modules → Lessons. Difficulty monotonic.
- Every lesson follows the rhythm: **felt problem → name it → show it (visual)
  → apply it → Takeaway → Quiz.**
- **Every lesson MUST** carry a Level badge, ≥1 objective set, a **Takeaway**,
  and a **Quiz** (scenario-based, with a `data-explain` that reinforces the takeaway).

**Visual density** ("diagrams, not walls of text")
- ≥1 figure / comparison / steps / table **per lesson**; never >~2 screens of
  unbroken prose. Diagrams are **inline `<svg>`** using `dgm-*` classes, with
  `role="img"`, `aria-label`, and a `<figcaption>` that states the picture's point.
- Real screenshots/photos: optimized data-URI `<img>` inside the same figure
  component (≤ ~200 KB each, course file ≤ ~3 MB) — see `reference.md §3`.
- ≥2 concrete cross-domain examples per concept — repetition across contexts
  is what makes it transfer.

**Accessibility (WCAG 2.2 AA)**
- Skip-link, landmarks, visible focus, 44px targets, keyboard-operable quizzes/
  accordions, reduced-motion, never color-only signaling. Details in `reference.md §5`.

**Content**
- Concrete over generic; ban empty intensifiers. Verify all facts/versions/model
  names and date them. Run `anti-slop-review` before shipping.

## Workflow

1. `cp template.html courses/<slug>.html`.
2. Set `<title>`, `<meta description>`, hero, sidebar brand, footer; pick
   `data-theme` (default `navy`).
3. Set `COURSE_SLUG`, `COURSE_TITLE`, the `LESSONS` array.
4. Outline Parts → Modules → Lessons with level bands **before** prose.
5. Author each lesson to the rhythm; copy `COMPONENT:` blocks; add the visual +
   mandatory Takeaway + Quiz.
6. Run the **Ship checklist** (`reference.md §10`): `node --check` the engine,
   keyboard pass, 375px mobile pass, both-color-modes pass (light default +
   toggle persists), anti-slop + fact check.

## The bar

A course ships only if a demanding learner would say all of: *I always knew
where I was; every screen taught me something; the pictures did work the text
couldn't; the examples were mine; it respected me (fast, keyboard, mobile, dark);
I could trust the facts; it stood on its own.* (`reference.md §9`.)
