## Track and resume

Keep a plan and ledger in the repo's declared ignored working directory, for
example `.agents/<task>-plan.md`. If durable documentation was requested, use the
requested path. Templates are in [TEMPLATES.md](../TEMPLATES.md).

Record goal, dependencies, actual models/effort when exposed, owned files,
acceptance, status, artifacts, start/last meaningful progress, deadline, resource/process
handles and the lead's verdict. Unknown cost and solo timing remain unknown.

On a shared host the ledger also carries the conductor job id and unit per run, server port
and mode, DB name or fixture hash, and the fingerprint a green refers to. A stop order is a
conductor command whose result is logged, not a chat message. A result without a fingerprint
is `unverified`, whatever the worker said.

States: `pending → briefed → running → reviewing → done | failed | skipped | blocked`.
Only the lead marks done after acceptance. Record partial results promptly.
Failed dependencies block their dependents; independent work continues.

On resume, reconcile the ledger with the current diff, running processes, tool
results, and external state. Preserve useful partial edits. Recheck completed
nodes if dependencies or artifacts changed. Retry failed nodes only after their
cause is addressed, and do not replay external writes blindly.

The ledger says *what* to resume; the harness resumes the worker with its own primitive
([fan-out patterns](../FANOUT-PATTERNS.md)) rather than a fresh re-brief from the ledger.
Resume only to return a worker its review findings or answer its blocked question, never
to relay rules (they live in the shared brief); after two resumes re-brief fresh. A resume
to an idle worker restarts a full context for nothing (measured: 197 resumes in one week
beside 512 spawns); an agent spawned only to wait is the same waste.

After compaction, use both the saved plan and the latest user steering. The plan
does not override newer instructions or authorize more work.

### Lead context budget and handoff

The lead's context is the costliest one: every tool result, message and notification is
re-read on every later turn (measured: median 327k, 760M cache reads in 17 h; a week later
ten leads averaged 250k–720k per turn and 21 % of all spend, having run 135 test/E2E
commands and 455 log reads in their own context). Work at ≤ 120k; never start a turn above
150k. The lead runs no gate, suite, build or browser itself: a runner from the
[work-nature table](routing.md#work-nature--tier) runs it and returns the verdict line.
At 120k, or after two corrections on one issue, write
`<workdir>/handoff.md` — GOAL · STATE (landed, in gate, live, in flight with agent ids
and results files) · NEXT 5 · OPEN RISKS · IDS · COMMANDS · READ FIRST — then `/clear`
and resume from that file plus the shared brief. `/compact <focus>` only below ~60k when
continuity matters: a compaction re-reads the whole context. Operator trigger, one word
each: `/handoff`, `/clear`, `/pickup`. Cross-session messages and notifications start
full-context turns: ≤ 5 lines plus a results path, batched.

## Continue and communicate

Do useful independent work while workers run. Wait and report on the harness's own
mechanism and cadence ([fan-out patterns](../FANOUT-PATTERNS.md)): observed progress,
remaining uncertainty, next checks. Never invent an ETA, and never claim a launch without
a successful tool result.

A helper crash calls for inspection and recovery, not automatic user escalation.
On cancellation, or before reassignment or taking over files, stop the old writer and
confirm it has stopped, including its child processes. A timeout or sent interrupt is
not proof of termination. Preserve partial artifacts; isolate a replacement if the old
writer cannot be stopped. Reconcile late returns against the current task before use.
At a deadline or sustained lack of meaningful progress, inspect the last artifact and
process state, then stop or replan; repeated status messages are not progress.
Probe liveness read-only (results file, process table, pushed branch) — a resume restarts
an idle worker, and a file mtime is not liveness. Retry by cause within the run budget:
cap/OOM → smaller scope; network → bounded backoff; deterministic → diagnose first; unknown
→ once; after two, abandon the node and replan. Check external state before replaying an uncertain write.
End when complete or when required information/authority is unavailable after
safe independent work is exhausted. Clearly name incomplete nodes and why.

Respect budget limits and the harness's configured concurrency and depth limits.
Record deliberate sampling or skipped coverage; do not imply exhaustive work.
