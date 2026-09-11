#!/usr/bin/env python3
"""
mine_history.py — incremental miner over local coding-agent conversation history.

Extracts *human-authored* turns (plus lightweight signals: slash commands, skills
invoked, correction/frustration markers, per-project memory files) from:

  * Claude Code / Claude Desktop : ~/.claude/projects/<slug>/*.jsonl
  * Claude Cowork               : ~/Library/Application Support/Claude/claude-code-sessions
                                  and .../local-agent-mode-sessions
  * Codex CLI / Codex Desktop   : ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl

It is a *scanner*, not an analyst. It writes a compact markdown digest that the
agent then reads and reasons over (see SKILL.md).

Incremental by default: reads a watermark from state/last-run.json and only emits
turns newer than it. `--full` ignores the watermark. The watermark is only
advanced when `--commit` is passed (so a crashed/abandoned analysis can be redone).

Usage:
  python3 mine_history.py                      # incremental since last run
  python3 mine_history.py --full               # everything, from the beginning
  python3 mine_history.py --since 2026-07-04   # explicit floor
  python3 mine_history.py --commit             # advance the watermark after a good run
  python3 mine_history.py --out /path/digest.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
SKILL_DIR = Path(__file__).resolve().parent
STATE_FILE = SKILL_DIR / "state" / "last-run.json"

CLAUDE_PROJECTS = HOME / ".claude" / "projects"
COWORK_ROOT = HOME / "Library" / "Application Support" / "Claude"
COWORK_DIRS = [COWORK_ROOT / "claude-code-sessions", COWORK_ROOT / "local-agent-mode-sessions"]
CODEX_SESSIONS = HOME / ".codex" / "sessions"
CODEX_ARCHIVED = HOME / ".codex" / "archived_sessions"

# ---------------------------------------------------------------- filters

# Machine-generated wrappers that are not human intent.
NOISE_PREFIXES = (
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<command-message>",
    "<user-prompt-submit-hook>",
    "<environment_context>",
    "<user_instructions>",
    "Caveat: The messages below",
    "[Request interrupted",
    "API Error",
    "This session is being continued from a previous",
    # Harness plumbing delivered on the user turn. Before this list existed the
    # digest reported 187 "corrections" of which 36 were human — 81% noise.
    "<task-notification>",
    "<recommended_plugins>",
    "<bash-stdout>",
    "<bash-stderr>",
    "<codex_internal_context",
    "<function_results>",
    "<attachment",
    # A re-injected project rulebook, not something the operator typed.
    "# AGENTS.md instructions",
    "# CLAUDE.md instructions",
    "--- BEGIN UNTRUSTED EXTERNAL CONTENT",
    "<in-app-browser-context",
    # Codex's own approval-reviewer prompt, delivered on the user turn.
    "The following is the Codex agent history",
)

# A turn that is only a harness envelope once the payload is stripped.
ENVELOPE_ONLY = re.compile(r"^\s*<[a-zA-Z_][\w:-]*[^>]*>.*</[a-zA-Z_][\w:-]*>\s*$", re.S)

# Codex wraps a real human objective inside a goal envelope. Recover it rather
# than dropping the turn — these are genuine operator instructions.
OBJECTIVE_RE = re.compile(r"<objective>(.*?)</objective>", re.S)

STRIP_BLOCKS = [
    re.compile(r"<system-reminder>.*?</system-reminder>", re.S),
    re.compile(r"<local-command-stdout>.*?</local-command-stdout>", re.S),
    re.compile(r"<environment_context>.*?</environment_context>", re.S),
    re.compile(r"<task-notification>.*?</task-notification>", re.S),
    re.compile(r"<recommended_plugins>.*?</recommended_plugins>", re.S),
    re.compile(r"<bash-stdout>.*?</bash-stdout>", re.S),
    re.compile(r"<bash-stderr>.*?</bash-stderr>", re.S),
    re.compile(r"<function_results>.*?</function_results>", re.S),
]

SLASH_RE = re.compile(r"<command-name>\s*(/[\w:.-]+)")

# Signals that the human is correcting the agent — the richest source of
# durable, reusable rules. Vietnamese + English.
CORRECTION_MARKERS = [
    "sai rồi", "sai r", "bị sai", "làm sai", "không đúng", "ko đúng", "đéo", "đm ", "vcl",
    "đã bảo", "đã nói", "nói rồi", "lại bị", "lại lỗi", "vẫn lỗi", "vẫn bị", "vẫn chưa",
    "đừng ", "không được ", "ko được ", "nhớ là", "lần sau", "từ giờ", "luôn luôn",
    "bịa", "tự chế", "ẩu", "cẩn thận", "kiểm tra lại", "check lại", "sửa lại",
    "why did you", "you broke", "that's wrong", "that is wrong", "don't ", "do not ",
    "again", "still broken", "still failing", "i told you", "stop ", "never ",
    "always ", "next time", "you must", "make sure",
]

# Signals that a turn describes a *repeatable procedure* worth codifying.
PROCEDURE_MARKERS = [
    "quy trình", "checklist", "template", "chuẩn", "standard", "playbook", "workflow",
    "mỗi lần", "every time", "each time", "pipeline", "script", "audit", "convention",
    "house rule", "best practice", "guideline", "rule",
]


def norm_text(raw) -> str:
    """Flatten a message content field to plain human text ('' if not human)."""
    if isinstance(raw, str):
        text = raw
    elif isinstance(raw, list):
        parts = []
        for b in raw:
            if not isinstance(b, dict):
                continue
            t = b.get("type")
            if t in ("text", "input_text"):
                parts.append(b.get("text", ""))
            elif t in ("tool_result", "tool_use", "thinking", "image", "input_image"):
                return ""  # tool plumbing, never human intent
        text = "\n".join(parts)
    else:
        return ""

    for pat in STRIP_BLOCKS:
        text = pat.sub("", text)
    return text.strip()


def classify(text: str):
    """Return (kind, payload) — kind in {slash, prompt, noise}."""
    m = SLASH_RE.search(text)
    if m:
        return "slash", m.group(1)
    # Recover the operator's words from a goal envelope before rejecting it.
    obj = OBJECTIVE_RE.search(text)
    if obj:
        text = obj.group(1).strip()
    if text.startswith(NOISE_PREFIXES):
        return "noise", None
    if ENVELOPE_ONLY.match(text):
        return "noise", None
    if not text:
        return "noise", None
    return "prompt", text


def parse_ts(value) -> str:
    if not value:
        return ""
    return str(value)


# ---------------------------------------------------------------- readers

def file_mtime_iso(path: Path) -> str:
    """Fallback timestamp. Cowork turns often carry no `timestamp` field; without a
    fallback they bypass the watermark and every 'incremental' run re-emits them."""
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    except OSError:
        return ""


def read_claude_jsonl(path: Path, floor: str, errors=None):
    """Yield turn dicts from a Claude Code/Cowork session file."""
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        if errors is not None:
            errors["unreadable_files"] += 1
        return
    fallback_ts = file_mtime_iso(path)
    with fh:
        for line_no, line in enumerate(fh, 1):
            try:
                d = json.loads(line)
            except Exception:
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            if not isinstance(d, dict):
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain"):
                continue
            ts = parse_ts(d.get("timestamp")) or fallback_ts
            if floor and ts <= floor:
                continue
            message = d.get("message") or {}
            if not isinstance(message, dict):
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            text = norm_text(message.get("content"))
            if not text:
                continue
            kind, payload = classify(text)
            if kind == "noise":
                continue
            yield {
                "ts": ts,
                "cwd": d.get("cwd") or "",
                "source": "claude",
                "kind": kind,
                "text": payload,
                "path": str(path), "line": line_no, "session": path.stem,
            }


def read_codex_jsonl(path: Path, floor: str, errors=None):
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        if errors is not None:
            errors["unreadable_files"] += 1
        return
    cwd = ""
    fallback_ts = file_mtime_iso(path)
    with fh:
        for line_no, line in enumerate(fh, 1):
            try:
                d = json.loads(line)
            except Exception:
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            if not isinstance(d, dict):
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            t = d.get("type")
            payload = d.get("payload") or {}
            if not isinstance(payload, dict):
                if errors is not None:
                    errors["malformed_records"] += 1
                continue
            if t == "session_meta":
                # Worker briefs are not independent human requests.
                origin = payload.get("source")
                if origin == "subagent" or (isinstance(origin, dict) and "subagent" in origin):
                    return
                cwd = payload.get("cwd", "") or cwd
                continue
            if t != "response_item" or payload.get("role") != "user":
                continue
            ts = parse_ts(d.get("timestamp")) or fallback_ts
            if floor and ts <= floor:
                continue
            text = norm_text(payload.get("content"))
            if not text:
                continue
            kind, tp = classify(text)
            if kind == "noise":
                continue
            yield {"ts": ts, "cwd": cwd, "source": "codex", "kind": kind, "text": tp,
                   "path": str(path), "line": line_no, "session": path.stem}


def dedupe(turns):
    """Drop replayed turns: resuming a session re-emits its opening prompt, so
    one instruction can appear 5-8 times and dominate the digest. Keep the
    earliest occurrence of each distinct text per project."""
    seen, out = {}, []
    for t in sorted(turns, key=lambda x: x["ts"]):
        key = (t.get("cwd") or t.get("path", ""), " ".join(t["text"].split()))
        occurrence = {k: t[k] for k in ("path", "line", "session", "ts") if k in t}
        if key in seen:
            seen[key]["occurrences"].append(occurrence)
            continue
        entry = dict(t, occurrences=[occurrence])
        seen[key] = entry
        out.append(entry)
    return out


def collect(floor: str, limit_chars: int, errors=None):
    turns, files_seen = [], 0

    claude_files = []
    if CLAUDE_PROJECTS.is_dir():
        claude_files += sorted(CLAUDE_PROJECTS.glob("*/*.jsonl"))
    for d in COWORK_DIRS:
        if d.is_dir():
            claude_files += sorted(p for p in d.rglob("*.jsonl") if "subagents" not in p.parts)

    for p in claude_files:
        files_seen += 1
        turns.extend(read_claude_jsonl(p, floor, errors))

    for root in (CODEX_SESSIONS, CODEX_ARCHIVED):
        for p in sorted(root.rglob("*.jsonl")) if root.is_dir() else []:
            files_seen += 1
            turns.extend(read_codex_jsonl(p, floor, errors))

    turns = dedupe(turns)
    for t in turns:
        if t["kind"] == "prompt" and len(t["text"]) > limit_chars:
            t["text"] = t["text"][:limit_chars] + " …[truncated]"
    return turns, files_seen


def collect_memory(floor: str, errors=None):
    """Per-project auto-memory files — already-distilled recurring feedback."""
    out = []
    for md in CLAUDE_PROJECTS.glob("*/memory/*.md"):
        try:
            mtime = datetime.fromtimestamp(md.stat().st_mtime, timezone.utc).isoformat()
        except OSError:
            if errors is not None:
                errors["unreadable_memory_files"] += 1
            continue
        if floor and mtime <= floor:
            continue
        try:
            body = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            if errors is not None:
                errors["unreadable_memory_files"] += 1
            continue
        out.append({"path": str(md), "mtime": mtime, "body": body[:2500]})
    out.sort(key=lambda m: m["mtime"])
    return out


# ---------------------------------------------------------------- digest

def project_of(cwd: str) -> str:
    return cwd if cwd else "(unknown)"


def has_marker(text: str, markers) -> bool:
    low = text.lower()
    return any(m in low for m in markers)


def build_digest(turns, memories, floor, files_seen, args) -> str:
    prompts = [t for t in turns if t["kind"] == "prompt"]
    slashes = [t for t in turns if t["kind"] == "slash"]

    by_project = defaultdict(list)
    for t in prompts:
        by_project[project_of(t["cwd"])].append(t)

    corrections = [t for t in prompts if has_marker(t["text"], CORRECTION_MARKERS)]
    procedures = [t for t in prompts if has_marker(t["text"], PROCEDURE_MARKERS)]

    L = []
    A = L.append
    A("# History digest for skill mining")
    A("")
    A(f"- Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    A(f"- Window: {'all discovered history (no date floor)' if not floor else 'since ' + floor}")
    A(f"- Session files scanned: {files_seen}")
    A("- Coverage: automated scan; excerpts below are capped samples, not full semantic review.")
    A(f"- Read/parse gaps: {dict(getattr(args, 'scan_errors', {}))}")
    for root, present in getattr(args, "stores", []):
        A(f"- Store: {root} · {'present' if present else 'absent'}")
    A(f"- Human prompts: {len(prompts)} | slash-command invocations: {len(slashes)}")
    A(f"- Correction-flavoured prompts: {len(corrections)} | procedure-flavoured: {len(procedures)}")
    A(f"- Projects touched: {len(by_project)}")
    A(f"- Memory files changed in window: {len(memories)}")
    A("")

    A("## Volume by project (sort key for 'is this recurring?')")
    A("")
    A("| Project | Prompts | First | Last |")
    A("|---|---:|---|---|")
    for proj, ts in sorted(by_project.items(), key=lambda kv: -len(kv[1])):
        A(f"| {proj} | {len(ts)} | {ts[0]['ts'][:10]} | {ts[-1]['ts'][:10]} |")
    A("")

    if slashes:
        A("## Slash commands / skills invoked (what the operator already reaches for)")
        A("")
        c = Counter(t["text"] for t in slashes)
        A(", ".join(f"`{k}`×{v}" for k, v in c.most_common(40)))
        A("")

    A("## Correction & standing-rule turns (highest-signal: recurring pain)")
    A("")
    A("_Turns where the operator corrected, scolded, or laid down a rule. A rule repeated")
    A("across ≥2 projects is skill material; a one-off preference is memory material._")
    A("")
    for t in corrections[-args.max_corrections:]:
        A(f"### {t['ts'][:16]} · {project_of(t['cwd'])} · {t['source']}")
        A(f"Source: {t.get('path', '?')}:{t.get('line', '?')} · occurrences: {len(t.get('occurrences', []))}")
        A("")
        A("```")
        A(t["text"][:args.excerpt])
        A("```")
        A("")

    A("## Procedure-flavoured turns (checklists, standards, workflows)")
    A("")
    for t in procedures[-args.max_procedures:]:
        A(f"### {t['ts'][:16]} · {project_of(t['cwd'])} · {t['source']}")
        A(f"Source: {t.get('path', '?')}:{t.get('line', '?')} · occurrences: {len(t.get('occurrences', []))}")
        A("")
        A("```")
        A(t["text"][:args.excerpt])
        A("```")
        A("")

    A("## Per-project prompt sample (task shapes)")
    A("")
    for proj, ts in sorted(by_project.items(), key=lambda kv: -len(kv[1])):
        A(f"### {proj} ({len(ts)} prompts)")
        A("")
        for t in ts[-args.per_project:]:
            first = " ".join(t["text"].split())[:args.oneline]
            A(f"- `{t['ts'][:10]}` {first}")
        A("")

    if memories:
        A("## Auto-memory files changed in window (already-distilled findings)")
        A("")
        if len(memories) > args.max_memory:
            A(f"_Showing the {args.max_memory} most recent of {len(memories)}._")
            A("")
        for m in memories[-args.max_memory:]:
            A(f"### {m['path']}  _(mtime {m['mtime'][:16]})_")
            A("")
            A("```markdown")
            A(m["body"])
            A("```")
            A("")

    return "\n".join(L)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="ignore the watermark, scan everything")
    ap.add_argument("--since", help="ISO date/time floor, e.g. 2026-07-04")
    ap.add_argument("--commit", action="store_true", help="advance the watermark to now")
    ap.add_argument("--out", help="digest path (default: state/digest-<ts>.md)")
    ap.add_argument("--excerpt", type=int, default=1200, help="max chars per quoted turn")
    ap.add_argument("--oneline", type=int, default=180, help="max chars per sample line")
    ap.add_argument("--per-project", type=int, default=25, help="sample prompts per project")
    ap.add_argument("--max-corrections", type=int, default=120)
    ap.add_argument("--max-procedures", type=int, default=80)
    ap.add_argument("--max-memory", type=int, default=40, help="memory files quoted in full")
    ap.add_argument("--limit-chars", type=int, default=4000, help="hard cap per stored turn")
    args = ap.parse_args()

    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            state = {}

    if args.full:
        floor = ""
    elif args.since:
        floor = args.since if "T" in args.since else args.since + "T00:00:00.000Z"
    else:
        floor = state.get("watermark", "")

    started = datetime.now(timezone.utc).isoformat()
    args.stores = [(str(root), root.is_dir()) for root in
                   (CLAUDE_PROJECTS, CODEX_SESSIONS, CODEX_ARCHIVED, *COWORK_DIRS)]
    args.scan_errors = Counter()
    turns, files_seen = collect(floor, args.limit_chars, args.scan_errors)
    memories = collect_memory(floor, args.scan_errors)
    digest = build_digest(turns, memories, floor, files_seen, args)

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    out = Path(args.out) if args.out else STATE_FILE.parent / (
        "digest-" + started.replace(":", "").replace("-", "") + ".md")
    # Private histories must not inherit a permissive shell umask. Exclusive create
    # also refuses symlinks and accidental replacement of earlier evidence.
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(digest)

    if args.commit and args.scan_errors:
        print("Refusing watermark advance: read/parse gaps remain.", file=sys.stderr)
        return 1
    if args.commit:
        state["watermark"] = started
        state.setdefault("runs", []).append({
            "at": started,
            "window": floor or "FULL",
            "files": files_seen,
            "prompts": sum(1 for t in turns if t["kind"] == "prompt"),
            "digest": str(out),
        })
        state["runs"] = state["runs"][-30:]
        if STATE_FILE.is_symlink():
            raise RuntimeError(f"refusing to write symlinked state file: {STATE_FILE}")
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(STATE_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | nofollow, 0o600)
        try:
            os.fchmod(fd, 0o600)
        except OSError:
            os.close(fd)
            raise
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(state, indent=2))

    print(json.dumps({
        "digest": str(out),
        "bytes": out.stat().st_size,
        "window": floor or "FULL",
        "files_scanned": files_seen,
        "scan_errors": dict(args.scan_errors),
        "prompts": sum(1 for t in turns if t["kind"] == "prompt"),
        "corrections": sum(1 for t in turns if t["kind"] == "prompt"
                           and has_marker(t["text"], CORRECTION_MARKERS)),
        "memory_files": len(memories),
        "watermark_committed": bool(args.commit),
        "previous_watermark": state.get("watermark", "") if not args.commit else started,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
