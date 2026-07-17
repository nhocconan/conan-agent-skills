#!/usr/bin/env python3
"""
Account mapping — make one account's Cowork sessions show up under another
account's login in Claude Desktop.

STORAGE MODEL (verified on macOS, Claude Desktop 2.1.x):

    ~/Library/Application Support/Claude/
        claude-code-sessions/<ACCOUNT-UUID>/<SPACE-UUID>/local_*.json
        local-agent-mode-sessions/<ACCOUNT-UUID>/<SPACE-UUID>/local_*.json (+ session dirs)

  * <ACCOUNT-UUID> = the logged-in account. Current login is `lastKnownAccountUuid`
    in config.json.
  * <SPACE-UUID>   = a "space" inside that account. Each account has its OWN space
    id, and the app lists sessions from the account's **active space** (the one it
    most recently wrote to). Sessions dropped under a different space id — even
    under the right account — will NOT appear.

So to move account A's sessions to account B, you must merge A's session files into
**B's active space folder**, in BOTH trees. That is exactly what --from does here.

Usage:
    python3 map_account.py --list
        Show current login + every account, its spaces, session counts, latest
        activity, and sample titles (to identify whose account is whose).

    python3 map_account.py --from <SRC_ACCOUNT_UUID> [--to <DST_ACCOUNT_UUID>]
                           [--to-space <SPACE_UUID>] [--dry-run] [--move]
        Merge every session under SRC account (across all its spaces) into DST
        account's active space.
        --to        defaults to the current login (lastKnownAccountUuid).
        --to-space  override the detected active space (rarely needed).
        --dry-run   preview only.
        --move      remove sessions from SRC after copying (relocate). Default is
                    copy (SRC keeps its sessions).
        Items already present in the target are skipped, never overwritten.

    NOTE: DST account must have logged in at least once (started a session) so its
    space exists. If DST has no space yet, this errors out — log in with DST, start
    one session, quit, then rerun.

After running, fully quit (Cmd+Q) and relaunch Claude Desktop so it re-indexes.
"""
import json, os, glob, shutil, sys, time

CL = os.path.expanduser("~/Library/Application Support/Claude")
CONFIG = os.path.join(CL, "config.json")
TREES = ["claude-code-sessions", "local-agent-mode-sessions"]

def current_uuid():
    try:
        return json.load(open(CONFIG)).get("lastKnownAccountUuid")
    except Exception:
        return None

def is_uuid(name):
    return name.count("-") == 4 and len(name) == 36

def account_folders():
    names = set()
    for t in TREES:
        base = os.path.join(CL, t)
        if os.path.isdir(base):
            for d in glob.glob(os.path.join(base, "*")):
                if os.path.isdir(d) and is_uuid(os.path.basename(d)):
                    names.add(os.path.basename(d))
    return names

def spaces_of(account):
    """{space_uuid: (session_count, latest_activity_ms)} across both trees."""
    out = {}
    for t in TREES:
        base = os.path.join(CL, t, account)
        if not os.path.isdir(base):
            continue
        for sp in glob.glob(os.path.join(base, "*")):
            if not (os.path.isdir(sp) and is_uuid(os.path.basename(sp))):
                continue
            name = os.path.basename(sp)
            cnt, latest = out.get(name, (0, 0))
            for f in glob.glob(os.path.join(sp, "local_*.json")):
                cnt += 1
                try:
                    la = json.load(open(f)).get("lastActivityAt") or int(os.path.getmtime(f) * 1000)
                except Exception:
                    la = int(os.path.getmtime(f) * 1000)
                latest = max(latest, la)
            out[name] = (cnt, latest)
    return out

def active_space(account):
    """The space the app is currently using = newest activity."""
    sp = spaces_of(account)
    if not sp:
        return None
    return max(sp.items(), key=lambda kv: kv[1][1])[0]

def titles_of(account, space):
    base = os.path.join(CL, "claude-code-sessions", account, space)
    ts = []
    for f in glob.glob(os.path.join(base, "local_*.json")):
        try:
            j = json.load(open(f))
            ts.append((j.get("lastActivityAt") or 0, j.get("title", "(no title)"), j.get("cwd", "")))
        except Exception:
            pass
    ts.sort(reverse=True)
    return ts

def cmd_list():
    cur = current_uuid()
    print(f"CURRENT login account UUID = {cur}\n")
    for acc in sorted(account_folders()):
        tag = "   <<< CURRENT LOGIN" if acc == cur else ""
        act = active_space(acc)
        print(f"ACCOUNT {acc}{tag}   active-space={act}")
        for sp, (cnt, latest) in sorted(spaces_of(acc).items(), key=lambda kv: -kv[1][1]):
            lt = time.strftime('%Y-%m-%d %H:%M', time.localtime(latest/1000)) if latest else "?"
            star = " *active" if sp == act else ""
            print(f"   space {sp}  [{cnt} sessions]  latest={lt}{star}")
        for _, t, c in titles_of(acc, act)[:3] if act else []:
            print(f"       • {t[:52]:52s}  {c}")
        print()

