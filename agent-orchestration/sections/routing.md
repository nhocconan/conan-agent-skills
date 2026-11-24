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
| Codex (OpenAI) | `gpt-6.2-sol` | `gpt-6.2-astra` | `gpt-6.2-sol` | `gpt-6.1-terra` (or `gpt-6-luna` where exposed) |
| agy (Antigravity CLI) | `gemini-4-neon` or an entitled Orchestrator (else `gemini-4-argon`). Free/Plus uses `gemini-3.8-flash` | `gemini-4-carbon`, then Neon (`xhigh`/`high`), Argon or Hydrogen where available. Free/Plus uses 3.8 Flash (`high`) when the task fits | `gemini-4-hydrogen` (`gemini-4-neon` for complex multi-file work), or 3.8 Flash | Hydrogen or 3.8 Flash (`low`) |

### Work nature → tier

Define the outcome, risk and observable checks first; then choose a capable model and effort
for the actual work, subject to required project review gates. The parent remains lead; only its context may grow (≤ 120k,
[tracking](tracking.md)); record each worker’s budget in its brief.

| Work | Tier | Effort | Cap | Return |
| --- | --- | --- | --- | --- |
| Specific unresolved hard question; an explicitly requested specialist | hardest scoped judgment (Fable / Astra / Carbon, else Neon or Argon) | as needed | 60 turns; reads the diff and artifacts, runs nothing heavier than `git`/`grep` | one line per finding |
| Broader or risky build, refactor, migration, integration or review; E2E flow authoring | bounded builder (Sonnet / Sol 6.2 / Hydrogen; Neon for complex multi-file builds) | task-dependent | 80 turns / 150k context | builder contract |
| Source-based writing, chart/screen interpretation, bounded app workflows; narrow, low-risk app edits with explicit acceptance checks | scoped specialist (Codex: Terra 6.1; Gemini: Hydrogen `medium`) | task-dependent | 60 turns / 150k context | artifact + evidence + uncertainties |
| Bounded multi-step triage, source verification, narrow low-risk edits with observable checks, or specified browser checks | focused checked work (Haiku 5.5 / Terra or Luna where exposed / Hydrogen `low`) | task-dependent | 60 turns | verdict + evidence |
| A single mechanical command, waiting, relaying, or a "placeholder" | no agent needed | — | — | command result or completion notification |

For specified browser checks give routes, selectors, widths and expected text; report
measurements such as `scrollWidth`. Escalate work exceeding the worker’s capability or scope.

**Specify the worker budget in its brief.** Use a supported turn limit such as Claude
`maxTurns` when available. Codex collaboration exposes model and effort overrides on
a fresh-context spawn and has no per-spawn turn-limit field. Treat a brief's turn
budget as advisory and a runtime limit as elapsed time. Re-brief workers
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
Haiku 4.5 (`claude-haiku-4-5-20251001`) remains active. The Claude API schedules Sonnet 4.5
(`claude-sonnet-4-5-20250929`) for retirement on 2026-11-30 and recommends Sonnet 5.5.
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

| Model | API ID | Standard $/MTok in → out | Knowledge cutoff |
| --- | --- | --- | --- |
| Astra 6.2 | `gpt-6.2-astra` | 8 → 40 | 2026-05-18 |
| Sol 6.2 | `gpt-6.2-sol` | 2 → 10 | 2026-06-01 |
| Astra 6 (previous) | `gpt-6-astra` | 10 → 50 | 2026-04-30 |
| Sol 6.1 (previous) | `gpt-6.1-sol` | 2 → 10 | 2026-04-30 |
| Terra 6.1 | `gpt-6.1-terra` | 1 → 5 | 2026-06-01 |
| Luna 6 | `gpt-6-luna` | 0.10 → 0.50 | 2026-05-18 |
| Sol 6 (fallback) | `gpt-6-sol` | 2 → 10 | 2026-04-20 |

All seven API models allow 1,050,000 tokens of context, including up to 922,000 input
and 128,000 output. Rates are uncached. Above 272K input tokens the full request
costs 2× input and 1.5× output. Work credits and service tiers have separate rates.

Use Sol 6.2 `medium` for features and fixes, `xhigh` for multistep builds. Use Astra
6.2 `medium` for complex planning or `xhigh` for open questions. Terra 6.1 `medium`
suits computer use and focused fixes. Luna `low` suits extraction and simple edits.

