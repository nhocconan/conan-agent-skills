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
