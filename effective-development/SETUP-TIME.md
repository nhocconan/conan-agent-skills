# Audit setup time before test time

The time of a slow loop is rarely in the tests: it is in waiting and setup around them
(O. Gretzinger, "How I made our CI 20x faster": 20,000 cases audited, the time was setup).

## 1. Split every run into wait / setup / running

Read the last 10+ runs of each kind (gate tier, E2E shard, affected check) from their logs
and put each second in one bucket:

| Bucket | What counts | Where it shows |
|---|---|---|
| wait | host lock, slot queue, a shard waiting for a free browser slot | "waiting" lines, first progress line per shard |
| setup | install, build cache miss, template DB clone, server start until ready, test runner import/collect/environment | runner duration breakdowns, build logs, server ready line |
| running | test time | per-file durations |

Fix the largest wait/setup sink first. Removing tests to save time is never the fix.

## 2. Sinks the split usually finds

- **Polling watchdog.** Every wrapped job ends on the poll boundary. Detect child exit within
  1 s (`wait` or a 1 s `kill -0` loop); keep the hung/idle CPU check on its own slower cadence.
  (2026-11-02: 30.1 s to 1.08 s for a 1 s job.)
- **More shards than execution slots.** Shards sit queued while others run. Default the shard
  count to slot capacity, read from the same source as the slot limiter; an explicit N still wins.
- **Cache key hashes inputs the build never reads.** A docs- or test-only commit rebuilds. Hash
  only what the build's generators read; test that an unread path keeps the key and a read one
  changes it.
- **Build repeats a check another tier ran.** Skip the build's own type-check when the same
  revision's typecheck passed (one flag, set only by the gate).
- **Task-runner hash includes CLI args or `TZ`.** Pass worker caps by env so identical runs hit
  the cache. (2026-11-02: 10 of 34 packages cached, 29 of 34 after.)
- **Gate steps run serially.** Run independent steps in dependency waves; keep an env switch that
  restores the serial order for debugging.
- **Pre-push reruns a gate that already passed.** Fingerprint content (git blob ids plus
  untracked files, commit-invariant) and accept a matching green result; test that a changed byte
  or a new untracked file reruns.

## 3. Test the skip logic itself

Affected selection that selects nothing reports green. Add a canary that hides a change in a
service, a pipeline, a job and a migration, and asserts each selects at least one test that
imports it (or the widening step that covers it); make the runner exit non-zero when a
changed runtime source selects zero tests. (2026-11-02: an empty selection exited 0 and
45 of 1,221 source files had no importing test.)

## 4. Candidates: adopt only after measuring on the repo

- Faster linter as a first pass (Oxlint), keeping the full linter for typed and invariant rules.
  Ports of compiler rules can disagree with the originals (23 false hits on one rule): keep
  such rules in the original linter until a seeded-violation parity check matches.
- Native typecheck (`tsgo`): adopt when its diagnostics equal `tsc` on the repo and on a
  seeded-error fixture; use it fail-fast and keep `tsc` authoritative.
- Test-runner isolation off (`isolate: false`): measure the import share of test time first;
  isolation pays only where import dominates (2026-11-02: no gain at 31 % import share).
  Use a per-file allow-list of files proven pure, a state-reset hook that fails on leaked
  env/globals/timers, and shuffled runs; a global switch bled mocks into 38-69 files.
- Re-measure worker count after every overlap fix: red runs at higher parallelism were often
  caused by overlapping runs, not by the tests (2026-11-02: 4 to 8 workers, 154 s to 96 s).
- Pre-push hook (format + fast lint + fast typecheck on changed files, < 9 s): a hook, not a
  written rule, because agents skip written steps in long sessions.
- Blobless CI checkout (`filter: blob:none`), never shallow when anything reads history.