Start new 6.2 API integrations at `medium`. Both 6.2 models reject `none`. Use Responses
for tool calls with 6.2 models, Astra 6, Terra 6.1 and Sol 6.1. Sol 6 and Luna also
support Chat Completions function calling at `none`.

The CLI defaults to 500K context for Sol 6.2 and Terra 6.1, 272K for Astra 6.2, all at
`low` effort. The five spawn models offer `low`, `medium`, `high`, `xhigh`, `max` and
`ultra`. Use Ultra only when the task permits automatic delegation. Sol 6.1
and Astra 6 are fallbacks for their respective roles when 6.2 is unavailable.
The 2026-10-01 API notice deprecates `gpt-5.3-codex`, `gpt-5.1` and
`gpt-5.4-nano` for removal on 2027-04-01.

### Gemini models

| Model | API ID | Status | GA | Context / output | $/MTok in → out |
| --- | --- | --- | --- | --- | --- |
| 4 Carbon | `gemini-4-carbon` | GA, most capable | 2026-11-10 | 1,048,576 / 65,536 (1M long decode) | 2 → 10 |
| 4 Neon | `gemini-4-neon` | GA, fast frontier | 2026-11-18 | 1,048,576 / 65,536 (1M long decode) | 3 → 15 |
| 4 Argon | `gemini-4-argon` | GA, efficient frontier | 2026-10-13 | 1,048,576 / 65,536 (1M long decode) | 2 → 10 |
| 4 Hydrogen | `gemini-4-hydrogen` | GA, fast workhorse | 2026-11-12 | 1,048,576 / 65,536 (1M long decode) | 1.50 → 7.50 |
| 3.8 Flash | `gemini-3.8-flash` | GA, previous Flash | 2026-09-02 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.6 Flash | `gemini-3.6-flash` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.5 Flash-Lite | `gemini-3.5-flash-lite` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.30 → 2.50 |
| 3.1 Pro | `gemini-3.1-pro-preview` | Preview | — | 1,048,576 / 65,536 | 2 → 12 (≤200K input) |

**Carbon targets hardest reasoning, Neon sits between Hydrogen and Carbon for complex
engineering, knowledge and science work (and is Google's recommended upgrade from 3.1 Pro
Preview), Argon is the earlier efficient frontier tier, and Hydrogen is the fast default and
recommended upgrade from 3.8 Flash.** All four Gemini 4 models share a unified 1,048,576
input+thinking+output window (1M long decode via `background: true` with `max_output_tokens >
65,536` or continuation; 65,536 streaming cap, with single non-streaming hops capped at 32,768
on Carbon/Argon and 65,536 on Neon/Hydrogen) and implicit-only caching (≥4,096 tokens; no
explicit cache). Neon runs at flat `$3 → $15` across 1M context (implicit cache `$0.15`; no
promo rate or Free API tier). Carbon and Argon run at `$2 → $10` intro API pricing through
2026-11-30 (`$4 → $20` from 2026-12-01; implicit cache `$0.10` then `$0.20`; no Free API
tier). Hydrogen runs at flat `$1.50 → $7.50` across 1M context (implicit cache `$0.075`, Free
API tier included) and serves as the default Antigravity Managed Agent model (`model`
overridable to `gemini-4-neon` or `gemini-4-carbon`). Antigravity offers 3.8 Flash on every
plan; paid Pro adds Neon, Argon and Hydrogen, eligible premium-device Pro trials include Neon
and Argon, and Ultra and Enterprise include Neon, Carbon, Argon and Hydrogen. Neon is
Antigravity's default conversation model where included (up to 512K session context
documented). Flash `$0.75 → $3.75` intro rates move to `$1.50 → $7.50` on 2027-01-01 and
retain explicit caching. `gemini-3.7-flash` and `gemini-3.5-flash` (deprecated 2026-10-08)
auto-route to `gemini-3.8-flash` and `gemini-3.6-flash`; `gemini-2.5-pro` auto-routes to
`gemini-3.8-flash` on 2026-12-01. On Gemini 4, `thinking_budget` is deprecated (HTTP 400 in
Interactions API or alongside `thinking_level`) and in-range custom
`temperature`/`top_p`/`top_k` are ignored.

| Model | Accepts (`thinking_level`) | Default |
| --- | --- | --- |
| 4 Carbon, 4 Argon, 3.8 Flash | `low`, `medium`, `high` | `medium` |
| 4 Neon, 4 Hydrogen | `low`, `medium`, `high`, `xhigh` | `high` |
| 3.6 Flash | `minimal`, `low`, `medium`, `high` | `medium` |
| 3.5 Flash-Lite | `minimal`, `low`, `medium`, `high` | `minimal` |
| 3.1 Pro (Preview) | `low`, `medium`, `high` | `high` |

