---
name: agent-orchestration
description: How one lead runs a fleet as a control tower — decide solo vs fleet, cut the work into a parallel DAG, route each node to a tier (frontier for judgment, mid for building, cheap for breadth, another lineage for red-team), brief each worker as a contract with a mode and return shape, verify every claim with fresh-context scored verifiers, run a bounded review–fix loop, keep plan and ledger on disk, integrate into one coherent change. Use when starting any multi-hour, multi-workstream or multi-agent task; when spawning subagents or workflows; when writing a handoff for another agent/CLI (Codex, agy); when a session may die mid-run; when the operator wants one lead that staffs the work itself ("control tower", "chief of staff", "mày tự chia việc", "giao cho đội làm", "tao chỉ duyệt"); or on "delegate", "giao cho Opus/Sonnet", "orchestrate", "fan out", "chạy song song", "multi-agent", "quality gate", "viết handoff", "resume", "đừng làm tuần tự", "đừng dừng giữa chừng".
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

## §0. Solo or fleet — decide this first, out loud

Fleets cost 3–15× the tokens of one agent and only pay on work that is genuinely
parallel. **Solo** when the job is under ~20 minutes, the pieces share a file or a
singleton resource, the steps are inherently sequential, or the spec is still moving.
**Fleet** only for ≥2 nodes with disjoint file ownership and independent acceptance
checks — default ceiling 3–5 workers per wave. Say which rule decided it.

The operator has exactly three touchpoints: **set the task → approve the plan (required
when it touches schema, money, tenancy, production, anything irreversible, or grows the
fleet past the ceiling; silence = wait) → accept against a real demo.** Everything else is
the lead's. Full contract, lanes, pilot metrics, front-door rules: `sections/operating-contract.md`.

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
   Both land in the repo's declared gitignored working path, never in `docs/`
   (`docs-sync` → "Where an artifact is allowed to land"); a superseded plan is deleted
   in the same change, so a resuming agent cannot pick the wrong one.
4. **Choose the fleet shape** (`FANOUT-PATTERNS.md` §1): inline subagents, a scripted
   workflow, cross-CLI, or just do it yourself. Cost scales with fleet size; anything
   above a handful of agents is the operator's call, not yours.
5. **Fan out wave 1 in a single message** — parallel means one message with N tool calls.
   N calls in N messages is sequential work wearing a fleet's clothes.

Then, and only then, the lead starts its own wave-1 node. The lead is never idle waiting
for agents; it reviews wave *N−1* while wave *N* runs.

---

## Section index — Read each section when its situation applies

The §1 launch sequence above is the entry point and is always read. Everything
below it lives in `sections/` and is read at the step that needs it — read the
section in full before doing its step; the router table is an address, not a
summary.

| When | Read this section |
|------|-------------------|
| the operator hands the lead the whole job — control-tower contract, lanes, approval thresholds, pilot metrics, chat/voice front-door security (§0) | `sections/operating-contract.md` |
| cutting the work into a DAG and writing each node's acceptance check (§2) | `sections/dag.md` |
| deciding which model tier runs which node (§3) | `sections/routing.md` |
| an agent is about to be spawned and needs its brief (§4) | `sections/brief.md` |
| choosing the worker's mode (investigate / build / patch / refactor / migrate / verify) and the return shape to demand (§4b) | `sections/worker-modes.md` |
| agents came back and you must decide what is true — verification, lenses, merging findings, the bounded review–fix loop, stalemates, reviewer slots, the quote gate (§5) | `sections/quality-gate.md` |
| parallel work is done and must become one coherent change (§6) | `sections/integrate.md` |
| the run is long, unattended, or may die — ledger, node states, cascade-skip, resume, compaction, narration discipline (§7, §8) | `sections/tracking.md` |
| the work should run without a human trigger — nightly, on push, on a schedule | `autonomous-loops` skill |
| harness mechanics: Agent tool, Workflow scripts, worktrees, cross-CLI | `FANOUT-PATTERNS.md` |
| you need a brief, plan file, fleet ledger, or verifier prompt to fill in | `TEMPLATES.md` |

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
`autonomous-loops` — when a node should keep running without anyone typing the prompt.
`secure-code-audit` / `web-perf-audit` — the checklists behind the §5.3 insurance lenses.
