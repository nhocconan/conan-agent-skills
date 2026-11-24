# App waterfalls, observability and CI budgets

Runtime fixes for full-stack web apps (Next.js App Router, React/Vite SPAs, SSR backends) plus measurement harnesses and CI gates that keep regressions from shipping back. Framework-neutral patterns first; Next.js specifics are called out where the mechanism is router-specific.

## Contents

1. [Dynamic-route link prefetch storms](#1-dynamic-route-link-prefetch-storms)
2. [Cookie-free public middleware bypass](#2-cookie-free-public-middleware-bypass)
3. [Server, RSC and DB waterfalls](#3-server-rsc-and-db-waterfalls)
4. [Single-trip SSR and client hydration](#4-single-trip-ssr-and-client-hydration)
5. [Runtime observability with Server-Timing](#5-runtime-observability-with-server-timing)
6. [Real-RTT headless Chromium benchmarking](#6-real-rtt-headless-chromium-benchmarking)
7. [CI budgets and post-deploy verification gates](#7-ci-budgets-and-post-deploy-verification-gates)

## 1. Dynamic-route link prefetch storms

In frameworks that viewport-prefetch `<Link>` targets (such as Next.js App Router), any route that reads per-request headers, cookies or CSP nonces is dynamic: every visible `<Link>` in sidebars, tables, breadcrumbs, cards or help trees fires a server-rendered prefetch (`?_rsc=*`) on viewport entry. On dense pages this generates 10–40 redundant origin hits per navigation, saturating CPU, DB connections and high-RTT browser queues.

- **Fix:** set `prefetch={false}` on dynamic-route `<Link>` usages (navigation trees, list rows, breadcrumbs, pagination, cards). Keep viewport prefetch only for proven high-probability next-step CTAs pointing to cheap/static routes.
- **Prevent recurrence:** add a static CI check (e.g., `audit:link-prefetch` in `scripts/audit/`, per `bug-class-audits`) scanning `<Link` JSX usages so new dynamic links cannot silently re-introduce storms; allow explicit opt-ins only with an inline justification comment.

## 2. Cookie-free public middleware bypass

Edge middleware, auth guards and reverse-proxy auth checks often execute session decryption, token verification, or DB/Redis lookups on every request — including anonymous hits to `/`, `/login`, `/help/*`, `/pricing`, `/api/health` and public assets.

- **Fix:** short-circuit immediately on public paths when no session cookie or `Authorization` header is present. Perform zero crypto/session/DB I/O for unauthenticated requests to public routes.
- **Safety check:** verify that authenticated users visiting those same routes still get expected redirects or personalized chrome when the session cookie *is* present, and never skip tenant/auth enforcement on protected routes.

## 3. Server, RSC and DB waterfalls

Sequential `await` chains in route handlers, layouts and Server Components multiply TTFB by the number of round trips to DB/cache/internal services.

- **Parallelize independent awaits:** fetch independent request metadata, locale/translations and read queries together with `Promise.all(...)` (or `Promise.allSettled` where optional widgets degrade gracefully). Move data fetches to the highest shared layout/loader only when every child needs them; otherwise stream lower sections behind `<Suspense>` boundaries so above-the-fold HTML flushes early.
- **Single-client transaction guard (critical):** parallelize DB queries **only across pool connections** (`pool.query` / separate pooled reads). **Never** run `Promise.all` over queries sharing a single DB client or transaction handle (`pg.PoolClient`, Drizzle/Prisma `tx`, SQLite connection):
  - Drivers either serialize silently, throw concurrent-query overlap errors, or corrupt connection-scoped transaction state (such as `SET LOCAL` tenant/RLS context).
  - Inside a transaction or RLS-scoped client, keep queries strictly sequential on that handle; extract read-only queries that do not depend on uncommitted writes onto pooled connections only if they still enforce explicit tenant scoping (`tenant-scope-integrity`).

## 4. Single-trip SSR and client hydration

- **Eliminate duplicate initial fetches:** when SSR already queried the initial payload, pass it into the client state or query cache (`initialData`, hydrated query state, or Server Component props) instead of letting `useEffect` / React Query / SWR re-fetch the exact same endpoint immediately on mount.
- **Coalesce same-screen widget requests:** when 4–6 dashboard cards mount together and hit separate endpoints backed by the same base tables, batch them into one summary endpoint (or shared server loader) so high-RTT clients pay 1 round trip instead of 6.
- **Avoid redirect chains on entry routes:** keep `/` → locale/app landing to at most 1 hop (never `http → https → www → /locale → /app` across 4 RTTs).

## 5. Runtime observability with Server-Timing

Emit an HTTP `Server-Timing` header on SSR HTML and critical API routes so operators separate origin compute from network RTT directly in browser DevTools → Network → Timing:

```text
Server-Timing: proxy;dur=1.4, auth;dur=3.8, db;dur=12.6, ssr;dur=28.1
```

- Keep stage names short and consistent (`proxy`, `auth`, `db`, `ssr`, `render`).
- **Privacy rule:** never include tenant IDs, user IDs, email addresses, raw SQL, internal hostnames or secrets in `Server-Timing` descriptions — the header is visible to every client and proxy.
- Pair `Server-Timing` with client-side RUM (`web-vitals` attribution build: `onLCP`, `onINP`, `onCLS`, `onTTFB`) tagged by route template, device class and release SHA so real-network p75 regressions surface per deploy.

## 6. Real-RTT headless Chromium benchmarking

Local `0 ms` loopback measurements hide network waterfalls (multiple blocking CSS files, font chains, sequential client API calls, redirect hops). Always benchmark **before and after** in headless Chromium under **both**:

1. **Origin / local (`0 ms` RTT):** isolates server TTFB, hydration, and main-thread work.
2. **Realistic user-to-origin RTT (e.g., `150–200 ms` latency for cross-region traffic, plus mobile throughput cap):** via CDP `Network.emulateNetworkConditions` (`latency`, `downloadThroughput`, `uploadThroughput`) in a fresh `BrowserContext` (cold cache) and a second reload in the same context (warm cache).

Record one comparable row per route (cold and warm):

| Field | What to verify |
| --- | --- |
| `TTFB`, `FCP`, `LCP`, `CLS` | Against targets (`LCP ≤ 2.5s`, `CLS ≤ 0.1`, `TTFB < 0.8s`); compare before → after deltas. |
| `blockingCount` | Render-blocking stylesheets/scripts before first paint (aim for ≤ 1 CSS). |
| `reqCount`, `fontKB`, `totalTransferKB` | Catches prefetch storms, unused font weights and uncompressed payloads. |
| `content-encoding`, `cache-control` | Confirms `br`/`zstd` (or `gzip`) and `immutable` vs `no-cache`/`no-store` per class. |
| `consoleErrors`, `failedRequests` | Must be `0` (filter normal Next.js aborted `?_rsc=` navigations per `browsing-web`). |

Reuse one headless browser with isolated `BrowserContext`s per run (`effective-development/SHARED-HOST.md`) and close it on exit.

## 7. CI budgets and post-deploy verification gates

Lock measured wins so later features cannot regress them silently:

1. **Route asset & JS budget gate:** assert compressed (gzip/brotli) JS and CSS bytes per critical route from build output or compressed response bodies. Keep the assertion independent of Node's `compress` setting so `compress: false` behind a reverse proxy never causes false failures.
2. **Static anti-regression audits:** wire cheap checks into pre-push / CI — dynamic `<Link prefetch={false}>`, unused preloaded font weights, missing `width`/`height` on `<img>`, oversized unoptimized images.
3. **Post-deploy header check (`verify-cache-headers.sh`):** run after every production rollout against the live URL (works with or without a CDN):
   - Fetch one content-hashed static asset → assert `200`, `cache-control` contains `immutable` and `max-age=31536000`, `content-encoding` in `br|zstd|gzip`, and `etag` present.
   - Fetch one un-hashed static asset (`/favicon.ico` or `/og.png`) → assert `cache-control` does NOT carry long `max-age` (`no-cache` + `etag`, and conditional `If-None-Match` returns `304`).
   - Fetch one dynamic/authenticated HTML route and one `/api/*` health/data route → assert `cache-control` contains `no-store` or `private, no-cache`, and (if a CDN is enabled) edge cache header is `DYNAMIC`/`BYPASS`, never `HIT`.
