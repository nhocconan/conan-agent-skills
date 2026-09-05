# Fan-out patterns — the mechanics

How the DAG in `SKILL.md` §2 actually gets launched. Harness-specific; check the tool
schemas in your own session before trusting any parameter here, because harness surfaces
change faster than this file.

## Contents

1. Choosing the fleet shape
2. Claude Code — the Agent tool
3. Claude Code — the Workflow tool (opt-in)
4. Other lineages — Codex, agy
5. Worktrees, by hand
6. Cost, caps, and the honest limits

---

## 1. Choosing the fleet shape

| Situation | Shape |
| --- | --- |
| 2–8 independent nodes, one wave, you'll judge the results yourself | inline subagents, one message, N calls |
| Multi-stage with a fixed structure (find → verify → synthesize), or ≥10 nodes | a scripted workflow, if the harness has one and the operator opted in |
| One load-bearing conclusion that needs an outside opinion | cross-lineage CLI (Codex / agy) |
| Long-running external work (CI, deploy, a big build) | background task + poll, never a blocking wait |
| Under ~20 min of work, or the pieces share a file | no fleet — do it yourself |

**The opt-in rule.** Fleets cost real money and some harnesses gate them. In Claude Code
today, the Workflow tool runs only on explicit user opt-in (the `ultracode` keyword, an
explicit "use a workflow / fan out agents", a skill that instructs it, or a named saved
workflow), and some session configs also gate the Agent tool the same way. When a fleet
would help but you lack the opt-in: describe the shape and the rough cost in two lines and
ask. Do not silently spawn, and do not silently do it sequentially either.

---

## 2. Claude Code — the Agent tool

The workhorse. One call = one subagent with its own context window.

**Parallel means one message.** Put every wave-1 call in a single assistant message.
Calls split across messages run one after another — the most common way a "parallel" run
turns out to have been sequential.

Parameters that matter for orchestration (verified against the tool schema, 2026-08):

- `subagent_type` — pick from the session's registry. `Explore` is read-only and built for
  breadth (it reads excerpts, not whole files) — the right default for surveys. `Plan`
  designs; `general-purpose` does everything; plugin-provided types (reviewers, validators)
  come from `.claude/agents/*.md` or the SDK.
- `model` — `opus | fable | sonnet | haiku`. Overrides the agent definition. Omit to
  inherit the session model. Route per `SKILL.md` §3.
- `run_in_background` — default true; you are notified on completion. Set `false` only
  when your very next action depends on the result and nothing else could usefully happen.
- `isolation: "worktree"` — a fresh git worktree per agent. Use only when agents mutate
  files in parallel and would otherwise collide; it costs setup time and disk.
