## Cut into a DAG, not a to-do list

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
- "B might need to know what A decided" — then the *lead* decides it up front (the seam contract in
  [integrate](integrate.md)) and both start now.
- Review of A need not block unrelated B. If B depends on A's validated contract
  or a safety precondition, keep the dependency; do not assume speculative rework
  is cheaper than waiting.

**Waves.** A wave is every node whose dependencies are satisfied. Launch the whole wave at
once. When a stage-2 node depends only on *its own* stage-1 node, do not wait for the whole
stage — pipeline it (each item flows through all stages independently). A barrier is
justified only when the next stage genuinely needs *all* prior results together: dedup
across the full finding set, early-exit on zero, or a synthesis that compares siblings.

**Write conflicts are the real limit on parallelism.** Two agents editing one module
produce a merge the lead has to resolve by hand. Options, in order of preference: (a) cut
so each file has exactly one writer, (b) give each agent its own git worktree,
(c) serialize those two nodes and parallelize something else. Parallelism whose outputs
cannot be verified or merged separately buys nothing.

**When not to parallelize:** the task is under ~20 minutes of work; the pieces share one
file; the spec is still moving; or the token cost of N agents exceeds the value of the
wall-clock saved. Say so out loud instead of fanning out for show.

---
