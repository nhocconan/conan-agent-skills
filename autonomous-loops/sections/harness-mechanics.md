## Harness mechanics

Discover the current product's scheduling, hook, and headless interfaces before
implementing a loop. Historical commands are not portable APIs.

1. Read the active tool definitions or installed CLI help and current official
   documentation for the exact harness.
2. Establish whether execution survives session closure, where credentials and
   skills load, and which identity performs writes.
3. Configure supported time/iteration/cost limits, overlap protection, error
   reporting, and a kill switch. Test a forced failure in an isolated environment.
4. Record the actual command/configuration and version in the project loop spec.
   Do not claim installation or scheduling from a drafted command.
5. Separate observation from external writes: posting a comment is a write.
   Use only the authority supplied for this recurring job; successful earlier
   read-only runs do not grant permission to merge, message, or deploy.

For Codex model routing, use `agent-orchestration/sections/routing.md`: Astra
owns orchestration and final quality, Terra/Luna perform suitable scoped work.
For a local cron/launchd job, record owner, schedule, logs, environment, overlap
lock, and the exact removal command. Disabling a trigger may not stop a running
job; verify both when asked to stop.
