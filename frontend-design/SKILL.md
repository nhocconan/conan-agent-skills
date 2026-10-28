---
name: frontend-design
description: Routing and quality method for making or reshaping UI that must look designed, not generated - landing pages (with motion), marketing sites, dashboards, app screens, components. Use when asked to design, build, redesign or beautify a page ("làm landing page", "thiết kế giao diện", "page đẹp hơn", "nhìn xấu quá làm lại", "add animation", "hero", "dashboard layout"), before writing UI code, or when a generated page looks templated. Grounds in the subject and existing brand tokens first, then plans, builds, and gates through design-qa, a11y-audit, web-perf-audit and anti-slop-review.
---

# Frontend design

The method for building or reshaping UI. Reviewing an already-rendered page is
`design-qa`; this skill is what runs before and while it gets built. The Anthropic
`frontend-design` plugin and `impeccable` are optional neighbours (plugin = taste prompt,
`impeccable` = heavy command set); this file stays usable without either.

## 1. Ground first - brand beats any style rule

1. Name the subject, audience and the one primary job of the page in one line each. Missing
   from the brief: propose them, state them, continue.
2. Read the existing system before choosing anything: the repo's tokens/CSS variables, font
   loading, icon set, i18n copy source, a brand skill if one exists (for example
   `younet-*-brand-identity`), and the nearest design rules in its `AGENTS.md`.
3. Precedence: **operator's words > project brand tokens and rules > this skill > upstream
   style rules**. Anything below this skill (including the fonts, gradient bans and palettes
   in `elayadesign/ai-design-skills`) is advisory and loses to a brand token. Never add a font
   or colour the brand does not own just to follow a style rule.
4. Real content only: product facts from docs or code. No invented logos, testimonials or
   numbers (see [sections/anti-slop.md](sections/anti-slop.md) "Content").

## 2. Design plan, before code

Write a compact plan and show it (chat or plan file), then challenge it:

- **Tokens**: 4-6 named colours (brand's own when they exist), type roles (display, body, data)
  and scale, radius and spacing steps, one elevation rule.
- **Layout**: one sentence per section plus an ASCII wireframe; state alignment.
- **Memorable thing**: exactly one element carries the boldness; the rest stays quiet.
- **Challenge**: run the same brief mentally; if the plan matches what any similar page would
  get, or hits a cluster in [sections/anti-slop.md](sections/anti-slop.md), revise and say what
  changed. Where the brief or brand fixes an axis, follow it even if it is a "default look".

## 3. Pick the path

| Surface | Path |
|---|---|
| Landing, marketing, product, pricing, campaign page | [sections/landing-page.md](sections/landing-page.md) (strategy first, then motion via [sections/motion.md](sections/motion.md)) |
| Dashboard, settings, admin, list/detail, tool UI | [sections/app-pages.md](sections/app-pages.md); CRUD baseline in `admin-crud-standards` |
| Charts inside either | the `dataviz` skill / project chart package |
| Course pages | `interactive-course-builder` owns its design system |

Upstream depth (read-only reference, summarized here, never executed):
`elayadesign/ai-design-skills` `landing-page-design` and `design-to-motion`; see
[REF.md](REF.md) for what is taken, what is overridden, and the MIT notice.

## 4. Build rules (all paths)

- Use the project's components, tokens, icon set and copy system; copy lives in the i18n
  source, not inline.
- One CSS ownership per concern; watch selector specificity so section and element rules do
  not cancel each other (padding/margin between sections is the usual victim).
- Responsive from 375px, light and dark if the project has both, visible keyboard focus,
  empty/loading/error states designed, not implied.
- Screenshot while building, and drive the interactive parts. A static screenshot does not
  prove a date picker, popover or menu works.

## 5. Review gate - not done until these pass

1. `design-qa` on the rendered page: both themes, 375px, wrap/collision/imbalance.
2. [sections/anti-slop.md](sections/anti-slop.md) checklist, with evidence per hit.
3. `a11y-audit` (contrast, focus, reduced-motion, targets).
4. `web-perf-audit` when the page has motion, large media, charts or a bundle budget.
5. `anti-slop-review` on the words (headline, CTA, FAQ, empty states).

Report the plan, what was verified at each gate, and what was skipped.
