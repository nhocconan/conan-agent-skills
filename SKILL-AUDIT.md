# Skill audit — 2026-10-02

Supersedes the 2026-09-15 audit. Scope: all 32 first-party skill entrypoints and the
files they reference, the install/update tooling (`harness.py`, `refsync.py`,
`loadouts/*`), and the validators. Six read-only reviewers covered the skills in parallel;
the orchestrator verified the install path with isolated fixtures and made the edits.
This is a source, fact and behavior review, not proof that any skill works against a live
third-party service.

## Install and update path

Fixtures ran with `HOME=$(mktemp -d)`, `CONAN_AGENT_ENSURE=0`, never against a real
home: fresh `apply --target all --profile core`, `verify`, a second `apply` (idempotent,
no new backups), `auto` with and without a browser, every explicit profile on a fresh
clone, `upgrade` on a copied checkout, dangling and stale links, pre-existing user files,
a same-name collision, and an agy directory holding unlisted entries. 49 checks pass.

Two defects were found and fixed, each with a unittest:

| Defect | Fix |
| --- | --- |
| `harness.py apply --profile auto` (the documented workstation command) linked the skills and then crashed in the audit step looking for `loadouts/auto.txt`; exit 1 on every fresh install | the audit resolves `auto` per target the same way `refsync.py loadout` does |
| A dangling link to a wanted skill (the checkout moved or an old clone was deleted) was treated as a collision and the whole apply was refused | a broken link protects nothing; it is repointed |

Also fixed: `ref-skills/tests/test_prune_dead_hooks.py` was pytest-style and never ran
under `unittest discover` (3 tests, now 11 in that suite); the suite is in the `AGENTS.md`
validation list and CI. `agent-session-backup/scripts/backup.py --help` created a
directory named `--help` and ran a backup into it. Two `.bak-*` files committed on
2026-09-30 are removed and the pattern ignored.

## Wraps and upstream drift

gstack `main` is at 1.91.12.0 (read 2026-10-02). `ship`, `qa` and `qa-only` now carve
their bodies into `sections/*.md` files that the wraps tell the agent to read, and
`upstreams.ini` listed only two of them. `refsync.py ensure` now fetches every section a
fetched `SKILL.md` references; one upstream references but has not published
(`qa-only/sections/browser-setup.md`) is reported, not fatal. Four of five wrap
fingerprints no longer match the vendored or the live upstream; `refsync.py upgrade`
(an authorized update, not run here) re-fetches and asks for `--accept` per wrap.

Every wrap now states that its `../.vendor/...` paths are relative to the skill's real
directory in the checkout, and what to do when a vendored file is absent. `browsing-web`
regained the Chrome-MCP ban its `REF.md` lists as a must-survive override.

## Corrections to shipped content

