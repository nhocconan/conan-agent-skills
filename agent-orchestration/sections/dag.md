## Cut into a DAG, not a to-do list

**Cut along verification seams.** A good node has local acceptance and an explicit
integration check at its dependent seam.
Nodes may deliver independently checkable contracts before the complete journey exists.

**The delegation test:** if you cannot write the acceptance check before the agent starts,
clarify its scope first. Judgment work can be delegated with criteria, raw evidence,
and stated uncertainty; the lead retains acceptance.

**Default cuts that work:** by package/layer (schema → API → UI), by screen, by connector,
by review dimension (correctness / security / perf / tests), by file group, by data window.

**Dependency discipline.** Draw an edge only for a *data* dependency — B literally cannot
start without A's output. These are not dependencies, and treating them as such is how
runs turn sequential:

- "It's cleaner to finish A first" — taste, not a dependency.
- "B might need to know what A decided" — then the *lead* decides it up front (the seam contract in
  [integrate](integrate.md)) and both start now.
- Review of A need not block unrelated B. If B depends on A's validated contract
  or a safety precondition, keep the dependency; do not assume speculative rework
  is cheaper than waiting.

**Waves.** A wave is every node whose dependencies are satisfied. Launch ready nodes
within available slots; prioritize nodes on the critical path
(the longest dependent chain), then independent coverage. Keep the lead useful rather
than filling slots with speculative work. When a stage-2 node depends only on *its own*
stage-1 node, do not wait for the whole
stage — pipeline it (each item flows through all stages independently). A barrier is
justified only when the next stage genuinely needs *all* prior results together: dedup
across the full finding set, early-exit on zero, or a synthesis that compares siblings.

**Write conflicts are the real limit on parallelism.** Two agents editing one module
produce a merge the lead has to resolve by hand. Options, in order of preference: (a) cut
so each file has exactly one writer, (b) give each agent its own git worktree,
(c) serialize those two nodes and parallelize something else. Parallelism whose outputs
cannot be verified or merged separately buys nothing.

**When not to parallelize:** coordination and integration cost exceed the likely saving;
the pieces share one file without isolation; or the spec is still moving. Duration alone
does not decide: a short independent check can be worthwhile. Use observed timings and
rework to improve the next partition; hypothetical solo speedups stay unknown.

---
