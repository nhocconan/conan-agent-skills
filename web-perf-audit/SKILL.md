---
name: web-perf-audit
description: Framework-agnostic runtime performance audit against Core Web Vitals — LCP, INP, CLS — plus bundle, network, and rendering bottlenecks. Use when the user reports a slow page/app, says "performance", "Core Web Vitals", "Lighthouse", "it feels janky/laggy", before shipping a user-facing release, or when a data-heavy page renders large lists/charts. Measures real rendered behavior; complements vercel-react-best-practices (which is source-level React/Next rules).
---

# Web Performance Audit (Core Web Vitals)

`vercel-react-best-practices` covers what to write. This skill measures what actually *renders* and finds the bottleneck in a running page. Optimize against the three Core Web Vitals; never guess — profile, fix the biggest contributor, re-measure.

## Targets (field "good" thresholds)
- **LCP** (Largest Contentful Paint) ≤ **2.5s** — load speed of the main content.
- **INP** (Interaction to Next Paint) ≤ **200ms** — responsiveness; replaced FID as a Core Web Vital in 2024. This is usually the one that's bad on interactive dashboards.
- **CLS** (Cumulative Layout Shift) ≤ **0.1** — visual stability.
- Supporting: TTFB < 0.8s, total JS transferred, main-thread long tasks (>50ms).

## How to measure (don't optimize blind)
1. **Lab baseline**: run Lighthouse (CLI `npx lighthouse <url> --only-categories=performance --form-factor=mobile` or DevTools) for a scored snapshot + opportunities. Mobile + throttling on — desktop hides real problems.
2. **Trace the bottleneck**: DevTools Performance panel — record a load and a key interaction. Find long tasks, layout thrashing, and what's blocking the main thread.
3. **Bundle**: inspect what ships (`@next/bundle-analyzer`, `vite-bundle-visualizer`, or `npx source-map-explorer`). Hunt large/duplicate deps (moment, lodash whole-import, two date libs, untree-shaken icon sets).
4. **Field data** if available (Chrome UX Report / RUM) — lab and field disagree; field is truth.

## Fix playbook (by metric)

### LCP too high
- Identify the LCP element. If an image: serve modern formats (AVIF/WebP), correct dimensions, `priority`/`fetchpriority=high`, preload it; lazy-load everything below the fold.
- Cut render-blocking CSS/JS; inline critical CSS; defer non-critical scripts.
- Slow TTFB → cache/CDN, move work server-side, stream HTML, avoid waterfalls of sequential data fetches.
- Self-host or `preconnect` fonts; `font-display: swap`; subset fonts.

### INP too high (interaction lag — common on data dashboards)
- Break up long tasks; `yield` to the main thread; move heavy compute to a Web Worker.
- Virtualize long lists/tables (TanStack Virtual / react-window) — never render 10k DOM rows.
- Memoize expensive renders; debounce filter/search; avoid re-rendering every chart on one filter change.
- Ship less JS: code-split routes, dynamic-import heavy widgets (charts, editors, maps), drop unused polyfills.

### CLS too high
- Reserve space for images/embeds/ads with explicit width/height or aspect-ratio.
- Don't inject content above existing content after load; reserve space for async/skeleton states.
- Preload fonts to avoid FOIT/FOUT reflow.

## Data-heavy app checklist (fits dashboard/BI work)
- Paginate or virtualize big tables; don't ship 100k rows to the client.
- Charts: cap series/points, render off-main-thread or canvas for large datasets, lazy-load the chart lib.
- Cache/memoize derived aggregates; avoid recomputing on every render.
- Images/screenshots in lists: lazy + correctly sized thumbnails, not full-res.

## Definition of done
Re-run the lab measurement after fixes and show before→after numbers for each affected metric. Report: starting scores, the bottleneck found, what changed, resulting scores. Don't claim a win without the re-measure.
