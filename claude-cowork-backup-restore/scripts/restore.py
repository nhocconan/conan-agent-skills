#!/usr/bin/env python3
"""
Restore a light backup produced by backup.py back into the live Claude dirs.

Usage:
    python3 restore.py SRC_DIR [--dry-run] [--force]

    SRC_DIR    the backup folder (contains Claude-Cowork/ and Claude-Code/)
    --dry-run  show what would happen, copy nothing
    --force    overwrite files that already exist (default: skip existing = safe merge)

Targets:
    Claude-Cowork/*  ->  ~/Library/Application Support/Claude/claude-code-sessions/
    Claude-Code/*    ->  ~/.claude/projects/

Safe by default: existing live files are never overwritten unless --force.
Restart the Claude Desktop / Cowork app after restoring so it re-indexes.
"""
import os, glob, shutil, sys

HOME = os.path.expanduser("~")
COWORK_DST = os.path.join(HOME, "Library/Application Support/Claude/claude-code-sessions")
CODE_DST   = os.path.join(HOME, ".claude/projects")

def restore_tree(src_root, dst_root, dry, force):
    copied = skipped = 0
    if not os.path.isdir(src_root):
        print(f"  (nothing at {src_root})")
        return copied, skipped
    for src in glob.glob(os.path.join(src_root, "**", "*"), recursive=True):
        if not os.path.isfile(src):
            continue
        rel = os.path.relpath(src, src_root)
        dst = os.path.join(dst_root, rel)
        if os.path.exists(dst) and not force:
            skipped += 1
            continue
        if dry:
            print(f"  would copy: {rel}")
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        copied += 1
    return copied, skipped

def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__); sys.exit(1)
    src = os.path.abspath(args[0])
    dry = "--dry-run" in args
    force = "--force" in args
    print(f"Restore from: {src}   dry_run={dry}  force={force}\n")

    print("Cowork ->", COWORK_DST)
    c1, s1 = restore_tree(os.path.join(src, "Claude-Cowork"), COWORK_DST, dry, force)
    print(f"  copied {c1}, skipped(existing) {s1}\n")

    print("Code   ->", CODE_DST)
    c2, s2 = restore_tree(os.path.join(src, "Claude-Code"), CODE_DST, dry, force)
    print(f"  copied {c2}, skipped(existing) {s2}\n")

    print(f"DONE. total copied={c1+c2}, skipped={s1+s2}")
    if not dry:
        print("Restart the Claude Desktop / Cowork app so it re-indexes the sessions.")

if __name__ == "__main__":
    main()
