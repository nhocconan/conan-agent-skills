---
name: verify
description: Use before committing code changes, or when the user says "verify". Runs the repo's own gates with exit codes, checks for residue, replays a named flow, blocks the commit on any failure.
---

# Verify before commit

Pre-commit check of the working tree. It does not push, bump versions or write
changelogs; that is [shipping-changes](../shipping-changes/SKILL.md). Docs- or
tests-only changes need only the gates that touch them.

1. **Run the repo's own gates.** Find them in `AGENTS.md`/`CLAUDE.md`, package scripts,
   `Makefile` or CI config; run every required one. Capture each exit status before any
   output filtering, per rule 4 of
   [shipping-changes](../shipping-changes/SKILL.md). Also `git diff --check`.
   In an orchestrated run a runner runs the gates and the lead reads the exit codes from
   its results file ([tracking](../agent-orchestration/sections/tracking.md)); a green run
   on this exact tree this session is reused, not repeated
   ([reuse valid evidence](../effective-development/SKILL.md#reuse-valid-evidence)).
2. **Inventory residue.** List what this run started (dev server, worker, container,
   tunnel, port, temp file) with pid/port in the report; tear down only what the task is
   finished with, per
   [dev-env-lifecycle](../dev-env-lifecycle/SKILL.md).
3. **Replay the operator's path.** If the user named a path or flow ("my login", a URL,
   an org), run it once on the running local or staging build and read the result. Otherwise write
   `not replayed`.
4. **Report one line per gate**: `<command> EXIT=<n>`, then what is verified (a command ran
   and was read this session) versus inferred. A failing, skipped or unrun required
   gate blocks the commit; say so first, do not commit around it, do not bypass hooks.
