---
name: agent-orchestration
description: How a lead model runs a fleet — delegate implementation to cheaper model tiers, write handoff briefs a weaker model can execute, verify their claims instead of trusting them, checkpoint long work to a resumable plan file so a dead session loses nothing, and escalate back up when a tier keeps failing. Use at the start of any multi-hour or multi-workstream task, when spawning subagents or parallel work, when writing a handoff for another agent/CLI (Claude Code, Codex, Gemini), when a session may die mid-run, or when the user says "delegate", "giao cho Opus/Sonnet làm", "orchestrate", "fanout sub-agents", "làm culy/lính lác", "viết handoff", "resume", "đừng dừng giữa chừng".
---

# Agent Orchestration

The strongest model available is the scarcest resource in the run. It should do exactly
four things: **decide, review, verify, and write the tricky 10%.** Everything else is
delegated to a cheaper tier. Two failure modes bracket this: burning the top tier on
mechanical edits, and delegating a judgment call to a model that cannot make it.

## 1. The tier table

| Work | Tier | Why |
| --- | --- | --- |
| Codebase survey, file inventory, doc reading, "where is X" | cheapest, parallel, read-only | breadth, zero judgment |
| Web research / fact-gathering | cheap, instructed to mark anything unverified | facts either verify or they don't |
| Implementation of an already-specified workstream | mid | needs competence, not final judgment |
| Docs, changelogs, copy drafts, test scaffolding | cheap → mid | review catches drift |
| Mechanical refactors with a mechanical check | cheap | the check is the safety net |
| Architecture decisions, diff review, gate verification, risk calls | strongest | this is where wrong is expensive |
| The tricky 10% — the part with no clean spec | strongest | if you can't spec it, you can't delegate it |

**The delegation test:** if you cannot write the acceptance check before the agent starts,
you cannot delegate the task. Write the check first. If the check is "looks good to me",
it is a judgment call — keep it.

## 2. The handoff brief

A brief is a contract, and the executor is a weaker model that will not infer what you
left out. Every brief carries:

- **Goal** in one sentence — the outcome, not the activity.
- **Files in scope.** Absolute paths. Everything else is off-limits, explicitly.
- **Acceptance checks** — the exact commands, with expected output. Not "make sure tests
  pass"; the command and what green looks like.
- **Known traps** for this area — the project's rulebook sections, past incidents, the
  specific mistakes already made here.
- **Boundaries** — "implement, do NOT commit", "do not touch migrations", "do not create
  new docs; if you must, check for an existing directory and that it's gitignored".
  (Stray files and stray docs are a repeat complaint: *"đừng có tạo docs bậy bạ"*.)
- **What to report back** — the diff summary, the command output, and anything it
  could not verify.

Briefs for *other CLIs* (Codex, Gemini, a fresh Claude Code session) need one more thing:
the environment. That agent does not share your shell, your paths, or your open browser.
State the working directory, the exact startup command, and which credentials exist.

## 3. Never trust a green claim

Agents report success they did not verify. The orchestrator re-runs the check itself
before believing anything. Two rules that have each cost a real incident:

- **Never pipe a build through `tail`/`head`/`grep`** — the exit code becomes the pipe's.
  Redirect and inspect both signals:
  `cmd > run.log 2>&1; echo "EXIT=$?"` then grep the log for a *positive* marker
  (`BUILD SUCCESSFUL`, an actual test count) **and** confirm `EXIT=0`.
- **A claim without an artifact is a guess.** "Tests pass" needs the count. "The page
  renders" needs the screenshot or the HTTP status. "The API returns X" needs the payload.

Review the diff hunk by hunk. Delegation moves the typing, not the accountability.

## 4. Checkpoint or lose the run

Long sessions die — context exhaustion, a crash, a rate limit, a closed laptop. Anything
that takes more than one sitting writes its state to disk **as it goes**, never at the end.

- One **plan file** in the repo (`docs/plans/<topic>-<yyyy-mm>.md`), holding: the goal,
  the ordered workstreams, and a status marker per item updated *the moment* it lands —
  not in a batch at the end.
- **Partial results land immediately.** A harvest, a migration, a batch job writes each
  completed unit to disk before starting the next one. A dropped connection at item 400
  must cost item 400, not items 1–400.
- **Resume must be one instruction.** The next session reads the plan file and continues.
  If resuming requires re-deriving where you were, the plan file failed.

The operator's standing instruction: *"đảm bảo ra plan chi tiết ra file và làm đến đâu
update đến đó, lần sau chỉ cần resume."*

## 5. Don't stop in the middle

Autonomous means autonomous. Finish the whole workstream; don't return after each step to
ask whether to continue. When genuinely blocked, do everything that isn't blocked first,
then surface the one decision — with your recommendation and the assumption you'd proceed
on. A run that stalls silently is worse than a wrong guess, because it burns wall-clock
with nothing to show. On long unattended runs, emit a cheap periodic progress line so the
operator can see the thing is alive.

## 6. Parallelize along verification seams

Two agents editing the same module is merge hell. Cut work where it verifies
independently — one agent per package/layer/screen, each with its own acceptance check.
When parallel agents must touch overlapping files, give each a **git worktree**.
Parallelism you cannot verify separately is not parallelism, it is a race.

## 7. Escalate — the ladder runs both ways

Delegation down is the default; **escalation up is mandatory after repeated failure.**
If the mid tier fails the same acceptance check twice, do not send it a third time —
the spec is wrong, or the task needed the top tier all along. Take it back, and either
re-spec it or do it yourself. The operator will notice the loop before you do:
*"OPUS CỨ MẮC LỖI HOÀI TẠI SAO LẠI SWITCH QUA OPUS HOÀI THẾ?"*

Symmetrically: if the top tier is doing something a cheap tier could verify mechanically,
that's waste. Both directions are errors.

## 8. Context budget

Everything the executor must know competes for its context with the work itself.

- A project rulebook (`CLAUDE.md` / `AGENTS.md`) that grows past its char limit stops
  being read. Keep it to invariants and traps; move the reference material to linked
  files the agent opens on demand.
- Briefs quote the sections that apply, not the whole rulebook.
- Push bulk output (searches, file dumps, surveys) into subagents so their intermediate
  reading never enters the orchestrator's context. Keep the conclusion, not the transcript.

## Companions

`senior-operator` — how to think on a hard task (this skill is how to *staff* it).
`bug-class-audits` — what to do with a defect a subagent surfaces.
