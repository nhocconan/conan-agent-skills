#!/usr/bin/env python3
"""Evaluate skill loading with real Claude Code, Codex or agy CLI calls (cost/network).

Default Claude interface is preserved. Add --harness codex|agy; --model is optional
for these harnesses and otherwise uses their configured default. Outputs contain
scores and skill names only, never prompts, tool output or CLI diagnostics.

Codex uses its read-only sandbox; agy uses plan mode plus terminal sandbox (not an
OS-wide read-only guarantee). Use an isolated fixture cwd,
without production integrations. agy session-only deny rules block file writes,
commands, URL reads/browser navigation and MCP actions; existing-tab browser
interactions and other undeclared action types are not claimed isolated. No
bypass-permission flags are used. --skills-dir explicitly grants AGY reads of
public Markdown files within each installed skill, resolving symlinks and excluding
private/dot directories and files escaping the individual skill. No global settings
are changed.

Completed successful root skill reads/invocations count; failed, malformed or
incomplete runs fail every case, including negatives. Codex shell recognition is
conservative: direct cat/head/sed reads with matching skill frontmatter. Other
reading mechanisms are undercounted. --max-turns is Claude-only; every harness has
a wall timeout and process-group cleanup. Recall cutoffs use assistant messages
for Claude, tool steps for Codex/agy (not model reasoning turns). Temporary default
workdirs are removed.
"""
import argparse
import json
import math
import os
import re
import shlex
import signal
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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


def skill_path(path):
    match = re.search(r"(?:^|/)([a-z0-9][a-z0-9-]*)/SKILL\.md$", str(path))
    return match.group(1) if match else None


def shell_skill_paths(command):
    """Recognize only simple file readers, never arbitrary shell mentions."""
    try:
        words = shlex.split(command)
        if len(words) >= 3 and words[0].rsplit('/', 1)[-1] in {'bash', 'sh', 'zsh'}:
            if words[1] not in {'-c', '-lc'} or len(words) != 3:
                return []
            words = shlex.split(words[2])
        if not words or any(re.search(r'[;&|<>`$\n]', w) for w in words):
            return []
        reader, args = words[0].rsplit('/', 1)[-1], words[1:]
        if reader == 'cat':
            paths = args[1:] if args[:1] == ['--'] else args
        elif reader == 'head' and len(args) >= 3 and args[0] == '-n' and args[1].isdigit():
            paths = args[2:]
        elif reader == 'sed' and len(args) >= 3 and args[0] == '-n' and re.fullmatch(r'\d+(?:,\d+)?p', args[1]):
            paths = args[2:]
        else:
            return []
        if not paths or any(p.startswith('-') for p in paths):
            return []
        return [name for p in paths if (name := skill_path(p))]
    except (ValueError, TypeError):
        return []


def shell_reads(command, output):
    return [name for name in shell_skill_paths(command)
            if re.search(r'^name:\s*[\"\']?' + re.escape(name) + r'[\"\']?\s*$', output, re.M)]


