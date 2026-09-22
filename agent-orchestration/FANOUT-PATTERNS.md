# Fan-out patterns

Harness mechanics for fan-out: what each harness actually enforces, how lanes are
configured, how a run resumes. Tool definitions in the active session are authoritative.
Names, fields, limits and resume semantics vary by product and version — inspect the live
schema before relying on anything below.

## Contents

1. Choose a shape
2. Concurrency and depth limits
3. Lane enforcement
4. Resume primitives
5. Progress cadence
6. Codex collaboration
7. Claude collaborators
8. Antigravity (agy) collaboration
9. Worktrees and integration

## Choose a shape

| Situation | Shape |
| --- | --- |
| Independent outcomes with owned files | Concurrent subagents |
| Workers need overlapping files | Separate worktrees, or serialize those writes |
| One important conclusion needs independent review | Fresh reviewer; another provider if available |
| CI, deploy, or external job in progress | Supported background completion and bounded waits |
| Small or inherently sequential change | The lead handles it directly |
| The same deterministic DAG, repeated, with mechanical checks | A harness workflow script (Claude Code's Workflow tool; a Codex scheduled task), not ad-hoc fan-out |

Do not start an external CLI solely because a native subagent call is unavailable.
Check authorization, available tools, and value before adding another harness.

Inspect the active schema; never assume a capability exists because another session
offered it. Surfaces worth confirming before use rather than assuming: Codex
`spawn_agent` / `fork_turns` (attested in `openai/codex` issue #20077, absent from the
published CLI reference), any cross-provider model ID inside a subagent tool, and any
hosted-execution or scheduling surface.

## Concurrency and depth limits

Read from the installed builds on 2026-09-15. Re-check after any upgrade; never state a
ceiling you have not read from the active configuration.

**Claude Code 2.1.272.** `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` caps concurrent
subagents (built-in default 20). `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` caps nesting
(built-in default 3). A slot is taken when a subagent launches, so the lead does not
consume one. Exceeding either limit returns an error instructing the agent to do the work
itself rather than retry.

**Codex CLI 0.154.0.** The `agents` config table carries
`max_concurrent_threads_per_session`, `max_depth`, `job_max_runtime_seconds`,
`default_subagent_model`, `default_subagent_reasoning_effort`. A completed agent keeps
occupying a concurrency slot until `close_agent`, so close each one as it lands.
Depth exhaustion returns `Agent depth limit reached. Solve the task yourself.`

## Lane enforcement

The lanes in [the operating contract](sections/operating-contract.md) are permissions,
not etiquette. Configure them, so a worker cannot leave its lane by deciding to.

| Lane | Claude Code | Codex | agy (Antigravity) |
| --- | --- | --- | --- |
| Scout, read-only | `permissionMode: plan`; a `tools` allowlist without Edit/Write | a role whose `config_file` sets a read-only `sandbox_mode` | built-in `research` type, or `define_subagent` with `enable_write_tools: false` |
| Builder, owned files | `tools` allowlist, `disallowedTools` for the rest | role `config_file` with a workspace-write `sandbox_mode` | `self` (or `define_subagent` with `enable_write_tools: true`); `Workspace: "share"` or `"branch"` |
| Verifier, read-only | as Scout, in its own definition so it cannot inherit builder tools | a separate read-only role | fresh context with `research` or `define_subagent` without write tools |
| MCP scoping | `disallowedTools` with `mcp__<server>` patterns; inline `mcpServers` in the definition | `mcp_servers` in the role's `config_file` | `define_subagent` with `enable_mcp_tools: false` |
| No nested fleets | omit `Agent` from `tools` | `agents.max_depth` | `define_subagent` with `enable_subagent_tools: false` |

Claude Code reads these from subagent frontmatter, alongside `model`, `effort`,
`maxTurns` and `isolation`. Codex declares a role — `description`, `config_file`,
`nickname_candidates` — and the role is chosen at spawn with `agent_type`; the
`config_file` it names is a config overlay, so the per-lane knobs are ordinary config
keys (`model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`). Read the
overlay's accepted keys from the installed build before relying on any one of them.
A full-history fork inherits the parent's agent type and refuses an `agent_type` override.

agy (Antigravity CLI): subagents are configured via `define_subagent` (setting
`enable_write_tools`, `enable_subagent_tools`, `enable_mcp_tools`) or loaded from `.md`
definitions with YAML frontmatter `subagent: true` and `model:`. The built-in `research`
type is read-only; `self` inherits parent capabilities. Spawning uses `invoke_subagent`
where `Model` selects a tier (`inherit` / `flash_lite` / `flash` / `pro`; `pro` is off-policy,
[routing](sections/routing.md)) and `Workspace` selects isolation (`inherit` / `branch` / `share`).
Recorded from the 2026-09-15 vendor refresh; the installed agy 1.2.3 was probed for
`agy models` and a `--model` call, and subagent schemas match the active harness.

This is what turns "workers cannot spawn further fleets" from a line in a brief into
something the harness enforces.

## Resume primitives

A ledger records that a node was running; it does not resume the node. Re-briefing a
fresh worker from the ledger discards the original worker's context and pays to rebuild
it. Resume the worker itself wherever the harness allows.

**Claude Code.** `SendMessage` to the agent id returned by the Agent tool continues that
agent with its context intact; a fresh `Agent` call starts over. A run that hits
`maxTurns` reports `stopped at its N-turn limit` — a partial result the same
`SendMessage` continues. Inside a subagent only synchronous subagents are available;
`run_in_background` is not.

**Codex.** `send_input` feeds an open agent, `wait_agent` blocks for completion,
`list_agents` enumerates, `resume_agent` restarts one, `close_agent` releases its slot.

**agy (Antigravity).** `send_message` with `Recipient=<conversationId>` continues a
subagent with its context intact. `manage_subagents` with `Action="list"` enumerates
active subagents and their states (`running`, `idle`, `waiting_for_input`, etc.);
`Action="kill"` cancels a worker. `manage_task` monitors background commands. The harness
resumes execution reactively on subagent messages or task completion without polling.

Use the ledger to decide *what* to resume, and the harness primitive to actually resume it.

## Progress cadence

The 60-second figure is a Codex convention, not a universal rule. Its system prompt says
to "avoid performing blocking sleep or wait calls longer than 60 seconds" and that the
user "should not be left without a commentary update for more than 60 seconds during
ongoing work"; `features.multi_agent_v2.min_wait_timeout_ms` / `max_wait_timeout_ms` /
`default_wait_timeout_ms` bound each wait. On Claude Code a foreground `sleep` is
blocked, and background completion notifications are the mechanism instead.
On agy (Antigravity), execution is event-driven: reactive wakeups notify the lead upon
subagent returns or background task completion, so do not run busy wait loops or terminal
`sleep`. For timed reminders or bounds, use the `schedule` tool.
[Tracking](sections/tracking.md) carries the harness-neutral obligation.

## Codex collaboration

Where `spawn_agent` exposes these fields, a scoped implementation uses:

```json
{
  "task_name": "implement",
  "model": "<builder tier from sections/routing.md>",
  "reasoning_effort": "medium",
  "fork_turns": "none",
  "message": "MODE: build. Working directory: /absolute/repo. Goal: ... Owned files: ... Acceptance: ... No commits or external writes. Return changed files, checks, assumptions, and gaps."
}
```

`fork_turns` omitted or `"all"` copies the parent's entire context into the worker and
inherits the parent's model and reasoning effort, and such a fork rejects `model` and
`reasoning_effort` overrides. Set `"none"` (or a positive count) with a self-contained
brief whenever you are choosing the worker's tier.

Launch the next independent node without awaiting earlier nodes; separate asynchronous
tool messages can still execute concurrently. Follow up on the existing worker for
repairs; use a fresh context for independent review.

If using a separately authorized installed Codex CLI, inspect `codex exec --help` first
and confirm the model ID exists in that environment. Never add sandbox or approval
bypass flags to make unattended execution convenient.

## Claude collaborators

Inspect the active Agent tool or installed CLI before using model aliases, background
execution, or isolation options. Model IDs and collaborator roles are maintained in
[routing](sections/routing.md).

A separate provider does not share browser sessions, environment, credentials, or
filesystem access by default. Supply bounded environment context and approved credential
mechanisms without copying secrets. Its verdict is evidence for the lead, not acceptance.

## Antigravity (agy) collaboration

Subagents are launched via `invoke_subagent`. The tool accepts an array `Subagents` to
launch an entire wave concurrently:

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "Scoped Builder",
      "Model": "flash",
      "Workspace": "share",
      "Prompt": "MODE: build. Working directory: /absolute/repo. Goal: ... Owned files: ... Acceptance: ... Return: ..."
    }
  ]
}
```

Set `Workspace` to `"share"` to share the repository directory like a git worktree, or
`"branch"` for an isolated clone. For read-only scout/verifier roles, pass
`TypeName: "research"`, or register a scoped worker first via `define_subagent` with
`enable_write_tools: false` and `enable_subagent_tools: false`. `Model` accepts
`inherit`, `flash_lite`, or `flash` ([routing](sections/routing.md)).

## Worktrees and integration

Inspect repository state before creating worktrees. Give each writer a clear owner scope
and branch/worktree path, and preserve user changes. The lead integrates in dependency
order and runs relevant checks on the combined tree.

Remove a worktree only after its changes and artifacts are integrated or explicitly
discarded within authorization. Never force-remove unreviewed partial work.

Cost, fallback, and the evidence rules that govern both are in
[the operating contract](sections/operating-contract.md).
