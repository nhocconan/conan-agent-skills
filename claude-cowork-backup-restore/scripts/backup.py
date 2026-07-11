#!/usr/bin/env python3
"""
Light backup of Claude Cowork + Claude Code session histories.

Rule: keep ONLY sessions whose working dir (cwd) still EXISTS on this machine.
This drops sessions that got mixed in from other machines / deleted worktrees.

Usage:
    python3 backup.py [DEST_DIR]
    # DEST_DIR defaults to ~/Claude_Light_Backup_<YYYYMMDD>

What it copies (light = history files only, no caches / VM / binaries):
    Cowork : ~/Library/Application Support/Claude/claude-code-sessions/<ws>/<sess>/local_*.json
    Code   : ~/.claude/projects/<slug>/*.jsonl
Structure is preserved verbatim so restore.py can mirror it straight back.
"""
import json, os, glob, shutil, collections, sys, time

HOME = os.path.expanduser("~")
COWORK_SRC = os.path.join(HOME, "Library/Application Support/Claude/claude-code-sessions")
CODE_SRC   = os.path.join(HOME, ".claude/projects")

def first_cwd_from_jsonl(path):
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if isinstance(d, dict) and d.get("cwd"):
                    return d["cwd"]
    except Exception:
        pass
    return None

def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HOME, "Claude_Light_Backup_" + time.strftime("%Y%m%d"))
    code_dest   = os.path.join(dest, "Claude-Code")
    cowork_dest = os.path.join(dest, "Claude-Cowork")
    os.makedirs(code_dest, exist_ok=True)
    os.makedirs(cowork_dest, exist_ok=True)

    man = ["Claude Light Backup — " + time.strftime("%Y-%m-%d %H:%M"),
           "Rule: keep only sessions whose cwd still exists on THIS machine.\n"]

    # ---- COWORK ----
    cw_keep = cw_skip = cw_bytes = 0
    kept = collections.Counter(); skipped = collections.Counter()
    for f in glob.glob(os.path.join(COWORK_SRC, "*", "*", "local_*.json")):
        try:
            d = json.load(open(f))
            cwd = d.get("cwd") or d.get("originCwd") or ""
        except Exception:
            continue
        if cwd and os.path.isdir(cwd):
            rel = os.path.relpath(f, COWORK_SRC)
            dst = os.path.join(cowork_dest, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(f, dst)
            cw_keep += 1; cw_bytes += os.path.getsize(f); kept[cwd] += 1
        else:
            cw_skip += 1; skipped[cwd or "(no cwd)"] += 1
    man += ["=" * 60, f"CLAUDE COWORK — kept {cw_keep} sessions, skipped {cw_skip}", "=" * 60,
            "\n[KEPT] cwd -> #sessions:"]
    man += [f"  {n:3d}  {c}" for c, n in sorted(kept.items())]
    man += ["\n[SKIPPED] cwd not on this machine:"]
    man += [f"  {n:3d}  {c}" for c, n in sorted(skipped.items())]

    # ---- CLAUDE CODE ----
    cc_proj = cc_sess = cc_skip = cc_bytes = 0
    kept_p = []; skipped_p = []
    for proj in sorted(glob.glob(os.path.join(CODE_SRC, "*"))):
        if not os.path.isdir(proj):
            continue
        jsonls = glob.glob(os.path.join(proj, "*.jsonl"))
        cwd = None
        for jf in jsonls:
            cwd = first_cwd_from_jsonl(jf)
            if cwd:
                break
        if cwd and os.path.isdir(cwd) and jsonls:
            slug = os.path.basename(proj)
            dd = os.path.join(code_dest, slug); os.makedirs(dd, exist_ok=True)
            for jf in jsonls:
                shutil.copy2(jf, os.path.join(dd, os.path.basename(jf)))
                cc_bytes += os.path.getsize(jf)
            cc_proj += 1; cc_sess += len(jsonls); kept_p.append((cwd, len(jsonls)))
        else:
            cc_skip += 1; skipped_p.append((cwd or "(no cwd)", len(jsonls), os.path.basename(proj)))
    man += ["\n" + "=" * 60,
            f"CLAUDE CODE — kept {cc_proj} projects / {cc_sess} sessions, skipped {cc_skip} projects",
            "=" * 60, "\n[KEPT] cwd -> #jsonl:"]
    man += [f"  {n:3d}  {c}" for c, n in sorted(kept_p)]
    man += ["\n[SKIPPED] project -> reason:"]
    man += [f"  {n:3d} jsonl  {c}   <{s}>" for c, n, s in skipped_p]
    man += ["\n" + "=" * 60,
            f"TOTAL DATA: Cowork {cw_bytes/1048576:.1f} MB | Code {cc_bytes/1048576:.1f} MB",
            "=" * 60]

    open(os.path.join(dest, "MANIFEST.txt"), "w").write("\n".join(man))
    # drop the restore guide next to the data
    guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RESTORE_TEMPLATE.md")
    if os.path.exists(guide):
        shutil.copy2(guide, os.path.join(dest, "RESTORE.md"))
    print("\n".join(man))
    print(f"\nBackup -> {dest}")

if __name__ == "__main__":
    main()