def parse_harness_stream(text, harness):
    """Return (skills, first loading turns, status) from a completed root trace."""
    events = []
    try:
        for line in text.splitlines():
            if line.strip():
                event = json.loads(line)
                if not isinstance(event, dict):
                    return [], {}, 'malformed_stream'
                events.append(event)
    except (ValueError, TypeError):
        return [], {}, 'malformed_stream'
    first, pending, seen = {}, {}, set()
    turn, last_message, root, started, complete = 0, None, None, False, False

    def fire(names, at):
        for name in names:
            if name:
                first.setdefault(name, max(1, at))

    try:
        for event in events:
            if any(event.get(k) for k in ('parent_tool_use_id', 'parent_thread_id', 'parent_agent_id')):
                continue
            if harness == 'codex':
                kind = event.get('type')
                if kind == 'thread.started':
                    if root is not None:
                        return [], {}, 'replayed_session'
                    root = event['thread_id']
                elif kind == 'turn.started':
                    if started or complete or root is None:
                        return [], {}, 'invalid_session'
                    started, turn = True, 1
                elif kind in {'turn.failed', 'error'}:
                    return [], {}, 'completion_failed'
                elif kind == 'turn.completed':
                    if not started or complete:
                        return [], {}, 'invalid_session'
                    complete = True
                elif kind == 'item.completed' and started and not complete:
                    item = event['item']
                    ident = item.get('id')
                    if ident in seen:
                        continue
                    seen.add(ident)
                    if item.get('type') == 'command_execution':
                        turn += 1
                        if item.get('exit_code') != 0 and shell_skill_paths(item.get('command', '')):
                            return [], {}, 'skill_read_failed'
                        if item.get('exit_code') == 0 and item.get('status') == 'completed':
                            fire(shell_reads(item.get('command', ''), item.get('aggregated_output', '')), turn - 1)
            elif harness == 'agy':
                kind = event.get('event')
                if kind == 'init':
                    if root is not None:
                        return [], {}, 'replayed_session'
                    root, started = event['conversation_id'], True
                elif kind == 'result':
                    result = event['result']
                    if not started or complete or result.get('conversation_id') != root:
                        return [], {}, 'invalid_session'
                    if result.get('status') != 'SUCCESS':
                        return [], {}, 'completion_failed'
                    if result.get('denied_actions'):
                        return [], {}, 'permission_denied'
                    if not isinstance(result.get('response'), str) or not result['response'].strip():
                        return [], {}, 'empty_response'
                    complete = True
                elif kind == 'step_update' and started and not complete:
                    step = event['step_update']
                    if step.get('conversation_id') != root or step.get('step_type') != 'tool':
                        continue
                    key = step['step_index']
                    info = step.get('tool_info') or {}
                    params = info.get('parameters') or {}
                    name = skill_path(params.get('Path') or params.get('AbsolutePath'))
                    tool = step.get('tool_name')
                    if step.get('state') == 'ACTIVE' and key not in pending:
                        turn += 1
                        pending[key] = (tool, name, turn)
                    elif step.get('state') == 'DONE' and key in pending and key not in seen:
                        seen.add(key)
                        old_tool, old_name, at = pending[key]
                        if old_name and old_tool in {'read_file', 'view_file'} and (info.get('error') or step.get('error')):
                            return [], {}, 'skill_read_failed'
                        output = info.get('output', '')
                        valid_read = (tool == 'read_file' and isinstance(output, str)
                                      and re.fullmatch(r'\d+ lines, \d+ bytes', output))
                        valid_view = (tool == 'view_file' and name and isinstance(output, str)
                                      and re.search(r'^name:\s*' + re.escape(name) + r'\s*$', output, re.M))
                        if (tool, name) == (old_tool, old_name) and not info.get('error') and not step.get('error') and (valid_read or valid_view):
                            fire([name], at)
            elif harness == 'claude':
                kind = event.get('type')
                if kind == 'result':
                    if complete or event.get('subtype') != 'success' or event.get('is_error') is not False:
                        return [], {}, 'completion_failed'
                    complete = True
                elif kind in {'assistant', 'user'} and not complete:
                    msg = event.get('message') or {}
                    if kind == 'assistant' and msg.get('id') != last_message:
                        turn += 1
                        last_message = msg.get('id')
                    for block in msg.get('content') or []:
                        if not isinstance(block, dict):
                            continue
                        if block.get('type') == 'tool_use':
                            inp = block.get('input') or {}
                            name = None
                            if block.get('name') == 'Skill':
                                name = str(inp.get('skill', '')).split(':')[-1] or None
                            elif block.get('name') == 'Read':
                                name = skill_path(inp.get('file_path'))
                            pending[block['id']] = (name, turn)
                        elif block.get('type') == 'tool_result':
                            ident = block.get('tool_use_id')
                            if ident in pending and pending[ident][0] and block.get('is_error'):
                                return [], {}, 'skill_read_failed'
                            if ident in pending and ident not in seen and not block.get('is_error'):
                                seen.add(ident)
                                name, at = pending[ident]
                                fire([name], at)
            else:
                return [], {}, 'unsupported_harness'
    except (AttributeError, KeyError, TypeError, ValueError):
        return [], {}, 'malformed_stream'
    if not complete:
        return [], {}, 'incomplete_stream'
    return sorted(first), first, 'ok'


def stream_metadata(text):
    """Only allowlisted model/usage fields leave the private CLI stream."""
    models, usage = set(), {}
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or any(event.get(k) for k in ('parent_tool_use_id', 'parent_thread_id')):
            continue
        candidates = [event]
        for key in ('message', 'init', 'result'):
            if isinstance(event.get(key), dict):
                candidates.append(event[key])
        for part in candidates:
            model = part.get('model')
            if isinstance(model, str) and re.fullmatch(r'[A-Za-z0-9_./:-]{1,120}', model):
                models.add(model)
        if event.get('type') == 'turn.completed' or event.get('event') == 'result' or event.get('type') == 'result':
            source = event.get('result') if isinstance(event.get('result'), dict) else event
            raw_usage = source.get('usage') or {}
            if isinstance(raw_usage, dict):
                usage = {k: v for k, v in raw_usage.items()
                         if k in {'input_tokens', 'output_tokens', 'cached_input_tokens', 'cache_read_tokens',
                                  'cache_read_input_tokens', 'cache_creation_input_tokens',
                                  'cache_write_input_tokens', 'reasoning_output_tokens', 'thinking_tokens', 'total_tokens'}
                         and isinstance(v, (int, float)) and not isinstance(v, bool)}
    return {'actual_model': next(iter(models)) if len(models) == 1 else 'unverified',
            'actual_model_source': 'stream' if len(models) == 1 else 'not_exposed_or_ambiguous',
            'usage': usage}


