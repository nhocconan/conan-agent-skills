# Fan-out patterns

Tool definitions in the active session are authoritative. Names, aliases, limits,
and resume semantics vary by product and version; examples here are conditional.

## Choose a shape

| Situation | Shape |
| --- | --- |
| Independent outcomes with owned files | Concurrent subagents |
| Workers need overlapping files | Separate worktrees or serialize those writes |
| One important conclusion needs independent review | Fresh reviewer; another provider if available |
| CI, deploy, or external job in progress | Supported background completion and bounded waits |
| Small or inherently sequential change | Astra handles it directly |

Do not start an external CLI solely because a native subagent call is unavailable.
Check authorization, available tools, and value before adding another harness.

## Codex collaboration

Where `spawn_agent` exposes these fields, a scoped implementation uses:

```json
{
  "task_name": "implement",
  "model": "gpt-5.6-terra",
  "reasoning_effort": "medium",
  "fork_turns": "none",
  "message": "MODE: build. Working directory: /absolute/repo. Goal: ... Owned files: ... Acceptance: ... No commits or external writes. Return changed files, checks, assumptions, and gaps."
}
```

Use `gpt-5.6-luna` for simple checked work and `gpt-6-astra` for critical review.
Full-history forks may reject overrides. Check actual slots including the lead.
Launch the next independent node without awaiting completion of earlier nodes;
separate asynchronous tool messages can still execute concurrently.
Follow up on the existing worker for repairs; use a fresh context for independent review.

If using a separately authorized installed Codex CLI, inspect `codex exec --help`
first. A model ID such as `gpt-5.6-terra` must exist in that environment.
Never add sandbox or approval bypass flags to make unattended execution convenient.

## Claude collaborators

Inspect the active Agent tool or installed CLI before using model aliases,
background execution, or isolation options. The API model IDs and collaborator
roles are maintained in [routing](sections/routing.md). Do not assume an alias like
`fable` or a Workflow API exists merely because another session offered it.

A separate provider does not share browser sessions, environment, credentials, or
filesystem access by default. Supply bounded environment context and approved
credential mechanisms without copying secrets. Its verdict remains evidence for Astra.

## Worktrees and integration

Inspect repository state before creating worktrees. Give each writer a clear owner
scope and branch/worktree path, and preserve user changes. Astra integrates in
dependency order and runs relevant checks on the combined tree.

Remove a worktree only after its changes and artifacts are integrated or explicitly
discarded within authorization. Never force-remove unreviewed partial work.

## Cost and fallback

Parallelism spends additional tokens to reduce elapsed time or improve coverage.
Use observed costs where available; do not promise a fixed speedup.
Unavailable specialists or model overrides are explicit limitations.
Astra's final quality ownership remains required under the model policy.
