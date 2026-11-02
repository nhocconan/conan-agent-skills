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

## Nothing escapes the conductor (incident 2026-11-01, host load 180)
Three agents ran tests directly (`pnpm exec vitest …`) beside a gate; each vitest worker launched its own Chromium and
ffmpeg, and a watchdog that started its command with `setsid` died while its children kept running. Rules, enforced in code:
1. **Refuse raw runs.** The test runner's config throws when it is not started by the conductor (an env marker the
   conductor sets; CI exempt; an explicit one-file override for a person).
2. **Kill the tree with the watchdog.** A watchdog traps EXIT/TERM and kills its command's process tree; the cgroup scope
   gets a hard `RuntimeMaxSec`, so even a SIGKILLed watchdog leaves nothing behind.
3. **Browsers are a host resource.** Tests share one browser per process (a context/tab per test) and take a host-wide
   slot before launching (≤ 2 browsers per host); E2E runs ≤ 2 shards with `workers: 1` each.
4. **Agents never run suites in parallel.** One suite at a time per host; builders run only their own test files through
   the conductor; a lead stops every builder's runs before starting a gate.
5. **Clean up.** After any run: no orphan test, browser or ffmpeg process (check by cwd and parent), no temp dirs.
6. **Shared checkout commits.** When writers commit through a temporary index (to leave other writers' hunks out), the
   real index goes stale: it still holds the pre-commit snapshot and shows the committed files as deleted or added. After
   each such commit run `git reset -q -- <own paths>`; before any plain `git commit`, check `git diff --cached` is only
   yours (2026-11-02: 44 stale entries, including deletes of freshly committed files, sat in a shared index). Release
   images build from a clean worktree of HEAD, never from a shared checkout.
7. **Edit another writer's dirty file read-first.** Read the whole file into a variable, assert the anchor, then write;
   never `open(f,'w').write(edit(open(f).read()))`, which truncates before it reads (2026-11-02: it emptied a doc holding
   another session's uncommitted edits). Recovery: blobs of dirty files often survive in the object store (a build cache
   that hashes the tree with `git add` into a temporary index): `git ls-tree -r <tree> -- <path>`, then `git cat-file -p`.