| Skill | Defect | Correction (source, 2026-10-02) |
| --- | --- | --- |
| secure-code-audit | step 1 named no secret-scan command; `--config auto` sends metrics by default; LLM Top 10 unversioned | gitleaks `git`/`dir --redact`, trufflehog `--no-verification`; `--metrics=off`; OWASP Top 10 for LLM Applications 2025 ids (genai.owasp.org) |
| a11y-audit | 3.3.8 described as "don't block paste"; large text "19px bold" | criterion text (no cognitive-function test without alternative); 18.66px bold |
| web-perf-audit | Next.js `priority` prop | deprecated in Next.js 16 for `preload`; `fetchPriority="high"` (nextjs.org docs) |
| appstore-review-guard | restore blockquote presented as guideline text; Play promo-video tolerances asserted | 3.1.1 quoted verbatim, rejection wording labelled; Play video requirements from answer/9866151, tolerances marked unverified |
| store-screenshots | example forced Kokoro voiceover while docs say silent default; example rendered the 6.5" slot; TTS "~1¢" | silent default; 1320×2868 (6.9"); token pricing from the OpenAI model page, per-preview cost unverified |
| mobile-app-playbook | `Uuid` "stable from Kotlin 2.4"; CMP "fatal-errors" stated as fact; keywords "100" without unit | `Uuid.random()` still Experimental in 2.4.0 (whatsnew24); claim marked unverified; 100 bytes |
| autonomous-loops | section index promised harness content the file no longer has; hook exit-code 2 stated for all events | index row rewritten; blockable events named; `/loop` 7-day expiry and `CLAUDE_CODE_DISABLE_CRON` added (code.claude.com docs) |
| routing.md | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` precedence incomplete | FORCE-alone and both-set behavior from the sub-agents page; no model ID, price or date changed |
| MANUAL.md | named one model per harness as "the lead" | the active parent session is the lead; model tables live only in routing.md |
| README / MANUAL / ARCHITECTURE / BOOTSTRAP | "verified 2026-09-15" for routing; "TanStack Table v8"; "~74 skills"; impeccable "23 commands"; toolchain versions from 2026-07; model names in an index row | dates match routing.md; TanStack v9 current; count dropped; 24 commands (impeccable 4.1.0); versions re-read from release feeds; model names removed |

Synthetic examples replaced product-specific residue in `metric-integrity`,
`backtest-integrity` and `demo-data-craft`; an employer file name left `AUDIT.md`;
`bug-class-audits` no longer competes with `investigating-bugs` on the same Vietnamese
trigger; `delegate-run` dropped bullets that restated `agent-orchestration`.

## Context budget

`anti-slop-review` grew on 2026-09-29 (formatting-slop, negative-parallelism and
process-stamp rules; a 23 KB sign catalogue as on-demand reference) and failed the
ratchet. The skeleton was trimmed and the ceilings raised deliberately (eager 4800,
on-demand 24600). Twelve other skills grew by 20–350 bytes from the corrections above
and their ceilings were raised to measurement + 5%; three shrank and were ratcheted down.

## Verification and limitations

Validators: `project_rules.py check`, `validate_skills.py` (32 skills, 0 errors,
0 warnings), `context_budget.py --no-ratchet`, and the four unittest suites pass;
`git diff --check` is clean. Facts carry the page they were read from and the date.

Not done: no live store submission, deployment, browser journey, history mining or real
restore. No installer ran; `.vendor/` was not refreshed and no wrap was `--accept`ed.
Model IDs, prices and dates in routing.md were not re-verified (owner did so 2026-09-30).
agy skills directory: Google's Antigravity docs list `~/.gemini/antigravity-cli/skills`
as the CLI's global directory, but a 2026-10-02 probe of agy 1.2.14 (`agy -p` asked to
list its skills) returned every entry of `~/.gemini/config/skills` plus built-ins and
none of the entries present only in `antigravity-cli/skills`. The repo keeps
`~/.gemini/config/skills`; the probe is model self-report, so re-probe on an agy upgrade. The Codex "2% of the
context window" cap does not state its unit. OpenAI's Codex docs now 308-redirect to
`learn.chatgpt.com`; routing.md keeps the original URLs until the redirect proves stable.

## 2026-10-17 — orchestration token review (one project, seven days)

Scope: every Claude Code transcript of one project from 2026-10-10 to 2026-10-17 — 10 lead
sessions and 507 subagents, 60,037 assistant turns — read by a streaming script over the
`usage` fields (input, cache read, cache creation, output per turn; list-price equivalent
from the routing tables). Private script, raw tables and incident references live in
`.agents/token-review-2026-10-17/`. One project, one harness: a measurement of this
operating pattern, not a benchmark of the models.

Totals: 10.37 B cache-read tokens, 314 M cache-creation, 6.7 M output, ≈ $5,100 list price;
cache reads are 80 % of it, so cost tracked context size × calls, not output. Two days
carried 61 % of the turns ($1,300 and $1,800). Ranked causes, each with the rule it changed:

| # | Measured cause | Share | Change |
| --- | --- | --- | --- |
| 1 | Long workers: 223 of 507 subagents passed 80 turns or 150k average context (Sonnet builders averaged 133–187 turns; 0 of 512 spawns set a turn cap, 5 set effort, 137 set no model) | 76 % of worker spend ($3,100 of $4,060) | routing: cap per tier, `maxTurns`/runtime control named, re-brief from the results file; brief: settings travel with the brief |
| 2 | Hardest tier doing runner work: 86 Fable subagents ($1,630, 32 %); 44 Fable reviewers made 1,881 shell calls including 79 test/E2E runs; the largest single review ran 455 turns ($127); 26 routine reviews ran on Fable although the definition says Sonnet | 32 % | routing: work-nature → tier table; a reviewer reads artifacts and runs no suite; 17 % of spend was review on the hardest tier |
| 3 | Lead context: ten Opus leads at 250k–720k average context (budget 120k), 6,517 turns, 4.8 M output tokens; 135 test/E2E commands and 455 log reads in the lead's own context; 197 resumes (median 532 B) beside 512 spawns; 3 agents spawned only to wait | 21 % ($1,070) | tracking: lead runs no gate/suite/browser itself; resume and placeholder waste named with numbers |
| 4 | Expensive tiers on browser/E2E work: 1,579 E2E commands in Sonnet agents, 292 Opus, 169 Fable, 107 Haiku; agents running them cost $1,450 (Opus), $1,340 (Sonnet), $860 (Fable), $9 (Haiku) | — | routing: mechanical-run row with what the cheapest tier did reliably (24 prod checks + 2 gate runs, correct verdicts, $10) and when it escalates |
| 5 | Overlap: 84 `git reset`/`restore --staged` commands untangling foreign staged files (one a step from reverting another agent's commit); 144 revert/restore/checkout commands; 68 `git add -A`/`.`; docs map 5 writers, review index 4, product spec 3; 3 agents referenced the same new migration number; writers blocked on another writer's typecheck | rework, not tokens | DAG: ownership manifest, reserved-resource ledger, commit-by-path, shared typecheck surface; templates carry both |

Not measured: wall-clock, operator interventions, defects caught per tier, and whether any
Haiku verdict was later contradicted (none found in lead text; 27 runs is a small sample).
Token counts are the harness's own usage fields; prices are the routing tables' list rates,
not the account's bill. Context budget: agent-orchestration on-demand ceiling raised for the
table and the ownership protocol; effective-development eager raised for one paragraph;
both recorded in `skill-miner/context-budget.json` in the same commit.
`effective-development` joined the core, codex-dev and agy-dev load-outs because the
quality gate and the runner rule both link to it.

## Maintenance bar

Keep a skill only when it changes a decision the base agent would otherwise get wrong and
has a distinct trigger boundary. Prefer updating an existing skill to adding a near-duplicate.
Re-verify vendor facts on a release, deprecation, rejected ID or retirement within 90 days.
Run `refsync.py upgrade` within an authorized update and review each wrap preview before
`--accept`; a wrap pointing at a vanished upstream section is wrong, not stale.
