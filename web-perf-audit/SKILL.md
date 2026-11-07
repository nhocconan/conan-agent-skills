---
name: web-perf-audit
description: >-
  Use when the user reports a slow page/app, says "performance", "Core Web Vitals",
  "Lighthouse", "it feels janky/laggy", before shipping a user-facing release, or when
  a data-heavy page renders large lists/charts. Framework-agnostic runtime audit
  against Core Web Vitals — LCP, INP, CLS — plus bundle, network and rendering
  bottlenecks. Complements optional vercel-react-best-practices (source-level
  React/Next rules).
---

# Web Performance Audit (Core Web Vitals)

Optional `vercel-react-best-practices` covers what to write. This skill measures what actually *renders* and finds the bottleneck in a running page. Optimize against the three Core Web Vitals; never guess — profile, report findings, and when fixes are requested, repair and re-measure.

## Targets (field "good" thresholds)

Evaluate these at the 75th percentile, separately for mobile and desktop. Record
the population and reporting window (CrUX uses a rolling 28-day window); a lab
snapshot does not establish a field pass. See [Web Vitals](https://web.dev/articles/vitals).
- **LCP** (Largest Contentful Paint) ≤ **2.5s** — load speed of the main content.
- **INP** (Interaction to Next Paint) ≤ **200ms** — responsiveness; replaced FID as a Core Web Vital in 2024. Check it on real dashboard interactions.
- **CLS** (Cumulative Layout Shift) ≤ **0.1** — visual stability.
- Supporting: TTFB < 0.8s, total JS transferred, main-thread long tasks (>50ms).

## How to measure (don't optimize blind)
1. **Lab baseline**: run Lighthouse (CLI `npx lighthouse <url> --only-categories=performance --form-factor=mobile` or DevTools) for a scored snapshot + opportunities. Mobile + throttling on — desktop hides real problems. A navigation run reports TBT, not INP: never report it as an INP pass. Measure INP from field data (CrUX, or RUM via `web-vitals` `onINP`), or in the lab with a Lighthouse user-flow timespan or a DevTools Performance trace over the real interactions; TBT is only a lab proxy.
2. **Trace the bottleneck**: DevTools Performance panel — record a load and a key interaction. Find long tasks, layout thrashing, and what's blocking the main thread.
3. **Bundle**: inspect what ships (`@next/bundle-analyzer`, `vite-bundle-visualizer`, or `npx source-map-explorer`). Hunt large/duplicate deps (moment, lodash whole-import, two date libs, untree-shaken icon sets).
4. **Field data** if available (Chrome UX Report / RUM) — lab and field disagree; field is truth.

Fix by metric only after the trace names the bottleneck. For Next.js images, check the installed version's [Image reference](https://nextjs.org/docs/app/api-reference/components/image#preload): `priority` is deprecated since 16. For a confirmed LCP image, choose `loading="eager"` or `fetchPriority="high"` where appropriate; use `preload` when early discovery is needed, without combining it with `loading` or `fetchPriority`.

## Data-heavy app checklist (fits dashboard/BI work)
- Paginate or virtualize big tables; don't ship 100k rows to the client.
- Charts: cap series/points, render off-main-thread or canvas for large datasets, lazy-load the chart lib.
- Cache/memoize derived aggregates; avoid recomputing on every render.
- Images/screenshots in lists: lazy + correctly sized thumbnails, not full-res.

## Definition of done
Re-run the lab measurement after fixes and show before→after numbers for each affected metric. Report: starting scores, the bottleneck found, what changed, resulting scores. Don't claim a win without the re-measure.
