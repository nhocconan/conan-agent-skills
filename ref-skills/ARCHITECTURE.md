# ref-skills — architecture proposal

**Status: BUILT (2026-07-25).** `refsync.py` + `SKILL.md` + `loadout.txt` ship in this
directory; three wraps (`shipping-changes`, `investigating-bugs`, `browsing-web`) are live
and the load-out is applied. §5 below was revised after reading gstack's installer — the
original plan was wrong. §8's questions are answered.

Goal, in the operator's words: *useful skills derived from gstack / Anthropic / other upstream
suites, living in this repo instead of their full-blown originals, marked as referring to
upstream, refined for my use case, and upgradable from the original on command.*

---

## 1. The finding that shapes everything

The obvious design is "fork the good upstream skills and 3-way merge on upgrade." Measured
against the actual upstream, that is the wrong default:

| gstack skill | Lines | Backing |
| --- | --- | --- |
| `design-review` | 1,994 | gstack binaries |
| `review` | 1,852 | gstack binaries |
| `retro` | 1,812 | gstack binaries |
| `qa` | 1,684 | gstack binaries + browse daemon |
| `ship` | 1,417 | gstack binaries |
| `cso` | 1,285 | gstack binaries |
| `investigate` | 1,074 | gstack binaries |
| `browse` | 1,022 | compiled `browse` binary |

Forking one means owning ~1,500 lines of merge surface **and** the `gstack-*` scripts it
shells out to. Ten forks would make every `gstack-upgrade` a multi-hour conflict event.
The upstream is not a document to copy — it is a program with a manual attached.

So the architecture has **two modes**, and for gstack the right one is *not* fork.

---

## 2. The two modes

### `wrap` — default for large or binary-backed upstreams (all of gstack)

You own a short skill (~40–60 lines). It carries the thing upstream does badly — **a
description that actually triggers** — plus your house overrides. The 1,400-line upstream
is not copied and not loaded; your body points at it by absolute path, and the agent reads
it only when the skill actually fires.

```markdown
---
name: shipping-changes
description: Ships a change end to end — tests, diff review, version bump, changelog,
  commit, push. Use when the user says "ship it", "land this", "đẩy lên", "commit and
  push", or a change is verified and ready to land. Enforces the house rules: main only,
  no feature branches, commits under the operator's identity, no assistant attribution.
---

# Shipping

House rules — these override upstream wherever they conflict:
- **main only.** Never create a feature branch. Never leave a stray branch behind.
- **Commit identity** is the operator's; no assistant co-author trailer.
- Pre-commit and pre-push hooks must pass; a skipped hook is a failed ship.

Then execute the upstream procedure: read `~/.shared-ai-skills/ship/SKILL.md`
(gstack 1.60.1.0) and follow it, applying the overrides above.
```

What this buys:
- **Triggering.** Upstream's description is 31 characters — *"Pre-landing PR review."* —
  which cannot route. Yours is a real routing rule.
- **Precision.** Your override rules sit at the top instead of being buried at line 900.
- **Zero merge tax.** Upstream can change freely; you own ~50 lines.
- **Context.** 1,400 lines load on demand, not at startup.

### `fork` — for small, pure-prose upstreams

Vendor the file, customize it, 3-way merge on upgrade. Correct for things like an
Anthropic reference skill or a community prose skill of a few hundred lines with no
runtime. Use it only when you genuinely intend to diverge from upstream's *content*.

---

## 3. Layout

```
~/.conan-agent-skills/
├── ref-skills/
│   ├── SKILL.md              # how to add/refine/upgrade a ref skill
│   ├── refsync.py            # the tool
│   └── ARCHITECTURE.md       # this file
│
├── shipping-changes/         # a wrap
│   ├── SKILL.md              # yours — the only thing that loads
│   └── REF.md                # provenance + overrides + upstream fingerprint
│
└── some-forked-skill/        # a fork
    ├── SKILL.md              # yours, customized
    ├── REF.md                # provenance + changelog of local edits
    └── .upstream/SKILL.md    # pristine snapshot at the vendored version (merge base)
```

`.upstream/` is dotted so the model never reads it; it is committed, because a 3-way merge
is impossible on a fresh clone without the base.

### `REF.md`

```markdown
---
mode: wrap                       # wrap | fork
upstream: gstack
source: local:~/.shared-ai-skills/ship/SKILL.md
version: 1.60.1.0
fingerprint: sha256:1a2b3c…      # of the upstream file as last reviewed
reviewed: 2026-07-25
---

## Why this exists
Upstream's description (31 chars) cannot trigger, and its default flow creates branches.

## Overrides that MUST survive an upgrade
1. main only — no branch creation
2. operator commit identity, no assistant attribution
3. hooks must pass

## Upstream sections this depends on
- "Version bump" — the VERSION/CHANGELOG sequence
- "Pre-flight checks" — the test gate
```

That last section is what makes upgrades checkable: if upstream deletes a section you
depend on, the tool can say so instead of silently drifting.

---

## 4. `refsync.py`

```bash
python3 refsync.py status      # what drifted since last review
python3 refsync.py upgrade     # apply: merge forks, re-verify wraps
python3 refsync.py upgrade shipping-changes   # one skill
python3 refsync.py add --mode wrap --source local:~/.shared-ai-skills/ship/SKILL.md
```

**`status`** — for each `REF.md`: resolve the source, hash it, compare to `fingerprint`.
Unchanged → clean. Changed → flag, and for wraps also check every "sections this depends
on" heading still exists in upstream.

**`upgrade`**:
- *wrap* — never edits your SKILL.md automatically. Shows the upstream diff, reports
  missing depended-on sections, and asks the agent to re-verify the wrapper's claims. On
  confirmation, updates `fingerprint` + `version` + `reviewed`.
