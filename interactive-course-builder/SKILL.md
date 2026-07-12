---
name: interactive-course-builder
description: House standard for authoring world-class interactive HTML training courses as standalone single-file pages (LMS-embedded or independent). Use when creating, reviewing, redesigning, or unifying the style of ANY interactive/self-paced learning course, lesson, curriculum, or training module rendered as HTML. Covers the shared design system (tokens, per-course themes, light-default + dark-toggle modes), the component kit (lesson cards, SVG diagrams, images, callouts, comparisons, takeaways, quizzes), the leveled pedagogy (L1→L5, felt-problem→takeaway→quiz rhythm), WCAG 2.2 AA accessibility, the framework-free interactivity engine, and the optional LMS progress contract. Trigger on "interactive course", "training course", "make a course", "lesson HTML", "course style", "unify course design", "add takeaways/quizzes/diagrams to a course".
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

## The kit (same folder)

| File | Role |
|---|---|
| **`template.html`** | The executable standard. A complete, working, accessible reference course. **Start every new course by copying it.** Every reusable block is marked `COMPONENT:`. |
| **`reference.md`** | The full spec: tokens, component vocabulary, leveled pedagogy, a11y, the LMS engine contract, the "world-class" bar, the ship checklist, and splitting rules. **Read it before authoring or reviewing.** |
| **`PLAYBOOK.md`** | The model-agnostic authoring pipeline: source digests → curriculum contract → (parallel) lesson fragments → scripted assembly → scripted validation → human pass. **Follow its phases for every build** — sequence + artifacts + mechanical gates are what make the result identical no matter which model does the work. Also holds the retrofit protocol for existing courses. |
| **`examples.md`** | The few-shot pack: GOLD vs FAIL pairs (felt-problem openings, quiz distractors, takeaways, analogies, diagram forms, formula treatment), each annotated with the load-bearing difference. **Every builder prompt includes it** — rules tell a strong model what to do; examples are what weaker models actually imitate. |
| **`scripts/validate_course.py`** | The ship checklist as executable checks (structure, per-lesson mandates, a11y, hex, slop lexicon, chrome localization, LMS contract). **Loop until 0 errors.** |
| **`scripts/assemble_course.py`** | Deterministic assembly for fan-out builds: JSON contract + module fragments → finished course (auto-runs the validator). Nobody hand-edits a 400KB HTML file. |
| `SKILL.md` | This loader. |

If template and reference ever disagree, the **template wins** (it's tested).

## When to use

- Creating a new interactive course / curriculum / training module as HTML.
- Reviewing or redesigning an existing course to the standard.
- Unifying the visual style across multiple courses.
- Adding the mandatory pieces (levels, takeaways, quizzes, SVG diagrams) a
  course is missing.

Sibling skills: `anti-slop-review` fact-checks the prose; `a11y-audit`
deep-checks accessibility. This skill owns the **house design system +
pedagogy** those plug into.

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
- **Coherence triangle:** each lesson has ONE core idea; the felt problem,
  takeaway and quiz all serve it (`reference.md §4`, `examples.md §4`).
  Quiz distractors are plausible misconceptions, never filler.
- **≤3 new terms per L1–L2 lesson**, each explained at first use.

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
- **Never author from memory:** every fact traces to a source digest file
  (`PLAYBOOK.md` Phase 1). Beginner courses follow the "dễ hiểu" rules
  (example before definition, first-use term explanations, one idea per
  paragraph, formula ⇒ worked number ⇒ plain-words reading).
- **Distribution gate:** declare PUBLIC or INTERNAL before digesting. Public
  courses carry no client names, real figures, or internal identifiers —
  anonymize the *digests*, not just the output, and run the validator's
  `--sensitive` pass (`reference.md §7`, `PLAYBOOK.md` Phase 1).

## Workflow (full detail: `PLAYBOOK.md` — follow its phases in order)

1. **Digest the sources** into `digests/*.md` — a fact not in a digest does
   not enter the course (this is the anti-hallucination gate).
2. **Curriculum contract before prose** — parts/modules/lessons + per-lesson
   briefs; this is what lets parallel builders (or a weaker model) produce
   composable, on-tone work.
3. Build lessons to the rhythm. Solo (≤ ~8 lessons): author in a copy of
   `template.html`. Bigger: fan-out with the fragment protocol
   (`PLAYBOOK.md` Phase 3 — svg ids prefixed `mNlK-`).
4. Fan-out builds: `python3 scripts/assemble_course.py <contract.json>`
   (theme/hero/LESSONS/chrome-localization handled deterministically).
5. **Loop `python3 scripts/validate_course.py <course.html>` to 0 errors**,
   then the human pass: keyboard, 375px, both color modes, fact-check vs
   digests, anti-slop, and the 5-question self-test (`PLAYBOOK.md` Phase 5).

## The bar

A course ships only if a demanding learner would say all of: *I always knew
where I was; every screen taught me something; the pictures did work the text
couldn't; the examples were mine; it respected me (fast, keyboard, mobile, dark);
I could trust the facts; it stood on its own.* (`reference.md §9`.)
