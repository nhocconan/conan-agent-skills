#!/usr/bin/env python3
"""
Light backup of Claude Cowork + Claude Code session histories.

Rule: keep ONLY sessions whose working dir (cwd) still EXISTS on this machine.
This drops sessions that got mixed in from other machines / deleted worktrees.

Usage:
    python3 backup.py [DEST_DIR]
    # DEST_DIR defaults to ~/Claude_Light_Backup_<YYYYMMDD>

What it copies (light = session metadata + transcript files only, no caches / VM / binaries):
    Cowork : ~/Library/Application Support/Claude/claude-code-sessions/<acct>/<space>/local_*.json
             ~/Library/Application Support/Claude/local-agent-mode-sessions/<acct>/<space>/local_*.json
    Code   : ~/.claude/projects/<slug>/*.jsonl
Cowork keeps history in BOTH trees — backing up only claude-code-sessions
silently loses the local-agent-mode half. In local-agent-mode-sessions, a
`local_<uuid>.json` metadata file may have a paired `local_<uuid>/` transcript
directory; copy that pair together. Structure is preserved verbatim so
restore.py can mirror it straight back.
"""
import json, os, glob, shutil, collections, sys, time

HOME = os.path.expanduser("~")
# (live source root, subfolder name inside the backup)
COWORK_TREES = [
    (os.path.join(HOME, "Library/Application Support/Claude/claude-code-sessions"),
     "Claude-Cowork"),
    (os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions"),
     "Claude-Cowork-Local"),
]
CODE_SRC = os.path.join(HOME, ".claude/projects")

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
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HOME, "Claude_Light_Backup_" + time.strftime("%Y%m%d"))
    code_dest = os.path.join(dest, "Claude-Code")
    os.makedirs(code_dest, exist_ok=True)

    man = ["Claude Light Backup — " + time.strftime("%Y-%m-%d %H:%M"),
           "Rule: keep only sessions whose cwd still exists on THIS machine.\n"]

    # ---- COWORK (both trees) ----
    cw_bytes = 0
    for cowork_src, sub in COWORK_TREES:
        cowork_dest = os.path.join(dest, sub)
        os.makedirs(cowork_dest, exist_ok=True)
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

    with open(os.path.join(dest, "MANIFEST.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(man))
    # drop the restore guide next to the data
    guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RESTORE_TEMPLATE.md")
    if os.path.exists(guide):
        shutil.copy2(guide, os.path.join(dest, "RESTORE.md"))
    print("\n".join(man))
    print(f"\nBackup -> {dest}")

if __name__ == "__main__":
    main()
