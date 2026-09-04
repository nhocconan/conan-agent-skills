---
name: delegate-run
description: >-
  Operating contract for a fully-delegated single-agent run: the operator
  states intent once and touches the work at exactly three points — intent,
  plan approval when the work is risky, acceptance. The agent writes
  acceptance checks and a plan file BEFORE editing, runs without mid-run
  questions, grounds every claim in a tool result, and returns one fixed-format
  exit report plus a trust-ledger line so autonomy can widen by track record.
  Use when the operator hands over a whole task and walks away: "giao việc",
  "làm trọn gói", "tự làm đi", "đừng hỏi giữa chừng", "delegate this",
  "run this autonomously", "làm đi đừng để tao babysit", "chạy xong báo".
---

# Delegate-run — the three-touchpoint contract for one agent

Babysitting has four causes: sessions stalling on permission prompts, green
claims nobody verified, mid-run questions, and state only readable by
scrolling a transcript. This contract removes all four for the common case —
**one agent, one delegated task**. A fleet is a different problem
(`agent-orchestration` §0); a recurring job is a different problem
(`autonomous-loops`); report language is governed by `senior-operator` §7 and
its ban-list. Read the per-repo map (`senior-operator/projects/<slug>.md`)
first when one exists — machine facts live there.

## Kickoff — before any edit

1. Restate the deliverable in one sentence: diagnosis, answer, or verified
   change. Wrong here, the whole run is waste.
2. Classify risk. Touching money, tenancy, schema/migrations, production, or
   anything outward or irreversible → write a short plan (dependencies,
   failure modes, verification, rollback) and **wait at the plan gate**.
   Anything below that threshold proceeds now; silence means wait, never
   consent.
3. Write the acceptance checks first — exact commands and what passing looks
   like. A task whose check cannot be stated gets its one clarifying question
   asked NOW, at kickoff, never mid-run.
4. Put the plan on disk (`docs/plans/<slug>-<yyyy-mm>.md` unless the repo
   says otherwise): goal, steps, acceptance, assumptions, and a "needs
   operator" list capped at 3 items. Update it as each step lands — it is
   both the glanceable status and the crash-recovery point, since current
   models recover state from the filesystem well.
5. Estimated cost beyond the operator's stated norm (hours of wall-clock,
   spawning agents) is a kickoff disclosure, not a silent spend.

## Run — the no-babysit laws

- **One run = ONE turn. Never end the turn to wait.** Ending a turn while
  helpers, gates or deploys are still running reads to the operator as
  "please confirm" — that is the babysitting the contract exists to remove.
  While anything runs in the background the lead BLOCKS on it (TaskOutput
  `block=true` in ≤10-minute slices, or a Monitor event), prints a status
  line between slices, then continues with the next step in the same turn.
  The turn ends at exactly two points: the exit report, or a hard block that
  only the operator can lift. "Waiting on X" is never the last line of a turn.
- **Heartbeat, or the run is silent.** While anything runs in the background
  (agents, gates, builds, deploys), the lead posts a user-visible status at
  least every 10 minutes: DONE / RUNNING (elapsed, what it is doing) / NEXT /
  BLOCKED. A turn never ends on a bare "waiting" line — either the next
  independent piece of work happens now, or the heartbeat goes out with a
  concrete ETA and the exact thing being waited on. More than 15 minutes with
  nothing visible to the operator is a defect of the run, reported in the
  exit report like any other.
- **A stopped or dead helper is a crash, not a question.** When a sub-agent
  is stopped, times out, or dies, inspect its worktree/output for partial
  work, then resume or relaunch from disk state and continue. Never turn a
  crash into "tell me whether to resume".

- No mid-run questions. Pick the most defensible assumption, log it in the
  plan file, continue; open questions batch into the exit report. The only
  hard stop is an irreversible action or an ambiguity that would invalidate
  the entire run.
- End the turn only when the task is complete or blocked on input only the
  operator can provide.
- The same check failed twice → change the approach or take it back to
  re-spec. Never a third identical attempt.
- Do everything that is not blocked before surfacing what is.

## Evidence — the machine checks the claim

- Before reporting progress or completion, audit each claim against a tool
  result from this session. A claim without an artifact is a guess.
- The project's canonical gate decides green; the touched journey also gets
  one direct behavior check (browser, probe, payload) — static gates miss
  whole bug classes.
- A load-bearing conclusion gets one fresh-context verifier that sees the
  diff and the criteria, never the reasoning or the verdict.

## Exit report — fixed format, the trust artifact

```
RESULT: <one line: done / partial / failed — stated plainly>
EVIDENCE: <commands run + positive markers; screenshot refs for UI>
DID: <short bullets>
DECIDED: <each assumption taken, one line each, all reversible>
SKIPPED: <what + why — never hidden>
NEEDS YOU: <0–3 concrete items, each with a recommendation>
PLAN FILE: <path>
```

A failed run reported cleanly builds trust; a dressed-up one destroys every
future run's credibility. Bad news goes in RESULT, line one.

## Trust ledger — how autonomy widens

Last line of the plan file:
`trust: <task class> · run N of this class · clean yes/no · <note>`.
Three consecutive clean runs in a class → the operator may drop the plan gate
for that class. One unclean run → the gate comes back. Autonomy follows the
recorded track record, not vibes or enthusiasm.

## Per-project instantiation (day one, once)

- **No prompt storms.** Every prompt a helper raises lands on the operator's
  screen. Two known generators: (1) `Read(...)` deny rules in the project's
  agent settings make the checker refuse ANY `cd <dir> && <cmd>` shell line —
  brief helpers to use absolute paths, `git -C`, `pnpm -C`, and the
  Read/Grep/Glob tools, never a `cd` prefix; (2) commands outside the
  allowlist. If a run produces more than a handful of prompts, that is a
  defect of the brief or the settings, fixed in the run and recorded here.

- **Permissions**: allowlist the repo's own read/verify commands (the
  canonical gate, test/lint/typecheck, `git status/diff/log`, search) and
  deny secret files in the project's shared agent settings. Stalled
  permission prompts are cause #1 of babysitting.
- **Routing**: one line in the repo rulebook mapping "giao việc / delegate"
  to this contract.
- **The canonical gate named in one place** — every brief and loop cites it
  instead of re-listing commands.

## Briefing the current model generation

See `agent-orchestration/sections/brief.md` → "Briefing the current
generation" for what to delete from old prompts (carried-over verification
nudges, anti-laziness pushes, emphasis sprawl) and what to add (outcome not
steps, reasons, evidence-grounded progress). Written for Opus 5 / Fable 5,
verified against Anthropic docs 2026-08-28.

## Non-negotiable

No commit/push unless the intent says so. Irreversible and outward actions
always return to the operator. Secrets never enter prompts, logs, or reports.
