---
name: agent-orchestration
description: >-
  Coordinate independent agent work with scoped ownership, model routing,
  resumable state, and evidence-based integration. Use for multi-workstream tasks,
  explicit delegation, parallel audits, or agent handoffs. Astra leads and owns
  final quality; Terra implements and Luna handles simple checked work.
---

# Agent orchestration

**GPT-6 Astra owns orchestration and final output quality.** Use the
[canonical model policy](sections/routing.md) before staffing: GPT-5.6 Terra
implements scoped work, GPT-5.6 Luna handles simple checked tasks, and Astra
retains architecture, difficult decisions, integration, and final acceptance.

## Start with the task

1. Classify the requested result: answer, diagnosis, review, or verified change.
   Preserve its scope and existing authorization.
2. Define observable acceptance and partition along independent outcomes.
   Use a fleet when independent work can proceed without shared-file or resource
   conflicts. Small, sequential work may stay with Astra; orchestration does not
   require spawning workers for every development edit.
3. Read the relevant project instructions and inspect the active tool schema.
   Respect actual model availability, permissions, budget, and concurrency.
4. For a single wave, record a short ledger; for longer runs also keep a plan in
   the repo's declared ignored working directory. Record model, owned files,
   acceptance, status, evidence, and the lead's verdict.
5. Launch independent workers without waiting for earlier independent workers
   to finish. Tool calls in separate messages can still run concurrently on
   asynchronous harnesses. Parallelize according to actual execution semantics.

Do useful lead work while workers run. A worker's return is input to Astra's
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
| Harness-specific mechanics | [Fan-out patterns](FANOUT-PATTERNS.md) |
| Brief, ledger and report examples | [Templates](TEMPLATES.md) |

## Keep delegation bounded

Each worker gets the outcome, context it cannot infer, owned paths, acceptance
checks, allowed side effects, and return shape. One writer per file unless
isolated worktrees are deliberately integrated. Workers cannot expand authority
or spawn further fleets without a bounded delegation contract.

After two failures on one acceptance check, Astra diagnoses the task or takes it
back. Keep evidence that distinguishes verified, failed, and unavailable checks.
Astra reviews the combined diff, verifies material behavior on the final tree,
and reports the coherent result with remaining limitations.

Read supporting skills only when the actual task needs them: `delegate-run`
for unattended completion, `autonomous-loops` for recurring execution, and
domain-specific audits for relevant risks. Do not load an entire skill suite
or invent dependencies on skills absent from the active environment.