Use Carbon `high` (or Neon `xhigh`/`high`, then Argon `high` where Carbon is unavailable) for
hardest architecture, subtle concurrency/race root-cause, math/science, security audits,
high-risk review and long decode, and Carbon `medium` when every step needs deeper
verification. Use Neon `high` (its default) or single-session Orchestrator (else Argon
`medium`) for general lead, repo-level debugging, complex multi-file refactoring, and dense
knowledge/science synthesis with faster completion and fewer output tokens than Carbon; set
Neon `medium` for interactive coding and latency-sensitive tool loops. Use Hydrogen `high`
(its default) for bounded builders, multi-step tool agents, routine review, and dense
multimodal/PDF/chart/video work. Set Hydrogen `medium` explicitly for well-specified coding
and UI prototyping; reserve `xhigh` (`Extra` in the App) on Neon or Hydrogen for hard
multi-step escalations where `high` falls short, since it can overthink simple prompts; use
`low` for fast checks, triage, inventory, extraction and narrow edits (`minimal` errors on
Gemini 4 and 3.8 Flash). On Antigravity Free/Plus, use 3.8 Flash at `medium` for general work,
`low` for quick checks and `high` for more demanding work within its capability.
Keep 3.8 Flash in API workloads when its `$0.75 → $3.75` intro rate
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
`CLAUDE_CODE_SUBAGENT_MODEL` wins. A mod's `agent.spawn` hook can replace the invocation's
model. Family aliases can retain the parent's exact version;
allowlists can substitute another model. The per-call `model` takes aliases only
(`fable` resolves to Fable 5.2 from 2.1.321); use a full ID in definition frontmatter or
`CLAUDE_CODE_SUBAGENT_MODEL` for deliberate version selection, and confirm the actual model
in `/tasks`. Do not assume Explore
or Plan runs on Haiku. Agent SDK definitions and tools may differ; inspect them.

