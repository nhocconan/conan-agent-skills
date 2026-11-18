#!/usr/bin/env python3
"""
Light backup of Claude Cowork + Claude Code session histories.

Rule: keep ONLY sessions whose working dir (cwd) still EXISTS on this machine.
This drops sessions that got mixed in from other machines / deleted worktrees.

Usage:
    python3 backup.py [DEST_DIR]
    # Defaults to a fresh ~/Claude_Light_Backup_<YYYYMMDD>_<suffix> directory.

What it copies (light = session metadata + transcript files only, no caches / VM / binaries):
    Cowork : ~/Library/Application Support/Claude/claude-code-sessions/<acct>/<space>/local_*.json
             ~/Library/Application Support/Claude/local-agent-mode-sessions/<acct>/<space>/local_*.json
    Code   : $CLAUDE_CONFIG_DIR (default ~/.claude)/projects/<slug>/*.jsonl
Cowork keeps history in BOTH trees — backing up only claude-code-sessions
silently loses the local-agent-mode half. In local-agent-mode-sessions, a
`local_<uuid>.json` metadata file may have a paired `local_<uuid>/` transcript
directory; copy that pair together. Structure is preserved verbatim so
restore.py can mirror it straight back.
"""
import json, os, glob, shutil, collections, sys, tempfile, time

HOME = os.path.expanduser("~")
# (live source root, subfolder name inside the backup)
COWORK_TREES = [
    (os.path.join(HOME, "Library/Application Support/Claude/claude-code-sessions"),
     "Claude-Cowork"),
    (os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions"),
     "Claude-Cowork-Local"),
]
# Claude Code config dir: CLAUDE_CONFIG_DIR when set, else ~/.claude.
CLAUDE_CONFIG = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
CODE_SRC = os.path.join(CLAUDE_CONFIG, "projects")

def first_cwd_from_jsonl(path):
    try:
        with open(path, "rb") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if isinstance(d, dict) and isinstance(d.get("cwd"), str) and d["cwd"]:
                    return d["cwd"]
    except OSError:
        pass
    return None


def copy_paired_transcript(metadata_path, cowork_src, cowork_dest):
    """Copy the `local_<uuid>/` transcript dir paired with metadata, if present.

    Only a directory with the exact metadata stem is session content. This avoids
    copying neighbouring local-agent-mode caches/configuration while preserving the
    transcript that makes the metadata-backed session readable after restore. Symlinks
    are deliberately skipped: following one could pull arbitrary machine data into a
    backup or recurse through a cycle.
    """
    transcript_src = os.path.splitext(metadata_path)[0]
    if not os.path.isdir(transcript_src):
        return False, 0, 0
    if os.path.islink(transcript_src):
        return False, 0, 1
    rel = os.path.relpath(transcript_src, cowork_src)
    transcript_dst = os.path.join(cowork_dest, rel)
    copied_bytes = skipped_links = 0
    for root, dirnames, filenames in os.walk(transcript_src, followlinks=False):
        linked_dirs = [name for name in dirnames if os.path.islink(os.path.join(root, name))]
        skipped_links += len(linked_dirs)
        dirnames[:] = [name for name in dirnames if name not in linked_dirs]

        relative_root = os.path.relpath(root, transcript_src)
        destination_root = (transcript_dst if relative_root == "." else
                            os.path.join(transcript_dst, relative_root))
        os.makedirs(destination_root, exist_ok=True)
        for filename in filenames:
            source = os.path.join(root, filename)
            if os.path.islink(source):
                skipped_links += 1
                continue
            if not os.path.isfile(source):
                continue
            destination = os.path.join(destination_root, filename)
            shutil.copy2(source, destination)
            copied_bytes += os.path.getsize(source)
    return True, copied_bytes, skipped_links

