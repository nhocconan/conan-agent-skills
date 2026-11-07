#!/usr/bin/env python3
"""Mechanical slop audit. Modes: --base REV [scope...] (added lines only), --paths P... (whole files).
Exit 0 clean, 1 errors, 2 usage. Same-line exception: `audit-ok-slop: <reason>` (reason "TODO" rejected)."""
import argparse, os, re, subprocess, sys

EXTS = (".ts", ".tsx", ".js", ".jsx", ".py")
SKIP_DIRS = {".git", ".vendor", ".agents", "node_modules"}
TEST_PATH = re.compile(r"\.(test|spec)\.|/tests?/|/__tests__/|/test_[^/]*\.py$")
MARKER = re.compile(r"audit-ok-slop:\s*(\S.*)")
VERBS = r"(Added|Removed|Changed|Updated|Fixed|Refactored|Moved|Renamed)"
NARRATION = re.compile(VERBS + r"\b.{0,60}\b(per|for|as requested|in response to)\b.{0,40}\b(task|ticket|issue|PR|review|request|user)\b")
SHA = re.compile(r"\b(?:commit|sha)[: ]\s*(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b", re.I)
DIRECTIVE = re.compile(r"type:|noqa|pragma|eslint-|@ts-|prettier-|-\*-")
CODE_CHARS = re.compile(r"[=({}\[;'\"]")
# E6 = statement shapes only (error); W10 = loose code-like prose (warning)
PY_STMT = re.compile(r"(import \w[\w.]*( as \w+)?|from [\w.]+ import [\w*, ]+|def \w+\(.*\):|class \w+(\(.*\))?:"
                     r"|return(\s+[\w.]+\(.*\))?)$")
JS_STMT_E = re.compile(r"((import|export)\b.*\bfrom\s+['\"].*|import\s+['\"].*|(const|let|var)\s+[\w$]+\s*=[^=].*"
                       r"|[\w$.]+\(.*\)\s*;|(return|await|throw)\b.*;)$")
PY_CODE = re.compile(r"(import [\w.]+( as \w+)?|from [\w.]+ import [\w*, ]+|def \w+\(.*|class \w+[:(].*|return\b.*)$")
JS_STMT = re.compile(r"([\w$.]+(\(|\s*=[^=])|(await|throw|import|export|const|let|var|return)\b)")
JS_CODE = re.compile(r"(import|export|const|let|var|return)\s")
LOG = r"(?:console\w*|logger\w*|log\b|\w*[lL]ogger\w*|\w*[lL]ogSpy)[\w.]*"
# (code, regex on code, fix); applied to test files only
CODE_RULES = [
    ("E1", r"\.only\(|\b(fit|fdescribe)\(", "remove the focus; it silently skips the rest of the suite"),
    ("E2", r"waitForTimeout\(", "wait on a condition (locator/expect/response), not a fixed delay"),
    ("E3", r"expect\((true|false|1)\)\.toBe\(\1\)", "assert a real outcome or delete the test"),
    ("E3py", r"^\s*assert (True|1 == 1)\s*$", "assert a real outcome or delete the test"),
    ("E4", r"expect\(\s*" + LOG + r"\s*\)\.toHaveBeenCalled(Times)?\(", "assert the behavior, not that something was logged"),
    ("W1", r"expect\(\s*(registry|catalog|routes|handlers|all|list)\s*\)\.toHaveLength\(", "assert membership, not a count that rises with every addition"),
    ("W2", r"toMatchSnapshot\(\s*\)", "name the snapshot or assert specific fields"),
    ("W3", r"\b(it|test)\(\s*['\"](works|should work|test|renders|basic)['\"]", "title the behavior under test"),
    ("W6", r"readFileSync\([^)]*\.(ts|js|tsx|jsx)\b", "test behavior, not source text"),
    ("W8py", r"time\.sleep\(", "poll a condition instead of sleeping"),
]
# "py" suffix = Python-only; the rest are JS/TS-only (fixture strings in Python tests would match)
CODE_RULES = [(c[:2], c.endswith("py"), re.compile(r), t) for c, r, t in CODE_RULES]

def find_comment(line, py):
    """Index of a real comment marker: outside strings, at line start or after whitespace."""
    q = None
    i = 0
    while i < len(line):
        ch = line[i]
        if q:
            if ch == "\\":
                i += 1
            elif ch == q:
                q = None
        elif ch in "'\"" or (ch == "`" and not py):
            q = ch
        elif (py and ch == "#") or (not py and line.startswith("//", i)):
            if i == 0 or line[i - 1].isspace():
                return i
            if not py:
                i += 1
        i += 1
    return -1

def comment_lines(lines, py):
    """Yield (idx, code_before, comment_text, standalone) skipping docstrings/blocks/templates."""
    state = None  # open multi-line string/block delimiter
    for n, line in enumerate(lines):
        s = line.strip()
        delims = ('"""', "'''") if py else ("`",)
        if state:
            if state == "*/" and "*/" in line or state != "*/" and line.count(state) % 2:
                state = None
            continue
        if not py and (s.startswith("*") or s.startswith("/*")):
            if "*/" not in s:
                state = "*/"
            continue
        opened = next((d for d in delims if line.count(d) % 2), None)
        if opened:
            state = opened
            continue
        i = find_comment(line, py)
        if i >= 0 and not s.startswith("#!"):
            yield n, line[:i], line[i + (1 if py else 2):].strip(), not line[:i].strip()

