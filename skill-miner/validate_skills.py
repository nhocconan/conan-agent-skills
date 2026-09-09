#!/usr/bin/env python3
"""
validate_skills.py — check SKILL.md files against Anthropic's published authoring spec.

Rules encoded (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

  ERROR   frontmatter must open with `---` on line 1
  ERROR   `name` required; <=64 chars; [a-z0-9-] only
  ERROR   local convention: `name` must equal the directory name
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

try:
    import yaml
except ModuleNotFoundError:  # validator must still run on a bare interpreter
    yaml = None
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9-]+$")
XML_RE = re.compile(r"<[a-zA-Z/][^>]*>")
RESERVED = ("anthropic", "claude")
PRIVATE_PARTS = {".git", ".vendor", "history", "project-private", "private", "local", "state"}
LINK_RE = re.compile(
    r"\[[^\]]+\]\(\s*(?:<([^>]+)>|([^\s)#]+(?:#[^\s)]*)?))"
)
CODE_PATH_RE = re.compile(
    r"(?<![\w./-])((?:\.\.?/)?(?:[\w.-]+/)*[\w.-]+\.md(?:#[\w.-]+)?)"
)
WHEN_HINTS = ("use when", "use this", "use for", "use it", "use proactively",
              "trigger", "apply when", "apply proactively", "invoke when", "run before",
              "run after", "when the user", "when working", "when building",
              "when reviewing", "when creating", "when asked", "before ", "after ")
FIRST_PERSON = ("i can ", "i will ", "you can use this", "we ")


def parse_frontmatter(text: str):
    """Return (fields, body, opened_ok)."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, text, False
    end = next((i for i, line in enumerate(lines[1:], 1) if line == "---"), None)
    if end is None:
        return {}, text, False
    raw, body = "\n".join(lines[1:end]), "\n".join(lines[end + 1:])
    fields, key = {}, None
    for line in raw.split("\n"):
        m = re.match(r"^([a-zA-Z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[key] = value
        elif key and line.strip():
            fields[key] += " " + line.strip()
    # YAML is the source of truth when available: this correctly unwraps quoted
    # scalars and block descriptions. The line parser above remains the fallback
    # for bare interpreters where PyYAML is intentionally unavailable.
    if yaml is not None:
        try:
            parsed = yaml.safe_load(raw)
        except Exception:
            pass
        else:
            if isinstance(parsed, dict):
                fields = parsed
    return fields, body, True


def _reference_target(raw: str) -> str | None:
    """Return a local relative .md path, or None for non-local/placeholder text."""
    target = raw.strip().split("#", 1)[0].split("?", 1)[0]
    if not target or target.startswith(("#", "~", "$", "/")):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    if re.match(r"^[A-Za-z]:[\\/]", target) or any(c in target for c in "<>*?{}"):
        return None
    return target


def _references(text: str):
    """Yield (path, is_markdown_link) references from one document."""
    for match in LINK_RE.finditer(text):
        target = match.group(1) or match.group(2)
        target = _reference_target(target)
        if target and target.lower().endswith(".md"):
            yield target, True
    for code in re.findall(r"`([^`\n]+)`", text):
        # Angle-bracket placeholders are examples, not repository references.
        if "<" in code or ">" in code:
            continue
        for match in CODE_PATH_RE.finditer(code):
            target = _reference_target(match.group(1))
            if target and target.lower().endswith(".md"):
                yield target, False


def _inside(root: Path, target: Path) -> bool:
    """Keep validation inside the skill; never read sibling/private trees."""
    try:
        relative = target.relative_to(root)
    except ValueError:
        return False
    # senior-operator/projects is explicitly gitignored and can contain employer
    # context. Do not recurse into it even when a local path happens to resolve.
    if root.name == "senior-operator" and relative.parts[:1] == ("projects",):
        return False
    return not any(part in PRIVATE_PARTS for part in relative.parts)


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

    # Claude Code parses this frontmatter leniently; Codex and agy parse it as
    # real YAML. An unquoted scalar containing ": " (very easy to write in a
    # description full of trigger phrases) is valid to one and a syntax error to the
    # others — the skill then silently fails to register outside Claude. Fix by making
    # the value a block scalar (`description: >-`) or quoting it.
    if opened and yaml is not None:
        lines = text.splitlines()
        end = next((i for i, line in enumerate(lines[1:], 1) if line == "---"), None)
        raw = "\n".join(lines[1:end]) if end is not None else ""
        try:
            parsed = yaml.safe_load(raw)
        except Exception as e:
            errors.append(
                "frontmatter is not valid YAML — Codex/agy will reject it "
                f"({str(e).splitlines()[0]}); use `description: >-` or quote the value"
            )
        else:
            if not isinstance(parsed, dict):
                errors.append("frontmatter does not parse to a mapping")

    raw_name = fields.get("name", "")
    name = raw_name if isinstance(raw_name, str) else str(raw_name) if raw_name is not None else ""
    if raw_name not in ("", None) and not isinstance(raw_name, str):
        errors.append("`name` must be a string")
    raw_desc = fields.get("description", "")
    desc = " ".join(raw_desc.split()) if isinstance(raw_desc, str) else ""
    if raw_desc not in ("", None) and not isinstance(raw_desc, str):
        errors.append("`description` must be a string")

    if not name:
        errors.append("missing `name`")
    else:
        if len(name) > 64:
            errors.append(f"`name` is {len(name)} chars (max 64)")
        if not NAME_RE.match(name):
            errors.append(f"`name` '{name}' must be lowercase letters/numbers/hyphens only")
        if name != skill_dir.name:
            errors.append(
                f"local convention: `name` '{name}' != directory '{skill_dir.name}'"
            )
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

    # Follow local references recursively. Progressive-disclosure routers may
    # intentionally route to another sibling; report only an actually missing
    # source-relative path, never the depth of an existing reference.
    root = skill_dir.resolve()
    queue = [(sk.resolve(), body)]
    seen = {sk.resolve()}
    while queue:
        source, source_body = queue.pop(0)
        for rel, is_link in sorted(set(_references(source_body))):
            candidates = [source.parent / rel]
            # Backtick paths are often commands documented from the skill root;
            # retain that convention after trying the source-relative location.
            if not is_link:
                candidates.append(skill_dir / rel)
            target = next((candidate.resolve() for candidate in candidates
                           if candidate.exists()), None)
            if target is None:
                # Code spans commonly document paths in the target project (for
                # example `CLAUDE.md`) and are not links from this skill. Validate
                # them when they resolve locally, but do not turn examples into
                # false missing-file warnings.
                if not is_link:
                    continue
                missing = (source.parent / rel).resolve()
                if _inside(root, missing):
                    warns.append(f"{source.relative_to(root)}: referenced file missing: {rel}")
                continue
            if not _inside(root, target) or not target.is_file() or target in seen:
                continue
            seen.add(target)
            try:
                sub = target.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            sub_lines = len(sub.split("\n"))
            head = "\n".join(sub.split("\n")[:40]).lower()
            if sub_lines > 100 and not any(k in head for k in ("## contents", "## table of contents",
                                                               "# contents", "toc")):
                warns.append(f"{target.relative_to(root)} is {sub_lines} lines with no table of contents")
            queue.append((target, sub))
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--errors-only", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    # Only directories that actually define a skill are skills. This lets the
    # repository grow test/docs/support folders without false "no SKILL.md" errors.
    dirs = sorted(p for p in root.iterdir()
                  if p.is_dir() and not p.name.startswith(".") and (p / "SKILL.md").is_file())

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
