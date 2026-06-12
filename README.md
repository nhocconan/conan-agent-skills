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
| 1 | [store-screenshots](store-screenshots/SKILL.md) | Turns raw app screenshots into high-converting App Store / Play Store marketing screenshots — outcome-driven copy (pain → shift → proof → delivery story sequence), branded device-frame graphics generated with the bundled PIL template (`frame_screenshots.py`). |
