# Account mapping (make another account's sessions visible under the current login)

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
- **The email↔UUID map is NOT on disk.** Identify the source account from `--list`
  (session count, latest activity, sample titles/cwds); usually the one you just
  logged out of.
- **Target account must have logged in at least once** (started a session) so its
  space exists. If it has no space yet, the tool errors — log in with it, start
  one session, quit, then rerun.
- Copy is the default and non-destructive; existing items in the target are never
  overwritten. Always `--dry-run` first. Operates on both session trees.
