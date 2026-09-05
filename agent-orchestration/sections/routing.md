## §3. Route each node to a tier

Tiers are **roles**, not brand names. Map roles to whatever the harness exposes today —
the Claude Code Agent tool takes `model: opus | fable | sonnet | haiku` plus an effort
dial, and other CLIs have their own. Relative model strength moves every few months:
**check what the session actually offers rather than trusting this mapping**, and re-check
it whenever a new family ships.

| Work | Role tier | Effort | Why |
| --- | --- | --- | --- |
| Decompose, decide architecture, resolve ambiguity | lead (frontier) | high+ | wrong here is expensive and silent |
| Diff review, gate verification, risk calls, the merge | lead (frontier) | high+ | accountability cannot be delegated |
| The tricky 10% with no clean spec | lead (frontier) | high+ | if you can't spec it, you can't delegate it |
| Adversarial verification of a load-bearing finding | frontier, **fresh context** | high | needs judgment *and* independence |
| Implementation of an already-specified workstream | mid | medium | competence, not final judgment |
| Test writing against a stated contract | mid | medium | the contract is the spec |
| Codebase survey, "where is X", file inventory | cheap, read-only, parallel | low | breadth, zero judgment |
| Mechanical refactor with a mechanical check | cheap | low | the check is the safety net |
| Docs, changelog, copy drafts | cheap → mid | low | review catches drift |
| Web research / fact gathering | cheap, told to mark UNVERIFIED | low | facts either verify or they don't |
| Red team on a decision the whole fleet shares | **different lineage** (Codex, agy) | — | same-model verifiers share blind spots |

**Effort is a second dial, cheaper than a tier bump.** A mid model at high effort often
beats a frontier model at low effort, at a fraction of the cost. Reach for effort first.

**Cross-lineage matters for one thing: independence.** Verified on this machine —
`codex` and `agy` are installed (`FANOUT-PATTERNS.md` §4). A second
Claude agent shares Claude's blind spots; when a conclusion is load-bearing and the fleet
agreed too easily, ask a different lineage.

**Anti-patterns.** Routing by prestige ("it's important, use the big one") instead of by
whether the check is mechanical. Sending a frontier model to grep. Sending a cheap model
to a task whose acceptance check is "use good judgment".

---