**Codex.** Set `model`/`reasoning_effort` with `fork_turns: "none"` and a self-contained
brief; fork inheritance, role config keys and concurrency limits are in
[fan-out patterns](../FANOUT-PATTERNS.md#codex-collaboration). On 2026-11-18 the
spawn schema offered Sol 6.2, Astra 6.2, Terra 6.1, Sol 6.1 and Astra 6.
The Codex CLI 0.170.0 catalog also listed Luna 6 and Sol 6. Check the active
spawn tool before assigning either model.

**agy (Antigravity CLI), 1.5.15 (`agy --version`, `agy models`, 2026-11-24).** The catalog
exposes `gemini-4-neon-{low,medium,high,xhigh}`, `gemini-4-carbon-{low,medium,high}`,
`gemini-4-argon-{low,medium,high}`, `gemini-4-hydrogen-{low,medium,high,xhigh}`,
`gemini-pro-orchestrator-neon`, `gemini-pro-orchestrator`, `gemini-pro-orchestrator-argon`
and `gemini-3.8-flash-{low,medium,high}`. It also lists Opus and Sonnet 5.5 at `low`,
`medium` and `high` (`gpt-oss-120b-medium` remained in the catalog on 2026-11-24 past its
scheduled 2026-11-18 removal; Claude 4.6 was removed). Confirm access on first use; CLI
sessions also support Gemini 4 models with a Gemini API key or Google Cloud ADC
(`AGY_ADC_AUTH`; 1.5.13 added Neon under `AGY_ADC_AUTH` and enterprise model gateways).
Orchestrator pairs Neon (paid/eligible-trial Pro, Ultra), Carbon (Ultra;
also CLI `/model` on Enterprise and `AGY_ADC_AUTH` from 1.5.10 when both Carbon and Hydrogen
are selectable, though marked absent on Enterprise in the App matrix) or Argon
(paid/eligible-trial Pro, Ultra) planning and review with Hydrogen execution in one
conversation. Since 1.5.14, consumer-plan local sessions configure Orchestrator's `Planner`
and `Executor` models and per-role thinking `Effort` in `/model` (saved under `"orchestrator"`
in `settings.json` / `--settings`; 1.5.15 sets default role effort to `high` when available),
while `--effort`/`/effort` remain rejected on fixed-effort Orchestrator presets. Since 1.3.4, `--model` and
`/model` accept a base name without `--effort` (runs the model's default thinking level —
`high` on Neon/Hydrogen, `medium` on Carbon/Argon/3.8 Flash) or pair with `--effort`
(`low|medium|high|xhigh|max`). Both `invoke_subagent` and `run_workflow`'s `agent(...)` helper
expose coarse tiers (`inherit`, `flash_lite`, `flash`, `pro`; `flash_lite` is in the live
schema though omitted from the subagents page, and exact tier-to-model-ID mapping is
undocumented): `flash_lite` for light lookups/checks, `flash` for bounded builders, scouts
and routine verifiers, `pro` (or `inherit` when the parent runs the target model/effort) for
complex refactors, architecture or high-risk verification. `/swarm` (preview, available on
all plans; business/enterprise when admin-allowed, checked 2026-11-24) accepts exact catalog
IDs on `add` (`model`) and in-place switches on waiting members (`action: "model"`),
defaulting to the coordinator's model unless multi-model routing is requested; never invoke
`swarm` unprompted (use only when `/swarm` was explicitly invoked, a skill instructs it, or a
swarm is already active). Mechanics:
[fan-out patterns](../FANOUT-PATTERNS.md#antigravity-agy-collaboration).

### Freshness and evidence

Re-verify on a release, a deprecation, a rejected model ID, a retirement date coming within
90 days, or a maintenance audit. Check the vendor model pages and the session catalog before
changing a default, and preserve the user's explicit model choice. Keep historical benchmarks
dated. Google released Gemini 4 Neon on 2026-11-18; the Gemini API release notes, Neon model
and migration guides, and Antigravity plan matrix were checked on 2026-11-19, and live agy
1.5.15 (`agy models`, `agy --help`, `invoke_subagent`, `run_workflow`, `swarm`), Antigravity
subagents, swarm, CLI reference and changelog docs were re-checked on 2026-11-24. Anthropic's model overview and the local Claude Code
2.1.327 installation's catalog (fetched 2026-11-17) listed the four current Claude IDs.
OpenAI released Sol 6.2 and Astra 6.2 on 2026-11-17. The API model cards, Work/Codex
guidance, CLI 0.170.0 catalog and active spawn schema were checked on 2026-11-18.
Restricted-access models (Mythos 5.2, GPT-6 Cyber, Rosalind) are not routing
targets. Before adopting a release for unattended production work, replay representative
tasks with the incumbent and candidate using the same tools, permissions and acceptance
checks. Compare task pass rate, tool errors, latency, cost and rework. Retain the previous
working pin for rollback if a required check regresses.

Sources:
- [Claude models overview](https://platform.claude.com/docs/en/models/overview)
- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- [Claude choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [Claude Fable 5.2](https://platform.claude.com/docs/en/models/fable-5-2/overview)
- [Claude Code model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)
- [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)
- [Claude effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Claude model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [OpenAI API changelog](https://developers.openai.com/api/docs/changelog)
- [ChatGPT and Codex changelog](https://learn.chatgpt.com/docs/changelog)
- [OpenAI models](https://developers.openai.com/api/docs/models)
- [Sol 6.2 API](https://developers.openai.com/api/docs/models/gpt-6.2-sol)
- [Astra 6.2 API](https://developers.openai.com/api/docs/models/gpt-6.2-astra)
- [Sol 6.1 API](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Terra API](https://developers.openai.com/api/docs/models/gpt-6.1-terra)
- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [OpenAI GPT-6.2 guide](https://developers.openai.com/api/docs/guides/latest-model)
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- [Work/Codex models and product retirement](https://learn.chatgpt.com/docs/models)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models)
- [Gemini API release notes](https://aistudio.google.com/docs/changelog)
- [Gemini choosing a model](https://ai.google.dev/gemini-api/docs/choosing-a-model)
- [Latest Gemini models](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini 4 Carbon](https://ai.google.dev/gemini-api/docs/models/gemini-4-carbon)
- [Gemini 4 Neon](https://ai.google.dev/gemini-api/docs/models/gemini-4-neon)
- [What's new in Gemini 4 Neon](https://ai.google.dev/gemini-api/docs/whats-new-gemini-4-neon)
- [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
- [Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/models/gemini-4-hydrogen)
- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Antigravity models](https://antigravity.google/docs/models)
- [Antigravity changelog](https://antigravity.google/docs/changelog)
- [Antigravity subagents](https://antigravity.google/docs/subagents)
- [Antigravity swarm](https://antigravity.google/docs/swarm)
- [Antigravity CLI docs](https://antigravity.google/docs/cli/)
