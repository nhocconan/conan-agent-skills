## §3. Model routing and quality ownership

Verified 2026-09-08. This is the canonical model policy; companion skills link here
instead of maintaining separate model tables.

**GPT-6 Astra owns orchestration and final output quality.** It defines acceptance,
resolves architecture, reviews the combined diff and evidence, and decides whether
the deliverable is complete. Worker completion is never final acceptance.

| Role | Default model ID | Starting effort | Boundary |
| --- | --- | --- | --- |
| Lead, architecture, final review and integration | `gpt-6-astra` | high | Final quality accountability |
| Scoped implementation and meaningful tests | `gpt-5.6-terra` | medium | Works within Astra's contract |
| Inventory, simple docs, mechanically checked edits | `gpt-5.6-luna` | low or medium | No unresolved architecture or critical invariant decisions |
| Difficult implementation or independent critical review | `gpt-6-astra` | high | Escalate for risk or failed checks |

Use only models and effort values offered by the active harness. These are starting
choices, not universal performance claims. Terra is the default builder; Luna gets
small tasks whose correctness can be checked reliably. After two failures of the same
acceptance check, Astra diagnoses the contract or takes the task back.

### Claude collaborators

When a connected Claude harness is available and authorized, use these current API IDs:

| Model | Appropriate collaborator role |
| --- | --- |
| `claude-fable-5-1` | Difficult reasoning or independent review |
| `claude-opus-5` | Complex agentic coding |
| `claude-sonnet-5` | Scoped implementation |
| `claude-haiku-4-5-20251001` | Read-only breadth or simple checked work |

Claude collaborators report to Astra. A Claude-only session may prepare work and
evidence, but must identify final Astra review as pending under this policy. Do not
silently substitute Fable, Sol, or a Google model for the requested Astra lead.
A user may explicitly choose a different lead for a particular run.

API IDs are not automatically accepted by every subagent tool. Inspect its schema
and installed catalog before using provider aliases. A Codex surface offering only
OpenAI models cannot spawn Claude IDs; use a separate available Claude connector
or CLI only when authorized. Do not invent access.

If Astra is unavailable, complete safe preparation and report that limitation before
claiming final approval. A skill cannot change the current session's model. Record
the actual model returned by the harness when exposed; otherwise label it unverified.

### Harness mechanics

For Codex `spawn_agent` surfaces supporting model overrides, set `fork_turns: "none"`
(or a supported positive count) when setting `model` or `reasoning_effort`; provide
a self-contained brief. Full-history forks may reject overrides. The active schema wins.

Do not inherit Astra for every worker by omitting the model when overrides are
available. If overrides are unavailable, disclose inherited execution and keep the
fleet small. Respect the actual concurrency ceiling, including the lead slot.

### Freshness and evidence

Before changing defaults, check official model pages and the session catalog.
Preserve the user's explicit model choice. Re-evaluate on a release, deprecation,
rejected model ID, or maintenance audit. Keep historical benchmarks dated; do not
relabel old runs as new models.

Sources:
- [OpenAI Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [OpenAI Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [OpenAI Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [Claude models and API IDs](https://platform.claude.com/docs/en/models/overview)

Routing and final ownership are the operator's policy, not a vendor guarantee.
Google model upgrades are outside this update; discover available models if requested.
