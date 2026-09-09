# Working in this skills repository

Shared project rules live only in this `AGENTS.md` (or the appropriate scoped
`AGENTS.md`). When asked to save a shared rule, edit that canonical file, never
`CLAUDE.md`, `GEMINI.md`, or platform-private auto-memory. Those two adapters must
remain imports only. Platform-only settings belong in platform configuration;
do not duplicate shared policy there. See `coding-env-bootstrap/PROJECT-RULES.md`.

Model policy: read `agent-orchestration/sections/routing.md` when delegating.
GPT-6 Astra owns orchestration and final output quality. GPT-5.6 Terra implements
scoped work; GPT-5.6 Luna handles simple, mechanically checked tasks. Use only
models exposed by the active harness. Do not claim Astra approval if unavailable.

Keep skills concise and task-specific. Preserve user intent and existing authority;
review-only requests do not authorize installs, global configuration, or publication.
Use dated official sources for changing models and vendor requirements. Keep model
IDs in the canonical routing policy instead of duplicating tables across skills.

Working plans and agent ledgers belong in `.agents/` (ignored). Public documentation
must not contain private histories, account IDs, credentials, or internal project maps.
Preserve unrelated work. Do not run installers or real history backup/restore for tests.

Validation after relevant changes:

- `python3 coding-env-bootstrap/project_rules.py check --root .`
- `python3 skill-miner/validate_skills.py`
- `python3 skill-miner/context_budget.py --no-ratchet`
- `python3 -m unittest discover -s skill-miner/tests -v`
- `python3 -m unittest discover -s agent-session-backup/tests -v`
- `python3 -m unittest discover -s coding-env-bootstrap/tests -q`
- `git diff --check`

Use isolated temporary fixtures for scripts. A clean validator proves structural
properties, not skill quality or real-service compatibility; state testing limits.
