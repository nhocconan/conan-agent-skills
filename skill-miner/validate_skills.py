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

Local, repo-specific rules (AGENTS.md) added on top of the platform spec:

  ERROR   `§N` / `SKILL.md §x` cross-references resolve to a real heading
          (bare `§N` — anywhere in the skill; `SKILL.md §x` — in SKILL.md
          itself). Fenced code blocks (``` ... ```) are not scanned: they
          are examples, not live citations. If a skill has no `§` headings
          at all, any `§` citation inside it is an error.
  ERROR   (repo-wide, not per-skill) a `gpt-N`/`claude-{opus,sonnet,haiku,
          fable,mythos}-`/`gemini-N` model-ID literal outside
          agent-orchestration/sections/routing.md — the canonical routing
          policy. A line containing the marker `model-id-allow` is exempt.
  WARN    house-style slop ban-list (senior-operator/OPERATING-MANUAL.md,
          "Self-praise" rule) — read dynamically from that file at import
          time so it tracks edits there; quoted spans (`"…"`/`"…"`) are
          skipped since frontmatter `description` fields quote user
          trigger phrases on purpose.

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

# --- cross-reference (§) check -------------------------------------------------
# A heading line that opens a numbered section. Two spellings are both live in
# this repo: the "§" glyph form ("## §5. Astra's quality gate", "## §OP.") and
# a plain numbered form with no glyph at all ("## 0. [CORE] Preconditions",
# "### 3b. [DEV] ...", "## 4 · Pedagogy — ..." with a middle-dot separator).
# The glyph form allows a pure-letter token (§OP); the plain form requires at
# least one digit, an optional single letter, then one of ". ) ·  :" — else
# "## 2026 Report" would look like a numbered heading.
HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:§(?P<glyph>[A-Za-z0-9]+)\b"
    r"|(?P<plain>\d+[A-Za-z]?)\s*[.)·:])"
)
# A citation in prose: an optional local filename immediately before the "§"
# (backticks/whitespace allowed in between — "`SKILL.md` §5.6",
# "BOOTSTRAP.md §4b", "reference.md §9") resolves against THAT file's own
# headings; a bare "§N" resolves against the whole skill's headings. The
# filename may be a real ".md" path, or a bare ALL-CAPS document stem used
# without its extension ("OPERATING-MANUAL §4" for OPERATING-MANUAL.md) —
# common when the file is named a line earlier and the reference wraps.
CITE_RE = re.compile(
    r"(?:(?P<file>[\w./<>-]*\.md|[A-Z][A-Z-]{2,})[`\s]*)?§(?P<token>[A-Za-z0-9]+)"
)
FENCE_RE = re.compile(r"^\s*`{3,}")
# "§N" used as a literal fill-in-the-number placeholder in documentation about
# the citation convention itself (senior-operator/DISTILL.md, PLAYBOOK.md) —
# never a real section number, so never worth resolving.
CITE_PLACEHOLDER_TOKENS = {"N"}
LINT_ALLOW_MARKER = "lint-allow"

# --- model-ID containment check -------------------------------------------------
MODEL_ID_RE = re.compile(
    r"\b(?:gpt-[0-9][A-Za-z0-9_.-]*"
    r"|claude-(?:opus|sonnet|haiku|fable|mythos)-[A-Za-z0-9_.-]*"
    r"|gemini-[0-9][A-Za-z0-9_.-]*)"
)
MODEL_ID_ALLOW_MARKER = "model-id-allow"
ROUTING_POLICY_REL = Path("agent-orchestration") / "sections" / "routing.md"
MODEL_ID_SKIP_DIRS = {".git", "__pycache__", ".vendor", "node_modules", ".agents"} | PRIVATE_PARTS
MODEL_ID_SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2",
    ".zip", ".mp4", ".mov", ".gz", ".pyc",
}
# This checker's own test fixtures synthesize model-ID-shaped strings as
# isolated test data (AGENTS.md: tests use isolated fixtures) — that is not
# real documentation duplicating routing.md, so it is not a repo violation to
# route to anyone. Skip this one directory, by exact
# relative path, rather than every "tests/" directory in the repo (a skill's
# own tests/ folder with real duplicated content should still be caught).
MODEL_ID_SELF_TEST_DIR = ("skill-miner", "tests")

