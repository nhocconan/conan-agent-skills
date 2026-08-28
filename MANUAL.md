# Manual — Tien's coding-agent skill setup

What you have, how to use it, and how to fix it when it breaks.
Each skill's own `SKILL.md` has the detail; this is the map.

---

## TL;DR — how to use it

**Just talk normally. There is nothing to run.**

Skills fire on their own from what you say. "Số liệu này sai" pulls in `metric-integrity`;
"ship it" pulls in `shipping-changes`; "sao lại lỗi" pulls in `investigating-bugs`. You
never have to remember a skill name.

Three things worth remembering, and only three:

| You want | Say / run |
| --- | --- |
| Update everything | "upgrade skills" — or `refsync.py upgrade` |
| Something feels broken | `python3 ~/.conan-agent-skills/skill-miner/validate_skills.py` |
| Undo the whole setup | See §7 Rollback |

Everything below is reference. You do not need it day to day.

---

## 1. Prerequisites

On **this** machine: nothing. It is already set up.

On a **new** machine you need only:

| Need | Why | Check |
| --- | --- | --- |
| `git` | clone the skills repo | `git --version` |
| `python3` (3.9+) | every tool here is stdlib-only — no pip install, ever | `python3 --version` |
| Claude Code | the thing that loads skills | `claude --version` |

