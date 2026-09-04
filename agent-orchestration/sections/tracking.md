## §7. Track progress and quality out loud

Long runs die — context exhaustion, a crash, a rate limit, a closed laptop. State goes to
disk **as it happens**, never at the end.

- One **plan file** in the repo (`docs/plans/<topic>-<yyyy-mm>.md`), holding the goal, the
  DAG with waves, and a status marker per node updated *the moment* it lands.
- One **fleet ledger** beside it — node, tier, status, acceptance check, artifact,
  verdict, cost. It is what makes "how's it going" answerable in one line, and it is the
  input to the final report. Format in [`TEMPLATES.md`](TEMPLATES.md).
- **Partial results land immediately.** A harvest, a migration, a batch job writes each
  completed unit before starting the next. A dropped connection at item 400 costs item
  400, not items 1–400.
- **Resume is one instruction.** The next session reads the plan file and continues. If
  resuming requires re-deriving where you were, the plan file failed.
- **No silent caps.** If you capped the fan-out, sampled, took top-N, or skipped a retry,
  write it down. A silent cap reads as "covered everything" when it was not.
- On long unattended runs, emit a cheap periodic progress line so the operator can see the
  thing is alive.

The operator's standing instruction: *"đảm bảo ra plan chi tiết ra file và làm đến đâu
update đến đó, lần sau chỉ cần resume."*

---

## §8. Don't stop in the middle

Autonomous means autonomous. Finish the whole workstream; don't return after each step to
ask whether to continue. When genuinely blocked, do everything that isn't blocked first,
then surface the one decision — with your recommendation and the assumption you would
proceed on. A run that stalls silently is worse than a wrong guess: it burns wall-clock
with nothing to show.

Two exceptions that are not stalling: anything on the harness's confirm-first list
(irreversible, outward-facing, destructive), and a fleet expansion big enough to be the
operator's budget call.

---

## §7b. Node state, cascade-skip, and the two lies a lead can tell itself

**One status vocabulary**, written to the plan file the moment it changes:
`pending → briefed → running → reviewing → done | failed | skipped | blocked`.
`done` is the lead's verdict after re-running the check, never the worker's self-report.

**Cascade-skip.** When a node fails for good (unfixable review, two-strikes escalation
exhausted, environment gone), mark it `failed` with the error, then mark every
*transitive dependent* `skipped: dependency <id> failed`. Remove them from the ready
queue. **Independent nodes keep running** — a failed node is a gap to name, not a reason
to abort the run.

**Resume** re-evaluates each node: `done` stays; `failed` resets to `pending` with its
scratch state cleared; `skipped` returns to `pending` only if its dependencies are now
`done`; anything caught mid-flight (`running`, `reviewing`) is a crash — reset it and
retry from a clean brief, do not try to "continue" a worker whose context is gone.

**Reseed after compaction.** If the session's context is summarized mid-run, rebuild the
working task list from the plan file on disk — not from memory of the conversation. The
plan file is authoritative precisely because it survives what the transcript does not.

**Tool-call discipline (the narration lie).** Every action described in prose must be
backed by a tool call *in the same response*. "Launching the builder for N4…" with no
`Agent` call is a hallucinated launch, and the run stalls on it. Spawn first; narrate
afterwards, in past tense, with the returned id.

**Scripts enforce invariants, prompts don't.** A scout told "only under `apps/api`" will
still report whatever its search fed it. Every scoping rule the run depends on is a
filter the lead applies to the returned data (or a workflow-script check), with dropped
items logged — a live run once shipped ~50 out-of-scope findings on prompt text alone.
Silent truncation reads as full coverage: every cap gets a `log()` line.

## Heartbeat — the operator must see the tower working

Background workers make the lead look idle. Every 10 minutes of fleet time the
lead posts one status block to the operator: per workstream DONE / RUNNING
(elapsed) / NEXT, plus the one blocker if any and an ETA for the next
integration point. A turn that ends on "waiting for agents" without that block
is a defect. The ledger on disk is for crash recovery; the heartbeat is for the
human — both are required, neither substitutes for the other. A worker that is
stopped or dies is resumed or relaunched from its worktree/output by the lead,
not surfaced to the operator as a question (incident 2026-09-03: an hour of
silence, then a question, on a delegated run).
The lead does not end its turn to wait for workers: it blocks on them (TaskOutput
`block=true`, ≤10-minute slices) and prints the heartbeat between slices, so the
fleet run is one continuous turn from kickoff to integration report. A turn that
ends mid-fleet is read by the operator as a confirmation request (incident
2026-09-03, second occurrence).
