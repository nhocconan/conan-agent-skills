#!/usr/bin/env python3
"""Trigger eval: does the real Claude Code harness load the expected skill for a prompt?

Needs the `claude` CLI and makes REAL model calls (cost, network). Not part of the
always-run validators. Codex has no runner yet; there is no equivalent for it here.

Runs `claude -p` per case in an empty temp dir (or --cwd / EVAL_CWD, e.g. a fixture
repo), read-only tools, no session persistence. A case fires skill X if the transcript
has a Skill tool_use for X or a Read of .../X/SKILL.md. Each result row carries
`fired`, `extra` (fired minus expect, i.e. precision) and `turn` (1-based assistant
turn of the first fire, None when nothing fired); the summary reports recall@turn
for the turn cut-offs in --recall-at.

Usage: trigger_eval.py SET.json OUT.json [--model M] [--runs N] [--only id,id] [-j N]
       [--cwd DIR] [--max-turns N] [--recall-at 3,6]
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

DENY = ["Bash", "Edit", "Write", "Agent", "WebFetch", "WebSearch", "NotebookEdit", "Workflow"]
DEFAULT_MODEL = "claude-opus-5-5"  # model-id-allow


def parse_stream(text):
    """Pure parser for `claude --output-format stream-json` output.

    Returns (fired, first_turn): `fired` is the sorted list of skill names loaded,
    `first_turn` maps each to the 1-based assistant turn of its first load. Malformed
    lines are skipped. Assistant events sharing a message id count as one turn.
    """
    first = {}
    turn = 0
    last_id = None
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict) or ev.get("type") != "assistant":
            continue
        msg = ev.get("message", {})
        if not isinstance(msg, dict):
            continue
        mid = msg.get("id")
        if mid is None or mid != last_id:
            turn += 1
        last_id = mid
        for block in msg.get("content", []) or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            inp = block.get("input", {}) or {}
            name = None
            if block.get("name") == "Skill":
                name = str(inp.get("skill", "")).split(":")[-1] or None
            elif block.get("name") == "Read":
                m = re.search(r"/([^/]+)/SKILL\.md$", str(inp.get("file_path", "")))
                name = m.group(1) if m else None
            if name:
                first.setdefault(name, turn)
    return sorted(first), first


def score(expect, fired, ok_status=True):
    """A positive case passes if any expected skill fired; a negative if none did."""
    if not ok_status:
        return False
    exp = set(expect)
    return bool(exp & set(fired)) if exp else not fired


def recall_at(rows, cutoff):
    """Positive rows whose expected skill first fired by `cutoff` turns, as 'k/n'."""
    pos = [r for r in rows if r["expect"]]
    hit = 0
    for r in pos:
        turns = [t for s, t in (r.get("first_turns") or {}).items() if s in r["expect"]]
        if turns and min(turns) <= cutoff:
            hit += 1
    return f"{hit}/{len(pos)}"


def run_case(prompt, model, workdir, max_turns=3):
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--max-turns", str(max_turns), "--disallowedTools", *DENY]
    try:
        out = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=240).stdout
    except subprocess.TimeoutExpired:
        return None, {}, "timeout"
    fired, first = parse_stream(out)
    return fired, first, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set")
    ap.add_argument("out")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--only", default="")
    ap.add_argument("-j", type=int, default=4)
    ap.add_argument("--cwd", default="", help="working dir for each run (fixture repo); overrides EVAL_CWD")
    ap.add_argument("--max-turns", type=int, default=6)
    ap.add_argument("--recall-at", default="3,6")
    a = ap.parse_args()
    cases = json.load(open(a.set))["cases"]
    if a.only:
        keep = set(a.only.split(","))
        cases = [c for c in cases if c["id"] in keep]
    work = a.cwd or os.environ.get("EVAL_CWD") or tempfile.mkdtemp(prefix="trig-", dir=os.environ.get("EVAL_TMP"))
    jobs = [(c, r) for c in cases for r in range(a.runs)]

    def one(job):
        c, r = job
        fired, first, status = run_case(c["prompt"], a.model, work, a.max_turns)
        exp = set(c["expect"])
        shown = fired or []
        return {"id": c["id"], "run": r, "expect": c["expect"], "fired": fired,
                "extra": sorted(set(shown) - exp),
                "turn": min(first.values()) if first else None,
                "first_turns": first,
                "ok": score(c["expect"], shown, fired is not None), "status": status}

    with ThreadPoolExecutor(a.j) as ex:
        res = list(ex.map(one, jobs))
    pos = [x for x in res if x["expect"]]
    neg = [x for x in res if not x["expect"]]
    summary = {"model": a.model, "runs": len(res),
               "recall": f'{sum(x["ok"] for x in pos)}/{len(pos)}',
               "negatives_clean": f'{sum(x["ok"] for x in neg)}/{len(neg)}'}
    for cut in (int(t) for t in a.recall_at.split(",") if t.strip()):
        summary[f"recall@{cut}"] = recall_at(res, cut)
    json.dump({"summary": summary, "results": res}, open(a.out, "w"), indent=1, ensure_ascii=False)
    for x in res:
        print(("PASS" if x["ok"] else "FAIL"), x["id"], "expect", x["expect"], "fired", x["fired"],
              "extra", x["extra"], "turn", x["turn"], x["status"])
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
