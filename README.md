# conan-agent-skills

My personal, reusable Claude Code and Codex agent skills. This repo is the single source
of truth. Claude loads the curated symlinks under `~/.claude/skills`; Codex loads them
under its documented user scope, `~/.agents/skills`. "Installed" and "active" are
deliberately separate, because upstream suites install far more than should be competing
for the model's attention.

👉 **[MANUAL.md](MANUAL.md) — start here** (tiếng Việt): what's here, what fires when,
how to upgrade, how to roll back.

## Setup on a new machine

```bash
git clone https://github.com/nhocconan/conan-agent-skills.git ~/.conan-agent-skills
python3 ~/.conan-agent-skills/coding-env-bootstrap/harness.py \
  apply --target both --profile core --with-mcp
```

Full runbook (toolchain, agent CLIs, plugins, MCP, secrets):
[`coding-env-bootstrap/BOOTSTRAP.md`](coding-env-bootstrap/BOOTSTRAP.md).

## Upgrading everything

```bash
python3 ~/.conan-agent-skills/ref-skills/refsync.py upgrade
```

Do **not** run an upstream installer (`/gstack-upgrade`) directly — it rewrites
`~/.claude/skills` with its whole suite. See [`ref-skills`](ref-skills/SKILL.md).

## Adding a new skill

1. Create `<skill-name>/SKILL.md` (frontmatter: `name` matching the directory,
   `description` that states what **and when**), plus any scripts/assets beside it.
2. Add the name to the relevant file under `ref-skills/loadouts/` (and to
   [`ref-skills/loadout.txt`](ref-skills/loadout.txt) for the Claude workstation), then
   run `refsync.py loadout --target <claude|codex> --profile <name> --apply`.
3. **Validate** — `python3 skill-miner/validate_skills.py`. Errors here make a skill
   silently untriggerable.
4. Add a row to the index below, commit, push.

Deriving from someone else's skill instead? Read [`ref-skills`](ref-skills/SKILL.md) —
wrap by default, fork only when you mean to diverge.

## Skill index

