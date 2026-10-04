## Harness mechanics

Inspect the current scheduling, hook and headless interfaces; historical commands
are not portable APIs.

1. Read the active tool definitions or installed CLI help and current official
   documentation for the exact harness.
2. Establish whether execution survives session closure, where credentials and
   skills load, and which identity performs writes. Session-scoped schedulers do
   not survive it: Claude Code `/loop` tasks fire only while that session runs and
   recurring ones expire after 7 days; cloud routines run at a 1-hour minimum
   interval (scheduled-tasks docs, read 2026-10-02).
3. Configure supported time/iteration/cost limits, overlap protection, error
   reporting, and a kill switch. Test a forced failure in an isolated environment,
   including a duplicate trigger, expired budget and stop during a running job.
   The gate must return failure to the scheduler; logging a failed exit is insufficient.
4. Record the actual command/configuration and version in the project loop spec.
   Do not claim installation or scheduling from a drafted command.
5. Separate observation from external writes: posting a comment is a write.
   Use only the authority supplied for this recurring job; successful earlier
   read-only runs do not grant permission to merge, message, or deploy.

Use `agent-orchestration/sections/routing.md` for routing and lead ownership.
For a local cron/launchd job, record owner, schedule, logs, environment, overlap
lock, and the exact removal command. Disabling a trigger may not stop a running
job; verify both when asked to stop.
