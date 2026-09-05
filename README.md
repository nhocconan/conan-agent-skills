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

The skills themselves are plain Markdown and name no harness-specific tool, so a skill
written here works in all three. Only the install path differs.

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
Production box that must stay headless: pass `--profile core` instead of `auto`.

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

impeccable installs its own per-harness trees (`.claude/`, `.agents/`, `.gemini/`, and a
dozen more) and is therefore listed in [`ref-skills/loadouts/keep.txt`](ref-skills/loadouts/keep.txt),
which the load-out neither creates nor removes. `refsync.py upgrade` / `ensure` is what
runs `npx impeccable install --yes --global` — do not run that installer by hand.

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
| 13 | [interactive-course-builder](interactive-course-builder/SKILL.md) | House standard for interactive HTML courses (single self-contained file, LMS-embedded or standalone): tested `template.html` + full `reference.md` spec — semantic-token design system with per-course themes, **light-default + persisted dark toggle**, responsive 375px→desktop, component kit (lesson cards, SVG diagrams `dgm-*`, images, callouts, comparisons, takeaways ⭐, scenario quizzes ⭐), L1→L5 leveled pedagogy, WCAG 2.2 AA (aria-current, live regions, focus management), framework-free engine with resume/progress/keyboard nav + optional LMS `postMessage` contract. |
| 14 | [senior-operator](senior-operator/SKILL.md) | Cross-project senior-operator playbook — a Fable→Opus model handoff that works in ANY repo: `OPERATING-MANUAL.md` (project-agnostic craft: read the real ask, decompose along verification lines, risk = blast radius × silence, verify by re-derivation, known-vs-guessed labeling, attack your own conclusion, answer-first communication, false-competence tells, 5-question self-test), `projects/<slug>.md` per-repo execution-flow maps (commands, gates, ground truth, symptom→cause trap tables — distilled from each repo's rulebook + `scripts/` + session memory), and `DISTILL.md` (the recipe for generating a new project map, so the strongest model available keeps training the next one). The repo's own CLAUDE.md always wins on conflict. |
| 15 | [agent-session-backup](agent-session-backup/SKILL.md) | Light backup & restore of Claude Cowork + Claude Code session histories on macOS, filtered to sessions whose `cwd` still exists on this machine. Covers **all three history trees** (`claude-code-sessions`, `local-agent-mode-sessions`, `~/.claude/projects`) via `backup.py`/`restore.py` (dry-run, safe-merge by default), plus `map_account.py` to merge another account's sessions into the current login's active space (the account/space two-level model, verified on Claude Desktop 2.1.x). |
| 16 | [mobile-app-playbook](mobile-app-playbook/SKILL.md) | End-to-end playbook for building & shipping top-chart Android+iOS apps/games, written as a strong-model→weaker-model handoff: numeric quality bar (§0) + model-tier orchestration (§OP), KMP/CMP architecture seams & platform traps, game-feel/UX checklists, retention meta-system ladder, store-policy-proof monetization (Families ads, consent stack, money-correctness matrix), fake-green-proof verification discipline with cold-repo `verify.sh` bootstrap, submission rollout ladder + staged-release dwell rules, ASO (listing, review-prompt policy, localization), LiveOps cadence, and a generalized failure catalog. Fact-checked against Apple/Google primary docs; execution-tested on Sonnet and Opus. |
| 17 | [agent-orchestration](agent-orchestration/SKILL.md) | How a lead model runs a fleet — **parallel-first by default** (everything runs concurrently until a *data* dependency proves otherwise; waves launched in one message; pipeline over barrier), a role→tier routing table across model families and lineages (effort dial before tier bump; Codex/agy for independent red-team), the delegation test (can't write the acceptance check ⇒ can't delegate), the brief-as-contract, a quality gate that never trusts a green claim (exit-code/`tail` trap, artifact rule, fresh-context verifiers scored 1–10 with a discard-below-8 default, diverse lenses with security+perf always on, fingerprint dedup, loop-until-dry, completeness critic), the **integration protocol** the merge actually needs (seam contracts fixed before fan-out, one writer per file, combined-diff coherence pass, one full gate on the merged tree), a live plan file + fleet ledger so progress and quality are trackable and resumable, and the escalation ladder back **up** after two failed attempts. Companions: `FANOUT-PATTERNS.md` (Agent tool, opt-in Workflow scripts, worktrees, cross-CLI) and `TEMPLATES.md` (brief, schemas, verifier prompt, ledger, report). |
| 18 | [resilient-data-harvest](resilient-data-harvest/SKILL.md) | Data collection that survives reality — per-item checkpointing with a manifest (a dropped connection costs one unit, not the run), human-paced serialized requests with backoff instead of block/CAPTCHA escalation, driving the operator's real logged-in session, schema/volume drift detection against the previous run, a staging quality gate before ingest, and the rule that the harvester updates itself the moment reality changes. Plus migration invariants: preserve identity/timestamps, suppress notifications, dry-run first. |
| 19 | [coding-env-bootstrap](coding-env-bootstrap/SKILL.md) | Reproduce this coding-agent environment on a new/remote machine: `BOOTSTRAP.md` is an agent-executable runbook (toolchain → agent CLIs → skills repo → portable settings → plugins → MCP → secrets protocol → live verification) tiered `[CORE]`/`[DEV]`/`[MAC]` so a production box gets the useful half, not the workstation clone; `AUDIT.md` records the source-machine scan and the changes to make (secrets out of `settings.json`, allowlist instead of blanket dangerous mode, unversioned skill tree, malformed frontmatter). |
| 20 | [skill-miner](skill-miner/SKILL.md) | Mine local agent history (Claude Code + Cowork + Codex) for pain that deserves to be a skill — `mine_history.py` scans incrementally against a stored watermark (`--full` / `--since` / `--commit`), emits a digest of human turns, corrections, procedures and changed memory files; the SKILL then applies the four-part bar (recurring ≥2 projects · generalizable · procedural · not already covered), folds near-misses into existing skills, and records rejections so the next run re-litigates nothing. Ships `validate_skills.py`, which encodes Anthropic's authoring spec (frontmatter delimiter, `name` = directory + no reserved words, ≤1024-char description, ≤500-line body, one-level references) — the errors it catches make a skill silently untriggerable. |
| 21 | [ref-skills](ref-skills/SKILL.md) | Derive skills from upstream suites and keep them current. Two modes — **wrap** (own ~50 lines that fix upstream's triggering + carry house rules, point at the 1,000–2,000-line original by path; the only workable mode for gstack, which is binary-backed) and **fork** (vendor `.upstream/` as a merge base, `git merge-file --diff3` on upgrade). `refsync.py` does drift detection by fingerprint, merges, validates, and **re-applies the load-out** — necessary because gstack's installer rewrites `~/.claude/skills` with its whole suite on every upgrade and no flag prevents it. |
| 22 | [shipping-changes](shipping-changes/SKILL.md) | Wrap over gstack `ship`. Carries the house rules upstream gets wrong: main only (never a feature branch), operator commit identity with no assistant attribution, hooks must pass rather than be skipped, and never pipe a gate through `tail`/`head` (the exit code becomes the pipe's). |
| 23 | [investigating-bugs](investigating-bugs/SKILL.md) | Wrap over gstack `investigate`. Reproduce before editing — never edit code to test a theory, it overwrites the evidence; verify the presupposition first; verify by re-deriving rather than recognising; escalate a repeated shape to `bug-class-audits`. |
| 24 | [browsing-web](browsing-web/SKILL.md) | Wrap over gstack `browse` (compiled binary — wrap is the only possible mode). The sanctioned browser path; never the Chrome MCP. Don't stop to re-confirm an already-open logged-in session; bulk collection hands off to `resilient-data-harvest`. |
| 25 | [web-qa](web-qa/SKILL.md) | Wrap over gstack `qa` + `qa-only` — one job with a mode switch, not two skills. **Report-only is the default**; fixing happens only when asked, and then under the `shipping-changes` house rules. Every finding carries an artifact and is reproduced before it is written down; the scope and tier actually covered are stated, not implied. Routes visual defects to `design-review`, wrong numbers to `metric-integrity`. One browser stack (gstack `browse`) — never the Chrome MCP, never `agent-browser`. |
| 26 | [design-qa](design-qa/SKILL.md) | Wrap over gstack `design-review` — the visual lens `web-qa` doesn't cover. Carries the six recurring defect classes drawn from real reports (text wrapping/dropping lines, content not using its width, chart/text collisions, layout imbalance, cross-page inconsistency, AI-slop layout), and the rule that both themes **and** 375px get checked. Fixing is in scope, under `shipping-changes` house rules. |
| 28 | [dev-env-lifecycle](dev-env-lifecycle/SKILL.md) | Own the lifecycle of everything a run starts. Inventory before starting; one documented `up`/`down`/`status` artifact each; `down` reclaims **all** of it (workers, schedulers, tunnels, sidecars), verified against the port and process tables rather than an exit code; scratch output is ephemeral by default; confirm-with-sizes before deleting anything you did not create, and delete the files, not just the index row. Inverts on a `prod` host: inventory and report only. |
| 29 | [remote-host-access](remote-host-access/SKILL.md) | The "I opened the port and it still won't connect" ladder, descended one rung at a time: read the failure (timeout = dropped, refused = nothing bound — never edit a firewall for a refusal) → resolution → TCP path from two networks → the perimeter you cannot see from inside (cloud SG, hypervisor firewall) → which host firewall is actually in charge (iptables-as-nft shim, front-ends that regenerate rules, chain order, zero packet counters) → bind address → socket-activated units → the app's own allowlist and its ban daemon. Plus durable remote agent sessions (multiplexer + auto-reconnect + keepalive). |
| 30 | [tenant-scope-integrity](tenant-scope-integrity/SKILL.md) | Scope as an argument, not a filter. Five invariants: every write carries an explicit scope; "none selected" is a defined state and never means *all* on a write; scoped writes are constrained at the layer nearest the database; **every uniqueness/upsert/idempotency key is scope-prefixed** (where the cross-tenant overwrite actually happens); the selection is visible and persisted. Ranked failure sites — imports, connectors, jobs and retries, bulk deletes, admin tooling, caches. Covers the write path `metric-integrity` and `secure-code-audit` both miss. |
| 31 | [reference-parity](reference-parity/SKILL.md) | Rebuilding to match an existing artifact: extract the reference's own inventory first — every tab, sub-tab, content type, **state** (empty/partial/error/denied), input and number — turn it into a parity checklist with status + evidence + decision columns, and report progress as a fraction, not as effort. Order of work is the reviewer's order: coverage → content → hierarchy → polish. Deliberate differences are recorded as decisions; the reference is the oracle, and where it looks wrong that is a finding for its owner. |
| 27 | [delegate-run](delegate-run/SKILL.md) | Three-touchpoint contract for a fully-delegated single-agent run: acceptance checks + plan file before any edit, plan gate only for risky work, no mid-run questions (assumptions logged, batched to the exit report), every claim audited against a tool result, fixed exit-report format, and a trust ledger — three consecutive clean runs in a task class lets the operator drop that class's plan gate. Solo counterpart to `agent-orchestration` (fleets) and `autonomous-loops` (recurring jobs). |
