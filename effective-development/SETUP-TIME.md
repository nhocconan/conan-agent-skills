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
