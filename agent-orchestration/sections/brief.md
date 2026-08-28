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
