## Integrate

Parallel work is not done when the agents return. It is done when the combined change is
coherent, and only the lead sees the whole of it.

- **Decide the seams before fan-out.** Shared types, interfaces, table columns, route
  names, i18n keys, file paths — the lead fixes these in the briefs. Contracts invented
  independently by three agents will not meet.
- **Integrate in dependency order**: contracts and schemas first, then implementations,
  then cross-cutting concerns (i18n, docs, tests) that reference both.
- **Ownership holds through integration** ([DAG](dag.md) manifest and ledger). A second
  change to one file is applied by the lead by hand, or the nodes ran in worktrees and the
  lead merges; the lead edits the shared index files itself after the writers land.
- **Read the combined diff as a stranger.** Duplicate helpers that should be one, two
  names for one concept, an interface nobody ended up calling, a seam left dangling. Each
  agent's diff can be locally perfect and the union still incoherent — this pass is the
  only place that gets caught.
- **Verify the final tree.** Wait for writers, then apply the [quality gate](quality-gate.md)
  on the recorded revision + working-diff fingerprint; per-node green alone does not prove
  the union.
- **Then report as one change**, not as N agent reports stapled together.

---
