## Model routing and quality ownership

Canonical model policy; companion skills link here. OpenAI/Anthropic tables retain
their 2026-09-30 verification; Gemini/agy rows were re-verified 2026-10-14. Targeted
2026-10-04 refresh: OpenAI deprecations and model selection, Codex configuration and
Claude subagent mechanics. Table dates do not imply current account access.

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

The active parent session is the harness lead. The table recommends models for future
sessions and scoped workers; it does not replace or disqualify the current lead. A stronger
worker supplies advice or independent review, never final acceptance. Do not substitute a
lead across harnesses. Preserve the user's explicit model choice. Report final review pending
when the actual harness lead cannot review, or an explicitly required review is unavailable;
an unavailable optional specialist alone does not block acceptance.

| Harness | General session / technical work | Hardest scoped judgment | Bounded builder | Focused checked work |
| --- | --- | --- | --- | --- |
| Claude (Claude Code, Agent SDK) | `claude-opus-5-5` | `claude-fable-5-1` | `claude-sonnet-5-5` | `claude-haiku-4-5-20251001` |
| Codex (OpenAI) | `gpt-6.1-sol` | `gpt-6-astra` | `gpt-6.1-sol` | `gpt-6-luna` |
| agy (Antigravity CLI) | `gemini-4-argon` / `gemini-3.8-flash` | `gemini-4-argon` | `gemini-3.8-flash` | `gemini-3.8-flash` (`low`) / `gemini-3.5-flash-lite` |

Select the least costly model and effort that meet the task's acceptance checks. Use Luna
for extraction, inventory, fine edits and focused patches with clear constraints and
observable checks. Use Sol 6.1 for general coding and coordinated technical work, and Astra
for demanding architecture, conflicting evidence or sustained judgment. On Claude,
Anthropic recommends Opus 5.5 for most workloads; Sonnet 5.5 is our bounded-builder cost
choice. Use Fable for demanding reasoning or when higher-effort Opus evaluations fall short.
Haiku suits simple work; use Sonnet where the bounded task needs stronger reasoning. On
Google/agy, use Argon for frontier judgment and complex multi-step engineering, 3.8 Flash
as the bounded builder and cross-plan workhorse, and 3.8 Flash (`low`) or 3.5 Flash-Lite
for focused checked work.

