---
name: ref-skills
description: Maintain this skill setup by reviewing drift, upgrading upstream suites, merging forks, reapplying the curated load-out, and validating. Use for "upgrade skills", "update gstack", "nâng cấp skill", "upgrade đám skill", "check skill drift", adding an upstream-derived skill, or maintenance. Use instead of an upstream installer directly.
---

# Ref skills — derive, refine, upgrade

Skills here that are derived from an upstream suite carry a `REF.md`. Two modes:

- **`wrap`** — you own a short skill that fixes upstream's triggering and carries your
  house rules, then points at the full upstream by path. Upstream is not copied.
  **Default for anything large or binary-backed** — a gstack skill runs up to roughly
  1,900 lines and shells out to `gstack-*` binaries (`wc -l .vendor/gstack/*/SKILL.md`,
  2026-09-15: 443 to 1,897), so forking one means owning that merge surface plus its
  infrastructure.
- **`fork`** — upstream is vendored to `.upstream/SKILL.md` as a merge base and 3-way
  merged on upgrade. Only for small, pure-prose upstreams you intend to diverge from.

## Upgrade boundary

Use `status` and loadout dry runs for review-only requests. `upgrade`, `ensure`, and
`--apply` can fetch remote content, execute installers, and change user-level settings.
Run them only within an installation/update request. Record resolved versions/commits
and review upstream diffs; a moving branch or `@latest` is not a reproducible pin.
On controlled hosts, use an approved pinned toolchain or disable network installation
with `CONAN_AGENT_ENSURE=0`. Do not claim this installer alone certifies production safety.

## The one command

```bash
python3 ~/.conan-agent-skills/ref-skills/refsync.py upgrade
```

It does, in order: fast-forward this repo (skips a dirty tree) → fetch wrap sources
listed in `ref-skills/upstreams.ini` (gstack **files** into `.vendor/`, not a gstack
install; impeccable via npx) → check every `REF.md` source for drift → merge forks /
flag wraps → run `validate_skills.py` → re-apply the load-out. Report each step
honestly, including what it skipped. Default target is `all`; default profile is `auto`.

On a machine without a real browser, `auto` selects `core` for Claude and skips
those fetches. `CONAN_AGENT_HEADLESS=1` forces that; `CONAN_AGENT_ENSURE=0`
skips the network step. Pass an explicit workstation profile only when you mean
to require its full set.

Other entry points:

```bash
python3 refsync.py status                    # drift + load-out diff, changes nothing
python3 refsync.py ensure                    # fetch wrap markdown + keep-upstreams
python3 refsync.py upgrade shipping-changes  # one skill
python3 refsync.py upgrade <name> --accept   # record the new fingerprint after review
python3 refsync.py loadout                   # dry-run the auto-selected load-out diff
python3 refsync.py loadout --apply           # apply auto; optional third-parties are skipped
python3 refsync.py loadout --target codex --profile codex-dev --apply
python3 refsync.py loadout --target both --profile core --apply
python3 refsync.py rescue                    # list skills that exist ONLY on this machine
python3 refsync.py rescue --out <dir>        # tarball them, excluding vendored deps
```

## `rescue` — the unversioned-tree problem

A skills tree with no git remote holds anything living only there on exactly one machine.
`rescue` lists those skills with their true content size, skipping `node_modules`, `.git`,
`dist`, `build`, `__pycache__`, `.venv` — for a skill with an installed dependency tree
those are nearly all the bytes, so `du` overstates the loss. Read `rescue`'s number.

Run it before wiping or migrating any machine. The tarball belongs **off** the machine —
writing it to the same disk defeats the purpose. Vendoring these into this repo instead
would make them git-backed automatically, but this repo is public, so that is a licensing
decision rather than a technical one.

## Keep the selected load-out

Upstream installers may repopulate active skill directories. After an authorized
install, preview and re-apply the curated profile; keep unrelated external skills.

## Upgrading a wrap (never automatic)

A wrapper's value is the local rules, so `refsync.py` will not rewrite one. On drift it
writes the new upstream to `.upstream-preview.md` and stops. Then:

1. Read the preview against the wrapper's **"Upstream sections this depends on"**.
2. If a depended-on section vanished or its commands changed, **re-point the wrapper**
   before trusting it — a wrapper that routes to a section that no longer exists sends
   the agent into 1,400 lines with no anchor.
3. Re-read the wrapper's overrides: does upstream now do one of them natively? Drop it
   if so — a rule that restates upstream is noise.
4. `refsync.py upgrade <name> --accept`, then delete the preview.

## Adding a new ref skill

Read `sections/adding-a-ref-skill.md` — the wrap-vs-fork decision, the five steps, and
**"REF.md fields"**, which states what each `REF.md` key means. Most-misread field:
`version:` is the wrapper's own revision, **not** the upstream's — the upstream is
identified only by `source` + `fingerprint`.

## The cost, stated plainly

Every ref skill is a standing obligation. A wrap is cheap — re-verified only when its
fingerprint moves. A fork is a merge every release, forever. **Wrap by default; fork
only when you truly intend to diverge.** Cap the set: ten wraps is a working system,
forty is a second job. A wrap must earn itself with real overrides or a real triggering
fix — "upstream's wording is a bit off" is not a reason.

## Context budget

`skill-miner/context_budget.py` grades every skill against committed ceilings in
`skill-miner/context-budget.json` and runs inside `upgrade`. Shrinks lower the ceiling and lock;
growth past one fails the run — raise the ceiling deliberately, in the same diff.
Over ~12KB of SKILL.md, carve the reference bulk into `sections/` behind a
"Section index" table and leave the doctrine in the skeleton. Trim redundant description text while preserving precise triggers; avoid giant
capability lists that compete with unrelated skills.
See ARCHITECTURE.md → "Context budget".

## Related

`skill-miner` — decides whether something should be a skill at all, and ships
`validate_skills.py`. `coding-env-bootstrap` — installs this setup on a new machine;
`loadout.txt` is its exact install list.