- *fork* — `git merge-file --diff3 SKILL.md .upstream/SKILL.md <new upstream>`. Clean
  merge → write through, refresh `.upstream/`, bump the fingerprint. Conflict → leave
  markers in `SKILL.md.merge` and report; never half-apply.
- Always finishes by running `skill-miner/validate_skills.py`, because an upgrade can
  reintroduce a spec violation (an over-length description, a >500-line body).

Sources: `local:<path>` · `github:<owner>/<repo>@<ref>:<path>` · `https:<url>`.

---

## 5. The load-out problem (this blocks everything else)

`~/.claude/skills` is a **symlink to `~/.shared-ai-skills`**, and gstack's installer owns
that directory. Consequences today:

- Every one of gstack's ~74 skills is in the model's startup context whether you want it
  or not. 123 of the 137 outstanding validator warnings are theirs, and you cannot fix
  them — `gstack-upgrade` regenerates them.
- You cannot name a wrap `ship`, because gstack's `ship/` already occupies that name in
  the same namespace.
- You cannot hide an upstream skill; deleting it just invites the installer to restore it.

**Proposed fix — separate "installed" from "active".** Make `~/.claude/skills` a real
directory of symlinks generated from a manifest:

```
~/.shared-ai-skills/     gstack's tree — installed, upgradable, NOT all active
~/.agents/skills/        other suites — installed, not active
~/.conan-agent-skills/   yours — the source of truth
        ↓ loadout.txt
~/.claude/skills/        real dir; only what you chose is symlinked here
```

Then: your 20 skills + a handful of wraps are active; gstack's binaries and files stay
installed and reachable by path; `gstack-upgrade` keeps working because it targets
`~/.claude/skills/gstack`, which stays symlinked.

This is also what makes the production bootstrap exact — `loadout.txt` *is* the install
list, replacing the "install the curated subset" prose in `coding-env-bootstrap`.

**Revised after reading `gstack/setup` (this corrects the original plan).** Both install
branches call `link_claude_skill_dirs "$SOURCE_GSTACK_DIR" "$INSTALL_SKILLS_DIR"`, and in
the non-skills-shaped branch `INSTALL_SKILLS_DIR` is reassigned to `$HOME/.claude/skills`
before that call. **There is no layout or flag under which gstack leaves that directory
alone** — it repopulates its ~74 skills on every upgrade.

So the load-out is **enforced, not configured**: `refsync.py loadout --apply` runs *after*
any upstream installer, and `refsync.py upgrade` ends with it for exactly that reason.
Running `/gstack-upgrade` by hand silently reverts the load-out.

One hard dependency, found by testing rather than reasoning: gstack's skills resolve their
binary at the literal path `$HOME/.claude/skills/gstack/browse/dist/browse`. The load-out
must therefore keep a `gstack` entry, or `browse` — the most-used skill on this machine —
reports `NEEDS_SETUP` and tries to rebuild a 60 MB binary that already exists.

---

## 6. Cost, honestly

Every ref skill is a standing obligation. A wrap is cheap (~50 lines, re-verified when
upstream's fingerprint moves). A fork is not — it is a merge every release, forever.

Recommended discipline:
- **Wrap by default. Fork only when you intend to diverge from upstream's content.**
- A wrap must earn itself: real overrides, or a description that fixes a real triggering
  failure. "Upstream's wording is a bit off" is not a reason.
- Cap the set. Ten wraps is a working system; forty is a second job.

---

## 7. Candidates (evidence-ranked)

Usage counts are explicit invocations only, so they undercount auto-triggered skills.

| Upstream | Uses | Mode | Why |
| --- | --- | --- | --- |
| gstack `ship` | 15 | **wrap** | Real conflict: upstream branches/PRs, house rule is main-only, operator identity, no assistant attribution. Highest value. |
| gstack `investigate` | 19 | **wrap** | Most-used prose workflow; pairs with `senior-operator`'s verify-by-re-derivation. |
| gstack `browse` | 56 | **wrap** | Most-used skill on the machine. Binary-backed, so wrap is the only option; thin wrapper carries the "always use browse, never the Chrome MCP" rule already in the global rulebook. |
| gstack `review` | 6 | wrap | Overlaps `code-review` plugin + `bug-class-audits`; decide which one owns the job before wrapping. |
| gstack `qa` / `qa-only` | 0 | defer | Four overlapping browser-QA skills already. Consolidate first, wrap second. |
| Anthropic `skill-creator` | — | fork | Small, pure prose, and directly relevant to `skill-miner`. Genuine fork candidate. |

---

## 8. Decisions taken

1. **Load-out adopted.** `~/.claude/skills` is now a real directory built from
   `loadout.txt`: 93 active skills → 43. Old symlink preserved as
   `~/.claude/skills.symlink-backup-2026-07-25` for rollback.
2. **Three wraps built** — `shipping-changes`, `investigating-bugs`, `browsing-web`.
3. **Both modes built.** `wrap` is live; `fork` (`.upstream/` merge base +
   `git merge-file --diff3`) is implemented and awaiting its first candidate —
   Anthropic's `skill-creator` is the intended one.

## 9. Still open

- The 3-way merge path is **tested** (2026-07-25, synthetic fixture): a change in an
  untouched region merges cleanly while local edits survive; an adjacent-line change
  conflicts, writes `SKILL.md.merge` and leaves `SKILL.md` untouched; re-running is
  idempotent. Testing also caught conflict markers printing temp paths — now labelled
  YOURS / BASE / THEIRS. No *real* fork exists yet, so no upstream has been tracked
  over an actual release.
- `refsync upgrade` does not itself run gstack's installer; it assumes the upstream tree
  is already updated. Wiring the installer invocation in (so one command truly does
  everything) is the next increment.
