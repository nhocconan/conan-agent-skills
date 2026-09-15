#!/usr/bin/env python3
"""Context-budget ratchet — lock a skill's token cost so it cannot creep back.

Three numbers per skill, all measured in bytes of what the model actually reads:

  always_on  the frontmatter description. Paid in EVERY session, for every
             skill in the load-out, whether or not it ever fires.
  eager      the whole of SKILL.md. Paid once, when the skill fires.
  on_demand  every file SKILL.md references (sections/, reference/, TEMPLATES.md,
             etc — followed transitively, the same way validate_skills.py follows
             them), summed. Not paid unless a step actually needs that file, but
             unlike eager it was previously invisible to this tool entirely — a
             skill could carve unbounded growth into sections/ with nothing
             noticing. It gets its own ceiling so that growth is visible too.

The ratchet is monotonic. A shrink lowers the ceiling and locks it. Growth past
a ceiling is an error you must either undo or raise deliberately, in the diff,
where a reviewer sees it.

  python3 context_budget.py            # grade, auto-lower on shrink
  python3 context_budget.py --report   # show every skill's numbers, change nothing
  python3 context_budget.py --no-ratchet   # grade only, never write
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

CEILINGS = Path(__file__).resolve().parent / "context-budget.json"
HEADROOM = 0.05  # a ceiling sits 5% above the measurement that set it

# Mirrors validate_skills.py's _inside()/PRIVATE_PARTS: on-demand measurement
# must never read into a private/gitignored tree. senior-operator/projects/ in
# particular holds per-project maps that can name internal systems — pulling
# their byte count into a committed context-budget.json would be a real leak,
# not just a wrong number.
PRIVATE_PARTS = {".git", ".vendor", "history", "project-private", "private", "local", "state"}


def _inside_skill(skill_dir: Path, target: Path) -> bool:
    root = skill_dir.resolve()
    try:
        relative = target.relative_to(root)
    except ValueError:
        return False
    if skill_dir.resolve().name == "senior-operator" and relative.parts[:1] == ("projects",):
        return False
    return not any(part in PRIVATE_PARTS for part in relative.parts)

# Same link/code-path shapes validate_skills.py resolves references with, kept
# independent (no cross-import) since the two scripts each own their own file.
_LINK_RE = re.compile(r"\[[^\]]+\]\(\s*(?:<([^>]+)>|([^\s)#]+(?:#[^\s)]*)?))")
_CODE_PATH_RE = re.compile(r"(?<![\w./-])((?:\.\.?/)?(?:[\w.-]+/)*[\w.-]+\.md(?:#[\w.-]+)?)")


def _reference_target(raw: str):
    target = raw.strip().split("#", 1)[0].split("?", 1)[0]
    if not target or target.startswith(("#", "~", "$", "/")):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    return target


def _referenced_paths(text: str):
    paths = set()
    for match in _LINK_RE.finditer(text):
        target = _reference_target(match.group(1) or match.group(2))
        if target and target.lower().endswith(".md"):
            paths.add(target)
    for code in re.findall(r"`([^`\n]+)`", text):
        if "<" in code or ">" in code:
            continue
        for match in _CODE_PATH_RE.finditer(code):
            target = _reference_target(match.group(1))
            if target and target.lower().endswith(".md"):
                paths.add(target)
    return paths


def measure(skill_dir: Path):
    f = skill_dir / "SKILL.md"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = m.group(1) if m else ""
    d = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", fm + "\n", re.S | re.M)
    desc = " ".join(d.group(1).split()) if d else ""
    return {
        "always_on": len(desc.encode()),
        "eager": len(text.encode()),
        "on_demand": measure_on_demand(skill_dir),
    }


def measure_on_demand(skill_dir: Path) -> int:
    """Bytes of every file SKILL.md references, followed transitively.

    A router file (SKILL.md, or a sections/ file it points to) may itself
    point further in — e.g. sections/router.md -> sections/nested/deeper.md —
    so references are followed breadth-first, same as validate_skills.py.
    """
    sk = skill_dir / "SKILL.md"
    if not sk.exists():
        return 0
    seen = {sk.resolve()}
    total = 0
    queue = [sk]
    while queue:
        src = queue.pop(0)
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for rel in sorted(_referenced_paths(text)):
            candidates = [src.parent / rel, skill_dir / rel]
            target = next((c.resolve() for c in candidates if c.exists()), None)
            if target is None:
                continue
            if not _inside_skill(skill_dir, target):
                continue  # never follow a reference outside the skill, or into a private tree
            if target in seen or not target.is_file():
                continue
            seen.add(target)
            total += target.stat().st_size
            queue.append(target)
    return total


def cap(n: int) -> int:
    return -(-int(n * (1 + HEADROOM)) // 100) * 100


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--no-ratchet", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    ceilings = json.loads(CEILINGS.read_text()) if CEILINGS.exists() else {}
    # Keep the committed values separate from the candidate ratchet. Reporting and
    # --no-ratchet must be able to inspect proposals without mutating the source map.
    proposed_ceilings = copy.deepcopy(ceilings)
    read_only = args.report or args.no_ratchet

    rows, over, lowered, new, added = [], [], [], [], []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        got = measure(d)
        if got is None:
            continue
        rows.append((d.name, got))
        have = ceilings.get(d.name)
        if have is None:
            proposed_ceilings[d.name] = {k: cap(v) for k, v in got.items()}
            new.append(d.name)
            continue
        candidate = proposed_ceilings[d.name]
        for k, v in got.items():
            ceiling = have.get(k)
            if ceiling is None or v > ceiling:
                if ceiling is None:
                    candidate[k] = cap(v)
                    added.append((d.name, k, cap(v)))
                else:
                    over.append((d.name, k, v, ceiling))
            elif cap(v) < ceiling:
                candidate[k] = cap(v)
                lowered.append((d.name, k, ceiling, cap(v)))

    if args.report:
        rows.sort(key=lambda r: -r[1]["eager"])
        print(f"{'eager':>8} {'ceiling':>8} {'always':>7} {'on_demand':>10} {'ceiling':>8}  skill")
        for name, g in rows:
            c = ceilings.get(name, {})
            print(f"{g['eager']:8d} {c.get('eager', 0):8d} {g['always_on']:7d} "
                  f"{g['on_demand']:10d} {c.get('on_demand', 0):8d}  {name}")
        te = sum(g["eager"] for _, g in rows)
        ta = sum(g["always_on"] for _, g in rows)
        to = sum(g["on_demand"] for _, g in rows)
        print(f"\n{len(rows)} skills · always-on {ta} B (~{ta//4} tok) · "
              f"eager if all fired {te} B (~{te//4} tok) · "
              f"on-demand if all loaded {to} B (~{to//4} tok)")

    if read_only and (new or added or lowered):
        print("\nproposals (read-only; not written):")
    prefix = "would capture" if read_only else "captured"
    for name in new:
        print(f"  {prefix} {name} (first ceiling)")
    for name, k, now in added:
        action = "would add" if read_only else "added"
        print(f"  {action} {name}.{k}: {now}")
    prefix = "would ratchet" if read_only else "ratcheted"
    for name, k, was, now in lowered:
        print(f"  {prefix} {name}.{k}: {was} → {now}")
    for name, k, v, ceiling in over:
        print(f"  OVER      {name}.{k}: {v} B > ceiling {ceiling} B (+{v - ceiling})")

    if (new or added or lowered) and not read_only:
        CEILINGS.write_text(json.dumps(proposed_ceilings, indent=2, sort_keys=True) + "\n")

    if over:
        eager_over = any(k == "eager" for _, k, _, _ in over)
        on_demand_over = any(k == "on_demand" for _, k, _, _ in over)
        advice = []
        if eager_over:
            advice.append("carve eager growth into sections/ (loaded on demand)")
        if on_demand_over:
            advice.append("trim or split on_demand content further — it has nowhere "
                           "further to be carved into")
        advice.append(f"or raise the ceiling in {CEILINGS.name} deliberately, in the same diff")
        print(f"\n{len(over)} skill(s) over budget. " + "; ".join(advice) + ".")
        return 1
    suffix = " (read-only)" if read_only else ""
    print(f"\ncontext budget: {len(rows)} skills within ceilings{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
