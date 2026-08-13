---
name: agent-orchestration
description: How a lead model runs a fleet — cut the work into a parallel DAG, route each node to the right model tier (frontier for judgment, mid for implementation, cheap for breadth, a different lineage for red-team), brief each one as a contract, verify every claim with independent scored verifiers instead of trusting green, track progress and quality in a live ledger, and integrate the parallel output back into one coherent change. Use at the start of any multi-hour, multi-workstream or multi-agent task; when spawning subagents, workflows or parallel work; when writing a handoff for another agent/CLI (Claude Code, Codex, Gemini); when a session may die mid-run; or when the user says "delegate", "giao cho Opus/Sonnet làm", "orchestrate", "fan out sub-agents", "chạy song song", "multi-agent", "quality gate", "viết handoff", "resume", "đừng làm tuần tự", "đừng dừng giữa chừng".
---

# Agent Orchestration — running a fleet

The lead model is the scarcest resource in the run, and wall-clock is the second scarcest.
The lead does exactly four things: **decide, delegate, verify, integrate** — plus write the
tricky 10% nobody can be briefed on. Three failure modes bracket the job:

1. Burning the frontier tier on mechanical edits.
2. Delegating a judgment call to a model that cannot make it.
3. **Running in sequence what had no data dependency** — the invisible one, because the
   result still looks correct; it just cost three hours instead of forty minutes.

The third is the one that goes unnoticed, so it gets the strongest rule in this skill:
**everything is parallel until a data dependency proves otherwise.**

**Router**

| You're here because… | Go to |
| --- | --- |
| A big task just landed and you don't know how to staff it | §1, §2 |
| You know the pieces but not who should do them | §3 |
| An agent is about to be spawned | §4 |
| Agents came back and you have to decide what's true | §5 |
| Parallel work is done and must become one change | §6 |
| The run is long, unattended, or may die | §7, §8 |
| The same tier keeps failing the same check | §5.6 |

Companion files: [`FANOUT-PATTERNS.md`](FANOUT-PATTERNS.md) (harness mechanics — Agent
tool, Workflow scripts, worktrees, cross-CLI), [`TEMPLATES.md`](TEMPLATES.md) (brief,
plan file, fleet ledger, verifier prompt).

---

## §1. Launch sequence — ten minutes before anything spawns

Do not spawn on reflex. A fleet launched against a bad cut is a fast way to produce
merge conflicts and confident wrong answers.

1. **Classify the deliverable.** Diagnosis, answer, or verified change? A fleet built for
   the wrong deliverable is pure waste (`senior-operator` §1).
2. **Cut the work into a DAG** (§2), writing the acceptance check for each node *before*
   deciding who runs it.
3. **Write the plan file and the fleet ledger to disk** (§7) — before wave 1, not after.
   A single wave of two or three agents needs only the ledger; anything multi-wave or
   longer than one sitting gets the file, because that is what makes it resumable.
4. **Choose the fleet shape** (`FANOUT-PATTERNS.md` §1): inline subagents, a scripted
   workflow, cross-CLI, or just do it yourself. Cost scales with fleet size; anything
   above a handful of agents is the operator's call, not yours.
5. **Fan out wave 1 in a single message** — parallel means one message with N tool calls.
   N calls in N messages is sequential work wearing a fleet's clothes.

Then, and only then, the lead starts its own wave-1 node. The lead is never idle waiting
for agents; it reviews wave *N−1* while wave *N* runs.

---

## §2. Cut into a DAG, not a to-do list

**Cut along verification seams.** A good node has a pass/fail check that does not require
any sibling node to exist yet. If two nodes can only be checked together, they are one node.

**The delegation test:** if you cannot write the acceptance check before the agent starts,
you cannot delegate the task. Write the check first. If the check is "looks good to me",
it is a judgment call — keep it.

**Default cuts that work:** by package/layer (schema → API → UI), by screen, by connector,
by review dimension (correctness / security / perf / tests), by file group, by data window.

**Dependency discipline.** Draw an edge only for a *data* dependency — B literally cannot
start without A's output. These are not dependencies, and treating them as such is how
runs turn sequential:

- "It's cleaner to finish A first" — taste, not a dependency.
- "B might need to know what A decided" — then the *lead* decides it up front (§6 seam
  contract) and both start now.
- "I want to review A before B starts" — review happens off the critical path, in parallel
  with B; if A turns out wrong, B's rework is usually cheaper than the serialized wait.