# --- banned-word (house-style slop) check ---------------------------------------
# Read from senior-operator/OPERATING-MANUAL.md's "Self-praise" ban-list line so
# this tracks that file instead of duplicating a hand-typed word list that can
# drift out of sync with it. Falls back to a fixed snapshot if that file is
# unreadable (bare-interpreter installs, or ~/.claude/skills without it).
DEFAULT_BANNED_TERMS = ("successfully", "comprehensive", "robust", "seamless",
                         "hoàn thành xuất sắc")
QUOTED_SPAN_RE = re.compile(r'"[^"]*"|“[^”]*”')


def load_banned_terms(manual_path: "Path | None" = None) -> tuple[str, ...]:
    """Parse the quoted self-praise terms out of OPERATING-MANUAL.md.

    Looks for the bullet starting "**Self-praise.**" and pulls every
    double-quoted span out of it. Never raises: any read/parse failure falls
    back to DEFAULT_BANNED_TERMS so the check still runs.
    """
    path = manual_path or (
        Path(__file__).resolve().parent.parent / "senior-operator" / "OPERATING-MANUAL.md"
    )
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return DEFAULT_BANNED_TERMS
    line = next((l for l in text.splitlines() if "Self-praise" in l), None)
    if not line:
        return DEFAULT_BANNED_TERMS
    terms = tuple(m.group(0)[1:-1] for m in QUOTED_SPAN_RE.finditer(line))
    return terms or DEFAULT_BANNED_TERMS


BANNED_TERMS = load_banned_terms()


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


def _skill_markdown_files(skill_dir: Path):
    """Every authored .md file in this skill (private/gitignored trees, and
    hidden dotfiles like `.upstream-preview.md` — a vendored snapshot of an
    upstream skill kept for diffing, not this repo's own content — excluded)."""
    root = skill_dir.resolve()
    return sorted(
        p.resolve() for p in skill_dir.rglob("*.md")
        if p.is_file() and not p.name.startswith(".") and _inside(root, p.resolve())
    )


def _non_fenced_lines(text: str):
    """Yield (1-based lineno, line) skipping anything inside ``` fences.

    Template/example blocks routinely show placeholder `§N` citations for a
    hypothetical *other* project (see agent-orchestration/TEMPLATES.md's brief
    template) — those are documentation of a convention, not a live citation
    into this skill, so they must not be scanned.
    """
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield lineno, line


def _non_fenced_paragraphs(text: str):
    """Yield (first-lineno, joined text) for citation scanning.

    Markdown hard-wraps prose ("...see `senior-operator`\\nOPERATING-MANUAL
    §4.") — a citation split across that soft line break would never be seen
    as one unit by a plain per-line scan. Consecutive non-blank, non-heading
    lines (already fence-filtered) are joined with a space; a blank line or a
    heading starts a new paragraph.
    """
    paragraphs = []
    buf: list[str] = []
    start = None
    for lineno, line in _non_fenced_lines(text):
        if not line.strip() or HEADING_RE.match(line):
            if buf:
                paragraphs.append((start, " ".join(buf)))
                buf = []
            continue
        if not buf:
            start = lineno
        buf.append(line.strip())
    if buf:
        paragraphs.append((start, " ".join(buf)))
    return paragraphs


def _resolve_named_file(skill_dir: Path, raw: str) -> "Path | None":
    """Resolve a citation's named `.md` file to a real path inside this skill.

    Tries the path as given (relative to the skill root — "SKILL.md",
    "reference/launch-and-growth.md"), then falls back to a same-name search
    anywhere in the skill (a citation naming just "reference.md" without its
    real subdirectory). Returns None — meaning "skip, unverifiable" — for a
    templated placeholder ("projects/<slug>.md"), a name that isn't actually
    in this skill (a different skill, or an external project's own file), or
    anything outside the skill boundary.
    """
    if "<" in raw or ">" in raw:
        return None  # "projects/<slug>.md" — a template placeholder, not a path
    if not raw.lower().endswith(".md"):
        raw = raw + ".md"  # bare stem, e.g. "OPERATING-MANUAL" for OPERATING-MANUAL.md
    root = skill_dir.resolve()
    direct = (skill_dir / raw).resolve()
    if direct.is_file() and _inside(root, direct):
        return direct
    basename = Path(raw).name
    for candidate in skill_dir.rglob(basename):
        resolved = candidate.resolve()
        if resolved.is_file() and _inside(root, resolved):
            return resolved
    return None


