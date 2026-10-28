# Motion for a website

## Contents
- Budget
- Moments
- Tokens
- Clock
- Reduced motion and performance
- Check

Website mode of upstream `design-to-motion` (summarized; see [../REF.md](../REF.md)). Showcase
mode (frame-exact capture, MP4/GIF export, ffmpeg) is out of scope unless the operator asks
for a marketing video.

## Budget
Motion is named and counted before it is written. List each moment, its trigger, duration and
what it communicates. Typical landing page: 1 hero appear + 1 signature moment + at most one
story per visual-bearing section. Fade-and-slide-up on every section and hover lift on every
card is the generic default; do not ship it. Text-only sections (headline blocks, FAQ, pricing,
CTA, footer) get at most the page's single plain reveal.

## Moments
| Moment | Rule |
|---|---|
| Hero appear | On load, once. Elements rise 6px and resolve from 2px blur, 50-70ms stagger in reading order, done in about 1.2s. Page opens plain. |
| Section intro | When about 30% of the section is visible (IntersectionObserver), once, stagger inside the section only. |
| Story loop | Only on a visual (chart, list, flow, prompt, counter). 3-8s, one sentence of story, returns to rest, cards offset so they do not move in unison. |
| Product mockup | Loading intro (surfaces stay, contents load). Ask before adding stories. |
| Logos, integrations | Marquee or gentle light-up. |

## Tokens
Define as CSS variables, never default `ease`/`linear` for entrances:

- `--e: cubic-bezier(0.16, 1, 0.3, 1)` transforms, about 1.05s
- `--e2: cubic-bezier(0.33, 1, 0.68, 1)` opacity and blur, 0.7-0.8s
- `--io: cubic-bezier(0.65, 0, 0.35, 1)` wipes, fills, sweeps

If the project already has motion tokens or a reveal/driver component, reuse it and map
these onto it instead of adding a second system.

## Clock
CSS transitions for intros. One shared rAF clock for time-based stories (a small
`track(keys, t)` keyframe helper), not many timers. Triggers use IntersectionObserver, never a
scroll listener. Pause the clock when the section leaves the viewport and resume on return;
a story that runs off-screen is a defect. Where the project audits idle animation, infinite
animations must be gated on an in-view attribute.

## Reduced motion and performance
- `prefers-reduced-motion: reduce` renders the final state: no intro, no stories.
- Animate `transform`, `opacity`, `filter`, `clip-path` only; never `top/left/width/height`.
  Blur 14px or less. No layout shift from motion (reserve space).
- Prefer a small client island per section on SSR frameworks; add no animation library for
  this scope. Measure bundle and INP with `web-perf-audit` before and after.

## Check
Frame the page at rest, mid-intro and after the stories; confirm each story returns to the
resting design, nothing escapes its card, and the page still reads with motion disabled.
