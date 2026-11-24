# Delivery, compression, caching and optional CDN

Vendor-neutral delivery architecture for web apps and static sites. Everything in sections 1–4 works directly on a plain origin or behind any reverse proxy (Traefik, Caddy, Nginx, Envoy) with **zero CDN dependency**. Section 5 isolates optional CDN settings (Cloudflare Free as a concrete example) when an edge proxy sits in front.

## Contents

1. [Compression off the app event loop](#1-compression-off-the-app-event-loop)
2. [Zero-stale-deploy caching contract](#2-zero-stale-deploy-caching-contract)
3. [Static and marketing site delivery](#3-static-and-marketing-site-delivery)
4. [Critical path: Early Hints, fonts and LCP images](#4-critical-path-early-hints-fonts-and-lcp-images)
5. [Optional CDN layer (Cloudflare Free example)](#5-optional-cdn-layer-cloudflare-free-example)

## 1. Compression off the app event loop

Node/Next.js built-in compression runs single-threaded `gzip` on the application event loop. When a TLS-terminating reverse proxy sits in front of the app in production, move compression to the proxy so responses negotiate **Brotli (`br`)** or **Zstd (`zstd`)** with `gzip` fallback:

- **Expected gain:** ~14–35% smaller HTML, RSC, JSON, CSS and JS wire bytes than gzip, plus less CPU contention on the Node event loop. Verify `Content-Encoding` (`br`/`zstd`/`gzip`) and `Vary: Accept-Encoding` on HTML, JS, CSS, JSON and SVG responses so shared caches never mix compressed and raw variants.
- **Reverse-proxy config examples:**
  - **Traefik:** `compress` middleware with `encodings: ["br", "zstd", "gzip"]` (or `["br", "gzip"]`) and `excludedContentTypes: ["text/event-stream"]`.
  - **Caddy:** `encode zstd br gzip` (skips already-compressed formats automatically).
  - **Nginx:** `brotli on;` + `gzip on;` with `proxy_buffering off;` on streaming/SSE locations.
- **App config:** set `compress: false` in `next.config.*` (or remove Express/Fastify compression middleware) **only** when a reverse proxy compresses production traffic. Keep app-level compression enabled if the app terminates TLS directly.
- **SSE and streaming guard:** always exclude `text/event-stream` (and NDJSON/chunked progress streams) from proxy compression and buffering (`X-Accel-Buffering: no`, `excludedContentTypes: ["text/event-stream"]`), or events stall in proxy buffers until flush.
- **Bare-origin E2E test trap:** Playwright or curl assertions running against `http://127.0.0.1:<port>` without the reverse proxy will read uncompressed `transferSize` once `compress: false` is set. Compute real compressed bytes in budget tests (`zlib.gzipSync` or `zlib.brotliCompressSync` on response payloads, or route E2E through the proxy) instead of asserting raw loopback `transferSize` against compressed budgets.

## 2. Zero-stale-deploy caching contract

This header matrix works identically on a direct origin, behind Traefik/Caddy/Nginx, or behind any CDN. Its goal: maximum cache hit rate on repeat visits with **zero stale-chunk white screens** across zero-downtime rolling deploys.

| Asset class | Example paths | `Cache-Control` | Validator | Why |
| --- | --- | --- | --- | --- |
| Content-hashed build assets | `/_next/static/*`, `/assets/app.<8hex>.js`, `/assets/site.<8hex>.css` | `public, max-age=31536000, immutable` | `ETag` (`304`) | Filename changes on every content edit; safe to cache 1 year in browsers and any shared cache. |
| Un-hashed static assets & canonical aliases | `/favicon.ico`, `/robots.txt`, `/og.png`, `/logo.svg` | `private, no-cache` (or short `max-age` only when staleness is acceptable) | `ETag` / `Last-Modified` (`304 Not Modified`) | Revalidates cheaply without serving stale icons, manifests or social cards after a release. |
| Dynamic / authenticated HTML & RSC payloads | `/app/*`, `/dashboard/*`, `?_rsc=*` | `private, no-cache, no-store, must-revalidate` (or `private, no-store`) | None | Prevents cross-tenant cache leaks and stops stale HTML from referencing deleted chunk hashes after a rolling deploy. |
| Public static / docs HTML (optional shared cache) | `/`, `/pricing`, `/help/*` (zero cookies/PII) | `public, max-age=0, must-revalidate` (default); use `s-maxage` only with atomic purge or old-chunk retention | `ETag` (`304`) | Safe during rolling deploys; avoids 404 chunk waterfalls when container revisions roll. |
| Mutable API responses | `/api/*` | `private, no-store` | `ETag` only on explicit conditional-GET endpoints | Never risk stale or cross-user API responses. |

**Rolling-deploy rule:** never put an edge or shared proxy HTML cache rule in front of an app whose HTML embeds content-hashed JS/CSS URLs unless old hashed chunks remain served for at least the HTML TTL (or every deploy runs a verified atomic purge). For authenticated or multi-tenant apps, leaving HTML uncached also blocks cross-tenant cache leaks (`tenant-scope-integrity`). Keeping HTML uncached while every hashed chunk is `immutable` gives near-instant repeat loads with zero stale-deploy incidents.

**Never slap long `max-age` on un-hashed files.** A 30-day `max-age` on `/styles.css` or `/logo.png` locks users onto broken layouts or old branding until manual cache clears. Either content-hash the filename or serve `private, no-cache` + `ETag`.

## 3. Static and marketing site delivery

When a landing page, docs portal or marketing site ships as static HTML/CSS/JS (behind Nginx, Caddy, Traefik, or object storage):

- **Collapse render-blocking CSS into one content-hashed stylesheet** (e.g., `site.<8hex>.css` instead of `reset.css` + `tokens.css` + `page.css`) and eliminate chained CSS `@import` rules. On a 180 ms RTT connection, collapsing 3 blocking stylesheets into 1 saves 1–2 full round trips before first paint.
- **Hash every versioned subresource** (`css`, `js`, hero images, diagrams) referenced by internal markup so it earns `public, max-age=31536000, immutable`.
- **Keep canonical un-hashed aliases** (`/favicon.ico`, `/og.png`, `/apple-touch-icon.png`) only for external links/crawlers, served with `private, no-cache` + `ETag`.
- **Defer non-critical scripts** (`defer` or dynamic import on interaction/idle); keep analytics and chat widgets off the critical path.

## 4. Critical path: Early Hints, fonts and LCP images

- **HTTP `Link: rel=preload` headers (works with or without a CDN):** emit `Link: </assets/site.<hash>.css>; rel=preload; as=style` (and at most 1–2 confirmed LCP resources such as the hero image or primary variable font) from the origin or reverse proxy. Browsers parse `Link` on the final 200 response immediately, HTTP/2–3 proxies with Early Hints support flush HTTP `103 Early Hints` during server think time, and adding a CDN later upgrades those exact headers to edge 103 hints automatically with zero code change. Never preload >4 resources or non-LCP assets (bandwidth contention hurts LCP).
- **Web-font preload audit:** grep actual CSS/UI font declarations (`font-family`, `font-weight`, `font-style`) against preloaded or imported font files (`@font-face`, `next/font`) and check browser DevTools for *"was preloaded using link preload but not used"* console warnings. Removing unused weights (e.g., `300`, `800`, italic, or display fonts unused above the fold) routinely cuts 35–80 KB before LCP on every route. Always set `font-display: swap` (or `optional` when layout shift matters more than custom face on slow links) and subset only the needed unicode ranges.
- **LCP image discovery and priority:**
  - Identify the confirmed above-the-fold LCP element from a trace (hero visual or first 1–2 visible cards). Never lazy-load it (`loading="eager"` + `fetchpriority="high"`).
  - For Next.js 16+, `priority` on `<Image>` is deprecated: use `preload` for early discovery, or `loading="eager"` / `fetchPriority="high"` where appropriate, without combining `preload` with `loading` or `fetchPriority` ([Next.js Image](https://nextjs.org/docs/app/api-reference/components/image#preload)).
  - Give all below-the-fold images `loading="lazy"` and explicit `width`/`height` (or CSS `aspect-ratio`) so CLS stays ≤ 0.1.

## 5. Optional CDN layer (Cloudflare Free example)

Skip this entire section when serving direct from origin or a self-hosted reverse proxy. Apply it only when fronting the site with Cloudflare Free (or adapt equivalent settings for CloudFront/Fastly):

- **Proxy mode & TLS:** orange-cloud (proxied) DNS on web hostnames, `Full (Strict)` TLS, automatic Brotli + HTTP/2 + HTTP/3.
- **Zero HTML Cache Rules by default:** leave app and dynamic HTML `DYNAMIC` so rolling deploys never serve stale HTML pointing at retired chunk hashes. Let origin `Cache-Control: public, max-age=31536000, immutable` drive edge caching (`cf-cache-status: HIT`) for hashed static assets.
- **Edge features worth turning on (zero code lock-in):**
  - **Early Hints (103):** reads the origin's `Link: rel=preload` headers from section 4 and flushes `103` while the origin computes HTML.
  - **Smart Tiered Cache:** consolidates upper-tier cache fills to reduce origin static traffic.
- **Trusted proxy IPs & rate limiting:** when requests travel `CDN → reverse proxy → app`, expand the app/proxy trusted-proxy CIDR list (e.g., `AUTH_TRUSTED_PROXIES` / Nginx `set_real_ip_from` / Traefik `forwardedHeaders.trustedIPs`) with the CDN's published IP ranges (re-verified from vendor IP-range endpoints) so per-IP rate limiting and audit logs resolve the real client IP instead of throttling the CDN edge.
- **Verify plan limits before proxying:** Cloudflare Free enforces a **100 MiB** HTTP request body ceiling and a **100 s** idle read timeout (verify current plan limits in vendor docs). Endpoints handling >100 MiB uploads need direct-to-object-storage presigned URLs or a non-proxied (grey-cloud) upload subdomain; SSE / long-running responses need heartbeat comments every ≤ 15–30 s.
- **Live header verification:** after enabling the CDN, confirm with `curl -sI`:
  - Hashed static asset: `cf-cache-status: HIT` (by second request), `cache-control: public, max-age=31536000, immutable`, `content-encoding: br`.
  - Dynamic HTML & `/api/*`: `cf-cache-status: DYNAMIC` or `BYPASS`, `cache-control: private, no-store` (or `no-cache`).