def _names_a_document(skill_dir: Path, raw: str) -> bool:
    """Is a citation's prefix a document name (so a miss means "outside this
    skill, unverifiable") or just a capitalised word before a "§"?

    A ".md" path or a templated placeholder always is. A bare ALL-CAPS stem
    ("OPERATING-MANUAL") is only if some `<STEM>.md` exists in a sibling skill;
    otherwise "MUST §5" / "EVERY §5.2" would be silently skipped as a file miss
    instead of resolved as the bare citation it is.
    """
    if raw.lower().endswith(".md") or "<" in raw or ">" in raw:
        return True
    name = raw + ".md"
    repo = skill_dir.resolve().parent
    for pattern in (f"*/{name}", f"*/*/{name}", f"*/*/*/{name}"):
        for hit in repo.glob(pattern):
            parents = hit.relative_to(repo).parts[:-1]
            if hit.is_file() and not any(
                part in PRIVATE_PARTS or part.startswith(".") for part in parents
            ):
                return True
    return False


def check_cross_references(skill_dir: Path):
    """§-citations must resolve to a real heading (see module docstring).

    - "`<file>.md` §x" resolves against THAT file's own headings if the named
      file exists in this skill; if it names a file this skill doesn't have
      (another skill, an external project's own file, a templated
      placeholder), it is unverifiable from here and is skipped, never
      errored — verifying another skill's or another repo's content is out
      of scope for a per-skill check. A bare ALL-CAPS prefix counts as a
      filename only when `<PREFIX>.md` exists in some sibling skill; else it
      is an ordinary word ("MUST §5") and the citation is treated as bare.
    - a bare "§N" (no filename on the same citation) resolves against every
      heading in the whole skill.
    Both skip citations inside fenced code blocks (examples, not live
    citations) and inside quoted spans (`"§33"` as a written-out example of
    the citation convention itself), and the literal placeholder token "N".
    A line containing the marker `lint-allow` is a deliberate, documented
    exception and is skipped entirely.
    """
    root = skill_dir.resolve()
    errors = []
    md_files = _skill_markdown_files(skill_dir)
    texts = {}
    for f in md_files:
        try:
            texts[f] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

    skill_headings: set[str] = set()
    file_headings: dict[Path, set[str]] = {}
    for f, text in texts.items():
        headings = file_headings.setdefault(f.resolve(), set())
        for _, line in _non_fenced_lines(text):
            m = HEADING_RE.match(line)
            if m:
                token = m.group("glyph") or m.group("plain")
                headings.add(token)
                skill_headings.add(token)

    for f, text in texts.items():
        rel = f.relative_to(root)
        for lineno, raw_para in _non_fenced_paragraphs(text):
            if LINT_ALLOW_MARKER in raw_para:
                continue
            line = QUOTED_SPAN_RE.sub("", raw_para)
            for m in CITE_RE.finditer(line):
                token = m.group("token")
                if token in CITE_PLACEHOLDER_TOKENS:
                    continue
                file_ref = m.group("file")
                target = _resolve_named_file(skill_dir, file_ref) if file_ref else None
                if file_ref and target is None:
                    if _names_a_document(skill_dir, file_ref):
                        continue  # names a file outside this skill — unverifiable
                    file_ref = None  # "MUST §5": a capitalised word, not a file — bare citation
                if target is not None:
                    if token not in file_headings.get(target, set()):
                        target_rel = target.relative_to(root)
                        errors.append(
                            f"{rel}:{lineno}: `{file_ref} §{token}` has no matching "
                            f"heading in {target_rel}"
                            + (f" ({target_rel} has no numbered headings at all)"
                               if not file_headings.get(target) else "")
                        )
                elif token not in skill_headings:
                    errors.append(
                        f"{rel}:{lineno}: `§{token}` has no matching heading "
                        f"anywhere in this skill"
                        + (" (this skill has no § headings at all)" if not skill_headings else "")
                    )
    return errors


