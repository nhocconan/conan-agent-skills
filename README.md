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
| 1 | [store-screenshots](store-screenshots/SKILL.md) | Turns raw app screenshots into high-converting App Store / Play Store marketing screenshots **and App Preview videos** — outcome-driven copy (pain → shift → proof → delivery story sequence), simulator/emulator capture recipes (`-uiScreenshots` debug arg pattern), branded device-frame graphics (`store_frames.py` + `example_screenshots.py`) and a Ken Burns 886×1920 preview-video template (`preview_video.py`, verified Apple spec incl. required stereo AAC track). |
| 2 | [admin-crud-standards](admin-crud-standards/SKILL.md) | Non-negotiable baseline for every admin/list/CRUD/upload page: pagination + search + filters everywhere, type-ahead & tree pickers, destructive-action confirms, preview-before-commit upload flows, menu reachability — plus modern data-grid (TanStack Table v8) + virtualization patterns and a WCAG 2.2 accessibility floor. |
| 3 | [a11y-audit](a11y-audit/SKILL.md) | WCAG 2.2 AA UI-correctness auditor (distinct from aesthetics): automated axe/Lighthouse pass + manual keyboard/screen-reader pass covering focus, ARIA, contrast (both themes), labeled inputs, 24px touch targets, reduced-motion, semantic HTML and the new 2.2 criteria. Run → fix → re-check. |
| 4 | [secure-code-audit](secure-code-audit/SKILL.md) | Portable, vendor-neutral app-sec pass: secret scan (gitleaks/trufflehog) → dependency/CVE audit (npm/pip/osv/trivy) → SAST (semgrep/bandit/gosec) → manual OWASP Top 10 review (access control, injection, crypto, SSRF, file-upload, multi-tenant). Severity-ranked findings + fixes, all local tools. |
| 5 | [web-perf-audit](web-perf-audit/SKILL.md) | Runtime Core Web Vitals audit (LCP / INP / CLS) — measure with Lighthouse + DevTools traces + bundle analysis, fix the biggest bottleneck, re-measure. Data-heavy dashboard playbook (virtualize tables, lazy-load charts, debounce filters). Complements vercel-react-best-practices (source-level rules). |
| 6 | [anti-slop-review](anti-slop-review/SKILL.md) | Fact-check & de-slop content (courses, docs, UI copy): every number/link verified against live sources, delete AI-filler patterns, language/proofreading pass, anonymization before publishing. |
| 7 | [docs-sync](docs-sync/SKILL.md) | Keep PRD, end-user manual, decision log and business-rule docs in sync with shipped reality; styled HTML wired to in-app docs routes, excalidraw diagrams, progress-marked audit docs. |
