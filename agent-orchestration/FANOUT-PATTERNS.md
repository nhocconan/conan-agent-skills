# Fan-out patterns

Harness mechanics for fan-out: what each harness actually enforces, how lanes are
configured, how a run resumes. Tool definitions in the active session are authoritative.
Names, fields, limits and resume semantics vary by product and version — inspect the live
schema before relying on anything below.

## Contents

[Shapes](#choose-a-shape) · [Limits](#concurrency-and-depth-limits) ·
[Lanes](#lane-enforcement) · [Resume](#resume-primitives) · [Cadence](#progress-cadence) ·
[Codex](#codex-collaboration) · [Claude](#claude-collaborators) ·
[agy](#antigravity-agy-collaboration) · [Shared-host](#shared-host-resources) · [Worktrees](#worktrees-and-integration)

## Choose a shape

| Situation | Shape |
| --- | --- |
| Independent outcomes with owned files | Concurrent subagents (`invoke_subagent` / `Agent` / `spawn_agent`; or agy `/swarm` only when explicitly active and shared-board coordination helps) |
| Workers need overlapping files | Separate worktrees, or serialize those writes |
| One important conclusion needs independent review | Fresh reviewer; another provider if available |
| CI, deploy, or external job in progress | Supported background completion and bounded waits |
| Small or inherently sequential change | The lead handles it directly |
| Code-driven fan-out over many items, staged pipelines, or aggregated cross-checks | A harness workflow script (Claude Code's Workflow tool, agy `run_workflow` Python script, or a Codex scheduled task), not ad-hoc fan-out |
| Large mechanical change split into independent units | Claude Code `/batch` (5–30 worktree subagents) or a workflow (`run_workflow` `parallel`/`pipeline` on agy); agent teams are experimental and off by default |

Do not start an external CLI solely because a native subagent call is unavailable.
Check authorization, available tools, and value before adding another harness.

Inspect the active schema; never assume a capability exists because another session
offered it. Surfaces worth confirming before use rather than assuming: Codex
`spawn_agent` / `fork_turns` (attested in `openai/codex` issue #20077, absent from the
published CLI reference), any cross-provider model ID inside a subagent tool, and any
hosted-execution or scheduling surface.

## Concurrency and depth limits

Read from the installed builds and vendor docs on 2026-11-11. Re-check after any upgrade; never state a
ceiling you have not read from the active configuration.

**Claude Code ≥ 2.1.219 (checked on 2.1.322).** `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
caps concurrent subagents (built-in default 20). `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`
caps nesting (built-in default 3). A slot is taken when a subagent launches, so the lead
does not consume one. A launch over the concurrency cap fails with `Concurrent subagent
limit reached` and the error tells the agent not to retry. At the depth limit the `Agent`
tool is withheld from the subagent, so it does the work itself. A workflow runs up to 16
concurrent agents by default and 1,000 agents per run.

**Codex CLI (keys first seen 0.154.0, still present in 0.167.1 on 2026-11-11; `max_depth` and
`job_max_runtime_seconds` are absent from the public config reference).** The `agents` config table carries
`max_concurrent_threads_per_session`, `max_depth`, `job_max_runtime_seconds`,
`default_subagent_model`, `default_subagent_reasoning_effort`. On surfaces with `close_agent`, release completed workers when their
results are integrated. Use the lifecycle operations exposed by the active tool.
The depth-limit string `Agent depth limit reached. Solve the task yourself.` was seen in
0.154.0 and not found in the 0.167.1 binary.

## Lane enforcement

Configure supported permission boundaries for the lanes in
[the operating contract](sections/operating-contract.md). A tool allowlist or
workspace-write sandbox does not enforce ownership of individual files. Shell and MCP
tools can write even when Edit/Write are absent; restrict those routes or use an actual
read-only boundary. Where enforcement is unavailable, record the limitation and use
isolation plus diff review. Do not change global permissions merely to staff a lane.

| Lane | Claude Code | Codex | agy (Antigravity) |
| --- | --- | --- | --- |
| Scout, read-only | `permissionMode: plan`; a `tools` allowlist without Edit/Write | a role whose `config_file` sets a read-only `sandbox_mode` | built-in `research` type (read-only sandbox, **no network access**), or `define_subagent` with `EnableWriteTools: false` |
| Builder, owned files | `tools` allowlist, `disallowedTools` for the rest | role `config_file` with a workspace-write `sandbox_mode` | `self` (or `define_subagent` with `EnableWriteTools: true`); `Workspace` / `workspace`: `"share"` or `"branch"` |
| Verifier, read-only | as Scout, in its own definition so it cannot inherit builder tools | a separate read-only role | fresh context with `research` or `define_subagent` (`EnableWriteTools: false`) |
| MCP scoping | `disallowedTools` with `mcp__<server>` patterns; inline `mcpServers` in the definition | `mcp_servers` in the role's `config_file` | `define_subagent` with `EnableMCPTools: false`, or custom `.agents/agents/` `mcpServers` |
| No nested fleets | omit `Agent` from `tools` | `agents.max_depth` | `define_subagent` with `EnableSubagentTools: false` |

Claude Code reads these from subagent frontmatter (`model`, `effort`, `maxTurns`,
`isolation`). Codex roles (`description`, `config_file`, `nickname_candidates`) are chosen
with `agent_type`; the `config_file` is a config overlay (`model`, `model_reasoning_effort`,
`sandbox_mode`, `mcp_servers`), and current docs also describe standalone
`.codex/agents/*.toml` definitions. Antigravity reads reusable subagents from
`.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md` (and the same layouts under
`~/.gemini/config/agents/` and `plugins/<plugin>/agents/`; frontmatter supports `tools`,
`model`, `commandExecutionPolicy`, `mcpServers`). Check exact `tools` names, as unmapped
entries can hang the subagent. Read the accepted keys from the installed build; a
full-history fork can reject `agent_type` overrides.
Sources: [Claude subagents](https://code.claude.com/docs/en/sub-agents),
[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
(checked 2026-11-11), [Antigravity subagents](https://antigravity.google/docs/subagents)
(checked 2026-11-24).

Check the effective permissions after inheritance and runtime overrides. Claude plugin
subagents ignore `permissionMode`, inline `mcpServers` and subagent hooks; Codex live
parent overrides can supersede custom-agent defaults. These controls need verification,
not assumed enforcement (official docs checked 2026-11-11).

## Resume primitives

Resume existing workers when supported; a ledger alone cannot restore worker context.

**Claude Code.** `SendMessage` to the agent id returned by the Agent tool continues that
agent with its context intact; a fresh `Agent` call starts over. A run that hits
`maxTurns` returns its output marked partial (≥ 2.1.246); the same `SendMessage`
continues it. The built-in Explore and Plan agents are one-shot and return no
id, so use `general-purpose` or a custom subagent for work you may need to resume.
Subagents can themselves launch background subagents, within the depth limit above.

**Codex.** CLI surfaces may expose `send_input`, `resume_agent` and `close_agent`.
The current collaboration surface uses `send_message` for a running worker,
`followup_task` to trigger an idle worker, `interrupt_agent` to interrupt and
`list_agents` / `wait_agent` to observe. It exposes no close tool. Use the live schema;
do not copy CLI lifecycle calls into another surface or treat interruption as cleanup.

**agy (Antigravity).** When an `invoke_subagent` worker finishes and goes idle, the harness
delivers its final output to the parent automatically (workers should return their final
response rather than calling `send_message("parent", ...)` without a real `conversationId`).
`send_message` with `Recipient=<conversationId>` continues an idle subagent with its context
intact. `manage_subagents` with `Action="list"` enumerates active direct subagents and live
states (`running`, `idle`, `killed`); `Action="kill"` / `"kill_all"` ends workers permanently
and deletes their branched workspaces (preserving logs/artifacts). `run_workflow` runs in the
background by default (`WaitMsBeforeAsync=0`) and notifies the lead on completion. In
`/swarm`, `waiting` members sleep at zero token cost until `@mentioned`; quota-exhausted
members pause until `@mentioned` or switched in place via `swarm` `action: "model"` (never
`kill` + `add` to switch models). `/swarm board` or `Alt+S` opens the 3-pane board (`Alt+X`
dismisses the status row). `manage_task` monitors background commands and active `schedule`
timers; reactive wakeups resume execution without polling.

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
`reasoning_effort` overrides. Set `"none"` with a self-contained brief whenever you
are choosing the worker's tier. The current schema accepts only `"all"` or `"none"`;
use numeric forks only if the active schema explicitly supports them.
Explicit spawn settings beat `agents.default_subagent_model` and
`default_subagent_reasoning_effort`, which never override a full-history fork.
`agents.max_threads` is the legacy alias of `max_concurrent_threads_per_session`, which
counts spawned threads excluding the primary; a collaboration tool whose limit includes the
lead counts differently, so inspect the live schema.

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

Verified against live `agy 1.5.15` schemas and official Antigravity docs on 2026-11-24.
Pick the native surface that fits the shape:

- **Few independent tasks (`invoke_subagent`).** Emit parallel `invoke_subagent` calls in one
  turn to launch a wave concurrently:

```json
{
  "TypeName": "self",
  "Role": "Scoped Builder",
  "Model": "flash",
  "Workspace": "share",
  "Prompt": "MODE: build. Working directory: /absolute/repo. Goal: ... Owned files: ... Acceptance: ... Return: ..."
}
```

Set `Workspace` to `"share"` (git worktree / shared repo storage) or `"branch"` (isolated
clone); readers and verifiers keep `"inherit"`. Since `1.5.5`, isolated Git copies include
staged, unstaged and untracked changes, and non-Git workspaces copy folders up to 100,000
entries / 4 GiB. Built-in CLI types are `self`, `research`
(read-only sandbox with **no network access**), and `image-generator`. Note the `browser`
difference: in Antigravity CLI (and business/enterprise accounts), browser control uses
`/browser` to attach to Chrome rather than an auto-launched `browser` subagent type (App
v2.30.0+ personal accounts only). Register session-scoped workers via `define_subagent`
(`EnableWriteTools`, `EnableMCPTools`, `EnableSubagentTools`). `Model` accepts coarse tiers
`inherit`, `flash_lite`, `flash`, or `pro` ([routing](sections/routing.md)); `flash_lite`,
`manage_subagents` and `Enable*` come from the live schema, so re-inspect on upgrades. Docs
state a maximum nesting depth of 10 beneath the primary agent and no concurrency cap.

- **Code-driven fan-out and staged pipelines (`run_workflow`).** GA for all plans (`1.5.9+`,
  uses the CLI's bundled Python so no host Python install is needed; trailing top-level
  `return` supported from `1.5.14`). Use `run_workflow` when
  orchestration itself is code — fanning out over a list of files/modules/bugs/lenses,
  running staged pipelines where stage N feeds stage N+1, or aggregating/filtering/cross-checking
  many agent outputs. Read the built-in `run-workflow` skill before authoring a script; do
  not use it for a single delegated task (`invoke_subagent` is simpler). Pass a Python 3.8+
  `Script` or `ScriptPath` plus optional `Args`, `Cwd`, and `WaitMsBeforeAsync` (0–10,000 ms;
  default 0 backgrounds immediately). Built-in helpers: `agent(prompt, schema=..., role=...,
  type_name=..., workspace=..., model=...)` (returns a reusable multi-turn handle when called
  again; `schema` enforces a JSON `finish` output), `parallel(items, fn)` (fail-fast: an
  unhandled error cancels siblings), `pipeline(items, fn)` (streams each item across stages
  without a full-wave barrier), `phase(name)`, `log(...)`, `call_tool(name, **args)`, and
  `trajectory(...)`.

- **Shared-board coordination (`/swarm` and `swarm` tool).** Preview, available on all plans
  (business/enterprise when admin-allowed, checked 2026-11-24). **Strict user-initiation gate
  (`1.5.13+`):** the swarm skill is not offered to agents automatically; never call `swarm`
  (`add`, `status`, `models`, `title`) unprompted — use it only when the user explicitly
  invoked `/swarm`, a skill instructs it, or the conversation already has an active swarm.
  `swarm` `action: "add"` spawns named workers (or `tasks`/`n` sharded groups)
  with `workspace: "share"` or `"branch"` (land changes before `kill`, which deletes that
  copy) and optional `fork` (branch from `"coordinator"` or another member's history). Omit
  `model` to inherit the coordinator's model; pass an exact ID from `swarm` `models`
  (`all: true`) only when multi-model routing is authorized ([routing](sections/routing.md)).
  `/swarm board` (`Alt+S`) includes a live `Overview` section (goal, task progress, up to 6
  workstream threads, `1.5.14+`). Single-session Orchestrator hands off planner/builder
  inside one conversation (configurable `Planner`/`Executor` models and effort in `/model`
  since `1.5.14`, default `high` in `1.5.15`) rather than spawning independent lanes; use
  `invoke_subagent`, `run_workflow` or `/swarm` for parallel fan-out or fresh-context review.

- **Headless CLI & TUI controls.** Non-interactive runs use `agy -p` / `--print` with
  explicit `--mode accept-edits|auto|plan` (unset defaults to `auto`), `--output-format
  text|json|stream-json`, `--input-format stream-json`, `--json-schema`, `--print-timeout`,
  `--sandbox`, and `--settings` (inline JSON or file, never saved). `GEMINI_API_KEY` mode
  disables `--remote-control`, `--remote-agent`, `/voice` and `/record` (exit 2). In the
  interactive TUI: `Alt+J` jumps to a subagent waiting confirmation, `Ctrl+K` fast-approves
  a pending action, `Alt+S` opens `/swarm board`, and `/agents`, `/tasks`, `/skills reload`,
  `/plan`, `/compact` (`AGY_CLI_AUTO_COMPACT_OVERRIDE` sets auto-compaction threshold in
  `1.5.15`), `/goal`, `/teamwork` (per-run state under CLI app data dir since `1.5.5`),
  `/boost`, `/schedule` control sessions and jobs.

## Shared-host resources

Worktrees, lanes and tool allowlists isolate files, not memory, CPU, ports, databases or
browsers; heavy jobs go through one lead-owned runner. Method:
[SHARED-HOST](../effective-development/SHARED-HOST.md).

Staff by the content's natural partition (one worker per dashboard tab or screen; halve the
count under load); tier per the [work-nature table](sections/routing.md#work-nature--tier).
Test method per worker: [effective-development](../effective-development/SKILL.md) (production
build, one browser with many contexts, API-level parity, component tests).

## Worktrees and integration

Inspect repository state before creating worktrees. Give each writer a clear owner scope
and branch/worktree path, and preserve user changes. Confirm the actual base revision:
Claude isolated subagents can start from the default branch rather than parent HEAD.
Worktrees isolate files, not ports, databases, credentials or external writes; reserve
those resources separately. The lead integrates in dependency
order and runs relevant checks on the combined tree.

Remove a worktree only after its changes and artifacts are integrated or explicitly
discarded within authorization. Never force-remove unreviewed partial work.

Cost, fallback, and the evidence rules that govern both are in
[the operating contract](sections/operating-contract.md).
