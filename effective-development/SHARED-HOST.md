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

