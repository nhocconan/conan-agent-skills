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

## 2026-11-03 — design-skill trigger review (one project, ~4 days)

Scope: Claude Code transcripts of one project, 3 lead sessions and 132 subagents
(2026-10-31 to 2026-11-03, all that was on disk), scanned for UI-file edits and Skill calls;
private script and per-session table in `.agents/design-review-2026-11-03/`. Codex sessions
were not scanned. Counts, not trends.

| Measured | Result | Change |
| --- | --- | --- |
| Significant UI-editing sessions (≥3 UI files or ≥150 lines) that invoked any design skill before the first UI edit | 0 of 6 (1 invoked `design-qa` after its edits) | `frontend-design` description now fires on any visible change, chrome and small tweaks included, with Vietnamese phrasing; body is a 7-step loop with artifacts |
| Worker briefs that named the design skills ("use if available") | 4 of 6; none loaded one before editing | brief.md: UI acceptance is the loop's evidence, not advice |
| Screenshots in UI sessions / with dark mode | 6 of 11 / 3 of 11 | loop step 4 fixes the set: 1440 and 390, light and dark, open states |
| Detector hook | 335 stop-hook passes, 2 findings (both one `side-tab`) | documented as a source floor; composition goes to `design-qa`'s counted rubric and `layout-probe.js` |

Three docs disagreed on the owner of UI building (MANUAL said impeccable, README said conan
`frontend-design`, design-qa pointed at impeccable). README and MANUAL now name one entry point
and route impeccable by command. Context budget: `frontend-design` and `design-qa` always-on and
on-demand ceilings raised in the same commit for the wider trigger text, the rubric and the probe.
The Codex load-out (`codex-dev`) still omits the design skills; adding one is an operator
decision because that load-out is capped by Codex's description budget.

## 2026-11-05 — full review, usage history, upstream comparison

Scope: all 34 skills (33 after one merge). Six read-only reviewers by skill group and nine
builders with one owner per directory (Sonnet 5.5); one integration review of the combined
diff (Fable 5.1: ACCEPT-WITH-FIXES, 0 P1, 16 P2; 11 fixed, 5 accepted as noted below); lead
Opus 5.5. Private tables, briefs and the history scan scripts live in
`.agents/skill-review-2026-11-05/`.

Reviews raised 145 findings (6 P1). The P1s:

| Defect | Change |
| --- | --- |
| `context_budget.py --no-ratchet` exited 1 at base: three skills over their ceilings, one by 99 KB from a vendored upstream | ceilings set deliberately in the same diff (list below) |
| vendored taste-skill shipped a nested `SKILL.md` with its own frontmatter (a second UI skill one glob away from registering) | renamed `UPSTREAM-SKILL.md` |
| `shipping-changes` (and `investigating-bugs`, `web-qa`, `design-qa` REFs) sent the agent to upstream sections that no longer exist (`refsync.py status`) | re-pointed to the current vendored text; fingerprints left for `refsync.py upgrade --accept` |
| private project names in a public file (`effective-development`) | anonymized; they remain in git history and three commit subjects |
| `agent-orchestration`: one section said clear the lead's context at 300k, two said 120k | 120k, owned by tracking.md |

Usage, from this machine's Claude Code and Codex history (local history starts 2026-10-26:
39 lead sessions, 803 subagent sessions, 27 Codex rollouts, 630 human turns; agy logs are
not parseable): every skill showed some use; the lowest were `backtest-integrity` and
`interactive-course-builder` (one spawn mention each). Leads rarely call the Skill tool
(`agent-orchestration` 9); most use is by path read.

Pain clusters (372 human turns, 16 clusters, 12 verified in context): in six of them the
covering skill existed and was not loaded in the session where the pain happened.

| Cluster (prompts / sessions / projects) | Change |
| --- | --- |
| Agent stops to ask or hands the operator commands after authority was delegated (19 / 8 / 5); `delegate-run` loaded 0 times, `agent-orchestration` 8 | `delegate-run` merged into `agent-orchestration` (operating-contract, two eager lines, its triggers) and retired |
| Covering skill not loaded (runaway processes, slop, instance-not-class fixes, sign-in loops) | skill-routing table in `coding-env-bootstrap/templates/global-instructions.md` |
| Paid third-party jobs: invented caps, retries while a job runs (16 / 5 / 4) | "Paid third-party jobs" in agent-orchestration `sections/cost.md` |
| Lead's own detached job dies unnoticed (9 / 4 / 3) | liveness check in `sections/tracking.md` |
| Unsourced thresholds, limits or causes (6 / 5 / 4) | source-or-"assumed" rule in `senior-operator` |
| Host resource-share caps (4 prompts / 3 projects) | enforced mechanically, checked in the process table (`dev-env-lifecycle`) |

