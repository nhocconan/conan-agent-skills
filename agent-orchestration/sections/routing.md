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
| agy (Antigravity CLI) | `gemini-4-argon` / `gemini-3.8-flash` | `gemini-4-carbon` (Ultra/Enterprise), else `gemini-4-argon` | `gemini-3.8-flash` | `gemini-3.8-flash` (`low`) |

### Work nature → tier

Define the outcome, risk and observable checks first; then choose a capable model and effort
for the actual work, subject to required project review gates. The parent remains lead; only its context may grow (≤ 120k,
[tracking](tracking.md)); every worker is capped and set explicitly on the spawn.

| Work | Tier | Effort | Cap | Return |
| --- | --- | --- | --- | --- |
| Specific unresolved hard question; an explicitly requested specialist | hardest scoped judgment (Fable / Astra / Carbon, else Argon) | as needed | 60 turns; reads the diff and artifacts, runs nothing heavier than `git`/`grep` | one line per finding |
| Broader or risky build, refactor, migration, integration or review; E2E flow authoring | bounded builder (Sonnet / Sol 6.1 / 3.8 Flash) | task-dependent | 80 turns / 150k context | builder contract |
| Source-based writing, chart/screen interpretation, bounded app workflows; narrow, low-risk app edits with explicit acceptance checks | scoped specialist (Codex: Terra 6.1) | task-dependent | 60 turns / 150k context | artifact + evidence + uncertainties |
| Bounded multi-step triage, source verification, narrow low-risk edits with observable checks, or specified browser checks | focused checked work (Haiku 5.5 / Luna / 3.8 Flash `low`) | task-dependent | 60 turns | verdict + evidence |
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
| 3.8 Flash | `gemini-3.8-flash` | GA, newest Flash | 2026-09-02 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.6 Flash | `gemini-3.6-flash` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.75 → 3.75 |
| 3.5 Flash-Lite | `gemini-3.5-flash-lite` | GA | 2026-07-21 | 1,048,576 / 65,536 | 0.30 → 2.50 |
| 3.1 Pro | `gemini-3.1-pro-preview` | Preview | — | 1,048,576 / 65,536 | 2 → 12 (≤200K input) |

**Carbon is Google's most capable reasoning model, Argon the efficient frontier tier, 3.8
Flash the cross-plan workhorse.** `gemini-4-carbon` shares Argon's limits, API pricing and
cache terms; Antigravity lists it for Ultra and Enterprise only, so Argon stays the fallback.
`gemini-4-argon` has a unified 1,048,576 input+thinking+output window (1M long decode
via `background: true`), Antigravity access on paid Pro/eligible-device trials,
Ultra and Enterprise (app, CLI, IDE extensions),
and `$2 → $10` intro API pricing through 2026-11-30 (`$4 → $20` from 2026-12-01; implicit
cache `$0.10` then `$0.20`; no explicit cache or Free API tier). Flash `$0.75 → $3.75`
intro rates move to `$1.50 → $7.50` on 2027-01-01. `gemini-3.7-flash` and
`gemini-3.5-flash` (deprecated 2026-10-08) auto-route to `gemini-3.8-flash` and
`gemini-3.6-flash`. Never combine `thinking_budget` with `thinking_level`.

| Model | Accepts (`thinking_level`) | Default |
| --- | --- | --- |
| 4 Carbon, 4 Argon, 3.8 Flash | `low`, `medium`, `high` | `medium` |
| 3.6 Flash | `minimal`, `low`, `medium`, `high` | `medium` |
| 3.5 Flash-Lite | `minimal`, `low`, `medium`, `high` | `minimal` |
| 3.1 Pro (Preview) | `low`, `medium`, `high` | `high` |

Use Carbon `high` (Argon `high` where Carbon is not entitled) for hardest architecture,
math/science, high-risk review and long decode; Argon `medium` for general lead and complex multi-step engineering; `low` for lighter
cost-sensitive reasoning. Use 3.8 Flash `high` for harder multi-step coding/agents or lead
fallback when Argon is unavailable; `medium` for standard bounded builds and routine
review; `low` for fast checks, inventory, extraction and narrow edits (`minimal` errors on
3.8 Flash; 3.5 Flash-Lite `minimal`/`low` suits the lightest high-volume API checks, but the
agy catalog does not list it).

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

**agy (Antigravity CLI), 1.5.5 (`agy --version`, `agy models`, 2026-11-11).** The catalog exposes
`gemini-4-carbon-{low,medium,high}`, `gemini-4-argon-{low,medium,high}` and
`gemini-3.8-flash-{low,medium,high}` (plus Claude 5.5 and `gpt-oss-120b-medium`, removed
2026-11-18). A listed Carbon entry is not entitlement: the 1.5.5 changelog ties it to ADC
sign-in and the models page to Ultra/Enterprise, so confirm with one spawn. Since 1.3.4, `--model` and `/model` accept a
base model name without `--effort` (default thinking level, else `medium`), or pair with
`--effort` (`low|medium|high|xhigh|max`). `invoke_subagent` tiers (`inherit`, `flash_lite`,
`flash`, `pro`; names from the installed schema, not a vendor page): `flash_lite` for light lookups/checks, `flash` for bounded builders,
scouts and routine verifiers, `pro` (or `inherit` on the desired Argon level) for complex
refactors, architecture or high-risk verification. Mechanics:
[fan-out patterns](../FANOUT-PATTERNS.md#antigravity-agy-collaboration).

### Freshness and evidence

Re-verify on a release, a deprecation, a rejected model ID, a retirement date coming within
90 days, or a maintenance audit. Check the vendor model pages and the session catalog before
changing a default, and preserve the user's explicit model choice. Keep historical benchmarks
dated; do not relabel an old run as a new model. All three vendors
were re-checked against their model, pricing, effort and deprecation pages on 2026-11-11:
Claude (Fable 5.2 released 2026-11-09), Gemini and agy 1.5.5 (Carbon GA 2026-11-10), OpenAI
(no general-availability change since 2026-11-07; Codex CLI 0.167.1). Not re-confirmed that
day: per-model limits for the Flash and 3.1 Pro rows (last 2026-11-07), Terra's Codex catalog
values (2026-10-29), and the `thinking_budget` rule. Restricted-access models (Mythos 5.2,
GPT-6 Cyber, Rosalind) are not routing targets. These are not account-specific quotes.
Compare candidate models on representative inputs and
checks; record quality, elapsed time, actual token usage and rework where available.

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
- [Gemini 4 Carbon](https://ai.google.dev/gemini-api/docs/models/gemini-4-carbon)
- [Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
- [Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
- [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Antigravity models](https://antigravity.google/docs/models)
- [Antigravity CLI docs](https://antigravity.google/docs/cli/)