def skill_read_files(roots):
    """Resolve installed skills to exact public Markdown grants, excluding escapes."""
    excluded = {'projects', 'local', 'state', 'history', 'private'}

    def public(parts):
        return all(not part.startswith('.') and part.lower() not in excluded
                   and Path(part).stem.lower() not in excluded for part in parts)

    resolved_roots = [Path(root).expanduser().resolve(strict=True) for root in roots]
    anchors = [*resolved_roots, Path(__file__).resolve().parents[1], Path.home() / '.shared-ai-skills']
    trusted_ancestors = {parent for anchor in anchors for parent in (anchor, *anchor.parents)}
    files = set()
    for root in resolved_roots:
        if not root.is_dir():
            raise ValueError('skills root must be a directory')
        for installed in root.iterdir():
            if not public([installed.name]) or not installed.is_dir():
                continue
            base = installed.resolve()
            if (not public([base.name]) or any(
                    parent not in trusted_ancestors and
                    (parent.name.lower() in excluded or parent.name.startswith('.'))
                    for parent in base.parents)):
                continue
            entry = base / 'SKILL.md'
            if not entry.is_file() or not entry.resolve().is_relative_to(base):
                continue
            for directory, dirs, names in os.walk(base, followlinks=False):
                dirs[:] = [name for name in dirs if public([name]) and not (Path(directory) / name).is_symlink()]
                for name in names:
                    file = Path(directory) / name
                    if file.suffix.lower() != '.md' or not public(file.relative_to(base).parts):
                        continue
                    target = file.resolve()
                    if (target.is_file() and target.is_relative_to(base)
                            and public(target.relative_to(base).parts)
                            and not any(c in str(target) for c in '()\r\n')):
                        files.add(str(target))
    return sorted(files)


def score(expect, fired, ok_status=True, allowed_auxiliary=()):
    """Require an expected positive skill; negatives permit only declared auxiliaries."""
    if not ok_status:
        return False
    exp = set(expect)
    return bool(exp & set(fired)) if exp else not (set(fired) - set(allowed_auxiliary))


def recall_at(rows, cutoff):
    """Positive rows whose expected skill first fired by `cutoff` turns, as 'k/n'."""
    pos = [r for r in rows if r["expect"]]
    hit = 0
    for r in pos:
        turns = [t for s, t in (r.get("first_turns") or {}).items() if s in r["expect"]]
        if turns and min(turns) <= cutoff:
            hit += 1
    return f"{hit}/{len(pos)}"