def main():
    args = sys.argv[1:]
    if args and args[0].startswith("-"):
        # `backup.py --help` used to create a directory literally named `--help`
        # and run a full backup into it.
        print(__doc__); sys.exit(0 if args[0] in ("-h", "--help") else 1)
    if args:
        dest = args[0]
        os.makedirs(dest, mode=0o700, exist_ok=True)
        if os.path.islink(dest) or os.listdir(dest):
            sys.exit("Choose a new or empty backup directory.")
    else:
        dest = tempfile.mkdtemp(prefix=time.strftime("Claude_Light_Backup_%Y%m%d_"), dir=HOME)
    code_dest = os.path.join(dest, "Claude-Code")
    os.mkdir(code_dest, mode=0o700)

    man = ["Claude Light Backup — " + time.strftime("%Y-%m-%d %H:%M"),
           "Rule: keep only sessions whose cwd still exists on THIS machine.\n"]

    # ---- COWORK (both trees) ----
    cw_bytes = 0
    for cowork_src, sub in COWORK_TREES:
        cowork_dest = os.path.join(dest, sub)
        os.mkdir(cowork_dest, mode=0o700)
        cw_keep = cw_skip = cw_transcripts = cw_skipped_links = 0
        kept = collections.Counter(); skipped = collections.Counter()
        for f in glob.glob(os.path.join(cowork_src, "*", "*", "local_*.json")):
            try:
                with open(f, encoding="utf-8") as handle:
                    d = json.load(handle)
                cwd = d.get("cwd") or d.get("originCwd") or ""
            except Exception:
                continue
            if cwd and os.path.isdir(cwd):
                rel = os.path.relpath(f, cowork_src)
                dst = os.path.join(cowork_dest, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(f, dst)
                has_transcript, transcript_bytes, skipped_links = copy_paired_transcript(
                    f, cowork_src, cowork_dest
                )
                if has_transcript:
                    cw_transcripts += 1
                cw_skipped_links += skipped_links
                cw_keep += 1; cw_bytes += os.path.getsize(f); kept[cwd] += 1
                cw_bytes += transcript_bytes
            else:
                cw_skip += 1; skipped[cwd or "(no cwd)"] += 1
        man += ["=" * 60,
                f"CLAUDE COWORK [{os.path.basename(cowork_src)}] — kept {cw_keep} sessions "
                f"({cw_transcripts} paired transcript dirs), skipped {cw_skip}; "
                f"ignored {cw_skipped_links} transcript symlink(s)",
                "=" * 60, "\n[KEPT] cwd -> #sessions:"]
        man += [f"  {n:3d}  {c}" for c, n in sorted(kept.items())]
        man += ["\n[SKIPPED] cwd not on this machine:"]
        man += [f"  {n:3d}  {c}" for c, n in sorted(skipped.items())]
        man += [""]

    # ---- CLAUDE CODE ----
    cc_proj = cc_bytes = 0
    kept_sessions = collections.Counter()
    skipped_sessions = collections.Counter()
    for proj in sorted(glob.glob(os.path.join(CODE_SRC, "*"))):
        if not os.path.isdir(proj):
            continue
        project_dest = os.path.join(code_dest, os.path.basename(proj))
        for jf in sorted(glob.glob(os.path.join(proj, "*.jsonl"))):
            cwd = first_cwd_from_jsonl(jf)
            if not cwd or not os.path.isdir(cwd):
                skipped_sessions[cwd or "(no cwd)"] += 1
                continue
            os.makedirs(project_dest, exist_ok=True)
            shutil.copy2(jf, project_dest)
            cc_bytes += os.path.getsize(jf)
            kept_sessions[cwd] += 1
        if os.path.isdir(project_dest):
            cc_proj += 1
    man += ["\n" + "=" * 60,
            f"CLAUDE CODE — kept {cc_proj} projects / {sum(kept_sessions.values())} sessions, "
            f"skipped {sum(skipped_sessions.values())} sessions",
            "=" * 60, "\n[KEPT] cwd -> #jsonl:"]
    man += [f"  {n:3d}  {c}" for c, n in sorted(kept_sessions.items())]
    man += ["\n[SKIPPED] cwd -> #jsonl:"]
    man += [f"  {n:3d}  {c}" for c, n in sorted(skipped_sessions.items())]
    man += ["\n" + "=" * 60,
            f"TOTAL DATA: Cowork {cw_bytes/1048576:.1f} MB | Code {cc_bytes/1048576:.1f} MB",
            "=" * 60]

    manifest_path = os.path.join(dest, "MANIFEST.txt")
    fd = os.open(manifest_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("\n".join(man))
    # drop the restore guide next to the data
    guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RESTORE_TEMPLATE.md")
    if os.path.exists(guide):
        shutil.copy2(guide, os.path.join(dest, "RESTORE.md"))
    print("\n".join(man))
    print(f"\nBackup -> {dest}")

if __name__ == "__main__":
    main()
