# How to restore this backup

This folder is a **light backup** of Claude session history, filtered to only
sessions whose working folder existed on the source machine.

```
Claude-Code/     -> restores to  ~/.claude/projects/
Claude-Cowork/   -> restores to  ~/Library/Application Support/Claude/claude-code-sessions/
MANIFEST.txt     -> what was kept / skipped, with sizes
```

## Restore with the helper script (recommended)

The script lives in the reusable skill at
`~/.conan-agent-skills/claude-cowork-backup-restore/scripts/restore.py`.

```bash
# 1. Quit the Claude Desktop / Cowork app first.
# 2. Dry-run to preview (copies nothing):
python3 ~/.conan-agent-skills/claude-cowork-backup-restore/scripts/restore.py "<THIS_FOLDER>" --dry-run

# 3. Real restore (safe: never overwrites existing live files):
python3 ~/.conan-agent-skills/claude-cowork-backup-restore/scripts/restore.py "<THIS_FOLDER>"

# Overwrite existing files instead of skipping them:
#   ... restore.py "<THIS_FOLDER>" --force

# 4. Relaunch Claude Desktop so it re-indexes. Claude Code picks up on next run.
```

## Restore manually (no script)

```bash
# Cowork sessions
rsync -av "<THIS_FOLDER>/Claude-Cowork/"  "$HOME/Library/Application Support/Claude/claude-code-sessions/"
# Claude Code sessions
rsync -av "<THIS_FOLDER>/Claude-Code/"    "$HOME/.claude/projects/"
```

(Add `--ignore-existing` to rsync to avoid overwriting live files.)

## Notes
- Cowork `<workspace-id>` folders are per-install UUIDs; restoring them verbatim
  works because the app scans the dir and reads `cwd` from each JSON file.
- A session only *resumes* if its `cwd` path also exists on this machine; the
  history is preserved either way.
- Backup date and full contents are listed in `MANIFEST.txt`.
