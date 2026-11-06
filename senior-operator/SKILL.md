---
name: senior-operator
description: >-
  Use when starting nontrivial work, before diagnosing a bug, touching
  money-math/dates/tenancy, shipping, or sending a hard conclusion; on "làm theo
  playbook", "đọc operating manual", "check theo self-test", "train Opus", "distill
  project này"; or when handing work to a weaker model. Craft discipline for hard or
  ambiguous tasks: classify the ask, verify by independent re-derivation, label
  verified vs inferred, attack your conclusion; plus a recipe for an optional private
  per-repo map.
---

# Senior Operator

Two files ship: a project-agnostic manual on how to work a hard task, and the recipe for
producing an optional per-repo map. Maps are private and a fresh clone has none.

| File | What it is | Load when |
| --- | --- | --- |
| [OPERATING-MANUAL.md](OPERATING-MANUAL.md) | How to think: 8 craft disciplines (procedure + synthetic example + failure prevented) + the 5-question self-test. Project-agnostic. | Start of any hard/ambiguous task; before sending any conclusion. |
| `projects/<slug>.md` (private, optional, gitignored) | How one repo runs: bootstrap, dev loop, verify gates, ground truth, trap table. | Hands-on work in that repo, if your machine has one. |
| [DISTILL.md](DISTILL.md) | The recipe for producing a new `projects/<slug>.md` from a repo + its session memory. | Entering a repo with no map (or a stale one); "distill project này". |

## Project maps (private, optional)

`projects/` is gitignored and never committed: maps describe how real repos run. If
`projects/INDEX.md` exists locally, start there; otherwise work from the repo's rulebook and
the manual. Run [DISTILL.md](DISTILL.md) when a reusable map is requested or materially
helps repeated work; its absence is not a blocker.

## Order of operations (any project)

1. **Bootstrap:** the repo's own `CLAUDE.md`/`AGENTS.md` (always authoritative — this skill NEVER overrides them) + its session-memory index if one exists + the matching `projects/<slug>.md` bootstrap section.
2. **Before acting:** OPERATING-MANUAL section 1 — what is actually being asked? Especially when the request presumes something is "wrong": verify the presupposition first.
3. **While working:**
   - Delegate via `agent-orchestration`.
   - Follow the project map's flow sections; check its trap table before inventing a diagnosis. No map → work from the manual alone and note candidate traps as you hit them.
4. **Before handing over:** OPERATING-MANUAL section 6 (attack the conclusion) + the 5-question self-test. Communicate per section 7: answer → reasoning → risk.

## Non-negotiables this skill exists to protect

- Green gates are not done: verify behavior on the user's own path in the real runtime
  ([manual §8](OPERATING-MANUAL.md)).
- Numbers reconcile to EXTERNAL ground truth, never to a re-derivation of the same code.
- Say out loud what is verified vs inferred vs assumed, and name the source of every
  threshold, limit, budget or cause.
- Comments are rare: one short WHY line; never restate code, incidents, commits or customer names; keep `audit-ok-*` and lint directives.

## Maintenance

- Maps are dated snapshots; the repo's own rulebook wins on conflict, fix the map to match.
- New recurring trap: record evidence, date and owner in the map. New repo distilled: new `projects/<slug>.md` plus an index row.
- `~/.conan-agent-skills` is the source of truth and the repo is public: never publish `projects/` without a private-context check.