def _item_meta(item):
    """Return (lastActivity_ms, cwd) for a local_*.json file OR its sibling dir.

    local-agent-mode-sessions stores BOTH `local_<uuid>.json` (metadata) and a
    `local_<uuid>/` dir (transcript) per session; they share one date from the
    .json. Falls back to file mtime when the json is missing/unreadable."""
    import time as _t
    if os.path.isdir(item):
        json_path = item + ".json"
    else:
        json_path = item
    try:
        d = json.load(open(json_path))
        la = d.get("lastActivityAt") or int(os.path.getmtime(json_path) * 1000)
        cwd = d.get("cwd") or d.get("originCwd") or ""
    except Exception:
        la = int(os.path.getmtime(item) * 1000)
        cwd = ""
    return la, cwd

def cmd_map(src, dst, dst_space, dry, move, since_days=None, cwd_filter=True):
    dst = dst or current_uuid()
    if not src or not dst:
        print("ERROR: need --from SRC and a resolvable --to/current account."); sys.exit(1)
    if src == dst:
        print("ERROR: source and target accounts are the same."); sys.exit(1)
    dst_space = dst_space or active_space(dst)
    if not dst_space:
        print(f"ERROR: target account {dst} has no space yet.\n"
              f"       Log in with it, start ONE session, quit, then rerun."); sys.exit(1)

    cutoff = (time.time() - since_days * 86400) * 1000 if since_days else None
    label = f" (since {since_days}d, cwd_filter={cwd_filter})" if since_days else ""
    print(f"{'MOVE' if move else 'COPY'} sessions:  {src}  ->  {dst}/{dst_space}"
          f"   dry_run={dry}{label}\n")
    total_add = total_skip = total_skip_age = total_skip_cwd = 0
    for t in TREES:
        src_base = os.path.join(CL, t, src)
        if not os.path.isdir(src_base):
            print(f"[{t}] no source account folder, skip"); continue
        dst_dir = os.path.join(CL, t, dst, dst_space)
        add = skip = skip_age = skip_cwd = 0
        for src_space in glob.glob(os.path.join(src_base, "*")):
            if not os.path.isdir(src_space):
                continue
            for item in glob.glob(os.path.join(src_space, "*")):
                name = os.path.basename(item)
                # Only session histories share the `local_*` namespace; the
                # local-agent-mode-sessions tree also holds per-account config
                # (cowork_settings.json, cowork-*-cache.json, memory/, agent/,
                # debug/, cowork_plugins/) that must NOT be copied across.
                if not name.startswith("local_"):
                    continue
                target = os.path.join(dst_dir, name)
                if os.path.exists(target):
                    skip += 1
                    continue
                la, cwd = _item_meta(item)
                if cutoff is not None and la < cutoff:
                    skip_age += 1
                    continue
                if cwd_filter and cwd and not os.path.isdir(cwd):
                    skip_cwd += 1
                    continue
                if dry:
                    print(f"  [{t}] would add {name}")
                else:
                    os.makedirs(dst_dir, exist_ok=True)
                    if os.path.isdir(item):
                        shutil.copytree(item, target)
                    else:
                        shutil.copy2(item, target)
                    if move:
                        (shutil.rmtree if os.path.isdir(item) else os.remove)(item)
                add += 1
            if move and not dry:
                try:
                    os.rmdir(src_space)
                except OSError:
                    pass
        print(f"[{t}] added {add}, skipped(existing) {skip}, "
              f"skipped(age) {skip_age}, skipped(cwd) {skip_cwd}")
        total_add += add; total_skip += skip
        total_skip_age += skip_age; total_skip_cwd += skip_cwd
    print(f"\nDONE. added={total_add}, skipped(existing)={total_skip}, "
          f"skipped(age)={total_skip_age}, skipped(cwd)={total_skip_cwd}"
          + (" (moved from source)" if move and not dry else ""))
    if not dry:
        print("Fully quit (Cmd+Q) and relaunch Claude Desktop so it re-indexes.")

def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    if "--list" in a:
        cmd_list(); return
    def val(flag):
        return a[a.index(flag)+1] if flag in a and a.index(flag)+1 < len(a) else None
    sd = val("--since-days")
    sd = int(sd) if sd else None
    cmd_map(val("--from"), val("--to"), val("--to-space"),
            "--dry-run" in a, "--move" in a,
            since_days=sd, cwd_filter=("--no-cwd-filter" not in a))

if __name__ == "__main__":
    main()