def scan(path, text, only_lines=None):
    py = path.endswith(".py")
    is_test = bool(TEST_PATH.search("/" + path.replace(os.sep, "/")))
    lines = text.splitlines()
    out = []
    def add(n, code, snippet, fix):
        if only_lines is not None and n + 1 not in only_lines:
            return
        m = MARKER.search(lines[n])
        if m and not m.group(1).strip().upper().startswith("TODO"):
            return
        out.append((path, n + 1, code, snippet.strip()[:80], fix))
    comments = {n: (cb, ct, st) for n, cb, ct, st in comment_lines(lines, py)}
    for n, line in enumerate(lines):
        code = comments[n][0] if n in comments else line
        if is_test:
            for c, py_only, rx, fix in CODE_RULES:
                if py == py_only and rx.search(code):
                    add(n, c, line, fix)
        if n not in comments:
            continue
        _, ct, standalone = comments[n]
        if SHA.search(ct) or NARRATION.search(ct):
            add(n, "E5", line, "state what the code does; history belongs in the commit message")
        elif re.match(VERBS + r"\b(?![-\w])", ct):
            add(n, "W9", line, "describe current behavior, not the edit made")
        if not ct or DIRECTIVE.search(ct):
            continue
        looks_code = (PY_CODE.match(ct) and (not ct.startswith("return") or CODE_CHARS.search(ct))) if py else (
            (ct.endswith(";") and JS_STMT.match(ct)) or (JS_CODE.match(ct) and CODE_CHARS.search(ct)))
        if (PY_STMT if py else JS_STMT_E).match(ct):
            add(n, "E6", line, "delete commented-out code; git keeps history")
        elif looks_code:
            add(n, "W10", line, "if this is disabled code, delete it; if prose, reword")
        if re.search(r"\b(TODO|FIXME)\b(?!\s*\(|\s*:?\s*#\d)", ct):
            add(n, "W4", line, "name an owner: TODO(name) or TODO #id")
        if re.search(r"\b\d{4}-\d{2}-\d{2}\b|\b(?!(?:UTF|RFC|SHA|ISO|ES|TLS|AES|HTTP|IPV|MD|GPT)-)[A-Z]{2,}-\d+\b", ct):
            add(n, "W7", line, "dates and ticket ids rot; state the reason instead")
        toks = {t.lower() for t in re.findall(r"[A-Za-z_]\w{2,}", ct)}
        nxt = lines[n + 1] if n + 1 < len(lines) else ""
        if standalone and len(toks) >= 3 and (n + 1) not in comments and (n - 1) not in comments and nxt.strip() \
                and toks <= {t.lower() for t in re.findall(r"[A-Za-z_]\w*", nxt)}:
            add(n, "W5", line, "comment restates the next line; delete or explain why")
    return out

def git(*args):
    p = subprocess.run(["git", *args], capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"git {args[0]} failed: " + p.stderr.strip())
    return p.stdout

def added_lines(base, scope):
    """Repo-root paths -> added line numbers; untracked files count as wholly added."""
    top = git("rev-parse", "--show-toplevel").strip()
    scope = [os.path.relpath(os.path.abspath(s), top) for s in scope]
    os.chdir(top)
    res, cur = {}, None
    for f in git("ls-files", "--others", "--exclude-standard", "-z", "--", *scope).split("\0"):
        if f:
            res[f] = None
    for l in git("diff", "-U0", "--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/",
                 base, "--", *scope).splitlines():
        if l.startswith("+++ "):
            cur = l[6:] if l.startswith("+++ b/") else None
            if cur:
                res[cur] = set()
        elif l.startswith("@@") and cur:
            m = re.search(r"\+(\d+)(?:,(\d+))?", l)
            start, cnt = int(m.group(1)), int(m.group(2) or 1)
            res[cur].update(range(start, start + cnt))
    return res

def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for r, ds, fs in os.walk(p):
                ds[:] = [d for d in ds if d not in SKIP_DIRS]
                yield from (os.path.join(r, f) for f in sorted(fs) if f.endswith(EXTS))
        else:
            yield p

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", metavar="REV", help="judge only lines added since REV")
    ap.add_argument("--paths", nargs="+", metavar="P", help="scan whole files or directories")
    ap.add_argument("scope", nargs="*", help="with --base: limit to these paths")
    a = ap.parse_args(argv)
    if bool(a.base) == bool(a.paths) or (a.paths and a.scope):
        ap.error("give exactly one of --base REV [scope...] or --paths P...")
    targets = {p: None for p in walk(a.paths)} if a.paths else added_lines(a.base, a.scope)
    found = []
    for path, only in targets.items():
        if not path.endswith(EXTS) or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            found += scan(path, f.read(), only)
    for p, n, c, snip, fix in sorted(found)[:150]:
        print(f"{p}:{n} {c} {snip} -> {fix}")
    errs = sum(1 for f in found if f[2][0] == "E")
    print(f"total: {errs} errors, {len(found) - errs} warnings" + (" (output capped at 150)" if len(found) > 150 else ""))
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