Upstream comparison: mattpocock/skills @4ae2317 (39 skills, MIT). Nothing installed: the
plugin is all-or-nothing, updates itself outside the load-out, collides with `/code-review`,
and its model-invocable skills add ~2.3k chars to Codex's ~8k skill list. Four techniques
ported with attribution: diagnosing-bugs → `investigating-bugs`, tdd → `effective-development`,
grilling → agent-orchestration intake, writing-for-agents → `skill-miner`.

Third-party load-out: of 17 names, `vercel-react-best-practices` is installed (vercel-labs/
agent-skills @1a2c79d, Claude and Codex); `context7` and OpenAI docs stay MCP servers; 14 were
removed (duplicates of repo skills, hooks or global config, or no findable upstream).

Routing: the Claude focused tier is now Haiku 5.5 (released 2026-10-07, effort `low`–`max`,
default `medium`); Haiku 4.5 is legacy (platform.claude.com, read 2026-11-05; IDs in routing.md).

Context budget: ceilings raised deliberately to about measurement + 3 % for growth the
review asked for — `agent-orchestration` (merged delegate-run, paid-job rules), `frontend-design`
on-demand 19,000 → 120,000 B (the vendored taste-skill; its step-1 reads cost about 30k tokens, so
the operator made the gate on demand the same day: new design, UI review, or when asked), `investigating-bugs` and `effective-development`
(ports), `skill-miner`, `secure-code-audit` and `resilient-data-harvest` (content moved to
on-demand files), `browsing-web`, `docs-sync`, `autonomous-loops`. 21 ceilings ratcheted down.

Accepted from the integration review without change: dated measurement notes in
agent-orchestration brief/tracking (no private names); attribution for the grilling port sits
beside the ported text in operating-contract.md.

Not done: stale vendor facts were flagged, not re-verified (store guidelines and slot sizes,
WCAG criterion text, Next.js image props, Playwright versions, the toolchain table, scanner
flags; list in the private results). Wrap drift is not accepted. The global template is edited,
not applied to any harness. Description edits kept every quoted trigger phrase (checked
mechanically) but trigger rates were not measured. Usage covers about ten days on one machine.
`harness.py` still writes `~/.claude/...` and ignores `CLAUDE_CONFIG_DIR` (backup scripts now honor
it); harmless where the account directory links back to `~/.claude`, as it does here.

## Maintenance bar

Keep a skill only when it changes a decision the base agent would otherwise get wrong and
has a distinct trigger boundary. Prefer updating an existing skill to adding a near-duplicate.
Re-verify vendor facts on a release, deprecation, rejected ID or retirement within 90 days.
Run `refsync.py upgrade` within an authorized update and review each wrap preview before
`--accept`; a wrap pointing at a vanished upstream section is wrong, not stale.

## 2026-11-06 — trigger firing and harness fit (34 skills)

Scope: whether skills load when they should in Claude Code 2.1.319 and Codex CLI 0.167.0,
judged by a three-reviewer panel (firing, decision value, portability). Harness facts were
read from the vendor docs on 2026-11-06 (code.claude.com skills/plugin-evals/changelog;
learn.chatgpt.com build-skills; agentskills.io specification).

| Finding | Evidence | Change |
| --- | --- | --- |
| Claude's skill listing sat at its budget (1 % of context); overflow drops the least-used skills' descriptions first | `/context`: Skills 9.9k tokens = 1.0 % | descriptions cut 15.9k → 14.5k chars, trigger clause first (≤ char 217); 8 by-name skills set `name-only` in the settings template |
| Skills fired on clean English tasks but not on complaint or correction phrasing | real-harness eval: 48/64 baseline, real-style prompts 10/24 | descriptions carry the operator's natural trigger phrases. Holdout set written before edits: 20/24 → 22/24 (two runs per case; within noise). On the set the new wording was drawn from: 48/64 → 62/64. Negatives 18/18, near-miss 8/8 |
| Codex load-out was cut to 12 skills on an 8,000-character premise | Codex budget is `skills.max_context_tokens` (2 % of window, ≤ 10,000 tokens); echo probe: 49 entries, none shortened | `codex-dev` carries all 34 first-party skills |
| No check that a description fires or is front-loaded | — | `validate_skills.py` warns on late trigger clause, > 520 chars, unknown keys (error); `skill-miner/trigger_eval.py` + synthetic set, run after description edits (AGENTS.md) |
| Claude Code runs a skill named `verify` before every commit (2.1.286) | changelog | new `verify` skill: repo gates with exit codes (runner in orchestrated runs), residue inventory, replay of the operator's named path |

Content cuts of base-default material (a11y, web-perf, admin-crud, remote-host, senior-operator,
effective-development) removed about 5.8 KB of eager text. Limits: one model (Opus 5.5),
two runs per case, read-only tools in a synthetic fixture repo; Codex firing is not measured
by a runner, only by catalog inspection.
