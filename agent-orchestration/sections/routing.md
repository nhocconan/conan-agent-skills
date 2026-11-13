## Model routing and quality ownership

Canonical model policy. [Verification dates](#freshness-and-evidence) do not establish access.

## Contents

- [Lead ownership](#the-lead-slot-belongs-to-the-active-harness)
- [Work nature → tier](#work-nature--tier)
- [Claude](#claude-models) · [OpenAI](#openai-models) · [Gemini](#gemini-models)
- [Cross-provider fleets](#cross-provider-fleets)
- [Harness mechanics](#harness-mechanics)
- [Freshness and evidence](#freshness-and-evidence)

### The lead slot belongs to the active harness

**The active harness owns the lead slot.** Its lead defines acceptance, resolves
architecture, reviews the combined diff and evidence, and accepts the result.

The active parent session is the harness lead. The table recommends models for future
sessions and scoped workers; it does not replace or disqualify the current lead. A stronger
worker supplies advice or independent review, never final acceptance. Do not substitute a
lead across harnesses. Preserve the user's explicit model choice. Report final review pending
when the actual harness lead cannot review, or an explicitly required review is unavailable;
an unavailable optional specialist alone does not block acceptance.

| Harness | General session / technical work | Hardest scoped judgment | Bounded builder | Focused checked work |
| --- | --- | --- | --- | --- |
| Claude (Claude Code, Agent SDK) | `claude-opus-5-5` | `claude-fable-5-2` | `claude-sonnet-5-5` | `claude-haiku-5-5` |
| Codex (OpenAI) | `gpt-6.1-sol` | `gpt-6-astra` | `gpt-6.1-sol` | `gpt-6-luna` |
| agy (Antigravity CLI) | `gemini-4-argon` / `gemini-4-hydrogen` (or `gemini-pro-orchestrator` / `gemini-pro-orchestrator-argon`) | `gemini-4-carbon` (Ultra/Enterprise/ADC), else `gemini-4-argon`, else `gemini-4-hydrogen` (`xhigh`) | `gemini-4-hydrogen` | `gemini-4-hydrogen` (`low`) |

### Work nature → tier

Define the outcome, risk and observable checks first; then choose a capable model and effort
for the actual work, subject to required project review gates. The parent remains lead; only its context may grow (≤ 120k,
[tracking](tracking.md)); every worker is capped and set explicitly on the spawn.

| Work | Tier | Effort | Cap | Return |
| --- | --- | --- | --- | --- |
| Specific unresolved hard question; an explicitly requested specialist | hardest scoped judgment (Fable / Astra / Carbon, else Argon) | as needed | 60 turns; reads the diff and artifacts, runs nothing heavier than `git`/`grep` | one line per finding |
| Broader or risky build, refactor, migration, integration or review; E2E flow authoring | bounded builder (Sonnet / Sol 6.1 / Hydrogen) | task-dependent | 80 turns / 150k context | builder contract |
| Source-based writing, chart/screen interpretation, bounded app workflows; narrow, low-risk app edits with explicit acceptance checks | scoped specialist (Codex: Terra 6.1; Gemini: Hydrogen `medium`) | task-dependent | 60 turns / 150k context | artifact + evidence + uncertainties |
| Bounded multi-step triage, source verification, narrow low-risk edits with observable checks, or specified browser checks | focused checked work (Haiku 5.5 / Luna / Hydrogen `low`) | task-dependent | 60 turns | verdict + evidence |
| A single mechanical command, waiting, relaying, or a "placeholder" | no agent needed | — | — | command result or completion notification |

For specified browser checks give routes, selectors, widths and expected text; report
measurements such as `scrollWidth`. Escalate work exceeding the worker’s capability or scope.

**Set `model`, effort and the turn cap on every spawn.** Omitted models inherit the parent
or definition. Enforce caps with available controls: Claude `maxTurns`, Codex
`job_max_runtime_seconds`, agy per-task runtime, plus the brief's budget. Re-brief workers
past 80 turns or 150k context from their results files to bound repeated context costs.

Escalate immediately when risk, ambiguity or capability exceeds the worker’s scope. After
two failures of the same acceptance check, the lead diagnoses or takes the task back before
choosing another model. Use the smallest context needed for a specific hard question; for
Astra, seek a capable cheaper pass and counterevidence first unless explicitly requested.
Choose effort for complexity and correctness, not price or inherited parent effort. Do not
force tiers or spawn solely to exercise a model. Vendor descriptions are not proof of project
performance. Require source/screen evidence, flag unreadable values, and verify app changes.
Tool support grants no write authority. If unavailable, choose a capable same-harness model
unless explicitly pinned.

### Claude models

| Model | API ID | Context | Max output | $/MTok in → out | Released | Retirement not before |
| --- | --- | --- | --- | --- | --- | --- |
| Fable 5.2 | `claude-fable-5-2` | 1M | 128K | 8 → 40 | 2026-11-09 | 2027-11-09 |
| Opus 5.5 | `claude-opus-5-5` | 1M | 128K | 4 → 20 | 2026-09-22 | 2027-09-22 |
| Sonnet 5.5 | `claude-sonnet-5-5` | 1M | 128K | 2 → 10 | 2026-09-28 | 2027-09-28 |
| Haiku 5.5 | `claude-haiku-5-5` | 1M | 128K | 0.10 → 0.50 (prompts ≤ 100K; 0.50 → 2.50 above) | 2026-10-07 | 2027-10-07 |

Fable 5.1 (`claude-fable-5-1`, 10 → 50, retirement not before 2027-09-01) is legacy and still
active; Anthropic advises migrating to 5.2.
Haiku 5.5 counts about 30 % more tokens than Haiku 4.5 for the same text (newer tokenizer).
Haiku 4.5 (`claude-haiku-4-5-20251001`) is legacy and still active, with no deprecation notice.
Sonnet 5 (`claude-sonnet-5`) and Opus 5 (`claude-opus-5`) remain active
but are superseded in this policy.
Opus 5.5 and Fable keep adaptive thinking always on. Fable, Opus and Sonnet reject forced
tool use. Dateless current IDs are pinned snapshots. Check each platform's ID and
capabilities rather than transforming Claude API IDs mechanically.

Claude Fable 5.2, Opus 5.5, Sonnet 5.5 and Haiku 5.5 support `low`, `medium`, `high`, `xhigh`
and `max` effort. API defaults are Fable `high`, Opus `medium`, Sonnet `high`, Haiku
`medium`; Claude Code defaults all four to `medium`, so set effort on the spawn instead of
relying on a default. Anthropic recommends Haiku 5.5 `low` for short tool tasks and simple high-volume
work, and starting Sonnet 5.5 at `medium` for well-specified agentic coding, raising it
for harder work. Re-evaluate effort on
representative tasks rather than carrying over the previous generation's setting.

### OpenAI models

| Model | API ID | Context | Max output | Standard $/MTok in → out | Knowledge cutoff |
| --- | --- | --- | --- | --- | --- |
| Astra | `gpt-6-astra` | 1,050,000 | 128K | 10 → 50 | 2026-04-30 |
| Sol 6.1 | `gpt-6.1-sol` | 1,050,000 | 128K | 2 → 10 | 2026-04-30 |
| Terra 6.1 | `gpt-6.1-terra` | 1,050,000 | 128K | 1 → 5 | 2026-06-01 |
| Luna 6 | `gpt-6-luna` | 1,050,000 | 128K | 0.10 → 0.50 | 2026-05-18 |
| Sol 6 (fallback) | `gpt-6-sol` | 1,050,000 | 128K | 2 → 10 | 2026-04-20 |

Max input is 922,000 tokens. Prices are uncached Standard API rates for ≤272K
input; above that threshold the full request costs 2× input and 1.5× output.
Cache, speed, regional processing and ChatGPT credits have separate rates.

Astra and Sol 6.1 API `reasoning.effort` accept `low`, `medium`, `high`, `xhigh`,
`max`; Terra 6.1, Sol 6 and Luna additionally accept `none`. Terra, Sol 6.1, Sol 6 and
Luna API default to `medium`. Use Luna `low` for simple edits/extraction, consider `xhigh`
for constrained research, start Sol 6.1 at `medium`, and use Astra `medium` for
broad demanding work or `xhigh` for the hardest analysis. Increase effort only
when the task or evaluations justify the added cost. Inside Codex the models page instead
starts Astra at `low` and Luna at `high`; follow the surface the worker runs on.

API support and harness controls differ. The current collaboration schema exposes
`low` through `max` for Luna and also `ultra` for Terra/Sol/Astra; it does not expose
`none`. The 2026-10-29 Codex catalog gives Terra a 500K context window and default
`low` effort, distinct from its API limits/default above. Sol 6.1 also defaults to
500K in Codex/Work, per its API model page. Inspect the active schema
rather than copying API values into a spawn call. Ultra may automatically delegate;
use it only when nested work is permitted by the task and harness.

Use Responses for tool-calling API workers: Terra and Sol 6.1 Chat Completions have no tool
calling; Sol 6/Luna Chat Completions function calling requires effort `none`.
Model rollout and workspace settings still control access. Choose from the active spawn
schema, not a cached CLI catalog alone. Prefer an exposed 6-series model suited to the
task; select a legacy 5.6 fallback only when the needed 6-series model is unavailable
and the active spawn schema exposes that fallback. Prefer Sol 6 when Sol 6.1 is
unavailable and the task remains suitable.
The 2026-10-01 API notice deprecates `gpt-5.3-codex`, `gpt-5.1` and
`gpt-5.4-nano` for removal on 2027-04-01. Deprecation is advance notice;
it is distinct from shutdown and from ChatGPT product retirement.

### Gemini models

| Model | API ID | Status | GA | Context / output | $/MTok in → out |
| --- | --- | --- | --- | --- | --- |
| 4 Carbon | `gemini-4-carbon` | GA, most capable | 2026-11-10 | 1,048,576 / 65,536 (1M long decode) | 2 → 10 |
| 4 Argon | `gemini-4-argon` | GA, efficient frontier | 2026-10-13 | 1,048,576 / 65,536 (1M long decode) | 2 → 10 |
| 4 Hydrogen | `gemini-4-hydrogen` | GA, fast workhorse | 2026-11-12 | 1,048,576 / 65,536 (1M long decode) | 1.50 → 7.50 |
| 3.8 Flash | `gemini-3.8-flash` | GA, previous Flash | 2026-09-02 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.6 Flash | `gemini-3.6-flash` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.5 Flash-Lite | `gemini-3.5-flash-lite` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.30 → 2.50 |
| 3.1 Pro | `gemini-3.1-pro-preview` | Preview | — | 1,048,576 / 65,536 | 2 → 12 (≤200K input) |

**Carbon is Google's deepest reasoning model, Argon the efficient frontier tier, and Hydrogen
the cross-plan Gemini 4 workhorse (recommended upgrade from 3.8 Flash).** All three Gemini 4
models share a unified 1,048,576 input+thinking+output window (1M long decode via
`background: true` or continuation; 65,536 streaming cap, with single non-streaming hops
capped at 32,768 on Carbon/Argon and 65,536 on Hydrogen) and implicit-only caching (≥4,096
tokens; no explicit cache). Carbon and Argon run at `$2 → $10` intro API pricing through
2026-11-30 (`$4 → $20` from 2026-12-01; implicit cache `$0.10` then `$0.20`; no Free API
tier). Hydrogen runs at flat `$1.50 → $7.50` across 1M context (implicit cache `$0.075`, Free
API tier included) and serves as the default Antigravity Managed Agent model. Antigravity
entitles Carbon on Ultra, Enterprise and Google Cloud ADC (`AGY_ADC_AUTH`), Argon on paid
Pro/eligible-device trials, Ultra and Enterprise, Hydrogen and 3.8 Flash on every plan, and
3.6 Flash / 3.1 Pro on Enterprise only. Flash `$0.75 → $3.75` intro rates move to
`$1.50 → $7.50` on 2027-01-01 and retain explicit caching. `gemini-3.7-flash` and
`gemini-3.5-flash` (deprecated 2026-10-08) auto-route to `gemini-3.8-flash` and
`gemini-3.6-flash`; `gemini-2.5-pro` auto-routes to `gemini-3.8-flash` on 2026-12-01. On
Gemini 4, `thinking_budget` is deprecated (HTTP 400 in Interactions API or alongside
`thinking_level`) and custom `temperature`/`top_p`/`top_k` are ignored.

| Model | Accepts (`thinking_level`) | Default |
| --- | --- | --- |
| 4 Carbon, 4 Argon, 3.8 Flash | `low`, `medium`, `high` | `medium` |
| 4 Hydrogen | `low`, `medium`, `high`, `xhigh` | `high` |
| 3.6 Flash | `minimal`, `low`, `medium`, `high` | `medium` |
| 3.5 Flash-Lite | `minimal`, `low`, `medium`, `high` | `minimal` |
| 3.1 Pro (Preview) | `low`, `medium`, `high` | `high` |

Use Carbon `high` (Argon `high` where Carbon is unentitled; Hydrogen `xhigh` on Free/Plus)
for hardest architecture, subtle concurrency/race root-cause, math/science, security audits,
high-risk review and long decode; Argon `medium` (or single-session Orchestrator) for general
lead and long-horizon engineering at lower per-turn token spend than Carbon, and Carbon
`medium` when every step needs deeper verification. Use Hydrogen `high` (its default) for
bounded builders, multi-step tool agents, routine review, dense multimodal/PDF/chart/video
work and Free/Plus lead; set `medium` explicitly for well-specified coding, UI prototyping
and latency-sensitive specialist passes; reserve `xhigh` (`Extra` in the App) for hard
multi-step escalations where `high` falls short, since it can overthink simple prompts; use
`low` for fast checks, triage, inventory, extraction and narrow edits (`minimal` errors on
Gemini 4 and 3.8 Flash). Keep 3.8 Flash (`low`–`high`) when its `$0.75 → $3.75` intro rate
(through 2026-12-31) or explicit API caching is required; 3.5 Flash-Lite `minimal`/`low`
suits the lightest high-volume API checks (absent from `agy models`).

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
`CLAUDE_CODE_SUBAGENT_MODEL` wins (sub-agents docs, read 2026-11-11). Family aliases can retain the parent's exact version;
allowlists can substitute another model. The per-call `model` takes aliases only
(`fable` resolves to Fable 5.2 from 2.1.321); use a full ID in definition frontmatter or
`CLAUDE_CODE_SUBAGENT_MODEL` for deliberate version selection, and confirm the actual model
in `/tasks`. Do not assume Explore
or Plan runs on Haiku. Agent SDK definitions and tools may differ; inspect them.

**Codex.** Set `model`/`reasoning_effort` with `fork_turns: "none"` and a self-contained
brief; fork inheritance, role config keys and concurrency limits are in
[fan-out patterns](../FANOUT-PATTERNS.md#codex-collaboration). This session exposes
Astra, Sol 6.1, Terra 6.1, Sol 6 and Luna 6 (checked 2026-10-29); other surfaces may
differ. The Work/Codex Terra release is dated 2026-10-26; official guidance requires
CLI 0.159.0+, but version alone does not establish catalog or workspace access.

**agy (Antigravity CLI), 1.5.7 (`agy --version`, `agy models`, 2026-11-13).** The catalog
exposes `gemini-4-carbon-{low,medium,high}`, `gemini-4-argon-{low,medium,high}`,
`gemini-4-hydrogen-{low,medium,high,xhigh}`, `gemini-pro-orchestrator`,
`gemini-pro-orchestrator-argon` and `gemini-3.8-flash-{low,medium,high}` (plus Claude 5.5 and
`gpt-oss-120b-medium`, removed with Free/Pro Claude 4.6 on 2026-11-18). A listed ID does not
prove plan entitlement; confirm on first use. Orchestrator pairs Carbon (Ultra) or Argon
(paid/eligible-trial Pro, Ultra; absent on Enterprise) planning and review with Hydrogen
execution in one conversation at fixed effort (`--effort` and `/effort` rejected). Since
1.3.4, `--model` and `/model` accept a base name without `--effort` (runs the model's default
thinking level — `high` on Hydrogen, `medium` on Carbon/Argon/3.8 Flash) or pair with
`--effort` (`low|medium|high|xhigh|max`). `invoke_subagent` exposes coarse tiers (`inherit`,
`flash_lite`, `flash`, `pro`; `flash_lite` is in the live schema though omitted from the
subagents page, and exact tier-to-model-ID mapping is undocumented): `flash_lite` for light
lookups/checks, `flash` for bounded builders, scouts and routine verifiers, `pro` (or
`inherit` when the parent runs the target model/effort) for complex refactors, architecture
or high-risk verification. `/swarm` (`Pro`/`Ultra` preview) accepts exact catalog IDs on
`add` (`model`) and in-place switches on waiting members (`action: "model"`), defaulting to
the coordinator's model unless multi-model routing is requested. Mechanics:
[fan-out patterns](../FANOUT-PATTERNS.md#antigravity-agy-collaboration).

### Freshness and evidence

Re-verify on a release, a deprecation, a rejected model ID, a retirement date coming within
90 days, or a maintenance audit. Check the vendor model pages and the session catalog before
changing a default, and preserve the user's explicit model choice. Keep historical benchmarks
dated; do not relabel an old run as a new model. Gemini and agy 1.5.7 were re-checked on
2026-11-13 across model, latest-model, thinking, pricing, deprecation, subagent and swarm
pages (Hydrogen GA 2026-11-12, Carbon GA 2026-11-10, Orchestrator, all Flash/3.1 Pro row
limits, `gemini-2.5-pro` 2026-12-01 auto-route, and the `thinking_budget` rule). Claude
(Fable 5.2 released 2026-11-09) and OpenAI (no general-availability change since 2026-11-07;
Codex CLI 0.167.1; Terra's Codex catalog values 2026-10-29) were last re-checked on
2026-11-11. Restricted-access models (Mythos 5.2, GPT-6 Cyber, Rosalind) are not routing
targets. These are not account-specific quotes. Compare candidate models on representative
inputs and checks; record quality, elapsed time, actual token usage and rework where
available.

Sources:
- [Claude models overview](https://platform.claude.com/docs/en/models/overview)
- [Claude choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [Claude Fable 5.2](https://platform.claude.com/docs/en/models/fable-5-2/overview)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)
- [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)
- [Claude effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Claude model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [OpenAI models](https://developers.openai.com/api/docs/models)
- [Sol 6.1 API](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Terra API](https://developers.openai.com/api/docs/models/gpt-6.1-terra)
- [Terra release](https://learn.chatgpt.com/docs/whats-new/october-26-30-2026) (2026-10-26)
- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [OpenAI GPT-6 guide](https://developers.openai.com/api/docs/guides/latest-model)
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- [Work/Codex models and product retirement](https://learn.chatgpt.com/docs/models)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models)
- [Latest Gemini models](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini 4 Carbon](https://ai.google.dev/gemini-api/docs/models/gemini-4-carbon)
- [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
- [Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/models/gemini-4-hydrogen)
- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Antigravity models](https://antigravity.google/docs/models)
- [Antigravity subagents](https://antigravity.google/docs/subagents)
- [Antigravity swarm](https://antigravity.google/docs/swarm)
- [Antigravity CLI docs](https://antigravity.google/docs/cli/)
