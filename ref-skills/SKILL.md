---
name: ref-skills
description: Keeps the skill setup current and under control — upgrades gstack and other upstream suites, re-checks every wrapper against its upstream for drift, 3-way merges forked skills, re-applies the curated load-out that upstream installers overwrite, and validates the result. Use when the user says "upgrade skills", "update gstack", "nâng cấp skill", "upgrade đám skill", "check skill drift", when adding a new skill derived from an upstream one, or on a periodic maintenance pass. Run this INSTEAD of calling an upstream installer directly.
---

# Ref skills — derive, refine, upgrade

Skills here that are derived from an upstream suite carry a `REF.md`. Two modes:

- **`wrap`** — you own a short skill that fixes upstream's triggering and carries your
  house rules, then points at the full upstream by path. Upstream is not copied.
  **Default for anything large or binary-backed** — every gstack skill is 1,000–2,000
  lines and shells out to `gstack-*` binaries, so forking one means owning a 1,500-line
  merge surface plus its infrastructure.
- **`fork`** — upstream is vendored to `.upstream/SKILL.md` as a merge base and 3-way
  merged on upgrade. Only for small, pure-prose upstreams you intend to diverge from.

## The one command

```bash
python3 ~/.conan-agent-skills/ref-skills/refsync.py upgrade
```

It does, in order: check every `REF.md` source for drift → merge forks / flag wraps →
run `validate_skills.py` → re-apply the load-out. Report each step honestly, including
what it skipped.

On a machine without a real browser, the default `auto` profile selects `core` and skips the workstation/browser load-out. Use `CONAN_AGENT_HEADLESS=1` to force that decision, or pass an explicit workstation profile only when its dependencies are present.

Other entry points:

```bash
python3 refsync.py status                    # drift + load-out diff, changes nothing
python3 refsync.py upgrade shipping-changes  # one skill
python3 refsync.py upgrade <name> --accept   # record the new fingerprint after review
python3 refsync.py loadout                   # dry-run the auto-selected load-out diff
python3 refsync.py loadout --apply           # apply auto; explicit profiles stay strict
python3 refsync.py loadout --target codex --profile codex-dev --apply
python3 refsync.py loadout --target both --profile core --apply
python3 refsync.py rescue                    # list skills that exist ONLY on this machine
python3 refsync.py rescue --out <dir>        # tarball them, excluding vendored deps
```

## `rescue` — the unversioned-tree problem

`~/.shared-ai-skills` has no git remote, so anything living only there exists on exactly
one machine. `rescue` lists those skills with their true content size (skipping
`node_modules`, `.git`, `dist`, `build`, `__pycache__`, `.venv` — which is most of the
bytes: one skill measures 279 MB on disk and 64 KB of actual content).

Run it before wiping or migrating any machine. The tarball belongs **off** the machine —
writing it to the same disk defeats the purpose. Vendoring these into this repo instead
would make them git-backed automatically, but this repo is public, so that is a licensing
decision rather than a technical one.

## Why the load-out has to be re-applied, not configured

gstack's `./setup` calls `link_claude_skill_dirs` into `$HOME/.claude/skills` in **both**
of its install branches. There is no flag or layout that stops it — every upgrade
repopulates that directory with its ~74 skills. So `loadout.txt` is *enforced after* the
installer runs, which is why upgrades go through this skill rather than through
`/gstack-upgrade` directly.

Consequence: if you ever run an upstream installer by hand, run
`refsync.py loadout --apply` afterwards or the load-out silently reverts.

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

1. **Decide the mode.** Large, binary-backed, or you only disagree with *how it triggers*
   → `wrap`. Small, pure prose, and you intend to change its *content* → `fork`.
2. Write your `SKILL.md`. For a wrap keep it ~40–60 lines: a description that actually
   routes, the overrides, and an explicit pointer to the upstream file and the sections
   to read. Do not restate upstream's procedure — that is the merge tax you are avoiding.
3. Write `REF.md`: `mode`, `source`, `version`, `fingerprint`, `reviewed`, why it exists,
   the overrides that must survive, and the upstream sections you depend on.
4. For a fork, snapshot the base: `mkdir .upstream && cp <upstream> .upstream/SKILL.md`.
5. Add the name to the relevant `loadouts/*.txt` profile (and `loadout.txt` for the
   Claude workstation), run `refsync.py loadout --target ... --profile ... --apply`, then
   `validate_skills.py`.

## The cost, stated plainly

Every ref skill is a standing obligation. A wrap is cheap — re-verified only when its
fingerprint moves. A fork is a merge every release, forever. **Wrap by default; fork
only when you truly intend to diverge.** Cap the set: ten wraps is a working system,
forty is a second job. A wrap must earn itself with real overrides or a real triggering
fix — "upstream's wording is a bit off" is not a reason.

## Context budget

`skill-miner/context_budget.py` grades every skill against committed ceilings in
`context-budget.json` and runs inside `upgrade`. Shrinks lower the ceiling and lock;
growth past one fails the run — raise the ceiling deliberately, in the same diff.
Over ~12KB of SKILL.md, carve the reference bulk into `sections/` behind a
"Section index" table and leave the doctrine in the skeleton. Never trim a
`description` to save tokens: that is the always-on cost that buys correct routing.
See ARCHITECTURE.md → "Context budget".

## Related

`skill-miner` — decides whether something should be a skill at all, and ships
`validate_skills.py`. `coding-env-bootstrap` — installs this setup on a new machine;
`loadout.txt` is its exact install list.
