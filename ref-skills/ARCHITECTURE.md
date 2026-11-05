# ref-skills — architecture

Goal: skills derived from upstream suites (gstack, Anthropic, others) live in this repo
in short form, marked as referring to upstream, refined for house rules, and upgradable
from the original on command. Commands and flags: `SKILL.md` and `refsync.py <cmd> --help`.

## Two modes

- **`wrap`** (default for large or binary-backed upstreams, all of gstack). The repo skill
  is short: a description that triggers plus house overrides. Its body points at the
  upstream file under `.vendor/` and the agent reads it only when the skill fires. Upstream
  can change freely; only the overrides are owned. Live example: `shipping-changes/` and
  its `REF.md`.
- **`fork`** (small, pure-prose upstreams you intend to diverge from). Vendor the file;
  `refsync.py upgrade` 3-way merges with `git merge-file --diff3` against `.upstream/SKILL.md`
  (committed, dotted so the model never reads it). A conflict writes `SKILL.md.merge` and
  leaves `SKILL.md` untouched. No real fork exists yet.

Discipline: wrap by default; a wrap must earn itself with real overrides or a fix for a
real triggering failure; cap the set.

## Layout

```
ref-skills/
  SKILL.md        how to add, refine and upgrade a ref skill
  refsync.py      the tool (status, upgrade, ensure, loadout, rescue)
  upstreams.ini   declared wrap sources, fetched into .vendor/ (individual SKILL.md files)
<skill>/
  SKILL.md        the only file that loads
  REF.md          provenance, overrides that must survive, upstream sections depended on
  .upstream/      forks only: pristine merge base
```

`REF.md` front matter records `mode`, `upstream`, `source`, `version`, `fingerprint`
(sha256 of the upstream file as last reviewed) and `reviewed`. `status` flags a changed
fingerprint and any depended-on section heading that vanished upstream. `upgrade` never
edits a wrap's SKILL.md; it shows the diff, and `--accept` refreshes fingerprint, version
and reviewed. Every upgrade ends with the load-out apply and `skill-miner/validate_skills.py`.

## Load-out is enforced, not configured

gstack's installer repopulates `~/.claude/skills` on every upgrade with no layout that
avoids it, so `refsync.py loadout --apply` runs after any upstream installer and
`upgrade` ends with it. Running `/gstack-upgrade` by hand silently reverts the load-out.
Since 2026-09 gstack is not installed; wraps read markdown fetched into `.vendor/gstack/`
by `refsync.py ensure`, and `loadout.txt` has no `gstack` entry.

## Context budget — the carve and the ratchet

Adopted from gstack v1.71 (2026-08-27), which cut its per-invocation prompt cost
~50%. Only part of that transfers: most of gstack's win was deleting an ~18KB
inline-bash preamble every one of its skills carried. Ours have no preamble. The
transferable half is the **section carve**, and the discipline that keeps it.

**Two numbers, measured by `skill-miner/context_budget.py`:**

- `always_on` — the frontmatter description. Paid in every session for every
  skill in the load-out. **Do not trim it to save tokens.** The description is
  the entire reason the wraps exist: it is what makes a skill fire on the
  phrasings actually used here. ~3.8K tokens for the whole set is the price of
  correct routing, and it is worth it.
- `eager` — all of SKILL.md, paid once when the skill fires. This is what a
  carve moves.

**When to carve.** A SKILL.md over ~12KB whose bulk is reference material
consulted at one step, not read-through doctrine. Below that, the indirection
and the extra Read round-trip cost more than they save. Four skills met the bar
(appstore-review-guard 28→3.5KB, mobile-app-playbook 26.6→6.8KB,
agent-orchestration 17.4→5.9KB, store-screenshots 15.8→7.6KB); the other 22 did
not, and were deliberately left whole.

**How to carve.** The skeleton stays a decision tree, never a summary: intro,
the doctrine that applies at all times, and a `## Section index — Read each
section when its situation applies` table mapping *situation* → file. Bodies go
to `sections/` (or the skill's existing `reference/`). Rewrite in-document
anchors to file paths — `(#some-heading)` silently goes dead the moment its
heading leaves the file. A rule whose absence causes a wrong action, not just a
slower one, stays in the skeleton even if it is also in a section.

**The ratchet.** `context_budget.py` grades every skill against
`skill-miner/context-budget.json` and runs inside `refsync.py upgrade`. A shrink
lowers the ceiling and locks it; growth past a ceiling fails the run. To grow a
skill on purpose, raise its ceiling in the same diff — visibly, where a reviewer
sees the trade.
