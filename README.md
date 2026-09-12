# conan-agent-skills

My personal, reusable agent skills for Claude Code, Codex and Antigravity CLI (agy). This repo is
the single source of truth; each agent gets a curated set of symlinks into it.
"Installed" and "active" are deliberately separate, because upstream suites install far
more than should be competing for the model's attention.

| Agent | User-scope skill directory | Load-out profile |
|---|---|---|
| Claude Code | `~/.claude/skills` | `claude-dev` (workstation) / `core` (headless) |
| Codex | `~/.agents/skills` — its documented user scope; it follows symlinks | `codex-dev` |
| Antigravity CLI (agy) | `~/.gemini/config/skills` | `agy-dev` |

Skills use Markdown entrypoints; optional scripts and harness-specific references have
platform requirements. Check the active tools before executing a referenced recipe.

Model policy: **GPT-6 Astra leads and owns final quality; GPT-5.6 Terra implements;
GPT-5.6 Luna handles simple checked work.** Current Claude collaborator IDs and fallback
rules live in [model routing](agent-orchestration/sections/routing.md).
See [the audit dated 2026-09-08](SKILL-AUDIT.md) for the then-current 32 skills and validation limits.

Project rules use one source: `AGENTS.md`, with native Claude/Gemini import adapters.
See [the shared-rule convention](coding-env-bootstrap/PROJECT-RULES.md) for safe
migration and drift checks; never save shared rules independently per platform.

Keep the active set small on purpose: Codex caps the injected skill list at 2% of the
context window (8,000 characters when it cannot tell), shortening descriptions and then
dropping skills entirely. An over-full directory does not fail loudly — it goes quiet.

👉 **[MANUAL.md](MANUAL.md) — start here** (tiếng Việt): what's here, what fires when,
how to upgrade, how to roll back.

## Setup on a new machine

```bash
git clone https://github.com/nhocconan/conan-agent-skills.git ~/.conan-agent-skills
python3 ~/.conan-agent-skills/coding-env-bootstrap/harness.py \
  apply --target all --profile auto --with-mcp
```

That one command links the skills, fetches the few gstack markdown files the wrappers
read (into `.vendor/gstack/`, not a gstack install), and on a workstation installs
impeccable for UI work. On a headless host `auto` selects `core` and skips those.
For a headless host, pass `--profile core`: 12 general-development skills.
Mobile/store, course, quant, demo, and UI specialists remain available in the
repository and workstation profiles; enable them only for relevant projects.

Full runbook (toolchain, agent CLIs, plugins, MCP, secrets):
[`coding-env-bootstrap/BOOTSTRAP.md`](coding-env-bootstrap/BOOTSTRAP.md).

## Upgrading everything

```bash
python3 ~/.conan-agent-skills/ref-skills/refsync.py upgrade
```

`upgrade` now does the whole sequence: fast-forward this repo (skips if the tree is
dirty), fetch wrap sources from GitHub into `.vendor/`, update impeccable when the
selected profile needs it, re-check wrapper fingerprints, validate, then re-apply the
load-out. Default target is `all` (Claude + Codex + agy); default profile is `auto`.

Do **not** run gstack's `./setup` or `/gstack-upgrade` — that writes ~74 skills into
`~/.claude/skills`. This repo only needs the markdown the wrappers point at. See
[`ref-skills`](ref-skills/SKILL.md).

`auto` keeps the workstation profile when a real browser is present and falls back to
`core` when it is not. Third-party skills that live only on this machine (no installer,
not in this repo) are skipped on a fresh clone instead of aborting the apply.

## The design stack — who owns what

Five things can claim a UI task; they are layered deliberately so they do not compete.

| Layer | Owner | Fires when |
|---|---|---|
| Build & refine | **impeccable** (upstream, `keep.txt`) | making or reshaping a UI: `shape`, `polish`, `critique`, `typeset`, `layout`, `animate`, `harden`, `adapt` — 23 commands + a deterministic detector binary |
| Taste & anti-default | `frontend-design` (official Anthropic plugin) | aesthetic direction, typography, avoiding the looks generated pages converge on |
| Visual defect review | [`design-qa`](design-qa/SKILL.md) | a rendered page that works but looks wrong — wrapping, collisions, imbalance, cross-page inconsistency |
| Correctness gates | [`a11y-audit`](a11y-audit/SKILL.md), [`web-perf-audit`](web-perf-audit/SKILL.md) | WCAG 2.2 AA; LCP/INP/CLS. Neither is negotiable by taste |
| Feature floor | [`admin-crud-standards`](admin-crud-standards/SKILL.md) | any admin/list/CRUD screen — pagination, filters, confirms |

