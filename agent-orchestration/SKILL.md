---
name: agent-orchestration
description: >-
  Coordinate independent agent work with scoped ownership, model routing,
  resumable state, and evidence-based integration. Use for multi-workstream tasks,
  explicit delegation, parallel audits, or agent handoffs. The lead of the active
  harness owns final quality; workers hold scoped, checkable tasks.
---

# Agent orchestration

One lead owns the outcome and final quality; workers hold scoped tasks and never
final acceptance. Routing is harness-conditional — the lead slot belongs to the
active harness's own lead model, with no cross-harness substitution. Read the
[canonical model policy](sections/routing.md) before staffing anything.

## Start with the task

1. Classify the requested result: answer, diagnosis, review, or verified change.
   Preserve its scope and existing authorization.
2. Define observable acceptance and partition along independent outcomes.
   Use a fleet when independent work can proceed without shared-file or resource
   conflicts. Small, sequential work stays with the lead; orchestration does not
   require spawning workers for every development edit.
3. Read the relevant project instructions and inspect the active tool schema.
   Respect actual model availability, permissions, budget, and the harness's
   configured concurrency and depth limits.
4. For a single wave, record a short ledger; for longer runs also keep a plan in
   the repo's declared ignored working directory. Record model, owned files,
   acceptance, status, evidence, and the lead's verdict.
5. Launch independent workers without waiting for earlier independent workers
   to finish. Tool calls in separate messages can still run concurrently on
   asynchronous harnesses. Parallelize according to actual execution semantics.

Do useful lead work while workers run. A worker's return is input to the lead's
review, never a declaration that the user's task is done.

## Read the relevant reference before its step

| Situation | Reference |
| --- | --- |
| Delegated-run scope and authority | [Operating contract](sections/operating-contract.md) |
| Partitioning dependencies and ownership | [DAG](sections/dag.md) |
| Choosing models and effort, availability fallback | [Routing](sections/routing.md) |
| Preparing a self-contained worker task | [Brief](sections/brief.md) |
| Investigation, build, patch, refactor, migrate, verify | [Worker modes](sections/worker-modes.md) |
| Evaluating claims and repairing defects | [Quality gate](sections/quality-gate.md) |
| Reviewing and verifying the combined result | [Integration](sections/integrate.md) |
| Resume, worker failure, progress updates | [Tracking](sections/tracking.md) |
| Harness limits, lanes, resume primitives | [Fan-out patterns](FANOUT-PATTERNS.md) |
| Brief, ledger and report examples | [Templates](TEMPLATES.md) |

## Keep delegation bounded

Each worker gets the outcome, context it cannot infer, owned paths, acceptance
checks, allowed side effects, and return shape. One writer per file unless
isolated worktrees are deliberately integrated. Workers cannot expand authority
or spawn further fleets — configure that in the harness rather than requesting it
in prose (`FANOUT-PATTERNS.md`, lane enforcement).

After two failures on one acceptance check, the lead diagnoses the task or takes
it back. Keep evidence that distinguishes verified, failed, and unavailable
checks. The lead reviews the combined diff, verifies material behavior on the
final tree, and reports the coherent result with remaining limitations.

Read supporting skills only when the task needs them: `delegate-run` for
unattended completion, `autonomous-loops` for recurring execution, domain audits
for relevant risks. Do not load a whole suite, or invent a dependency on a skill
absent from the active environment.
