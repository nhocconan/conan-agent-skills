# Test memory-lean on a shared host

Single owner of the conductor rule: heavy jobs on a shared host go through one runner.
Footprints seen on one 32-core host (2026-11-01): Playwright headless job 340-450 MB, vitest
~555 MB, `next start` 250 MB-1 GB, `next dev` 5-6.5 GB with an unbounded leak. Choose the
cheapest layer:

1. **Production build, not `next dev`.** `next build` once per tree fingerprint, then
   `next start`. Dev only for hot reload while editing: one per checkout, in a capped cgroup.
2. **Parallelism inside one browser.** Separate BrowserContexts/pages per test or tab, not
   extra browser processes or forked Playwright workers; `workers` 1-2 on a shared host; cap E2E at ≤ 2 shards with `workers: 1` each unless the repo's gate policy says otherwise.
3. **Data parity without a browser.** Call the server/API/resolver layer directly; the
   browser is for interaction, layout and visual checks only.
4. **UI logic in component tests** (vitest + Testing Library/jsdom): single-open popovers,
   pickers, i18n labels.
5. **The conductor.** Worktrees and allowlists isolate files, not memory, CPU, ports, DBs or
   browsers. One lead-owned runner provides per-class memory caps (cgroup `MemoryMax`) and a
   hard `RuntimeMaxSec`, serialized slots, admission on `MemAvailable`, result reuse by tree
   fingerprint, stop by unit (never `pkill -f`), and a host-wide browser slot (≤ 2 per host).
   Enforce it in code: the test runner's config refuses to start without the conductor's env
   marker (CI exempt, explicit one-file override for a person). The watchdog traps EXIT/TERM and
   kills its command's whole process tree. Agents never run suites in parallel: one suite per
   host, builders run only their own files through the conductor, a lead stops builders' runs
   before a gate. After any run no orphan test, browser or ffmpeg process (check by cwd and
   parent) and no temp dirs remain. (2026-11-01: raw runs beside a gate pushed host load to 180.)

## Diagnose a slow suite before adding workers

Order of checks (2026-11-01: a 3,400-test tier took 2,274 s on 8 workers with ~2.7 of 32 cores
busy; one 1,903 s file set the wall):

1. **CPU used vs cores** (`/usr/bin/time -v`: user+sys / wall). Low use means waiting or a
   long tail; more workers will not help.
2. **Slowest files** (per-file durations). The wall is at least the slowest file; split it, or
   move its rows to a cheaper layer and keep one full journey.
3. **Tier placement.** A heavy suite (ffmpeg, browser) runs in its own tier selected by the
   diff's import graph, not in every unit run as well.
4. **Caps against today's hardware.** A CPU cap set for a smaller host silently halves
   throughput after an upgrade; re-read caps when `nproc` changes.
5. **No overlap.** One host lock for gate, E2E and affected runs; overlap produced false
   failures and a full rerun.
6. **Typecheck.** Use the native checker for the inner loop once it matches `tsc` on the repo.

## Shared-checkout hazards (one line each)

- Release images build from a clean worktree of HEAD, never a shared checkout.
- Commits through a temporary index leave the real index stale: run `git reset -q -- <own paths>`
  after each, and check `git diff --cached` is only yours before a plain `git commit`.
- Never rewrite a file with `open(f,'w').write(edit(open(f).read()))`: read into a variable,
  assert the anchor, then write.
- Wait on a PID (`kill -0 $pid`) or a bracketed pattern (`pgrep -f '[c]heck-affected'`), never on
  `pgrep -f <text>`, which matches the waiting shell itself.