impeccable installs its own per-harness trees (`.claude/`, `.agents/`, `.agent/`, and a
dozen more) and is therefore listed in [`ref-skills/loadouts/keep.txt`](ref-skills/loadouts/keep.txt),
which the load-out neither creates nor removes. `refsync.py upgrade` / `ensure` is what
runs it — do not run that installer by hand.

Its `install` names the harnesses explicitly (`--providers=claude,codex,cursor,antigravity`).
Auto-detection finds the first three and silently skips agy, whose skills live under
`~/.gemini/config/skills` — impeccable calls that harness `antigravity` and writes it only
when asked by name. `ensure` now fails when a `keep` skill is still missing from a target
after the installer exits 0, so that gap cannot pass as green again.

The `~/.shared-ai-skills/frontend-design` copy was retired on 2026-09-05: a 2026-01
Codex-era port that shadowed the current official plugin under the same `name:`. See the
note at the end of [`ref-skills/loadout.txt`](ref-skills/loadout.txt).

## Adding a new skill

1. Create `<skill-name>/SKILL.md` (frontmatter: `name` matching the directory,
   `description` that states what **and when**), plus any scripts/assets beside it.
2. Add the name to the relevant file under `ref-skills/loadouts/` (and to
   [`ref-skills/loadout.txt`](ref-skills/loadout.txt) for the Claude workstation), then
   run `refsync.py loadout --target <claude|codex|agy|all> --profile <name> --apply`.
3. **Validate** — `python3 skill-miner/validate_skills.py`. Errors here make a skill
   silently untriggerable.
4. Add a row to the index below, commit, push.

Deriving from someone else's skill instead? Read [`ref-skills`](ref-skills/SKILL.md) —
wrap by default, fork only when you mean to diverge.

## Skill index

