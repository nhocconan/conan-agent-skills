# Test memory-lean on a shared host

Measured on one shared Linux host: Playwright headless job 340-450 MB, vitest ~555 MB,
`next start` of a production build 250 MB-1 GB, `next dev` 5-6.5 GB with an unbounded
Turbopack leak (one reached 40.6 GiB and hung the host). Choose the cheapest layer:

1. **Production build, not `next dev`.** `next build` once per tree fingerprint, then
   `next start`. Dev only for hot reload while editing: one per checkout, in a capped cgroup.
2. **Parallelism inside one browser.** Separate BrowserContexts/pages per test or tab, not
   extra browser processes or forked Playwright workers; `workers` 1-2 on a shared host.
3. **Data parity without a browser.** Call the server/API/resolver layer directly; the
   browser is for interaction, layout and visual checks only.
4. **UI logic in component tests** (vitest + Testing Library/jsdom): single-open popovers,
   pickers, i18n labels.
5. **Heavy jobs through one conductor**: per-class memory caps (cgroup `MemoryMax`),
   serialized slots, admission on `MemAvailable`, result reuse by tree fingerprint, stop by
   unit, never `pkill -f`. See [shared-host resources](../agent-orchestration/FANOUT-PATTERNS.md#shared-host-resources).


## Diagnose a slow suite before adding workers (measured 2026-11-01)

A 3,400-test vitest tier took 2,274 s with 8 workers on 32 cores, yet only ≈ 2.7 cores were
busy: the wall was the slowest file (one file, 1,903 s: five tests each rendering a full video
through real Chromium and ffmpeg). Order of checks:

1. **CPU used vs cores** (`/usr/bin/time -v`: user+sys ÷ wall). Low use means waiting or a
   long tail, and more workers will not help.
2. **Slowest files** (per-file durations). The wall is at least the slowest file; split it,
   or move its rows to a cheaper layer and keep one full journey.
3. **Tier placement.** A heavy suite (ffmpeg, browser) runs in its own tier, selected by the
   diff's import graph, not in every unit run as well.
4. **Caps against today's hardware.** A cgroup CPU cap set for a smaller host silently
   halves throughput after an upgrade; re-read caps when `nproc` changes.
5. **No overlap.** One host lock for gate, E2E and affected runs; overlap produced 85 false
   failures and a full rerun.
6. **Typecheck.** `tsgo` (native preview) type-checked a package in 4.3 s against 21.1 s for
   `tsc`, with the same 0 errors; adopt it for the inner loop once it matches on the repo.
