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
