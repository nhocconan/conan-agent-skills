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
- **The environment**, for any agent outside this session (Codex, agy, a fresh CLI):
  working directory, startup command, which credentials exist. It does not share your
  shell, your paths, or your open browser.

**Bias the brief toward independence.** A verifier that is told the previous agent's
conclusion will confirm it. Give a verifier the location and the rules — never the verdict.

---

## Briefing the current generation (Opus 5 / Fable 5 — verified vs Anthropic docs, 2026-08-28)

The documented direction is **subtractive**: scaffolding tuned for the 4.x
generation now degrades output. When writing or migrating briefs, skills, and
rule files:

- **Delete carried-over verification nudges.** Opus 5 "verifies its own work
  without being told to"; "double-check your answer" compounds into
  over-verification and cost. Evidence-grounding is different and stays:
  "before reporting progress, audit each claim against a tool result from
  this session" — this is the documented cure for fabricated status reports.
- **Delete anti-laziness pushes** ("if in doubt, use the tool", forced
  update cadences) — current models overtrigger on them.
- **Describe the outcome, not the steps; give the reason, not only the
  request.** Instruction-following is literal now: models don't silently
  generalize, and they generalize *well* from a stated why.
- **Emphasis budget: one line.** Emphasize many lines and none stands out.
- **Effort is the primary knob**, re-swept on every model upgrade (Fable:
  start `high` even for workloads that ran `xhigh` before). Prompt length
  no longer follows effort — steer verbosity explicitly.
- **Prefer fresh-context verifier subagents over self-critique**, async over
  blocking; cap spawn depth/concurrency/budget where the harness allows.
- **Prune prescriptive skills on upgrade** — prior-generation step-by-step
  skills "can degrade output quality"; keep outcome + constraints, drop
  narration.
- **Never ask the model to echo its reasoning** — on Fable this can trigger
  the `reasoning_extraction` refusal.

## Shell hygiene in every brief

Tell each worker: absolute paths only; never `cd <dir> && …` (a Read deny rule in
the project settings makes the permission checker refuse the whole line, and the
operator gets a prompt per command); `git -C`, `pnpm -C`/`--dir`; Read/Grep/Glob
tools over shell for reading and searching. A worker that raises prompts is
re-briefed at once, not left to page the operator (incident 2026-09-03).
