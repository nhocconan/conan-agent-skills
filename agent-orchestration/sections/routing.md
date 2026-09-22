## Model routing and quality ownership

Verified 2026-09-15 against the vendor pages listed under Sources. This is the canonical
model policy; companion skills link here instead of maintaining separate model tables.

## Contents

- [The lead slot belongs to the active harness](#the-lead-slot-belongs-to-the-active-harness) — the routing table
- [Claude models](#claude-models) · [OpenAI models](#openai-models) · [Gemini models](#gemini-models) — IDs, limits, prices, retirement
- [Cross-provider fleets](#cross-provider-fleets) — staffing workers from another vendor
- [Harness mechanics](#harness-mechanics) — how each harness actually selects a subagent model
- [Freshness and evidence](#freshness-and-evidence) — when to re-verify, and Sources

### The lead slot belongs to the active harness

**Whichever provider's harness is running owns the lead slot.** The lead defines acceptance,
resolves architecture, reviews the combined diff and evidence, and decides whether the
deliverable is complete. Worker completion is never final acceptance.

Do not substitute a lead across harnesses. A Claude session does not hand final approval to
Astra, and a Codex session does not hand it to Fable; a session that cannot reach its own
harness lead completes safe preparation and reports final review as pending. A user may name
a different lead for a particular run, and that choice wins over this table.

| Harness | Lead | Difficult scoped work | Default builder | Simple checked work |
| --- | --- | --- | --- | --- |
| Claude (Claude Code, Agent SDK) | `claude-fable-5-1` | `claude-opus-5` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` |
| Codex (OpenAI) | `gpt-6-astra` | `gpt-5.6-sol` | `gpt-5.6-terra` | `gpt-5.6-luna` |
| agy (Antigravity CLI) | `gemini-3.8-flash` | `gemini-3.8-flash` | `gemini-3.7-flash` | `gemini-3.5-flash-lite` |

Roles, not rankings. The lead keeps architecture, difficult decisions, integration, and final
acceptance. The default builder takes scoped implementation with meaningful tests. Simple
checked work means inventory, mechanical edits, and docs whose correctness a check can settle.
Escalate to the lead on risk or after two failures of the same acceptance check.

### Claude models

| Model | API ID | Context | Max output | $/MTok in → out | Released | Retirement not before |
| --- | --- | --- | --- | --- | --- | --- |
| Fable 5.1 | `claude-fable-5-1` | 1M | 128K | 10 → 50 | 2026-09-01 | 2027-09-01 |
| Opus 5 | `claude-opus-5` | 1M | 128K | 5 → 25 | 2026-07-24 | 2027-07-24 |
| Sonnet 5 | `claude-sonnet-5` | 1M | 128K | 2 → 10 | 2026-06-30 | 2027-06-30 |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | 200K | 64K | 1 → 5 | 2025-10-15 | 2026-10-15 |
| Mythos 5.1 | `claude-mythos-5-1` | 1M | 128K | 10 → 50 | 2026-09-01 | 2027-09-01 |

Haiku 4.5 reaches its earliest retirement date on 2026-10-15; re-check before relying on it.
Mythos 5.1 is invite-only through Project Glasswing and is not a routing default.
The 1M context window is the default on Fable 5.1, Opus 5, Sonnet 5 and Mythos 5.1 with no
beta header; Haiku 4.5 is fixed at 200K. From the 4.6 generation onward a dateless ID is the
pinned snapshot itself rather than an alias — Haiku 4.5 is the only current-lineup model
still on a dated ID (alias `claude-haiku-4-5`; the legacy `claude-opus-4-5-20251101` is
dated too). Bedrock prefixes with `anthropic.`; Vertex uses `@`-dated forms
for Haiku 4.5. Opus 5 and Mythos 5.1 are absent from Claude Platform on AWS.

### OpenAI models

| Model | API ID | Context | Max output | $/MTok in → out | Knowledge cutoff |
| --- | --- | --- | --- | --- | --- |
| Astra | `gpt-6-astra` | 1,050,000 | 128K | 10 → 50 | 2026-04-30 |
| Sol | `gpt-5.6-sol` | 1,050,000 | 128K | 4 → 20 | 2026-02-16 |
| Terra | `gpt-5.6-terra` | 1,050,000 | 128K | 2 → 12 | 2026-02-16 |
| Luna | `gpt-5.6-luna` | 1,050,000 | 128K | 0.20 → 1.20 | 2026-02-16 |

`reasoning_effort` on Astra accepts `low`, `medium`, `high`, `xhigh`, `max`; the 5.6 family
also accepts `none` and defaults to `medium`. Start the lead at `high` and reserve `xhigh`
for independent critical review. `gpt-5.4-cyber` is deprecated and leaves the API on
2026-10-01; migrate to `gpt-5.6-cyber`.

### Gemini models

| Model | API ID | Status | GA | Context / output | $/MTok in → out |
| --- | --- | --- | --- | --- | --- |
| 3.8 Flash | `gemini-3.8-flash` | GA, newest | 2026-09-02 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.7 Flash | `gemini-3.7-flash` | GA | 2026-08-13 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.6 Flash | `gemini-3.6-flash` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.5 Flash-Lite | `gemini-3.5-flash-lite` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.30 → 2.50 |
| 3.1 Pro | `gemini-3.1-pro-preview` | Preview | — | 1,048,576 / 65,536 | 2 → 12 (≤200K input) |

**Every agy role runs a Flash-family model.** `gemini-3.1-pro-preview` is not a routing
target: there is no generally available Gemini 3.x Pro *reasoning* model, and 3.1 Pro has sat
in Preview since 2026-02-19. (`gemini-3-pro-image` is stable, but it is an image model.) The
lead slot goes to 3.8 Flash, the newest stable model, which Google's model page calls "our
most intelligent Flash model, engineered for long-horizon software engineering, autonomous
agents, and complex enterprise workflows"; separate the lead from the builder with
`thinking_level` rather than by reaching for Pro. Revisit only when a Pro reasoning model
reaches GA. There is no API "Ultra" tier; Google AI Ultra is a consumer subscription. Flash
prices are introductory through 2026-12-31, after which 3.8 / 3.7 / 3.6 Flash move to
1.50 → 7.50. Reasoning is controlled by `thinking_level`, and **the default is not
uniform** — check it before assuming an effort level:

| Model | Accepts | Default |
| --- | --- | --- |
| 3.8 Flash, 3.7 Flash | `low`, `medium`, `high` | `medium` |
| 3.6 Flash, 3.5 Flash | `minimal`, `low`, `medium`, `high` | `medium` |
| 3.5 Flash-Lite | `minimal`, `low`, `medium`, `high` | `minimal` |
| 3.1 Pro (Preview) | `low`, `medium`, `high` | `high` |

The simple-checked-work slot, 3.5 Flash-Lite, therefore thinks at `minimal` unless raised.
Computer use is a Preview tool on 3.8 / 3.7 / 3.5 Flash and 3.5 Flash-Lite, not a
separate model.

### Cross-provider fleets

A lead may staff workers from another provider when the harness actually exposes them and the
user has authorized it. Antigravity CLI's own picker carries Claude models alongside Gemini.
Cross-provider workers report to the harness lead; they do not inherit the lead slot.

API IDs are not automatically accepted by every subagent tool. Inspect the active schema and
installed catalog before using a provider alias — a Codex surface offering only OpenAI models
cannot spawn Claude IDs. Proxy-routed agent types can pin the model and silently ignore a
`model` argument; record the model the harness reports, not the one requested, and label it
unverified when the harness exposes none. A skill cannot change the current session's model.

### Harness mechanics

**Claude Code / Agent SDK.** `AgentDefinition.model` accepts `fable`, `opus`, `sonnet`,
`haiku`, `inherit`, or a full model ID. With no model given, resolution runs: per-invocation
`model` parameter, then subagent frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then
the main conversation's model. That order changed at CLI 2.1.251 — the environment variable
used to win outright — so a configuration written against an older build routes differently
than its author expected. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (2.1.257+) overrides all
four steps: every subagent runs on `CLAUDE_CODE_SUBAGENT_MODEL`, or on the main model when
that is unset.

**Codex.** Set a worker's model through a custom agent definition in `~/.codex/agents/*.toml`
(`model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`) selected by `agent_type`,
and set `agents.default_subagent_model` so the policy holds when a brief omits the model.
The `spawn_agent` / `fork_turns` mechanics some briefs rely on do **not** appear in the
published Codex CLI reference; they are attested in the openai/codex source tree, in issue
#20077, and in the installed 0.154.0 binary's tool text.
Treat them as observed behaviour, not documented API, and re-check the active schema.

**agy (Antigravity CLI).** Subagents are spawned by the `invoke_subagent` tool. Agent
definitions can be declared dynamically via `define_subagent` (configuring write, subagent,
and MCP tool permissions) or loaded from `.md` files with YAML frontmatter `subagent: true`.
Built-in types include `self` (inherits parent configuration, tools, and model) and
`research` (read-only codebase exploration and search). **A subagent invocation's `Model`
parameter takes a tier — `inherit`, `flash_lite`, `flash` or `pro` — not a model ID.**
`flash_lite` maps to `gemini-3.5-flash-lite` for simple checked work; `flash` maps to
`gemini-3.7-flash` / `gemini-3.8-flash` for builders; `inherit` carries the parent's model.
**`model: pro` is off-policy**: on the installed agy 1.2.3 the only Pro entries in the picker
are `gemini-3.1-pro-high` / `-low` (Preview), so subagents use `flash`, `flash_lite`, or
`inherit`. The CLI accepts the bare API ID only with an effort — `agy --model
gemini-3.8-flash` fails with `--model gemini-3.8-flash requires --effort (available: low,
medium, high)` — and `agy models` lists the suffixed form (`gemini-3.8-flash-high`) next to
`claude-sonnet-4-6`, `claude-opus-4-6-thinking` and `gpt-oss-120b-medium`. Definitions are
discovered from `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md` in a
workspace, `~/.gemini/config/agents/` globally, and `plugins/<plugin>/agents/`. The older
`gemini` CLI is superseded and stopped serving consumer tiers on 2026-06-18. The Claude and
Codex mechanics above were read off the installed binaries; the agy definition format comes
from published documentation and active tool schemas, and the installed agy 1.2.3 was probed
only for `agy models`, `agy --help` and the `--model` call above — no subagent definition was
run.

### Freshness and evidence

Re-verify on a release, a deprecation, a rejected model ID, a retirement date coming within
90 days, or a maintenance audit. Check the vendor model pages and the session catalog before
changing a default, and preserve the user's explicit model choice. Keep historical benchmarks
dated; do not relabel an old run as a new model. Prices and context limits above are the
vendors' published list values on 2026-09-15, not a quote for any particular account.

Sources:
- [Claude models overview](https://platform.claude.com/docs/en/models/overview)
- [Claude model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [OpenAI models](https://developers.openai.com/api/docs/models)
- [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models)
- [Gemini API deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Antigravity CLI docs](https://antigravity.google/docs/cli/)

Routing and final ownership are the operator's policy, not a vendor guarantee.