**Waves.** A wave is every node whose dependencies are satisfied. Launch the whole wave at
once. When a stage-2 node depends only on *its own* stage-1 node, do not wait for the whole
stage — pipeline it (each item flows through all stages independently). A barrier is
justified only when the next stage genuinely needs *all* prior results together: dedup
across the full finding set, early-exit on zero, or a synthesis that compares siblings.

**Write conflicts are the real limit on parallelism.** Two agents editing one module is
merge hell. Options, in order of preference: (a) cut so each file has exactly one writer,
(b) give each agent its own git worktree, (c) serialize those two nodes and parallelize
something else. Parallelism you cannot verify or merge separately is not parallelism, it
is a race.

**When not to parallelize:** the task is under ~20 minutes of work; the pieces share one
file; the spec is still moving; or the token cost of N agents exceeds the value of the
wall-clock saved. Say so out loud instead of fanning out for show.

---

## §3. Route each node to a tier

Tiers are **roles**, not brand names. Map roles to whatever the harness exposes today —
the Claude Code Agent tool takes `model: opus | fable | sonnet | haiku` plus an effort
dial, and other CLIs have their own. Relative model strength moves every few months:
**check what the session actually offers rather than trusting this mapping**, and re-check
it whenever a new family ships.

| Work | Role tier | Effort | Why |
| --- | --- | --- | --- |
| Decompose, decide architecture, resolve ambiguity | lead (frontier) | high+ | wrong here is expensive and silent |
| Diff review, gate verification, risk calls, the merge | lead (frontier) | high+ | accountability cannot be delegated |
| The tricky 10% with no clean spec | lead (frontier) | high+ | if you can't spec it, you can't delegate it |
| Adversarial verification of a load-bearing finding | frontier, **fresh context** | high | needs judgment *and* independence |
| Implementation of an already-specified workstream | mid | medium | competence, not final judgment |
| Test writing against a stated contract | mid | medium | the contract is the spec |
| Codebase survey, "where is X", file inventory | cheap, read-only, parallel | low | breadth, zero judgment |
| Mechanical refactor with a mechanical check | cheap | low | the check is the safety net |
| Docs, changelog, copy drafts | cheap → mid | low | review catches drift |
| Web research / fact gathering | cheap, told to mark UNVERIFIED | low | facts either verify or they don't |
| Red team on a decision the whole fleet shares | **different lineage** (Codex, Gemini) | — | same-model verifiers share blind spots |

**Effort is a second dial, cheaper than a tier bump.** A mid model at high effort often
beats a frontier model at low effort, at a fraction of the cost. Reach for effort first.

**Cross-lineage matters for one thing: independence.** Verified on this machine —
`codex` 0.147.0 and `gemini` 0.55.1 are installed (`FANOUT-PATTERNS.md` §4). A second
Claude agent shares Claude's blind spots; when a conclusion is load-bearing and the fleet
agreed too easily, ask a different lineage.

**Anti-patterns.** Routing by prestige ("it's important, use the big one") instead of by
whether the check is mechanical. Sending a frontier model to grep. Sending a cheap model
to a task whose acceptance check is "use good judgment".

---

## §4. The brief is a contract

The executor is a weaker model with none of your context and no way to infer what you left
out. Full template in [`TEMPLATES.md`](TEMPLATES.md); every brief carries:

- **Goal** in one sentence — the outcome, not the activity.
- **Files in scope**, absolute paths. Everything else is explicitly off-limits.
- **Acceptance checks** — exact commands and what green looks like. Not "make sure tests
  pass"; the command, and the positive marker in its output.
- **Known traps** for this area — the project's rulebook sections, past incidents.
- **Non-functional acceptance, when it applies** — the tenancy filter, the auth check, the
  N+1 that must not appear, the query budget. Security and performance are cheaper
  specified in the brief than found in review (§5.3); the review is the backstop, not the
  design.
- **Boundaries** — "implement, do NOT commit", "do not touch migrations", "do not create
  new docs" (stray files and stray docs are a standing complaint).
- **Return format** — say exactly what to report: the diff summary, command output,
  and everything it could not verify. Structured output (a schema) beats prose whenever
  the result feeds a merge step.
- **The environment**, for any agent outside this session (Codex, Gemini, a fresh CLI):
  working directory, startup command, which credentials exist. It does not share your
  shell, your paths, or your open browser.

**Bias the brief toward independence.** A verifier that is told the previous agent's
conclusion will confirm it. Give a verifier the location and the rules — never the verdict.

---

## §5. Quality gate — verify the fleet, never trust it

### 5.1 Never trust a green claim

