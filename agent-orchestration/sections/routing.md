## §3. Route each node to a tier

Tiers are **roles**, not brand names. In software development, **always use agent orchestration**:
higher-level models (**Fable, Sol/Astra**; in Google `agy`, use **Gemini 3.8 Flash** across the board since 3.1 Pro is outdated) act as the orchestrator / control tower, and all other
workers use lower-level models (**Opus, Sonnet, GPT Terra, GPT Luna, Gemini Flash, etc.**) when suitable.
When a worker node faces **genuinely difficult work** (deep architectural ambiguity, complex
concurrency or state machines, critical money-math/tenancy invariants, or adversarial verification),
using the higher-level model (or max effort in Flash) for that worker is still completely appropriate.

### Lineage model routing

| Lineage / Harness | Orchestrator (Higher-Level Model) | Workers (Lower-Level, When Suitable) | Difficult / High-Risk Worker Override |
| --- | --- | --- | --- |
| **Anthropic (Claude Code)** | **Claude Fable** (frontier lead) | **Opus**, **Sonnet** (Haiku for breadth/survey) | **Claude Fable** |
| **OpenAI (Codex)** | **OpenAI Sol / Astra** (GPT-6 Astra / SOL) | **GPT Terra**, **GPT Luna** | **OpenAI Sol / Astra** |
| **Google (agy)** | **Gemini 3.8 Flash** (`gemini-3.8-flash-high`)* | **Gemini 3.8 Flash** (`gemini-3.8-flash-high`), Flash-Lite | **Gemini 3.8 Flash** (high effort) |

*\*Note on Google / agy: Gemini does not have a current-generation Pro yet. 3.1 Pro is several generations behind and outdated ("củ chuối"); use **Gemini 3.8 Flash** (`gemini-3.8-flash-high`) across the board for both lead and worker nodes until a next-gen Pro is released.*

Relative model strength moves every few months: **check what the session actually offers rather
than trusting a static list** (e.g. `agy models`, Codex model list), but maintain this orchestrator-versus-worker hierarchy.

### Work-to-role routing

| Work | Role tier | Suggested Model | Effort | Why |
| --- | --- | --- | --- | --- |
| Decompose, decide architecture, resolve ambiguity | lead (frontier) | Fable / Sol / Astra / Gemini 3.8 Flash | high+ | wrong here is expensive and silent |
| Diff review, gate verification, risk calls, the merge | lead (frontier) | Fable / Sol / Astra / Gemini 3.8 Flash | high+ | accountability cannot be delegated |
| The tricky 10% with no clean spec | lead (frontier) | Fable / Sol / Astra / Gemini 3.8 Flash | high+ | if you can't spec it, you can't delegate it |
| Adversarial verification of a load-bearing finding | frontier, **fresh context** | Fable / Sol / Astra / Gemini 3.8 Flash | high | needs judgment *and* independence |
| Complex/difficult worker subtask (invariants, math, auth) | frontier worker | Fable / Sol / Astra / Gemini 3.8 Flash | high | difficult work justifies frontier capacity |
| Implementation of an already-specified workstream | mid worker | Opus / Sonnet / Terra / Luna / Flash | medium | competence, not final judgment |
| Test writing against a stated contract | mid worker | Opus / Sonnet / Terra / Luna / Flash | medium | the contract is the spec |
| Codebase survey, "where is X", file inventory | cheap, read-only, parallel | Haiku / Luna / Flash-Lite | low | breadth, zero judgment |
| Mechanical refactor with a mechanical check | cheap worker | Haiku / Luna / Flash-Lite | low | the check is the safety net |
| Docs, changelog, copy drafts | cheap → mid worker | Sonnet / Terra / Flash | low | review catches drift |
| Web research / fact gathering | cheap, told to mark UNVERIFIED | Haiku / Luna / Flash-Lite | low | facts either verify or they don't |
| Red team on a decision the whole fleet shares | **different lineage** (Codex, agy) | Sol / Astra / Gemini 3.8 Flash / Fable | — | same-model verifiers share blind spots |

**Effort is a second dial, cheaper than a tier bump.** A mid model at high effort often
beats a frontier model at low effort, at a fraction of the cost. Reach for effort first.

**Cross-lineage matters for one thing: independence.** Verified on this machine —
`codex` and `agy` are installed (`FANOUT-PATTERNS.md` §4). A second
Claude agent shares Claude's blind spots; when a conclusion is load-bearing and the fleet
agreed too easily, ask a different lineage.

**Anti-patterns.** Routing by prestige ("it's important, use the big one") instead of by
whether the check is mechanical. Sending a frontier model to grep. Sending a cheap model
to a task whose acceptance check is "use good judgment". Refusing to use a higher-level
model when a worker subtask is genuinely hard.

---
