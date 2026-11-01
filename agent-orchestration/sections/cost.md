## Quota discipline

Measured on one week of a lead + subagent project (745M weighted token units): 70 % of
the cost was cache re-reads of long contexts, 74 % was subagents, and output was 9 %.
The cost of a call is the context it re-reads, so the levers are context size and turn
count, not prompt length.

| Sink (share of the week) | Rule |
| --- | --- |
| Builders running 150-480 turns, each turn re-reading a growing context | One outcome per agent; a hard turn budget (≈ 80); a fresh agent per task instead of "keep going until green"; stop after 2 failed gate loops and return the finding |
| Strongest model as builder | Strongest model writes ideas, specs and reviews; the default builder implements from that spec |
| Lead context above 300k tokens (average call 527k; a third of lead cost above 600k) | Hand off and clear at ≈ 300k, not near the window limit |
| Polling (30 % of lead tool calls were sleep/status/tail) | Run long jobs in the background and wait for the one completion notice; a cheap runner agent runs a gate and returns ≤ 5 lines |
| Long tool output in the lead (git status, whole-file greps, traces) | Pipe to a tail or summary; read large artefacts through a short brief file |
| Re-spawning for the same work | Resume the existing agent; check running work before a spawn |
| Heavy jobs overlapping on one host (false failures, full reruns) | One host lock for gate, E2E and affected runs; never start a test while a gate runs |

Before a fan-out, state the expected turns per agent and the stop condition in the brief.
After a session, compare the ledger with these rows; a sink that recurs becomes a check.