def check_banned_words(skill_dir: Path, banned_terms=BANNED_TERMS):
    """House-style slop ban-list, warning-only (senior-operator's ban is an error
    there; here it is advisory so a false positive can never block validation)."""
    warns = []
    for f in _skill_markdown_files(skill_dir):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = f.relative_to(skill_dir.resolve())
        for lineno, raw_line in enumerate(text.splitlines(), start=1):
            if LINT_ALLOW_MARKER in raw_line:
                continue
            # Quoted spans are frequently a user's own trigger phrase quoted
            # deliberately (frontmatter `description` fields do this constantly)
            # rather than the author praising their own work — skip them.
            line = QUOTED_SPAN_RE.sub("", raw_line)
            low = line.lower()
            for term in banned_terms:
                if not term:
                    continue
                if re.search(r"[a-z]", term, re.IGNORECASE) and " " not in term.strip() and term.isascii():
                    hit = re.search(rf"\b{re.escape(term.lower())}\b", low)
                else:
                    hit = term.lower() in low
                if hit:
                    warns.append(f"{rel}:{lineno}: banned term '{term}' — {raw_line.strip()[:80]}")
    return warns


def check_model_id_containment(root: Path):
    """Repo-wide: model-ID literals must live only in the canonical routing policy.

    AGENTS.md: "Keep model IDs in the canonical routing policy instead of
    duplicating tables across skills." Any gpt-/claude-.../gemini- literal
    found outside agent-orchestration/sections/routing.md is an error —
    whether it duplicates a real routing.md entry (the banned duplication) or
    names an ID routing.md doesn't even know about (worse: undocumented/stale).
    A line containing the literal marker `model-id-allow` (or the shared
    `lint-allow`) is a deliberate, documented exception and is skipped.
    Hidden dotfiles (vendored upstream previews, e.g. `.upstream-preview.md`)
    are skipped: that content isn't authored here and isn't governed by this
    repo's AGENTS.md.
    """
    routing_path = (root / ROUTING_POLICY_REL).resolve()
    if not routing_path.is_file():
        return []  # canonical file doesn't exist under this root; nothing to enforce
    try:
        routing_text = routing_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    errors = []
    root = root.resolve()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        resolved = p.resolve()
        if resolved == routing_path:
            continue
        rel = resolved.relative_to(root)
        if any(part in MODEL_ID_SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if rel.parts[:2] == MODEL_ID_SELF_TEST_DIR:
            continue
        if rel.parts[:2] == ("senior-operator", "projects"):
            continue  # gitignored per-project maps — same carve-out as _inside()
        if resolved.name.startswith("."):
            continue  # vendored upstream preview snapshot, not authored here
        if resolved.suffix.lower() in MODEL_ID_SKIP_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeDecodeError):
            continue  # binary or unreadable — not a text duplication risk
        for lineno, line in enumerate(text.splitlines(), start=1):
            if MODEL_ID_ALLOW_MARKER in line or LINT_ALLOW_MARKER in line:
                continue
            for m in MODEL_ID_RE.finditer(line):
                model_id = m.group(0)
                if model_id in routing_text:
                    errors.append(
                        f"{rel}:{lineno}: model ID '{model_id}' duplicates "
                        f"{ROUTING_POLICY_REL} — reference it by role instead"
                    )
                else:
                    errors.append(
                        f"{rel}:{lineno}: model ID '{model_id}' is not in "
                        f"{ROUTING_POLICY_REL} — undocumented/stale ID, or add it there"
                    )
    return errors


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

    errors.extend(check_cross_references(skill_dir))
    warns.extend(check_banned_words(skill_dir))
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

    model_id_errors = check_model_id_containment(root)
    if model_id_errors:
        n_err += len(model_id_errors)
        print("\n[repo-wide] model-ID containment")
        for e in model_id_errors:
            print(f"  ERROR  {e}")

    print(f"\n{'='*60}\n{len(dirs)} skills · {n_err} errors · {n_warn} warnings")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