- `SendMessage` (with the agent's id/name) continues an existing agent with its context
  intact. A fresh `Agent` call starts from zero — use it deliberately when you *want*
  independence (verifiers), not by accident.

**Reporting.** A subagent's final text is its return value and is not shown to the user.
The lead relays what matters. Ask for a compact, structured return (see `TEMPLATES.md`) —
prose returns force a re-read at merge time.

**Never predict a pending agent's result.** If the operator asks before the notification
arrives, say it is still running.

---

## 3. Claude Code — the Workflow tool (opt-in)

A JavaScript script that orchestrates subagents deterministically — loops, conditionals,
fan-out, staged pipelines — and runs in the background. Reach for it when the *structure*
of the fan-out should be code rather than model judgment.

**Requires explicit opt-in** (see §1). It can spawn dozens of agents.

The primitives (verified against the tool schema, 2026-08):

- `agent(prompt, opts)` → the subagent's text, or a validated object when `opts.schema`
  (a JSON Schema) is passed. Returns `null` if the agent died or was skipped — filter.
  `opts`: `label`, `phase`, `schema`, `model`, `effort` (`low|medium|high|xhigh|max`),
  `isolation: 'worktree'`, `agentType`.
- `pipeline(items, stage1, stage2, …)` — each item flows through every stage
  independently, **no barrier between stages**. This is the default for multi-stage work:
  wall-clock is the slowest single chain, not the sum of the slowest per stage.
- `parallel(thunks)` — a barrier: waits for all. Justified only when the next step needs
  every prior result together (dedup across the whole set, early-exit on zero, a synthesis
  that compares siblings). "I need to flatten/map first" is not a barrier — do it inside a
  pipeline stage.
- `phase(title)`, `log(msg)` — progress grouping and narrator lines for the operator.
- `budget` — `{total, spent(), remaining()}`; the token target is a hard ceiling. Scale
  fleet size off it (`while (budget.total && budget.remaining() > 50_000)`) rather than
  hard-coding a count.

Caps to design around: concurrency `min(16, cores − 2)` per workflow (excess queues),
1000 agents per run, 4096 items per `parallel`/`pipeline` call. Scripts are plain JS —
no TypeScript syntax, and `Date.now()` / `Math.random()` / argless `new Date()` throw
(they would break resume); pass timestamps in via `args`.

**Shape that earns its cost** — pipeline by default, verify as each dimension lands:

```js
export const meta = {
  name: 'review-changes',
  description: 'Review changed files across dimensions, verify each finding',
  phases: [{ title: 'Review' }, { title: 'Verify' }],
}
const results = await pipeline(
  DIMENSIONS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS }),
  review => parallel(review.findings.map(f => () =>
    agent(`Adversarially verify, then score 1-10: ${f.title}`,
          { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT, effort: 'high' })
      .then(v => ({ ...f, verdict: v })))),
)
return { confirmed: results.flat().filter(Boolean).filter(f => f.verdict?.score >= 8) }
```

**Loop until dry** (unknown answer count — `SKILL.md` §5.5): dedup against everything
*seen*, never against what survived the gate, or rejected findings return every round and
the loop never converges.

**Resume.** Each invocation persists its script and returns a `runId` and a script path.
Re-launch with `{scriptPath, resumeFromRunId}`: the longest unchanged prefix of `agent()`
calls returns cached results instantly, and the first edited call onward runs live. Before
diagnosing an empty result, read `journal.jsonl` in the transcript dir — it records what
each agent actually returned.

---

## 4. Other lineages — Codex, agy

For independence (`SKILL.md` §3), not for capacity. Verified installed on this machine:
`codex` 0.153.0, `agy` 1.1.27 — re-check before relying on flags, CLI surfaces move.

```bash
# Codex
codex exec --skip-git-repo-check -m "$MODEL" -c 'model_reasoning_effort="high"' "$PROMPT"

# Antigravity CLI (agy)
agy -p "$PROMPT" --effort high
```

- Give the full environment in the prompt: absolute working directory, the exact startup
  command, which credentials exist. It shares none of your session state.
- Sandbox/approval bypass flags exist and are what the upstream `codex-subagent` skill
  uses (for agy, use `--dangerously-skip-permissions` if non-interactive tool calls are needed);
  grant the narrowest thing that lets the task run, and never for a node that
  writes to anything production-shaped.
- Ask for a verdict plus its reasoning, and treat the answer as one vote — a different
  lineage is independent, not authoritative.

---

## 5. Worktrees, by hand

When agents must write to overlapping files and the harness's `isolation` flag is not
available:

```bash
git worktree add ../wt-<node> -b wip/<node>
# brief the agent with the worktree path as its working directory
git worktree remove ../wt-<node>          # after the merge
```

The lead merges, in the dependency order of `SKILL.md` §6. Never let an agent merge its
own branch into the integration branch.

---

## 6. Cost, caps, and the honest limits

- N agents cost roughly N × the tokens of doing it once, plus the lead's merge and review.
  Parallelism buys wall-clock, not tokens. Say so when proposing a fleet.
- Every cap you apply — top-N, no-retry, sampling, one verifier instead of three — gets
  logged in the ledger and stated in the report (`SKILL.md` §7).
- Partial fleets are fine: if one node dies, continue with the rest and name the gap.
  Specialists are additive; a missing lens is a stated limit, not a silent one.