- **Never pipe a build or test through `tail`/`head`/`grep`** — the exit code becomes the
  pipe's. Redirect and inspect both signals: `cmd > run.log 2>&1; echo "EXIT=$?"`, then
  grep the log for a *positive* marker (`BUILD SUCCESSFUL`, an actual test count) **and**
  confirm `EXIT=0`.
- **A claim without an artifact is a guess.** "Tests pass" needs the count. "The page
  renders" needs the screenshot or HTTP status. "The API returns X" needs the payload.
- The lead re-runs the check itself for anything load-bearing. Delegation moves the typing,
  not the accountability.

### 5.2 Independent verification, scored

For each finding or claim that matters, spawn a verifier with **fresh context** that sees
the location and the rules but not the reasoning. Ask for a 1–10 confidence score with a
written justification, and instruct it to explain *why not* below the bar.

| Score | Meaning | Action |
| --- | --- | --- |
| 9–10 | Re-derived independently; concrete failing input or exploit path | act on it |
| 7–8 | Strong pattern match, not re-derived | act, flag as unverified |
| 5–6 | Plausible | report with caveat only |
| ≤4 | Speculation | discard (keep in an appendix if severity would be P0) |

Default gate: **discard below 8** for anything that would cause a code change; loosen only
for a deliberately exhaustive sweep, and say that you did.

### 5.3 Diverse lenses beat redundant ones

Three identical verifiers mostly agree with each other. Give each a different lens —
correctness, security, performance, "does it actually reproduce" — when a finding can fail
in more than one way. **Security and performance are insurance lenses: run them even when
they are usually silent**, on anything touching auth, tenancy, money, user input, uploads,
migrations, or a hot query path.

### 5.4 Merge findings like a reviewer, not a stapler

Fingerprint each finding (`path:line:category`), group, keep the highest-confidence
version, and mark the rest as confirmations. **Two independent lenses hitting the same
fingerprint is real signal** — raise its confidence and say which lenses agreed. Then rank
by severity, and state the count you dropped and why.

### 5.5 Know when you are done looking

For discovery work with no known answer count, run until **two consecutive waves surface
nothing new** (dedup against everything seen, not against what survived the gate — or
rejected findings reappear forever). Then run one **completeness critic**: what modality
was never run, what claim was never verified, what source was never read? Its answer is
the next wave, or the honest limits paragraph in your report.

### 5.6 Escalate — the ladder runs both ways

Delegation down is the default; **escalation up is mandatory after repeated failure.**
If a tier fails the same acceptance check twice, do not send it a third time — the spec is
wrong, or the task needed the top tier all along. Take it back, re-spec it, or do it
yourself. Symmetrically: if the lead is doing something a cheap tier could verify
mechanically, that is waste. Both directions are errors.

---

## §6. Integrate — the merge is the lead's job

Parallel work is not done when the agents return. It is done when the combined change is
coherent, and nobody but the lead can judge that.

- **Decide the seams before fan-out.** Shared types, interfaces, table columns, route
  names, i18n keys, file paths — the lead fixes these in the briefs. Contracts invented
  independently by three agents will not meet.
- **Integrate in dependency order**: contracts and schemas first, then implementations,
  then cross-cutting concerns (i18n, docs, tests) that reference both.
- **One writer per file, always.** If two nodes must touch one file, the lead applies the
  second one by hand, or the nodes run in worktrees and the lead resolves the merge.
- **Read the combined diff as a stranger.** Duplicate helpers that should be one, two
  names for one concept, an interface nobody ended up calling, a seam left dangling. Each
  agent's diff can be locally perfect and the union still incoherent — this pass is the
  only place that gets caught.
- **Run the full gate once, on the merged tree, yourself.** Per-node green says nothing
  about the union.
- **Then report as one change**, not as N agent reports stapled together.

---

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

## §9. Context budget

Everything an executor must know competes with the work itself.

- Push bulk output (searches, file dumps, surveys) into subagents so their intermediate
  reading never enters the lead's context. Keep the conclusion, not the transcript. This
  is a *context* argument for delegation that holds even when the lead could do the work.
- Briefs quote the sections that apply, not the whole rulebook.
- A rulebook (`CLAUDE.md` / `AGENTS.md`) past its char limit stops being read. Invariants
  and traps stay; reference material moves to linked files opened on demand.
- Ask for structured returns. A schema-shaped result is smaller than prose and mergeable
  without re-reading.

---

## Companions

`senior-operator` — how to think on a hard task (this skill is how to *staff* it).
`bug-class-audits` — what to do with a defect a subagent surfaces.
`spec-task-breakdown` — when the DAG needs to be sprints of committable tasks.
`secure-code-audit` / `web-perf-audit` — the checklists behind the §5.3 insurance lenses.
