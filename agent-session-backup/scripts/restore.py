#!/usr/bin/env python3
"""
Restore a light backup produced by backup.py back into the live Claude dirs.

Usage:
    python3 restore.py SRC_DIR [--dry-run] [--force]

    SRC_DIR    the backup folder (contains Claude-Cowork/ and Claude-Code/)
    --dry-run  show what would happen, copy nothing
    --force    overwrite files that already exist (default: skip existing = safe merge)

Targets:
    Claude-Cowork/*        ->  ~/Library/Application Support/Claude/claude-code-sessions/
    Claude-Cowork-Local/*  ->  ~/Library/Application Support/Claude/local-agent-mode-sessions/
    Claude-Code/*          ->  ~/.claude/projects/

(Claude-Cowork-Local/ is absent in backups made before 2026-07; that's fine —
the script skips missing subfolders.)

Safe by default: existing live files are never overwritten unless --force.
Paired Cowork transcript directories are restored file-by-file with the same
safe-merge rule, so an existing live transcript file is never replaced.
Restore refuses symlinks at the selected roots and within their descendants;
it does not audit symlink aliases in ancestors above a user-selected root.
Restart the Claude Desktop / Cowork app after restoring so it re-indexes.
"""
import os, shutil, sys

HOME = os.path.expanduser("~")
# (backup subfolder, live destination)
TARGETS = [
    ("Claude-Cowork",
     os.path.join(HOME, "Library/Application Support/Claude/claude-code-sessions")),
    ("Claude-Cowork-Local",
     os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions")),
    ("Claude-Code",
     os.path.join(HOME, ".claude/projects")),
]


class RestoreSafetyError(RuntimeError):
    """The requested restore would traverse a symlink or invalid target."""


def validate_restore_roots(src_root, dst_root):
    """Reject selected-root symlinks before walking or writing either tree.

    This is static preflight validation, not an adversarial-filesystem sandbox.
    """
    if os.path.islink(src_root):
        raise RestoreSafetyError(f"Refusing symlink source root: {src_root}")
    if os.path.islink(dst_root):
        raise RestoreSafetyError(f"Refusing symlink destination root: {dst_root}")
    if os.path.lexists(dst_root) and not os.path.isdir(dst_root):
        raise RestoreSafetyError(f"Refusing non-directory destination root: {dst_root}")


def safe_destination(dst_root, relative_path):
    """Return a destination only when its target-root components are safe."""
    dst_root = os.path.abspath(os.fspath(dst_root))
    destination = os.path.normpath(os.path.join(dst_root, relative_path))
    if os.path.commonpath((dst_root, destination)) != dst_root:
        raise RestoreSafetyError(f"Refusing destination outside target root: {relative_path}")

    parent = dst_root
    for component in os.path.dirname(relative_path).split(os.sep):
        if not component:
            continue
        parent = os.path.join(parent, component)
        if os.path.islink(parent):
            raise RestoreSafetyError(f"Refusing symlink destination parent: {parent}")
        if os.path.lexists(parent) and not os.path.isdir(parent):
            raise RestoreSafetyError(f"Refusing non-directory destination parent: {parent}")
    if os.path.islink(destination):
        raise RestoreSafetyError(f"Refusing symlink destination file: {destination}")
    if os.path.lexists(destination) and not os.path.isfile(destination):
        raise RestoreSafetyError(f"Refusing non-regular destination file: {destination}")
    return destination


def restore_tree(src_root, dst_root, dry, force):
    copied = skipped = 0
    validate_restore_roots(src_root, dst_root)
    if not os.path.isdir(src_root):
        print(f"  (nothing at {src_root})")
        return copied, skipped
    for root, dirnames, filenames in os.walk(src_root, followlinks=False):
        linked_dirs = [name for name in dirnames if os.path.islink(os.path.join(root, name))]
        for name in linked_dirs:
            print(f"  skipped symlink: {os.path.relpath(os.path.join(root, name), src_root)}")
        skipped += len(linked_dirs)
        dirnames[:] = [name for name in dirnames if name not in linked_dirs]
        for filename in filenames:
            src = os.path.join(root, filename)
            rel = os.path.relpath(src, src_root)
            if os.path.islink(src):
                print(f"  skipped symlink: {rel}")
                skipped += 1
                continue
            dst = safe_destination(dst_root, rel)
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

    tot_c = tot_s = 0
    for sub, dst_root in TARGETS:
        print(f"{sub} -> {dst_root}")
        c, s = restore_tree(os.path.join(src, sub), dst_root, dry, force)
        print(f"  copied {c}, skipped(existing/symlink) {s}\n")
        tot_c += c; tot_s += s

    print(f"DONE. total copied={tot_c}, skipped={tot_s}")
    if not dry:
        print("Restart the Claude Desktop / Cowork app so it re-indexes the sessions.")

if __name__ == "__main__":
    main()
