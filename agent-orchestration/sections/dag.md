## Cut into a DAG, not a to-do list

**Cut along verification seams.** A good node has local acceptance and an explicit
integration check at its dependent seam.
Nodes may deliver independently checkable contracts before the complete journey exists.

**The delegation test:** if you cannot write the acceptance check before the agent starts,
clarify its scope first. Judgment work can be delegated with criteria, raw evidence,
and stated uncertainty; the lead retains acceptance.

On a shared host, cut by phase: code lanes, affected tier per lane, one integration gate on
a frozen fingerprint, E2E on the one server, visual parity, review; add an edge only where
the next phase consumes the previous artifact.

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
than filling slots with speculative work. For three or more similar nodes, push one through
brief → worker → verify → integrate first and fix the brief template and the check from that
evidence before fanning out. When a stage-2 node depends only on *its own*
stage-1 node, do not wait for the whole
stage — pipeline it (each item flows through all stages independently). A barrier is
justified only when the next stage genuinely needs *all* prior results together: dedup
across the full finding set, early-exit on zero, or a synthesis that compares siblings.

**Ownership before fan-out.** Two agents editing one module produce a merge the lead
resolves by hand, and a shared checkout lets one writer's `git add`/`reset` reach another's
work (measured over one week: 84 `git reset`/`restore --staged` commands spent untangling
foreign staged files, one of them a step from reverting another agent's commit; the docs
map had five writers; two plans claimed the same migration number). Before the first spawn
the plan file carries, and every writer checks before it commits:

- **Ownership manifest** — path or directory → one writer. Index files the whole fleet
  touches (docs map, progress, changelog, review index) belong to the lead, edited after the
  writers land. A writer commits only when `git diff --name-only` is a subset of its rows.
- **Reserved-resource ledger** — migration numbers, decision/ADR ids, release numbers,
  ports, DB names: claimed in the ledger before use, first claim wins, never taken as "next
  free" at commit time.
- **Commit through own paths only** — `git add <owned paths>` then commit at once; never
  `git add -A`/`.`, `commit -a`, or a staged index left behind. Before committing, unstage
  any foreign path in `git diff --cached --name-only` without touching the file.
- **Shared typecheck surface** — writers inside one package or app run in series or each in
  its own worktree; a writer checks only its own files, and the integrated typecheck/gate
  runs once on a frozen fingerprint after every writer in that surface has committed. A
  writer blocked on another's half-done typecheck is a sequencing error, not a wait.
- Surfaces that still overlap: (a) recut so each file has one writer, (b) one worktree per
  writer and the lead merges, (c) serialize those nodes and parallelize others.

**When not to parallelize:** coordination and integration cost exceed the likely saving;
the pieces share one file without isolation; or the spec is still moving. Duration alone
does not decide: a short independent check can be worthwhile. Use observed timings and
rework to improve the next partition; hypothetical solo speedups stay unknown.

---
