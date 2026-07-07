# conan-agent-skills

My personal, reusable [Claude Code agent skills](https://docs.claude.com/en/docs/claude-code/skills).
This repo is the single source of truth; `~/.claude/skills/` only holds symlinks
into it so every skill stays version-controlled here.

## Setup on a new machine

```bash
git clone https://github.com/nhocconan/conan-agent-skills.git ~/.conan-agent-skills
for d in ~/.conan-agent-skills/*/; do ln -sfn "$d" ~/.claude/skills/"$(basename "$d")"; done
```

## Adding a new skill

1. Create `~/.conan-agent-skills/<skill-name>/SKILL.md` (frontmatter: `name`, `description`)
   plus any template scripts/assets next to it.
2. Symlink it: `ln -s ~/.conan-agent-skills/<skill-name> ~/.claude/skills/<skill-name>`
3. Add a row to the index below, commit, push.

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
| 14 | [redacted-operator](redacted-operator/SKILL.md) | Operator handbook for the REDACTED_INTERNAL REDACTED_INTERNAL repo, written as a Fable→Opus model handoff: `EXECUTION-FLOWS.md` (12 flow groups distilled from CLAUDE.md + `scripts/` + ~95 memory files — dev-server lifecycle, verify gates, browser verification, ground-truth metric discipline, org export/import, seeding/demo, connectors/DLQ, Kalodata MI, AI plane, plus a symptom→cause trap table) + `OPERATING-MANUAL.md` (project-agnostic craft: read the real ask, decompose along verification lines, risk = blast radius × silence, verify by re-derivation, known-vs-guessed labeling, attack your own conclusion, answer-first communication, false-competence tells, 5-question self-test). CLAUDE.md always wins on conflict. |