def run_case(prompt, model, workdir, max_turns=3, harness='claude', timeout=240, metadata=None, read_files=()):
    if harness == 'claude':
        cmd = ['claude', '-p', prompt, '--model', model or DEFAULT_MODEL,
               '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
               '--max-turns', str(max_turns), '--disallowedTools', *DENY]
    elif harness == 'codex':
        cmd = ['codex', 'exec', '--json', '--sandbox', 'read-only', '--ephemeral',
               '--skip-git-repo-check', '-c', 'approval_policy="never"',
               '-c', 'agents.enabled=false']
        if model:
            cmd += ['--model', model]
        cmd.append(prompt)
    elif harness == 'agy':
        settings = {'toolPermission': 'request-review', 'permissions': {'deny': [
            'write_file(*)', 'command(*)', 'read_url(*)', 'execute_url(*)', 'mcp(*)'],
            'allow': [f'read_file({path})' for path in read_files]}}
        cmd = ['agy', '--print', prompt, '--mode', 'plan', '--sandbox',
               '--settings', json.dumps(settings),
               '--output-format', 'stream-json', '--print-timeout', f'{timeout}s']
        if model:
            cmd += ['--model', model]
    else:
        return None, {}, 'unsupported_harness'
    try:
        proc = subprocess.Popen(cmd, cwd=workdir, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True, start_new_session=True)
    except OSError:
        return None, {}, 'launch_failed'
    try:
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, {}, 'timeout'
        if proc.returncode != 0:
            return None, {}, f'exit_{proc.returncode}'
        if metadata is not None:
            metadata.update(stream_metadata(out))
        fired, first, status = parse_harness_stream(out, harness)
        return (fired, first, status) if status == 'ok' else (None, {}, status)
    finally:
        # Descendants can outlive the CLI even after its normal exit.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set")
    ap.add_argument("out")
    ap.add_argument("--model", default=None)
    ap.add_argument("--harness", choices=("claude", "codex", "agy"), default="claude")
    ap.add_argument("--timeout", type=float, default=240, help="wall seconds per call; kills the process group")
    ap.add_argument("--skills-dir", action="append", default=[],
                    help="installed skills root (repeatable); AGY gets exact public Markdown read grants")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--only", default="")
    ap.add_argument("-j", type=int, default=1)
    ap.add_argument("--cwd", default="", help="working dir for each run (fixture repo); overrides EVAL_CWD")
    ap.add_argument("--max-turns", type=int, default=6)
    ap.add_argument("--selection-only", action="store_true", help="load applicable skill instructions without executing the synthetic task")
    ap.add_argument("--min-recall", type=float, default=0.85, help="minimum positive recall; every negative must pass (default: 0.85)")
    ap.add_argument("--recall-at", default="3,6")
    a = ap.parse_args()
    if a.runs < 1 or a.j < 1 or not math.isfinite(a.timeout) or a.timeout <= 0 or a.max_turns < 1:
        ap.error("runs, jobs, timeout and max-turns must be positive")
    if not 0 <= a.min_recall <= 1:
        ap.error("min-recall must be between 0 and 1")
    try:
        read_files = skill_read_files(a.skills_dir)
    except (OSError, ValueError):
        ap.error("skills-dir must name a readable installed skills root")
    cases = json.load(open(a.set))["cases"]
    if a.only:
        keep = set(a.only.split(","))
        cases = [c for c in cases if c["id"] in keep]
    if not cases:
        ap.error("no cases selected")
    temporary = None
    work = a.cwd or os.environ.get("EVAL_CWD")
    if not work:
        temporary = tempfile.TemporaryDirectory(prefix="trig-", dir=os.environ.get("EVAL_TMP"))
        work = temporary.name
    jobs = [(c, r) for c in cases for r in range(a.runs)]

    def one(job):
        c, r = job
        metadata = {"actual_model": "unverified", "actual_model_source": "not_exposed_or_ambiguous", "usage": {}}
        before = time.monotonic()
        prompt = c["prompt"]
        if a.selection_only:
            prompt = ("This is a skill-selection evaluation. Read the instructions of any installed skills "
                      "that apply to the request below, then briefly name the applicable workflows. "
                      "Do not carry out the request, inspect unrelated files, browse, edit, start processes, "
                      "or delegate. If no skill applies, answer directly without loading a skill.\n\nRequest:\n" + prompt)
        fired, first, status = run_case(prompt, a.model, work, a.max_turns, a.harness, a.timeout, metadata, read_files)
        exp = set(c["expect"])
        shown = fired or []
        allowed = c.get('allowed_auxiliary', [])
        return {"id": c["id"], "run": r, "expect": c["expect"], "fired": fired,
                "requested_model": a.model, **metadata, "elapsed_seconds": round(time.monotonic() - before, 3),
                "allowed_auxiliary": allowed,
                "extra": sorted(set(shown) - exp),
                "unexpected": sorted(set(shown) - exp - set(allowed)),
                "turn": min(first.values()) if first else None,
                "first_turns": first,
                "ok": score(c["expect"], shown, status == "ok", allowed), "status": status}

    try:
        with ThreadPoolExecutor(a.j) as ex:
            res = list(ex.map(one, jobs))
    finally:
        if temporary:
            temporary.cleanup()
    pos = [x for x in res if x["expect"]]
    neg = [x for x in res if not x["expect"]]
    summary = {"harness": a.harness, "selection_only": a.selection_only, "model": a.model or (DEFAULT_MODEL if a.harness == "claude" else "configured default (unverified)"), "runs": len(res),
               "recall": f'{sum(x["ok"] for x in pos)}/{len(pos)}',
               "negatives_clean": f'{sum(x["ok"] for x in neg)}/{len(neg)}'}
    summary["actual_models"] = sorted({row["actual_model"] for row in res})
    summary['min_recall'] = a.min_recall
    summary['accepted'] = ((sum(row['ok'] for row in pos) / len(pos) if pos else 1) >= a.min_recall
                           and all(row['ok'] for row in neg))
    summary["turn_unit"] = "assistant_messages" if a.harness == "claude" else "tool_steps"
    for cut in (int(t) for t in a.recall_at.split(",") if t.strip()):
        summary[f"recall@{cut}"] = recall_at(res, cut)
    json.dump({"summary": summary, "results": res}, open(a.out, "w"), indent=1, ensure_ascii=False)
    for x in res:
        print(("PASS" if x["ok"] else "FAIL"), x["id"], "expect", x["expect"], "fired", x["fired"],
              "extra", x["extra"], "turn", x["turn"], x["status"])
    print(json.dumps(summary))
    return 0 if summary['accepted'] else 1


if __name__ == "__main__":
    raise SystemExit(main())