| # | Skill | What it does |
|---|---|---|
| 1 | [store-screenshots](store-screenshots/SKILL.md) | Branded store screenshots and App Preview videos from real captures. Current slot guidance, copy and rendering templates; silent preview by default, optional voiceover. Verify current submission requirements. |
| 2 | [admin-crud-standards](admin-crud-standards/SKILL.md) | Non-negotiable baseline for every admin/list/CRUD/upload page: pagination + search + filters everywhere, type-ahead & tree pickers, destructive-action confirms, preview-before-commit upload flows, menu reachability — plus modern data-grid (TanStack Table v8) + virtualization patterns and a WCAG 2.2 accessibility floor. |
| 3 | [a11y-audit](a11y-audit/SKILL.md) | WCAG 2.2 AA UI-correctness auditor (distinct from aesthetics): automated axe/Lighthouse pass + manual keyboard/screen-reader pass covering focus, ARIA, contrast (both themes), labeled inputs, 24px touch targets, reduced-motion, semantic HTML and the new 2.2 criteria. Report findings; when fixes are requested, repair and re-check. |
| 4 | [secure-code-audit](secure-code-audit/SKILL.md) | Portable, vendor-neutral app-sec pass: secret scan (gitleaks/trufflehog) → dependency/CVE audit (npm/pip/osv/trivy) → SAST (semgrep/bandit/gosec) → manual OWASP Top 10 review (access control, injection, crypto, SSRF, file-upload, multi-tenant) → LLM/AI feature review (prompt injection, tool-call authz, RAG tenancy, output handling, denial-of-wallet). Severity-ranked findings; fixes when requested. Inspect scanner network behavior. |
| 5 | [web-perf-audit](web-perf-audit/SKILL.md) | Runtime Core Web Vitals audit (LCP / INP / CLS) — measure with Lighthouse + DevTools traces + bundle analysis, report the bottleneck; when fixes are requested, repair and re-measure. Data-heavy dashboard playbook (virtualize tables, lazy-load charts, debounce filters). Complements vercel-react-best-practices (source-level rules). |
| 6 | [anti-slop-review](anti-slop-review/SKILL.md) | Fact-check & de-slop content (courses, docs, UI copy): consequential/current claims checked against suitable evidence, delete AI-filler patterns, language/proofreading pass, anonymization before publishing. |
| 7 | [docs-sync](docs-sync/SKILL.md) | Keep PRD, end-user manual, decision log and business-rule docs in sync with shipped reality; styled HTML wired to in-app docs routes, excalidraw diagrams, progress-marked audit docs. |
| 8 | [appstore-review-guard](appstore-review-guard/SKILL.md) | Review current store policies, entitlement/restore states, privacy disclosures, anonymous usable metadata links, screenshot assets, and release-only behavior. Keeps a rejection ledger; does not guarantee acceptance. |
| 9 | [metric-integrity](metric-integrity/SKILL.md) | Correctness audit for every displayed number (KPIs, dashboards, reports): no fabricated multipliers or fake denominators (render `—` + mode discriminator), one source of truth per formula (FE/BE/recon never drift), global filters reach every query block, business-timezone date bucketing, locale-aware formatting, operator-style verification against the source DB. |
| 10 | [backtest-integrity](backtest-integrity/SKILL.md) | Honesty checklist for quant/trading research: "great result = suspect a bug first", correct annualization, point-in-time features (slice equity, never pre-filter data), empirical survivorship testing, costs/capacity, walk-forward OOS + champion/challenger + decay monitoring, auditable provenance (config hash + data fingerprint), promotion gate before live money. |
| 11 | [demo-data-craft](demo-data-craft/SKILL.md) | Convincing, safe demo/seed data in three tiers: masked clone of a real tenant (uniform tokens so joins survive, dynamic table discovery, secrets faked, sensitive-data review), synthetic story-shaped seeds (internally consistent, one idempotent command), capture-time seeding for screenshots — plus env-gated demo forcing (inert by default) and a self-bootstrapping runbook. |
| 12 | [bug-class-audits](bug-class-audits/SKILL.md) | Fix the class, not the instance: when a bug greps to multiple sites, fix them all, append a numbered anti-pattern rule to the canonical AGENTS.md, write a mechanical audit script in `scripts/audit/`, wire it into pre-push/CI, and keep a rule→audit index. Allowlist only with cited justification; baselines only move down. |
| 13 | [interactive-course-builder](interactive-course-builder/SKILL.md) | House standard for interactive HTML courses (single self-contained file, LMS-embedded or standalone): tested `template.html` + full `reference.md` spec — semantic-token design system with per-course themes, **light-default + persisted dark toggle**, responsive 375px→desktop, component kit (lesson cards, SVG diagrams `dgm-*`, images, callouts, comparisons, takeaways ⭐, scenario quizzes ⭐), L1→L5 leveled pedagogy, WCAG 2.2 AA (aria-current, live regions, focus management), framework-free engine with resume/progress/keyboard nav + optional LMS `postMessage` contract. |
| 14 | [senior-operator](senior-operator/SKILL.md) | Cross-project craft handoff: operating manual, per-repo execution maps, and a distill recipe. The canonical `AGENTS.md` wins; `CLAUDE.md` and `GEMINI.md` remain import-only adapters. |
| 15 | [agent-session-backup](agent-session-backup/SKILL.md) | Light backup & restore of Claude Cowork + Claude Code session histories on macOS, filtered to sessions whose `cwd` still exists on this machine. Covers **all three history trees** (`claude-code-sessions`, `local-agent-mode-sessions`, `~/.claude/projects`) via `backup.py`/`restore.py` (dry-run, safe-merge by default), plus `map_account.py` to merge another account's sessions into the current login's active space (the account/space two-level model, verified on Claude Desktop 2.1.x). |
| 16 | [mobile-app-playbook](mobile-app-playbook/SKILL.md) | End-to-end playbook for building & shipping top-chart Android+iOS apps/games, written as a strong-model→weaker-model handoff: numeric quality bar (§0) + model-tier orchestration (§OP), KMP/CMP architecture seams & platform traps, game-feel/UX checklists, retention meta-system ladder, store-policy-proof monetization (Families ads, consent stack, money-correctness matrix), fake-green-proof verification discipline with cold-repo `verify.sh` bootstrap, submission rollout ladder + staged-release dwell rules, ASO (listing, review-prompt policy, localization), LiveOps cadence, and a generalized failure catalog. Fact-checked against Apple/Google primary docs; execution-tested on Sonnet and Opus. |
| 17 | [agent-orchestration](agent-orchestration/SKILL.md) | Astra leads independent workstreams, assigns Terra/Luna workers, reviews evidence, integrates, and owns final quality. Includes scoped briefs, current provider IDs, resumable tracking, bounded escalation, and proportional verification. |
| 18 | [resilient-data-harvest](resilient-data-harvest/SKILL.md) | Data collection that survives reality — per-item checkpointing with a manifest (a dropped connection costs one unit, not the run), human-paced serialized requests with backoff instead of block/CAPTCHA escalation, driving the operator's real logged-in session, schema/volume drift detection against the previous run, a staging quality gate before ingest, and the rule that the harvester updates itself the moment reality changes. Plus migration invariants: preserve identity/timestamps, suppress notifications, dry-run first. |
| 19 | [coding-env-bootstrap](coding-env-bootstrap/SKILL.md) | Reproduce this coding-agent environment on a new/remote machine: `BOOTSTRAP.md` is an agent-executable runbook (toolchain → agent CLIs → skills repo → portable settings → plugins → MCP → secrets protocol → live verification) tiered `[CORE]`/`[DEV]`/`[MAC]` so a production box gets the useful half, not the workstation clone; `AUDIT.md` records the source-machine scan and the changes to make (secrets out of `settings.json`, allowlist instead of blanket dangerous mode, unversioned skill tree, malformed frontmatter). |
| 20 | [skill-miner](skill-miner/SKILL.md) | Mine authorized local histories with source references, exact replay tracking, archive coverage and private digests. Separate scans from semantic review; require recurring procedural evidence across ≥2 projects, prefer existing skills, and preserve the watermark on read failures. |
| 21 | [ref-skills](ref-skills/SKILL.md) | Derive skills from upstream suites and keep them current. Two modes — **wrap** (own ~50 lines that fix upstream's triggering + carry house rules, point at the 1,000–2,000-line original by path; the only workable mode for gstack, which is binary-backed) and **fork** (vendor `.upstream/` as a merge base, `git merge-file --diff3` on upgrade). `refsync.py` does drift detection by fingerprint, merges, validates, and **re-applies the load-out** — necessary because gstack's installer rewrites `~/.claude/skills` with its whole suite on every upgrade and no flag prevents it. |
| 22 | [shipping-changes](shipping-changes/SKILL.md) | Wrap over gstack `ship`. Carries the house rules upstream gets wrong: repository branch/review controls, operator commit identity with no assistant attribution, hooks must pass rather than be skipped, and never pipe a gate through `tail`/`head` (the exit code becomes the pipe's). |
| 23 | [investigating-bugs](investigating-bugs/SKILL.md) | Wrap over gstack `investigate`. Reproduce before editing — never edit code to test a theory, it overwrites the evidence; verify the presupposition first; verify by re-deriving rather than recognising; escalate a repeated shape to `bug-class-audits`. |
| 24 | [browsing-web](browsing-web/SKILL.md) | Wrap over gstack `browse` (compiled binary — wrap is the only possible mode). Uses the selected, available browser with evidence and session discipline. Don't stop to re-confirm an already-open logged-in session; bulk collection hands off to `resilient-data-harvest`. |
| 25 | [web-qa](web-qa/SKILL.md) | Wrap over gstack `qa` + `qa-only` — one job with a mode switch, not two skills. **Report-only is the default**; fixing happens only when asked, and then under the `shipping-changes` house rules. Every finding carries an artifact and is reproduced before it is written down; the scope and tier actually covered are stated, not implied. Routes visual defects to `design-qa`, wrong numbers to `metric-integrity`. Uses the project-approved or user-selected available browser. |
| 26 | [design-qa](design-qa/SKILL.md) | Rendered visual review for text wrapping, collisions, imbalance, inconsistency, and unsupported decoration. Report-only unless fixes are requested; re-render repairs, ship only when authorized. |
| 27 | [delegate-run](delegate-run/SKILL.md) | Carry authorized work through acceptance checks, verification, and handoff with resumable state and proportional delegation. |
| 28 | [autonomous-loops](autonomous-loops/SKILL.md) | Design bounded recurring agent jobs with a trigger, reviewed prompt, hard gate, stop condition, and staged write access. |
| 29 | [dev-env-lifecycle](dev-env-lifecycle/SKILL.md) | Own the lifecycle of everything a run starts. Inventory before starting; one documented `up`/`down`/`status` artifact each; `down` reclaims **all** of it (workers, schedulers, tunnels, sidecars), verified against the port and process tables rather than an exit code; scratch output is ephemeral by default; confirm-with-sizes before deleting anything you did not create, and delete the files, not just the index row. Inverts on a `prod` host: inventory and report only. |
| 30 | [remote-host-access](remote-host-access/SKILL.md) | Diagnose DNS, routes, firewalls, listening sockets, activation, and auth from evidence. Refusal may be a listener or firewall REJECT. Authorized repairs preserve management access and narrow exposure. |
| 31 | [tenant-scope-integrity](tenant-scope-integrity/SKILL.md) | Scope as an argument, not a filter. Five invariants: every write carries an explicit scope; "none selected" is a defined state and never means *all* on a write; scoped writes are constrained at the layer nearest the database; **every uniqueness/upsert/idempotency key is scope-prefixed** (where the cross-tenant overwrite actually happens); the selection is visible and persisted. Ranked failure sites — imports, connectors, jobs and retries, bulk deletes, admin tooling, caches. Covers the write path `metric-integrity` and `secure-code-audit` both miss. |
| 32 | [reference-parity](reference-parity/SKILL.md) | Rebuilding to match an existing artifact: extract the reference's own inventory first — every tab, sub-tab, content type, **state** (empty/partial/error/denied), input and number — turn it into a parity checklist with status + evidence + decision columns, and report progress as a fraction, not as effort. Order of work is the reviewer's order: coverage → content → hierarchy → polish. Deliberate differences are recorded as decisions; the reference is the oracle, and where it looks wrong that is a finding for its owner. |
