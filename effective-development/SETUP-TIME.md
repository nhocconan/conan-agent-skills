# Audit setup time before test time

The time of a slow loop is rarely in the tests: it is in waiting and setup around them
(O. Gretzinger, "How I made our CI 20x faster": 20,000 cases audited, the time was setup).
Measured on a 32-core shared host, 2026-11-02 (content-engine dev loop round 2).

## 1. Split every run into wait / setup / running

Read the last 10+ runs of each kind (gate tier, E2E shard, affected check) from their logs
and put each second in one bucket:

| Bucket | What counts | Where it shows |
|---|---|---|
| wait | host lock, slot queue, a shard waiting for a free browser slot | "waiting" lines, first progress line per shard |
| setup | install, build cache miss, template DB clone, server start until ready, test runner import/collect/environment | runner duration breakdowns, build logs, server ready line |
| running | test time | per-file durations |

Fix the largest wait/setup sink first. Removing tests to save time is never the fix.

## 2. Sinks found by that split (each measured before/after)

| Sink | Symptom | Fix | Measured |
|---|---|---|---|
| Watchdog polls the child every N s | every wrapped job ends on an N-second boundary; step starts in a log are N s apart | detect exit within 1 s (`wait` or a 1 s `kill -0` loop); keep the hung/idle CPU check at its own slower cadence | `slots.sh vitest sleep 1`: 30.1 s → 1.08 s (median of 3); +101-184 s per affected check before |
| More shards than execution slots | shards with no test done for ~8 min while others run | default shard count = slot capacity (read from the same source as the slot limiter); explicit N still wins | 4 shards on 2 slots: ≈ 480 s queue per extra shard |
| Cache key hashes inputs the build never reads | a docs- or test-only commit misses the build cache and rebuilds | hash only what the build's generators read (grep the generators for the paths they open); exclude test files; test that an unread path keeps the key and a read one changes it | hash unchanged after a `docs/plans` edit; web build hit 1 of 4 E2E runs before |
| The build repeats a check another tier already ran | framework build type-checks again after the typecheck tier | skip the build's own check when the same revision's typecheck passed (one flag, set only by the gate) | 162-240 s per gate build (not yet applied) |

## 3. Test the skip logic itself

Affected selection that selects nothing reports green. Add a canary that hides a change in a
service, a pipeline, a job and a migration, and asserts each selects at least one test that
imports it (or the widening step that covers it); make the runner exit non-zero when a
changed runtime source selects zero tests. Found 2026-11-02: an empty selection exited 0, and
45 of 1,221 source files had no importing test.

## 4. Candidates: adopt only after measuring on the repo

- Faster linter as a first pass (Oxlint), keeping the full linter for typed and invariant rules.
- Native typecheck (`tsgo`): adopt when its diagnostics equal `tsc` on the repo and on a
  seeded-error fixture.
- Test-runner isolation off (`isolate: false`) with a per-file state reset and a check that
  leaked state fails loudly.
- Pre-push hook (format + fast lint + fast typecheck on changed files, < 9 s): a hook, not a
  written rule, because agents skip written steps in long sessions.
- Blobless CI checkout (`filter: blob:none`), never shallow when anything reads history.

## 5. Measured adoptions (msocloud monorepo, 2026-11-02)

| Change | Before | After | Guard that keeps coverage |
|---|---|---|---|
| Watchdog detects exit in 0.2 s; attach loop stops when the job ends | 1.5 s job = 5.3 s; 42 % of 1,091 jobs ≤ 5 s | 1.8 s | live timing test with a loaded-host bound |
| Content fingerprint (git blob ids + untracked), commit-invariant; pre-push accepts a matching green gate | pre-push 206-231 s | 0 s on a hit, full subset on a miss | tests: same bytes reuse, one byte or a new untracked file reruns |
| Runner worker cap via env, not CLI args (args and `TZ` enter the task-runner hash) | 10 of 34 packages cached | 29 of 34 | two identical runs compared |
| `isolate: false` only for files proven pure; everything else isolated by default | web suite 55.8 s | 37.0 s, same 12,530 tests | allow-list, 5 shuffled runs, a reset hook that fails on leaked env/globals/timers |
| Gate steps in dependency waves | serial ≈ 305 s | 235 s incl. E2E | `MSO_GATE_SERIAL=1` restores the order |
| Hybrid lint: Oxlint runs every rule it covers, a slim ESLint keeps the rest | full web lint 50 s cold | Oxlint 0.5 s; slim ESLint still 45 s cold (React Compiler rules) | seeded-violation parity; unused-disable directives judged by the tool that owns the rule |

- Global `isolate: false` failed 38-69 files (`vi.mock` bleed); a per-file allow-list is the safe form.
- `tsgo` gave text-identical diagnostics to `tsc` on 45 packages and a seeded fixture, 7.5x faster;
  only the exit code differs (1 vs 2). Use it as a fail-fast step; keep `tsc` authoritative.
- Oxlint's ports of compiler rules disagreed with the originals (23 false hits on `purity`):
  keep such rules in the original linter until the ports match.
- The 100x lint gain applies to the Oxlint-only fast path; the full lint is bounded by the rules
  only the original linter has.
