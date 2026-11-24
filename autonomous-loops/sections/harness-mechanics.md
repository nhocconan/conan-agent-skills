## Harness mechanics

Check harness interfaces; historical commands are not portable APIs.

1. Check tools, official docs and CLI help: `codex --help` /
   `codex exec --help`, or `agy --help` (checked on 1.5.15, 2026-11-24: print mode `-p`
   defaults to `--mode auto`, so pass `--mode` explicitly; supports `--print-timeout`,
   `--output-format json|stream-json`, `--json-schema`, and `--sandbox`). Headless does not
   imply scheduling or blocking hooks; use a CI/job gate where hooks cannot block.
2. Establish whether execution survives session closure, where credentials and
   skills load, and which identity performs writes. Session schedulers generally do
   not survive closure: Claude Code `/loop` fires only while that session runs (recurring
   tasks expire after 7 days); cloud scheduled tasks (formerly routines) have a 1-hour
   minimum interval; Desktop scheduled tasks run locally and survive closing the
   session (scheduled-tasks docs, read 2026-11-11).
   In **agy** (`1.5.15`, checked 2026-11-24), the built-in `schedule` tool (and `/schedule`)
   registers either a one-shot timer (`DurationSeconds`, optional `TimerCondition` for early
   cancellation on a matching message) or a 5-field `CronExpression` (`MaxIterations`,
   `ExactTiming` — jittered by default when false — and `IsDaemon` only for an independent
   standing cron that should keep firing after the current task finishes); cancel active
   schedules via `manage_task`, and never use shell `sleep` as a timer. Verify persistence
   across CLI restarts before relying on an in-harness daemon instead of system cron/CI.
   For `agy` command hooks (`hooks.json`, validated by `agy plugin validate`), timeouts and
   cancellations kill the hook's full process group on Linux/macOS (`1.5.14+`).
   Claude hooks: exit 2 blocks on PreToolUse, UserPromptSubmit, Stop, SubagentStop,
   PostToolBatch, PreCompact, TaskCreated/Completed (full table in the hooks docs); not
   on PostToolUse, Notification, PermissionRequest. Scheduler kill switch:
   `CLAUDE_CODE_DISABLE_CRON=1` (docs read 2026-11-11).
3. Configure supported time/iteration/cost limits, overlap protection, error
   reporting, and a kill switch. Test a forced failure in an isolated environment,
   including a duplicate trigger, expired budget and stop during a running job.
   The gate must exit non-zero to the scheduler; logging failure is insufficient.
4. Record the actual command/configuration and version in the project loop spec.
   Never claim installation or scheduling from a drafted command.
5. Separate observation from external writes: posting a comment is a write.
   Use only the authority supplied for this recurring job; prior
   read-only runs grant no permission to merge, message, or deploy.

Use `agent-orchestration/sections/routing.md` for routing and lead ownership.
For a local cron/launchd job, record owner, schedule, logs, environment, overlap
lock, and the exact removal command. Disabling a trigger may not stop a running
job; verify both when asked to stop.
