#!/usr/bin/env python3
"""
validate_skills.py — check SKILL.md files against Anthropic's published authoring spec.

Rules encoded (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

  ERROR   frontmatter must open with `---` on line 1
  ERROR   `name` required; <=64 chars; [a-z0-9-] only; must equal the directory name
  ERROR   `name` must not contain the reserved words "anthropic" or "claude"
  ERROR   `description` required, non-empty, <=1024 chars
  ERROR   no XML tags in `name` or `description`
  WARN    SKILL.md body <=500 lines (else split via progressive disclosure)
  WARN    description should say when to use it, not just what it does
  WARN    description should be third person (not "I can" / "you can")
  WARN    referenced files must exist, and be one level deep from SKILL.md
  WARN    reference files >100 lines should start with a table of contents
  WARN    no Windows-style backslash paths

Usage:
  python3 validate_skills.py                 # the conan skills repo
  python3 validate_skills.py ~/.claude/skills  # everything installed
  python3 validate_skills.py --errors-only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9-]+$")
XML_RE = re.compile(r"<[a-zA-Z/][^>]*>")
RESERVED = ("anthropic", "claude")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)\)")
WHEN_HINTS = ("use when", "use this", "use for", "use it", "use proactively",
              "trigger", "apply when", "apply proactively", "invoke when", "run before",
              "run after", "when the user", "when working", "when building",
              "when reviewing", "when creating", "when asked", "before ", "after ")
FIRST_PERSON = ("i can ", "i will ", "you can use this", "we ")


def parse_frontmatter(text: str):
    """Return (fields, body, opened_ok)."""
    if not text.startswith("---"):
        return {}, text, False
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, False
    raw, body = text[3:end], text[end + 4:]
    fields, key = {}, None
    for line in raw.split("\n"):
        m = re.match(r"^([a-zA-Z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()
    return fields, body, True


def check(skill_dir: Path):
    errors, warns = [], []
    sk = skill_dir / "SKILL.md"
    if not sk.exists():
        return ["no SKILL.md"], []
    try:
        text = sk.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [f"unreadable: {e}"], []

    fields, body, opened = parse_frontmatter(text)
    if not opened:
        errors.append("frontmatter does not open with `---` (never parsed → skill cannot trigger)")

    name = fields.get("name", "")
    desc = " ".join(fields.get("description", "").split())

    if not name:
        errors.append("missing `name`")
    else:
        if len(name) > 64:
            errors.append(f"`name` is {len(name)} chars (max 64)")
        if not NAME_RE.match(name):
            errors.append(f"`name` '{name}' must be lowercase letters/numbers/hyphens only")
        if name != skill_dir.name:
            errors.append(f"`name` '{name}' != directory '{skill_dir.name}'")
        for w in RESERVED:
            if w in name.lower():
                errors.append(f"`name` contains reserved word '{w}'")
        if XML_RE.search(name):
            errors.append("`name` contains an XML tag")

    if not desc:
        errors.append("missing/empty `description`")
    else:
        if len(desc) > 1024:
            errors.append(f"`description` is {len(desc)} chars (max 1024)")
        if XML_RE.search(desc):
            errors.append("`description` contains an XML tag")
        low = desc.lower()
        if not any(h in low for h in WHEN_HINTS):
            warns.append("`description` never says WHEN to use it — it is a trigger, not a summary")
        if any(p in low for p in FIRST_PERSON):
            warns.append("`description` is not third person")
        if len(desc) < 60:
            warns.append(f"`description` is only {len(desc)} chars — too thin to route on")

    n_lines = len(body.split("\n"))
    if n_lines > 500:
        warns.append(f"body is {n_lines} lines (>500) — split via progressive disclosure")

    # Windows paths, excluding shell/regex escapes (\n \t \r \0 \\ \d \s \w …)
    if re.search(r"[A-Za-z0-9_]\\(?![ntr0\\dswbAZ.*+?()\[\]{}|^$'\"])[A-Za-z0-9_]", body):
        warns.append("possible Windows-style path (use forward slashes)")

    # referenced files: must exist, and their own links must not go a further level deep
    for rel in set(LINK_RE.findall(body)):
        if rel.startswith(("http://", "https://")):
            continue
        target = (skill_dir / rel).resolve()
        if not target.exists():
            warns.append(f"referenced file missing: {rel}")
            continue
        try:
            sub = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sub_lines = len(sub.split("\n"))
        head = "\n".join(sub.split("\n")[:40]).lower()
        if sub_lines > 100 and not any(k in head for k in ("## contents", "## table of contents",
                                                           "# contents", "toc")):
            warns.append(f"{rel} is {sub_lines} lines with no table of contents")
        for nested in set(LINK_RE.findall(sub)):
            # a back-link to SKILL.md is navigation, not a deeper level
            if Path(nested).name == "SKILL.md" or nested.startswith(("http://", "https://")):
                continue
            if (target.parent / nested).exists():
                warns.append(f"nested reference {rel} → {nested} (keep links one level deep)")
                break
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--errors-only", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    dirs = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))

    n_err = n_warn = 0
    for d in dirs:
        errors, warns = check(d)
        if not errors and (args.errors_only or not warns):
            continue
        n_err += len(errors)
        n_warn += len(warns)
        print(f"\n{d.name}")
        for e in errors:
            print(f"  ERROR  {e}")
        if not args.errors_only:
            for w in warns:
                print(f"  warn   {w}")

    print(f"\n{'='*60}\n{len(dirs)} skills · {n_err} errors · {n_warn} warnings")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
