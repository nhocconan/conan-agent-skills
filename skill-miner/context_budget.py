#!/usr/bin/env python3
"""Context-budget ratchet — lock a skill's token cost so it cannot creep back.

Two numbers per skill, both measured in bytes of what the model actually reads:

  always_on  the frontmatter description. Paid in EVERY session, for every
             skill in the load-out, whether or not it ever fires.
  eager      the whole of SKILL.md. Paid once, when the skill fires. Files under
             sections/ or reference/ are deliberately NOT counted — that is the
             point of the carve: they load at the step that needs them.

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


def measure(skill_dir: Path):
    f = skill_dir / "SKILL.md"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = m.group(1) if m else ""
    d = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", fm + "\n", re.S | re.M)
    desc = " ".join(d.group(1).split()) if d else ""
    return {"always_on": len(desc.encode()), "eager": len(text.encode())}


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
        print(f"{'eager':>8} {'ceiling':>8} {'always':>7}  skill")
        for name, g in rows:
            c = ceilings.get(name, {})
            print(f"{g['eager']:8d} {c.get('eager', 0):8d} {g['always_on']:7d}  {name}")
        te = sum(g["eager"] for _, g in rows)
        ta = sum(g["always_on"] for _, g in rows)
        print(f"\n{len(rows)} skills · always-on {ta} B (~{ta//4} tok) · "
              f"eager if all fired {te} B (~{te//4} tok)")

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
        print(f"\n{len(over)} skill(s) over budget. Carve the growth into "
              f"sections/ (loaded on demand), or raise the ceiling in "
              f"{CEILINGS.name} deliberately, in the same diff.")
        return 1
    suffix = " (read-only)" if read_only else ""
    print(f"\ncontext budget: {len(rows)} skills within ceilings{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
