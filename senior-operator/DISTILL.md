# DISTILL — turn a repo into a project map (how a strong model trains the next one)

The point of this recipe: the strongest model available spends one session compressing a
repo's *operational reality* — not its code — into a map a weaker model can run on. Run it
when a repo has no `projects/<slug>.md`, or when the existing map's date stamp is stale
(rulebook grew, gates changed, a new trap burned a session).

## What a project map is (and is not)

- A map of **execution flows**: how work physically happens — start/stop, verify, seed,
  import, deploy — with the paid-for gotchas attached to each flow.
- **Not** a copy of the rulebook. Point at authoritative files (`CLAUDE.md §N`, script
  paths, docs); duplicate nothing that can drift. On conflict the repo wins, always.
- **Not** generic advice. Every line must be either a command someone will run or a trap
  that already cost a real session. If it would be true of any repo, cut it.

## Step 1 — Scan (in this order, cheapest signal first)

1. **The rulebook:** `CLAUDE.md` / `AGENTS.md` (root + nested). Note its structure and its
   stable rule numbering if any — cite, don't restate.
2. **The command surface:** root `package.json` scripts (and workspace ones that matter),
   `Makefile`, `justfile`, `scripts/` tree (`ls` recursively, read names not bodies —
   read a body only when the name is load-bearing and ambiguous).
3. **The gates:** CI workflows (`.github/workflows/`), pre-commit/pre-push hooks, audit
   scripts. Identify the ONE command that mirrors all gates, if it exists.
4. **Session memory:** whatever persistent per-project memory the harness keeps — Claude
   Code: `~/.claude/projects/<slug>/memory/` (read `MEMORY.md`, the index, fully; open
   individual files only for entries marked feedback/gotcha); other harnesses (Codex,
   Gemini): their session-notes / saved-context equivalent, or skip if none exists. This
   is where the traps live: memory is the residue of every past session's pain.
5. **Runbooks & docs:** `docs/` for runbooks, ADRs, credentials files, ground-truth
   references. Note ground-truth anchors (oracles, frozen expected values) explicitly —
   the weaker model must know that truth lives OUTSIDE the code.
6. **Project skills:** `skills/` or `.claude/` local skills — list them in the routing
   section, don't inline them.

## Step 2 — Write `projects/<slug>.md`

Header first: date stamp, sources scanned, and the sentence
**"This is a MAP, not a source of truth — on conflict, the repo's own rulebook wins."**

Then flow groups, in lifecycle order (keep only the ones the repo actually has):

| § | Group | Must answer |
| --- | --- | --- |
| 0 | Session bootstrap | What to read/run at the start of EVERY session; accounts; env traps |
| 1 | Dev runtime | Start/stop/restart, logs, ports, the ways it breaks |
| 2 | Verify gates | The one mirror command; what each gate does/does NOT catch; pre-push musts |
| 3 | Behavior verification | How to actually see it work (browser/device/CLI); login/interaction gotchas |
| 4 | Domain ground truth | Money/metric/date/tenancy invariants; where external truth lives |
| 5+ | Data lifecycle, integrations, background jobs, AI plane… | Per-repo as needed |
| n−1 | Shipping | Definition of done, docs sync, deploy |
| n | **Trap table** | Symptom → real cause → do this. One screen. The highest-value section. |

Trap-table admission rule: the entry must have actually happened. Format:
`| symptom as observed | real cause — action |`. Sort by frequency × cost.

## Step 3 — Wire it in

1. Save as `~/.conan-agent-skills/senior-operator/projects/<slug>.md`.
2. Add an index row in `projects/INDEX.md` (slug, repo name, date, distilling model).
   NOT in SKILL.md — the skills repo is public and `projects/` (including the index)
   is gitignored precisely so internal repo names never leave this machine.
3. Optional but strongest wiring: add one line to the repo's own rulebook routing section
   (`CLAUDE.md`, or `AGENTS.md` for Codex-native repos) —
   `Đầu session / task khó → invoke **senior-operator** (đọc projects/<slug>.md)`.
4. Do NOT commit the map — `projects/` is local-only by design. Commit/push only
   changes outside `projects/` (manual, DISTILL, SKILL.md).

## Step 4 — Verify the distillation (don't skip)

- Every command in the map: confirmed present in `package.json`/`scripts/` this session —
  not recalled from memory.
- Every trap: traceable to a memory entry, rulebook rule, or incident you can name.
- Read it back as the weaker model: could you, knowing nothing else, start the dev server,
  run the gates, and avoid the top three traps? If not, the map is prose, not a map.

## Quality bar

A good map fits in ~150 lines. If it's longer, you copied the rulebook; if a flow group is
empty of gotchas, you didn't read the memory. The test of "train Opus" is not that the map
sounds wise — it's that the next session on the weaker model doesn't re-pay for a lesson
already bought.
