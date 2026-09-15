---
name: senior-operator
description: >-
  Cross-project operating playbook: how to think on a hard or ambiguous task, plus
  per-repo execution-flow maps. Use at the start of any nontrivial task in any
  project, when onboarding a model to a codebase, before diagnosing a bug, touching
  money-math/dates/tenancy, or shipping — and before sending any hard conclusion.
  Triggers: "làm theo playbook", "đọc operating manual", "check theo self-test",
  "train Opus", "distill project này", or any request to hand work to a weaker model.
---

# Senior Operator

Three files: a project-agnostic manual on how to work a hard task, a per-repo map of how
one codebase actually runs, and the recipe for producing a new map.

| File | What it is | Load when |
| --- | --- | --- |
| [OPERATING-MANUAL.md](OPERATING-MANUAL.md) | How to think: 8 craft disciplines (procedure + real example + failure prevented) + the 5-question self-test. Project-agnostic. | Start of any hard/ambiguous task; before sending any conclusion. |
| `projects/<slug>.md` | How one repo runs: bootstrap, dev loop, verify gates, ground truth, data lifecycle, trap table. See index below. | Any hands-on work in that repo. |
| [DISTILL.md](DISTILL.md) | The recipe for producing a new `projects/<slug>.md` from a repo + its session memory. | Entering a repo with no map (or a stale one); "distill project này". |

## Project map index

The index and the maps themselves live in `projects/` — **local-only,
gitignored, never committed**: maps describe how real repos run (including
employer-internal systems), so they must never reach the public skills repo.
Start at `projects/INDEX.md`. No map for the repo you're in? Run
[DISTILL.md](DISTILL.md) — ideally on the strongest model available — then add
the row in `projects/INDEX.md`.

## Any-model use (Claude / Codex / agy)

Everything here is plain Markdown — no harness feature required. A harness without an available
skill loader uses it by reading files directly, in the
same order the table above prescribes: `SKILL.md` → `OPERATING-MANUAL.md` →
`projects/<slug>.md` for the repo at hand.

- **Wiring for Codex:** point the repo's `AGENTS.md` (or a `.codex/skills/` wrapper) at
  this directory with one line: "Nontrivial task → read
  `~/.conan-agent-skills/senior-operator/SKILL.md` and follow it."
- **Model policy:** [agent-orchestration](../agent-orchestration/SKILL.md) owns routing.
  Project maps contain commands and invariants usable by any worker.
- Harness-specific references inside the manual/maps (memory paths, browser tools,
  `CLAUDE.md`) are examples, not requirements — substitute the local equivalent.

## Order of operations (any project)

1. **Bootstrap:** the repo's own `CLAUDE.md`/`AGENTS.md` (always authoritative — this skill NEVER overrides them) + its session-memory index if one exists + the matching `projects/<slug>.md` bootstrap section.
2. **Before acting:** OPERATING-MANUAL section 1 — what is actually being asked? Especially when the request presumes something is "wrong": verify the presupposition first.
3. **While working:**
   - Delegate independent work through `agent-orchestration`; the lead retains final
     quality. Small or sequential tasks can stay with the lead.
   - Follow the project map's flow sections; check its trap table before inventing a diagnosis. No map → work from the manual alone and note candidate traps as you hit them.
4. **Before handing over:** OPERATING-MANUAL section 6 (attack the conclusion) + the 5-question self-test. Communicate per section 7: answer → reasoning → risk.

## Non-negotiables this skill exists to protect

- Green gates ≠ done. Verify behavior on the journey you touched, in the real runtime.
- Numbers reconcile to EXTERNAL ground truth, never to a re-derivation of the same code.
- Class-of-bug → rule + mechanical audit, never a one-site patch.
- Say out loud what is verified vs inferred vs assumed.

## Maintenance

- Project maps are dated snapshots — the repo's own rulebook wins on conflict; fix the map to match, never the reverse.
- New recurring trap → record evidence, date, and review owner in the project map; supersede stale rules explicitly.
- New repo distilled → new `projects/<slug>.md` + index row in `projects/INDEX.md`.
  `~/.conan-agent-skills` is the source of truth (`~/.claude/skills/` holds symlinks);
  the repo is PUBLIC, so `projects/` stays local-only — publish only when requested and after checking for private context.