That is the whole hard requirement. Optional, per what you actually do: `node`/`pnpm`
(JS projects), `gh` (PRs), `rg` (fast search), `docker` (containerised stacks), `bun`
(only if you rebuild gstack's `browse` binary).

Full new-machine runbook: `coding-env-bootstrap/BOOTSTRAP.md` — point an agent at it and
it installs and verifies itself.

---

## 2. Four directories, four roles

| Directory | What it is | Who owns it |
| --- | --- | --- |
| `~/.conan-agent-skills` | **Source of truth.** Your skills, in git, pushed to GitHub | You |
| `~/.shared-ai-skills` | gstack + other installed suites — **not all of it is active** | gstack's installer |
| `~/.claude/skills` | **What's actually running.** A real directory of symlinks built from `loadout.txt` | `refsync.py` |
| `~/.agents/skills` | Codex user skills. Repo-owned links are curated; unrelated suites are preserved | `refsync.py` + other installers |

The point: **"installed" ≠ "active."** gstack installs ~74 skills; you run 45. Inactive
skills are invisible to the model but their files stay on disk, and the wrappers still
read them by path.

For a production server, do not copy the 45-skill workstation set. Apply the self-contained
`core` profile to both agents:

```bash
python3 ~/.conan-agent-skills/coding-env-bootstrap/harness.py \
  apply --target both --profile core --with-mcp
```

Codex jobs use the installed bounded profile with `codex --profile production`.

`refsync.py loadout` and `refsync.py upgrade` use `auto` when one target is selected. On Claude, auto requires a detected real browser runtime and a complete workstation dependency tree; otherwise it selects the headless `core` profile and reports what it skipped. `CONAN_AGENT_HEADLESS=1` or `CONAN_AGENT_BROWSER=0` forces `core`; `CONAN_AGENT_BROWSER=1` is an explicit opt-in for a supported remote browser session. An explicit `--profile claude-dev` or `codex-dev` remains strict and fails on missing entries.

**Why bother:** every active skill's description competes for attention when the model
picks which one to fire. 89 skills with vague descriptions caused wrong picks. 45 with
sharp ones do not. It is a precision problem, not a disk-space one.

---

## 3. What you have (45 active)

### Yours — correctness checks
| Skill | Fires when |
| --- | --- |
| `metric-integrity` | Any displayed number: dashboard, KPI, report, chart |
| `backtest-integrity` | Trading research, backtests, Sharpe ratios |
| `anti-slop-review` | Content, courses, docs — fact-check and de-slop |
| `secure-code-audit` | Security pass before going public or shipping |
| `web-perf-audit` | Slow page, Core Web Vitals |
| `a11y-audit` | Is this UI actually WCAG-correct |
| `bug-class-audits` | A bug appears a second time → fix the class, add an audit script |

### Yours — how work gets done
| Skill | Fires when |
| --- | --- |
| `senior-operator` | Hard or ambiguous task. Read **before** acting |
| `agent-orchestration` | Delegating, fanning out sub-agents in parallel across model tiers, verifying + merging their work, multi-hour runs |
| `delegate-run` | Giao việc trọn gói cho MỘT agent: 3 điểm chạm (đề bài → duyệt plan nếu rủi ro → nghiệm thu), không hỏi giữa chừng, exit report format cứng + trust ledger |
| `investigating-bugs` | Something is broken — reproduce before editing |
| `shipping-changes` | Commit + push (main only, your identity, hooks must pass) |
| `browsing-web` | Anything involving a browser |
| `web-qa` | Test a running web app (reports by default; fixes only if you ask) |
| `design-qa` | "Nhìn xấu / rớt hàng / chữ bị đè" — visual defects, both themes + 375px |
| `resilient-data-harvest` | Scraping, backfills, system-to-system migration |

### Yours — building things
| Skill | Fires when |
| --- | --- |
| `interactive-course-builder` | HTML courses |
| `mobile-app-playbook` | Mobile app/game, build through store |
| `appstore-review-guard` | Before any store submission |
| `store-screenshots` | Store marketing screenshots and preview videos |
| `admin-crud-standards` | Admin / list / CRUD / upload screens |
| `demo-data-craft` | Demo and seed data |
| `docs-sync` | Bringing docs back in line with what shipped |

### Yours — infrastructure
| Skill | Fires when |
| --- | --- |
| `skill-miner` | Mine chat history for new skills; ships `validate_skills.py` |
| `ref-skills` | **Upgrade everything** (§5) |
| `coding-env-bootstrap` | Set up a new or production machine |
| `agent-session-backup` | Back up / restore session history |

The rest are third-party kept as-is: `context7` (live library docs — genuinely useful),
`playwright-skill` (writing reusable test scripts), `frontend-design`, `graphify`, `spec`.

---

## 4. The quality bar (always on)

`~/.claude/CLAUDE.md` holds a **Quality bar** section that applies to every request, even
a throwaway one: consider more than one approach → pick the best solution, not the first
one that works → verify against reality instead of memory → test and review before
reporting → report honestly, including what was skipped.

This is deliberately **not** a skill. A skill has to be triggered, so it would stay silent
exactly when you are chatting casually — which is when you said you most want it applied.

---

## 5. Upgrading — one command

```bash
python3 ~/.conan-agent-skills/ref-skills/refsync.py upgrade
```

Or just say **"upgrade skills"**.

It runs in order: check each upstream for changes → merge forks / flag wraps for review →
run the validator → **re-apply the load-out**.

When one target is selected, the default is `auto`: a headless or incomplete workstation install falls back to `core`, while an explicit workstation profile still fails instead of silently dropping entries. For a production refresh of both agents, use `harness.py apply --target both --profile core`.

> ⚠️ **Do not run `/gstack-upgrade` directly.** gstack's installer writes its ~74 skills
> into `~/.claude/skills` in *both* of its install branches, and no setting prevents it.
> Going through `refsync upgrade` works because re-applying the load-out runs last.
> If you already ran it by hand: `python3 refsync.py loadout --apply`.

Other commands:

```bash
refsync.py status            # what drifted + load-out diff; changes nothing
refsync.py loadout           # dry-run the auto-selected load-out diff
refsync.py loadout --apply   # apply the auto-selected load-out; explicit profiles stay strict
refsync.py loadout --target codex --profile codex-dev --apply  # explicit workstation profile
refsync.py rescue            # list skills that exist ONLY on this machine
refsync.py rescue --out ~/Backups   # tarball them (skips node_modules etc.)

python3 skill-miner/validate_skills.py ~/.claude/skills   # which skills are broken
```

---

## 6. Adding or changing a skill

**A new skill of your own:** let `skill-miner` propose it — say "scan my history for
skills". It applies a four-part bar: recurring across ≥2 projects, generalizable,
procedural, and not already covered. If it fails any one, it does **not** become a skill.

**A skill based on someone else's:** read `ref-skills/SKILL.md`.
- Upstream is large or binary-backed (all of gstack) → **wrap**: write ~50 lines of your
  own and point at the original by path. Never copy it.
- Upstream is small, pure prose, and you want to change its *content* → **fork**: vendor
  it as a merge base and 3-way merge on upgrade.

**After any skill edit, always run:**
```bash
python3 ~/.conan-agent-skills/skill-miner/validate_skills.py
```
Errors here make a skill **silently untriggerable** — nothing warns you. Real examples
already found: a missing `---` on line 1; `name` not matching the directory; `name`
containing the reserved word "claude" (one skill was invisible from the day it was
created because of that).

---

## 7. Rollback

| Problem | Fix |
| --- | --- |
| Load-out wrong / a skill vanished | `python3 refsync.py loadout --apply` |
| Undo the whole load-out change | `rm -rf ~/.claude/skills && mv ~/.claude/skills.symlink-backup-2026-07-25 ~/.claude/skills` |
| `browse` says NEEDS_SETUP | Check `gstack` is still a line in `loadout.txt` — the binary lives at `~/.claude/skills/gstack/browse/dist/browse` |
| Claude Code settings broken | `~/.claude/settings.json.bak-20260725` |
| Codex broken | `~/.codex/config.toml.bak-20260725` |
| A skill won't fire | Run `validate_skills.py` first |

---

## 8. Still open

- **Rotate the provider API tokens.** They sat in plaintext in `settings.json`; they are
  now in `~/.config/agent-keys.env` (chmod 600), but the old value may have been copied
  elsewhere. `~/.claude/settings.json.bak-20260725` still contains them — delete it once
  you are happy.
- **`~/.shared-ai-skills` has no git remote.** 16 skills exist only there — 428 KB of real
  content once vendored dependencies are excluded, including local fixes made on
  2026-07-25 to `interview-spec`, `spec-task-breakdown`, `frontend-responsive-ui` and
  `excalidraw-diagram-skill`. Run `refsync.py rescue --out <somewhere off this machine>`.
  Vendoring them into this repo instead would make them git-backed automatically, but
  this repo is public — that is a licensing call, not a technical one.
- **`refsync upgrade` does not yet run gstack's own installer** — it assumes the upstream
  tree is already updated, so "one command does everything" is not literally true yet.
  In practice: upgrade gstack however you normally do, then run `refsync upgrade`.