**Set `model` on every spawn:** an omitted one inherits the parent's or the agent definition's
tier (measured: routine reviews on the hardest tier were 24 % of one project's agent spend).
**Reviewer tier follows risk:** bounded-builder tier by default; the hardest tier only for
migrations, tenancy/RLS, auth, routing and prompts/evals, once per release over the combined
diff. **Cost = context × calls** (cache reads): cap workers near 80 turns / 150k context and
re-brief a fresh one.

Escalate immediately when risk, ambiguity or capability exceeds the worker's scope. After
two failures of the same acceptance check, the lead diagnoses or takes the task back before
choosing another model. Do not create workers solely to exercise a cheaper model. These
roles and acceptance rules are operator policy; vendor descriptions are starting points,
not proof of performance on a particular project.

### Claude models

| Model | API ID | Context | Max output | $/MTok in → out | Released | Retirement not before |
| --- | --- | --- | --- | --- | --- | --- |
| Fable 5.1 | `claude-fable-5-1` | 1M | 128K | 10 → 50 | 2026-09-01 | 2027-09-01 |
| Opus 5.5 | `claude-opus-5-5` | 1M | 128K | 4 → 20 | 2026-09-22 | 2027-09-22 |
| Sonnet 5.5 | `claude-sonnet-5-5` | 1M | 128K | 2 → 10 | 2026-09-28 | 2027-09-28 |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | 200K | 64K | 1 → 5 | 2025-10-15 | 2026-10-15 |

Haiku 4.5 is active. Its minimum retirement commitment ends on 2026-10-15; that is
not an announced shutdown date. Re-check the lifecycle page before relying on it.
Sonnet 5 (`claude-sonnet-5`) and Opus 5 (`claude-opus-5`) remain active
but are superseded in this policy.
Opus 5.5 and Fable keep adaptive thinking always on. All three current
reasoning models reject forced tool use. Dateless current IDs are pinned snapshots; Haiku uses the dated
ID above. Check each platform's ID and capabilities rather than transforming
Claude API IDs mechanically.

Claude Fable 5.1, Opus 5.5 and Sonnet 5.5 support `low`, `medium`, `high`, `xhigh`
and `max` effort. API defaults are Fable `high`, Opus `medium`, Sonnet `high`;
Haiku has no effort parameter. For well-specified agentic coding, Anthropic recommends
starting Sonnet 5.5 at `medium`, raising it for harder work. Re-evaluate effort on
representative tasks rather than carrying over the previous generation's setting.

### OpenAI models

| Model | API ID | Context | Max output | Standard $/MTok in → out | Knowledge cutoff |
| --- | --- | --- | --- | --- | --- |
| Astra | `gpt-6-astra` | 1,050,000 | 128K | 10 → 50 | 2026-04-30 |
| Sol 6.1 | `gpt-6.1-sol` | 1,050,000 | 128K | 2 → 10 | 2026-04-30 |
| Luna 6 | `gpt-6-luna` | 1,050,000 | 128K | 0.10 → 0.50 | 2026-05-18 |
| Sol 6 (fallback) | `gpt-6-sol` | 1,050,000 | 128K | 2 → 10 | 2026-04-20 |

Max input is 922,000 tokens. Prices are uncached Standard API rates for ≤272K
input; above that threshold the full request costs 2× input and 1.5× output.
Cache, speed, regional processing and ChatGPT credits have separate rates.

Astra and Sol 6.1 API `reasoning.effort` accept `low`, `medium`, `high`, `xhigh`,
`max`; Sol 6 and Luna additionally accept `none`. Sol 6.1, Sol 6 and Luna API
default to `medium`. Use Luna `low` for simple edits/extraction, consider `xhigh`
for constrained research, start Sol 6.1 at `medium`, and use Astra `medium` for
broad demanding work or `xhigh` for the hardest analysis. Increase effort only
when the task or evaluations justify the added cost.

API support and harness controls differ. The current collaboration schema exposes
`low` through `max` for Luna and also `ultra` for Sol/Astra; it does not expose
`none`. Inspect the
active schema rather than copying API values into a spawn call.

Use Responses for tool-calling API workers: Sol 6.1 Chat Completions has no tool
calling; Sol 6/Luna Chat Completions function calling requires effort `none`.
Model rollout and workspace settings still control access. During rollout, available
legacy fallbacks include `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`; do not
select them unless the active catalog exposes them. Prefer Sol 6 when Sol 6.1
is unavailable and the task remains suitable. GPT-5.5 (`gpt-5.5`) retires from
ChatGPT/Work/Codex on 2026-10-14; that notice does not retire its API model.
The 2026-10-01 API notice deprecates `gpt-5.3-codex`, `gpt-5.1` and
`gpt-5.4-nano` for removal on 2027-04-01. Deprecation is advance notice;
it is distinct from shutdown and from ChatGPT product retirement.

### Gemini models

| Model | API ID | Status | GA | Context / output | $/MTok in → out |
| --- | --- | --- | --- | --- | --- |
| 4 Argon | `gemini-4-argon` | GA, flagship | 2026-10-13 | 1,048,576 / 65,536 (1M long decode) | 2 → 10 |
| 3.8 Flash | `gemini-3.8-flash` | GA, newest Flash | 2026-09-02 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.6 Flash | `gemini-3.6-flash` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.5 Flash-Lite | `gemini-3.5-flash-lite` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.30 → 2.50 |
| 3.1 Pro | `gemini-3.1-pro-preview` | Preview | — | 1,048,576 / 65,536 | 2 → 12 (≤200K input) |

**Argon is the GA flagship reasoning model; 3.8 Flash is the cross-plan workhorse.**
`gemini-4-argon` has a unified 1,048,576 input+thinking+output window (1M long decode
via `background: true`), Antigravity Ultra/Enterprise access (app, CLI, IDE extensions),
and `$2 → $10` intro API pricing through 2026-11-30 (`$4 → $20` from 2026-12-01; implicit
cache `$0.10` then `$0.20`; no explicit cache or Free/AI Pro tier). Flash `$0.75 → $3.75`
intro rates move to `$1.50 → $7.50` on 2027-01-01. `gemini-3.7-flash` and
`gemini-3.5-flash` (deprecated 2026-10-08) auto-route to `gemini-3.8-flash` and
`gemini-3.6-flash`. Never combine `thinking_budget` with `thinking_level`.

| Model | Accepts (`thinking_level`) | Default |
| --- | --- | --- |
| 4 Argon, 3.8 Flash | `low`, `medium`, `high` | `medium` |
| 3.6 Flash | `minimal`, `low`, `medium`, `high` | `medium` |
| 3.5 Flash-Lite | `minimal`, `low`, `medium`, `high` | `minimal` |
| 3.1 Pro (Preview) | `low`, `medium`, `high` | `high` |

Use Argon `high` for hardest architecture, math/science, high-risk review and long decode;
`medium` for general lead and complex multi-step engineering; `low` for lighter
cost-sensitive reasoning. Use 3.8 Flash `high` for harder multi-step coding/agents or lead
fallback when Argon is unavailable; `medium` for standard bounded builds and routine
review; `low` for fast checks, inventory, extraction and narrow edits (`minimal` errors on
3.8 Flash; use 3.5 Flash-Lite `minimal`/`low` for the lightest high-volume checks).

### Cross-provider fleets

Cross-provider workers require exposed models and user authorization; they report to
the harness lead without inheriting acceptance. Antigravity's picker also carries Claude.

API IDs are not automatically accepted by every subagent tool. Inspect the active schema and
installed catalog before using a provider alias — a Codex surface offering only OpenAI models
cannot spawn Claude IDs. Proxy-routed agent types can pin the model and silently ignore a
`model` argument; record the model the harness reports, not the one requested, and label it
unverified when the harness exposes none. A skill cannot change the current session's model.

If a preferred worker or effort is rejected, inspect the catalog/schema and role
configuration, then choose an exposed model capable of meeting the checks or have
the lead do the work. Record the requested and actual model, effort and reason for
substitution. Do not silently substitute an explicitly required model; report that
requirement unavailable. Missing access does not authorize installs, configuration
changes, permission changes or starting another harness.

### Harness mechanics

**Claude Code.** Model resolution is invocation override → definition frontmatter
→ `CLAUDE_CODE_SUBAGENT_MODEL` → parent. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`
(2.1.257+) overrides those sources, with exceptions documented for forks and
inherited skill subagents; with FORCE alone, subagents run on the parent's model
(built-in Explore keeps its documented model), and with both variables set,
`CLAUDE_CODE_SUBAGENT_MODEL` wins (sub-agents docs, read 2026-10-04). Family aliases can retain the parent's exact version;
allowlists can substitute another model. Use an available full ID for deliberate
version selection and confirm the actual model in `/tasks`. Do not assume Explore
or Plan runs on Haiku. Agent SDK definitions and tools may differ; inspect them.

**Codex.** If collaboration exposes `model`/`reasoning_effort`, set them with
`fork_turns: "none"` or a positive count and a self-contained brief. An omitted or
`"all"` fork inherits parent model/effort and rejects overrides. This session exposes
Astra, Sol 6.1, Sol 6, Luna 6 and Sol 5.6; other surfaces may differ.
For CLI roles, inspect supported agent definitions/config overlays, `agent_type`,
`model`, `model_reasoning_effort`, `agents.default_subagent_model` and
`agents.default_subagent_reasoning_effort`. Explicit spawn settings take precedence;
defaults do not override a full-history fork. Current CLI documentation names
`agents.max_concurrent_threads_per_session` (spawned threads, excluding the primary);
`agents.max_threads` is its legacy alias. Do not apply that counting rule to a
collaboration tool whose limit includes the lead. Inspect the live schema;
CLI configuration is not a guarantee for this collaboration surface.

**agy (Antigravity CLI), 2026-10-14 snapshot (1.3.5).** `agy models` exposes
`gemini-4-argon-{low,medium,high}` and `gemini-3.8-flash-{low,medium,high}` (plus
Claude 5.5 and `gpt-oss-120b-medium`). Since 1.3.4, `--model` and `/model` accept a
base model name without `--effort` (using its default thinking level, else `medium`),
or pair with `--effort` (`low|medium|high|xhigh|max`). `invoke_subagent` uses tiers
`inherit`, `flash_lite`, `flash`, `pro` (not raw API IDs or explicit thinking levels):
use `flash_lite` for light lookups/checks, `flash` for standard bounded builders, scouts
and routine verifiers, and `pro` (or `inherit` when the lead is already on the desired
Argon thinking level) for complex multi-step refactors, architecture or high-risk
verification. `self` inherits; `research` is read-only. `define_subagent` configures
write, nested-agent and MCP permissions from `.agents/agents/`, `~/.gemini/config/agents/`
or plugins. See [fan-out patterns](../FANOUT-PATTERNS.md).

### Freshness and evidence

Re-verify on a release, a deprecation, a rejected model ID, a retirement date coming within
90 days, or a maintenance audit. Check the vendor model pages and the session catalog before
changing a default, and preserve the user's explicit model choice. Keep historical benchmarks
dated; do not relabel an old run as a new model. OpenAI/Anthropic values were checked on
2026-09-30; Gemini/agy values were re-verified on 2026-10-14. Neither is a quote
for a particular account. Compare candidate models on representative inputs and
checks; record quality, elapsed time, actual token usage and rework where available.

Sources:
- [Claude models overview](https://platform.claude.com/docs/en/models/overview)
- [Claude choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)
- [Claude effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Claude model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [OpenAI models](https://developers.openai.com/api/docs/models)
- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [OpenAI GPT-6 guide](https://developers.openai.com/api/docs/guides/latest-model)
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- [OpenAI Codex models and product retirement](https://developers.openai.com/codex/models)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models)
- [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini API deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Antigravity models](https://antigravity.google/docs/models)
- [Antigravity CLI docs](https://antigravity.google/docs/cli/)
