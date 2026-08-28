---
name: autonomous-loops
description: >-
  Turns a recurring job into a pre-written loop that runs without anyone typing the
  prompt — nightly data reconciliation, docs-drift checks, CI-failure summaries, weekly
  top-ups, post-deploy checks, "keep this PR green", "iterate until the tests pass".
  Defines what a real loop needs (trigger, prompt file in the repo, hard gate, stop
  condition), the five-rung ladder from a hand-run skill to a repo-resident agentic
  workflow, the brakes that keep an unattended agent from burning a night of tokens, and
  the escalation law (run by hand first, read-only CI next, scheduled with brakes, write
  access last and PR-only). Use when the user says "treo lịch", "chạy mỗi đêm", "tự chạy
  đi", "loop", "cron", "schedule", "routine", "automation", "babysit", "ralph", "keep
  going until", "đừng để tao phải gõ nữa", or asks which recurring job to automate first.
---

# Autonomous loops — design the loop, stop typing the prompt

"Stop prompting the agent. Design loops that prompt it for you." The idea is right; the
failure mode is an agent running loose overnight. A loop is only a loop when it has all
four parts — missing any one, it is either a habit or a runaway:

| Part | What it is | Missing it looks like |
| --- | --- | --- |
| **Trigger** | your hand, a session event, a repo event, a clock | "I'll remember to run it" |
| **Prompt file** | the task, frozen in the repo, diffable, reviewed like code | a prompt that drifts a little each time |
| **Gate** | a command whose exit code decides pass/fail; the loop's green is *not* success | "the run finished" |
| **Stop condition** | max iterations, wall-clock, token budget, no-progress detector | a $275k overnight token bill (reported, order-of-magnitude) |

**Green ≠ done.** A scheduled run's "success" means the run completed; only the gate
says the task succeeded. Every loop reports the gate's verdict, never the run's status.

## The ladder — five rungs, each with a stricter gate

| Rung | Trigger | Write access | What earns the next rung |
| --- | --- | --- | --- |
| 1 · Skill | a human invokes it | as the session allows | run by hand for ~a week, reading every output |
| 2 · Hook | a session event (before/after a tool, on stop) — exit code 2 *blocks* the action; this rung enforces, it does not advise | none of its own | the hook has never blocked something it should have allowed |
| 3 · Headless CI | repo event (push, PR) or CI cron; read-only, comments/reports only | **none** | outputs were correct for N runs and cheap to check |
| 4 · Scheduled | a clock outside the repo (routines, automations, `/loop`, cron on the box) | still read-only | brakes proven under a forced failure |
| 5 · Agentic workflow | lives in the repo as code; agent runs read-only, a separate narrowly-scoped job holds the token | **proposes PRs, never merges** | — |

**Escalation law:** hand → read-only CI → scheduled with brakes → write. Write access is
the *last* rung, and even there the output is a PR for a human. "Agents don't merge
code." Skipping a rung is how a loop ships a bad change at 3 a.m.

## Which job first — the ones three vendors independently listed

Nightly issue triage · docs-vs-code drift · CI-failure summary · daily/weekly status
report · post-deploy checks. What they share: **read-only or nearly, an output a human
can verify in two minutes, and it can run at night.** Pick the candidate whose gate is
already the strongest thing in the repo (a reconciliation script, an RLS assertion, a
verify command) — the loop inherits its trustworthiness from the gate, not from the prompt.

A loop is worth writing when the job has been done by hand **three times**. Before that,
it is a skill (rung 1) and nothing more.

## Brakes — the minimum set, no exceptions for "it's read-only"

- **Iteration cap** — a hard number, in the loop's own config, not in the prompt.
- **No-progress detection** — fingerprint each round's output; two identical rounds
  means stop and report, not try harder.
- **Budget** — tokens or wall-clock, whichever the harness can enforce; the loop reads
  it and stops early rather than being killed mid-write.
- **Single writer** — one loop per repo per window; two loops touching one tree is a
  race nobody scheduled.
- **Machine limits** — a loop competes with the humans' dev server for the same RAM and
  the same DB; schedule it when they are off (see the project map).
- **A kill switch** the operator can hit without reading the code: a file, a flag, a
  cron line to comment out.

## The completion promise — for "keep going until" loops

An in-session loop that feeds the same prompt back until done needs an explicit
**completion promise**: a phrase the agent may emit *only* when the statement is
completely true. Never emit it to escape a loop you are stuck in — say you are stuck,
name the blocker, and let the iteration cap end it. A false promise is worse than a
timeout: it reports success that did not happen.

## Section index — Read each section when its situation applies

| When | Read this section |
|------|-------------------|
| you are wiring the loop into a specific harness — Claude Code (`/loop`, wakeups, cron, routines, headless, hooks, GitHub Action, ralph), Codex automations, Cursor, GitHub agentic workflows | `sections/harness-mechanics.md` |
| you are writing the loop's spec file (trigger / prompt / gate / stop / brakes / owner) | `sections/loop-spec.md` |

## Related

`agent-orchestration` — the loop may itself fan out; the fleet rules still apply.
`senior-operator/projects/<slug>.md` — the repo's real gates and its machine limits.
`shipping-changes` — what a loop's PR must still pass; nothing lands without the operator.
