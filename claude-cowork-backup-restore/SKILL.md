---
name: claude-cowork-backup-restore
description: Light backup & restore of Claude Cowork + Claude Code session histories on macOS, filtered to only sessions whose working folder still exists on THIS machine (drops sessions mixed in from other machines / deleted worktrees). Copies just the history files (.jsonl / local_*.json) — no caches, VM images, or binaries. Trigger when the user asks to "backup Claude sessions", "backup Cowork", "backup Claude Code history", "restore my Claude sessions", "sao lưu session Claude", "backup light", or wants to move Claude session history between machines.
---

# Claude Cowork / Claude Code — light backup & restore

Backs up the two places Claude stores conversation history on macOS, keeping the
folders separate and **filtering to only sessions that belong to this machine**.

## Where the data lives (macOS)

| App | Path | History file |
|---|---|---|
| **Claude Cowork** (local agent mode in Claude Desktop) | `~/Library/Application Support/Claude/claude-code-sessions/<workspace-id>/<session-id>/` | `local_*.json` |
| **Claude Code** (CLI) | `~/.claude/projects/<slug>/` | `*.jsonl` |

Each history file records the session's `cwd` (working directory). That field is
the filter key.

## The filter rule (the whole point)

> Keep a session **only if its `cwd` still exists as a folder on this machine.**

Claude Desktop syncs session lists across machines, so the local store gets
polluted with sessions whose project folders live on *another* machine, plus
stale `.claude/worktrees/…` dirs that were already deleted. Filtering by
"cwd exists here" cleanly keeps only the sessions that are actually yours on this
box. Cowork reads `cwd`/`originCwd` from each JSON; Claude Code reads `cwd` from
the first line of each `.jsonl`.

"Light" = copy only the history files. No `~/Library/Caches`, no `claude-code-vm`,
no `Session Storage`, no binaries.

## Backup

```bash
python3 scripts/backup.py [DEST_DIR]
# DEST_DIR defaults to ~/Claude_Light_Backup_<YYYYMMDD>
```

Produces:

```
DEST_DIR/
  Claude-Code/     <slug>/*.jsonl              (kept projects only)
  Claude-Cowork/   <ws-id>/<sess-id>/local_*.json  (kept sessions only)
  MANIFEST.txt     full kept/skipped list + sizes
  RESTORE.md       restore instructions (copied from RESTORE_TEMPLATE.md)
```

Structure is preserved verbatim so restore is a straight mirror-back. Review
`MANIFEST.txt` to confirm the KEEP/SKIP split looks right before relying on it.

## Restore

```bash
python3 scripts/restore.py SRC_DIR [--dry-run] [--force]
```

- Mirrors `Claude-Cowork/` back to `~/Library/Application Support/Claude/claude-code-sessions/`
  and `Claude-Code/` back to `~/.claude/projects/`.
- **Safe by default**: never overwrites an existing live file (merge/skip). Use
  `--force` to overwrite. Always dry-run first: `--dry-run`.
- **Quit the Claude Desktop / Cowork app before restoring**, then relaunch so it
  re-indexes. Claude Code picks sessions up on next launch.

### Cross-machine notes
- The Cowork `<workspace-id>` folders are per-install UUIDs. Restoring the UUID
  folders verbatim works because the app scans the directory and reads `cwd` from
  each file; it does not depend on the UUID matching the new install.
- A restored session only resumes meaningfully if its `cwd` also exists on the
  target machine (same absolute path). History is preserved regardless.
- This repo (`~/.conan-agent-skills`) is git-synced, so this skill travels with
  you — run `backup.py` on the source machine, copy `DEST_DIR` across, run
  `restore.py` on the target.

## Account mapping (make another account's sessions visible under the current login)

Claude Desktop shows **only** the sessions of the currently-logged-in account.
The on-disk model is **two levels** — `account / space / session` (verified on
Claude Desktop 2.1.x, macOS):

```
~/Library/Application Support/Claude/
    claude-code-sessions/<ACCOUNT-UUID>/<SPACE-UUID>/local_*.json
    local-agent-mode-sessions/<ACCOUNT-UUID>/<SPACE-UUID>/local_*.json (+ session dirs)
```

- **`<ACCOUNT-UUID>`** = the account. Current login = `lastKnownAccountUuid` in
  `config.json`.
- **`<SPACE-UUID>`** = a "space" inside that account. Each account has its **own**
  space id, and the app lists sessions from the account's **active space** (the
  one it most recently wrote to). ⚠️ Sessions placed under the right account but a
  **different space id will NOT show** — this is the trap. You must merge into the
  target account's *active space*.

So to move account A → account B, merge A's session files into **B's active space
folder**, in both trees. `scripts/map_account.py` does exactly that:

```bash
# 1. Identify accounts + spaces (counts, latest activity, active-space, titles):
python3 scripts/map_account.py --list

# 2. Preview merging a source account's sessions into the CURRENT login's active space:
python3 scripts/map_account.py --from <SRC_ACCOUNT_UUID> --dry-run
#    (--to defaults to lastKnownAccountUuid; target's active space auto-detected)

# 3. Do it — COPY by default (source account keeps its sessions):
python3 scripts/map_account.py --from <SRC_ACCOUNT_UUID>
#    Relocate instead (remove from source):  ... --from <SRC> --move
#    Force a specific target space:           ... --from <SRC> --to-space <SPACE-UUID>

# 4. Fully quit (Cmd+Q) and relaunch Claude Desktop so it re-indexes.
```

Notes:
- **The email↔UUID map is NOT on disk** (oauth tokens are encrypted). Identify the
  right source account from `--list`: session count, latest activity, sample
  titles/cwds. The account with the most recent activity is normally the one you
  just logged out of.
- **Target account must have logged in at least once** (started a session) so its
  space exists. If it has no space yet, the tool errors — log in with it, start
  one session, quit, then rerun.
- Copy is the default and non-destructive; existing items in the target are never
  overwritten. Always `--dry-run` first. Operates on both session trees.
- Common trap (learned the hard way): naively copying `A/<A-space>/…` into
  `B/<A-space>/…` puts the sessions under B but in A's space id → the app shows
  nothing. Always merge into B's **own active space**.

## When NOT to just trust it
- If the user reorganized/renamed a project folder, its old sessions get SKIPPED
  (cwd no longer exists). If they want those too, note it — the rule is literal.
- Deleted worktrees are intentionally skipped; they're throwaway.
