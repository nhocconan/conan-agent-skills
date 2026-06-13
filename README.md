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
| 2 | [verify-before-done](verify-before-done/SKILL.md) | Mandatory self-QA before claiming any web task done: start dev, walk changed pages in a real browser, run the recurring-bug checklist (dark/light, filters, date pickers, i18n, pagination), run the prod build, report with screenshots. |
| 3 | [prod-deploy-docker](prod-deploy-docker/SKILL.md) | Deploy readiness + step-by-step guide for Docker Compose prod behind Traefik: prod-image build check, safe migrations, data-safety guards, copy-pasteable `pull → build → down → up` block, explicit "rebuild required" warnings. |
| 4 | [excel-data-reconcile](excel-data-reconcile/SKILL.md) | Reconcile system numbers vs customer Excel/PPTX (GMV/NMV-style): freeze formulas into FORMULA-REFERENCE.md with cell-level citations, independent recompute script, per-day per-platform 3-way comparison, safe Excel generation that opens in MS365. |
| 5 | [admin-crud-standards](admin-crud-standards/SKILL.md) | Non-negotiable baseline for every admin/list/CRUD/upload page: pagination + search + filters everywhere, type-ahead & tree pickers, destructive-action confirms, preview-before-commit upload flows, menu reachability. |
| 6 | [anti-slop-review](anti-slop-review/SKILL.md) | Fact-check & de-slop content (courses, docs, UI copy): every number/link verified against live sources, delete AI-filler patterns, Vietnamese proofreading, anonymization before publishing. |
| 7 | [repo-hygiene-scrub](repo-hygiene-scrub/SKILL.md) | Repo secret/privacy hygiene: stack-aware .gitignore (private/, refs/, .playwright-mcp, logs), secret scanning before going public, and the emergency git-history rewrite procedure when something sensitive was pushed. |
| 8 | [git-rescue](git-rescue/SKILL.md) | Standard recovery for "git pull failed" / conflicts / hook rejections on a solo-dev-on-main workflow: protect local work first, merge (not rebase), regenerate lockfiles, verify the app still starts, push under Tien Le. |
| 9 | [docs-sync](docs-sync/SKILL.md) | Keep PRD, Vietnamese user manual, decision log and formula docs in sync with shipped reality; styled HTML wired to /prd and /manual routes, excalidraw diagrams, progress-marked audit docs. |