| # | Skill | What it does |
|---|---|---|
| 1 | [store-screenshots](store-screenshots/SKILL.md) | Turns raw app screenshots into high-converting App Store / Play Store marketing screenshots **and App Preview videos** — outcome-driven copy (pain → shift → proof → delivery story sequence), simulator/emulator capture recipes (`-uiScreenshots` debug arg pattern), branded device-frame graphics (`store_frames.py` + `example_screenshots.py`) and a full-bleed 886×1920 preview-video pipeline (`preview_core.py` + `preview_clips.py` + `example_preview.py`, verified Apple spec incl. required stereo AAC track). |
| 2 | [admin-crud-standards](admin-crud-standards/SKILL.md) | Non-negotiable baseline for every admin/list/CRUD/upload page: pagination + search + filters everywhere, type-ahead & tree pickers, destructive-action confirms, preview-before-commit upload flows, menu reachability — plus modern data-grid (TanStack Table v8) + virtualization patterns and a WCAG 2.2 accessibility floor. |
| 3 | [a11y-audit](a11y-audit/SKILL.md) | WCAG 2.2 AA UI-correctness auditor (distinct from aesthetics): automated axe/Lighthouse pass + manual keyboard/screen-reader pass covering focus, ARIA, contrast (both themes), labeled inputs, 24px touch targets, reduced-motion, semantic HTML and the new 2.2 criteria. Run → fix → re-check. |
| 4 | [secure-code-audit](secure-code-audit/SKILL.md) | Portable, vendor-neutral app-sec pass: secret scan (gitleaks/trufflehog) → dependency/CVE audit (npm/pip/osv/trivy) → SAST (semgrep/bandit/gosec) → manual OWASP Top 10 review (access control, injection, crypto, SSRF, file-upload, multi-tenant) → LLM/AI feature review (prompt injection, tool-call authz, RAG tenancy, output handling, denial-of-wallet). Severity-ranked findings + fixes, all local tools. |
| 5 | [web-perf-audit](web-perf-audit/SKILL.md) | Runtime Core Web Vitals audit (LCP / INP / CLS) — measure with Lighthouse + DevTools traces + bundle analysis, fix the biggest bottleneck, re-measure. Data-heavy dashboard playbook (virtualize tables, lazy-load charts, debounce filters). Complements vercel-react-best-practices (source-level rules). |
| 6 | [anti-slop-review](anti-slop-review/SKILL.md) | Fact-check & de-slop content (courses, docs, UI copy): every number/link verified against live sources, delete AI-filler patterns, language/proofreading pass, anonymization before publishing. |
| 7 | [docs-sync](docs-sync/SKILL.md) | Keep PRD, end-user manual, decision log and business-rule docs in sync with shipped reality; styled HTML wired to in-app docs routes, excalidraw diagrams, progress-marked audit docs. |
| 8 | [appstore-review-guard](appstore-review-guard/SKILL.md) | Pre-submission compliance gate that prevents repeat App Store / Play rejections. A growing **rejection ledger** (real rejections + their fixes) + a checklist by guideline area: Restore Purchases reachable in every entitlement state (3.1.1), full-bleed no-frame preview video (2.3.4), metadata links that return HTTP 200 anonymously, privacy label matches the binary (5.1), background modes ↔ real BG tasks (2.5.4), debug/QA hooks gated out of release (2.3.1) — plus a Google Play checklist (Play Protect: R8/ProGuard, v2+ signing, permissions; data safety form). Run before every submit, enrich after every rejection. Complements `store-screenshots` (assets/copy). |
| 9 | [metric-integrity](metric-integrity/SKILL.md) | Correctness audit for every displayed number (KPIs, dashboards, reports): no fabricated multipliers or fake denominators (render `—` + mode discriminator), one source of truth per formula (FE/BE/recon never drift), global filters reach every query block, business-timezone date bucketing, locale-aware formatting, operator-style verification against the source DB. |
| 10 | [backtest-integrity](backtest-integrity/SKILL.md) | Honesty checklist for quant/trading research: "great result = suspect a bug first", correct annualization, point-in-time features (slice equity, never pre-filter data), empirical survivorship testing, costs/capacity, walk-forward OOS + champion/challenger + decay monitoring, auditable provenance (config hash + data fingerprint), promotion gate before live money. |
| 11 | [demo-data-craft](demo-data-craft/SKILL.md) | Convincing, safe demo/seed data in three tiers: masked clone of a real tenant (uniform tokens so joins survive, dynamic table discovery, secrets faked, zero-residue verification), synthetic story-shaped seeds (internally consistent, one idempotent command), capture-time seeding for screenshots — plus env-gated demo forcing (inert by default) and a self-bootstrapping runbook. |
| 12 | [bug-class-audits](bug-class-audits/SKILL.md) | Fix the class, not the instance: when a bug greps to multiple sites, fix them all, append a numbered anti-pattern rule to CLAUDE.md, write a mechanical audit script in `scripts/audit/`, wire it into pre-push/CI, and keep a rule→audit index. Allowlist only with cited justification; baselines only move down. |
| 13 | [interactive-course-builder](interactive-course-builder/SKILL.md) | House standard for world-class interactive HTML courses (single self-contained file, LMS-embedded or standalone): tested `template.html` + full `reference.md` spec — semantic-token design system with per-course themes, **light-default + persisted dark toggle**, responsive 375px→desktop, component kit (lesson cards, SVG diagrams `dgm-*`, images, callouts, comparisons, takeaways ⭐, scenario quizzes ⭐), L1→L5 leveled pedagogy, WCAG 2.2 AA (aria-current, live regions, focus management), framework-free engine with resume/progress/keyboard nav + optional LMS `postMessage` contract. |
| 14 | [senior-operator](senior-operator/SKILL.md) | Cross-project senior-operator playbook — a Fable→Opus model handoff that works in ANY repo: `OPERATING-MANUAL.md` (project-agnostic craft: read the real ask, decompose along verification lines, risk = blast radius × silence, verify by re-derivation, known-vs-guessed labeling, attack your own conclusion, answer-first communication, false-competence tells, 5-question self-test), `projects/<slug>.md` per-repo execution-flow maps (commands, gates, ground truth, symptom→cause trap tables — distilled from each repo's rulebook + `scripts/` + session memory), and `DISTILL.md` (the recipe for generating a new project map, so the strongest model available keeps training the next one). The repo's own CLAUDE.md always wins on conflict. |
| 15 | [agent-session-backup](agent-session-backup/SKILL.md) | Light backup & restore of Claude Cowork + Claude Code session histories on macOS, filtered to sessions whose `cwd` still exists on this machine. Covers **all three history trees** (`claude-code-sessions`, `local-agent-mode-sessions`, `~/.claude/projects`) via `backup.py`/`restore.py` (dry-run, safe-merge by default), plus `map_account.py` to merge another account's sessions into the current login's active space (the account/space two-level model, verified on Claude Desktop 2.1.x). |
| 16 | [world-class-mobile-app](world-class-mobile-app/SKILL.md) | End-to-end playbook for building & shipping top-chart Android+iOS apps/games, written as a strong-model→weaker-model handoff: numeric quality bar (§0) + model-tier orchestration (§OP), KMP/CMP architecture seams & platform traps, game-feel/UX checklists, retention meta-system ladder, store-policy-proof monetization (Families ads, consent stack, money-correctness matrix), fake-green-proof verification discipline with cold-repo `verify.sh` bootstrap, submission rollout ladder + staged-release dwell rules, ASO (listing, review-prompt policy, localization), LiveOps cadence, and a generalized failure catalog. Fact-checked against Apple/Google primary docs; execution-tested on Sonnet and Opus. |
| 17 | [agent-orchestration](agent-orchestration/SKILL.md) | How a lead model runs a fleet — the tier table (decide/review/verify/tricky-10% stays at the top, everything else delegates), the delegation test (can't write the acceptance check ⇒ can't delegate), the handoff-brief contract, never trusting a green claim (never pipe a build through `tail` — the exit code becomes the pipe's), checkpointed plan files so a dead session loses nothing, don't-stop-in-the-middle, parallelizing along verification seams, and the escalation ladder back **up** after two failed attempts. |
| 18 | [resilient-data-harvest](resilient-data-harvest/SKILL.md) | Data collection that survives reality — per-item checkpointing with a manifest (a dropped connection costs one unit, not the run), human-paced serialized requests with backoff instead of block/CAPTCHA escalation, driving the operator's real logged-in session, schema/volume drift detection against the previous run, a staging quality gate before ingest, and the rule that the harvester updates itself the moment reality changes. Plus migration invariants: preserve identity/timestamps, suppress notifications, dry-run first. |
| 19 | [coding-env-bootstrap](coding-env-bootstrap/SKILL.md) | Reproduce this coding-agent environment on a new/remote machine: `BOOTSTRAP.md` is an agent-executable runbook (toolchain → agent CLIs → skills repo → portable settings → plugins → MCP → secrets protocol → live verification) tiered `[CORE]`/`[DEV]`/`[MAC]` so a production box gets the useful half, not the workstation clone; `AUDIT.md` records the source-machine scan and the changes to make (secrets out of `settings.json`, allowlist instead of blanket dangerous mode, unversioned skill tree, malformed frontmatter). |
| 20 | [skill-miner](skill-miner/SKILL.md) | Mine local agent history (Claude Code + Cowork + Codex) for pain that deserves to be a skill — `mine_history.py` scans incrementally against a stored watermark (`--full` / `--since` / `--commit`), emits a digest of human turns, corrections, procedures and changed memory files; the SKILL then applies the four-part bar (recurring ≥2 projects · generalizable · procedural · not already covered), folds near-misses into existing skills, and records rejections so the next run re-litigates nothing. Ships `validate_skills.py`, which encodes Anthropic's authoring spec (frontmatter delimiter, `name` = directory + no reserved words, ≤1024-char description, ≤500-line body, one-level references) — the errors it catches make a skill silently untriggerable. |
| 21 | [ref-skills](ref-skills/SKILL.md) | Derive skills from upstream suites and keep them current. Two modes — **wrap** (own ~50 lines that fix upstream's triggering + carry house rules, point at the 1,000–2,000-line original by path; the only workable mode for gstack, which is binary-backed) and **fork** (vendor `.upstream/` as a merge base, `git merge-file --diff3` on upgrade). `refsync.py` does drift detection by fingerprint, merges, validates, and **re-applies the load-out** — necessary because gstack's installer rewrites `~/.claude/skills` with its whole suite on every upgrade and no flag prevents it. |
| 22 | [shipping-changes](shipping-changes/SKILL.md) | Wrap over gstack `ship`. Carries the house rules upstream gets wrong: main only (never a feature branch), operator commit identity with no assistant attribution, hooks must pass rather than be skipped, and never pipe a gate through `tail`/`head` (the exit code becomes the pipe's). |
| 23 | [investigating-bugs](investigating-bugs/SKILL.md) | Wrap over gstack `investigate`. Reproduce before editing — never edit code to test a theory, it overwrites the evidence; verify the presupposition first; verify by re-deriving rather than recognising; escalate a repeated shape to `bug-class-audits`. |
| 24 | [browsing-web](browsing-web/SKILL.md) | Wrap over gstack `browse` (compiled binary — wrap is the only possible mode). The sanctioned browser path; never the Chrome MCP. Don't stop to re-confirm an already-open logged-in session; bulk collection hands off to `resilient-data-harvest`. |
| 25 | [web-qa](web-qa/SKILL.md) | Wrap over gstack `qa` + `qa-only` — one job with a mode switch, not two skills. **Report-only is the default**; fixing happens only when asked, and then under the `shipping-changes` house rules. Every finding carries an artifact and is reproduced before it is written down; the scope and tier actually covered are stated, not implied. Routes visual defects to `design-review`, wrong numbers to `metric-integrity`. One browser stack (gstack `browse`) — never the Chrome MCP, never `agent-browser`. |
| 26 | [design-qa](design-qa/SKILL.md) | Wrap over gstack `design-review` — the visual lens `web-qa` doesn't cover. Carries the six recurring defect classes drawn from real reports (text wrapping/dropping lines, content not using its width, chart/text collisions, layout imbalance, cross-page inconsistency, AI-slop layout), and the rule that both themes **and** 375px get checked. Fixing is in scope, under `shipping-changes` house rules. |
