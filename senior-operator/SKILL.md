---
name: senior-operator
description: Cross-project senior-operator playbook — a model-to-model craft handoff (written by Claude Fable 5 to train successor/weaker models like Opus) plus per-project execution-flow maps. Three parts — OPERATING-MANUAL.md (how to think on hard tasks: read the real ask, decompose along verification lines, risk = blast radius × silence, verify by re-derivation, label known-vs-guessed, attack your own conclusion, answer-first communication, false-competence tells, 5-question self-test), projects/<slug>.md (how a specific repo actually runs: commands, gates, ground truth, trap tables), and DISTILL.md (the recipe for generating a new project map, so a strong model can train the next one). Use at the START of any nontrivial or ambiguous task in ANY project, when onboarding a new model/agent (Opus, Codex, Gemini) to a codebase, before diagnosing bugs / touching money-math, dates, tenancy / shipping, when the user says "làm theo playbook", "đọc operating manual", "check theo self-test", "train Opus", "distill project này", or asks how to hand work to a weaker model.
---

# Senior Operator

A capability handoff: the craft of a stronger model, written down so any model can run on
it. Two layers — **how to think** (universal) and **how this repo runs** (per project) —
plus the **distill recipe** that lets the strong model keep training the next one.

| File | What it is | Load when |
| --- | --- | --- |
| [OPERATING-MANUAL.md](OPERATING-MANUAL.md) | How to think: 8 craft disciplines (procedure + real example + failure prevented) + the 5-question self-test. Project-agnostic. | Start of any hard/ambiguous task; before sending any conclusion. |
| `projects/<slug>.md` | How one repo runs: bootstrap, dev loop, verify gates, ground truth, data lifecycle, trap table. See index below. | Any hands-on work in that repo. |
| [DISTILL.md](DISTILL.md) | The recipe for producing a new `projects/<slug>.md` from a repo + its session memory. | Entering a repo with no map (or a stale one); "distill project này". |

## Project map index

| Slug | Repo | Distilled | By |
| --- | --- | --- | --- |
| [redacted-internal](projects/redacted-internal.md) | `REDACTED_COMPANY/REDACTED_INTERNAL_REPO` (REDACTED_INTERNAL_PRODUCT) | 2026-07-07 | Fable 5 |
| [redacted-internal-project-1](projects/redacted-internal-project-1.md) | `REDACTED_INTERNAL_REPO` (multi-tenant SaaS chatbot platform) | 2026-07-07 | Opus 4.8, reviewed by Fable 5 |
| [redacted-internal-project-2](projects/redacted-internal-project-2.md) | `REDACTED_INTERNAL_REPO` (marketing-content Spam/Attribute/Sentiment QC) | 2026-07-07 | Opus 4.8, reviewed by Fable 5 |
| [vnstock-trading-system](projects/vnstock-trading-system.md) | `Trading/vnstock-trading-system` (vnquant — VN quant trading, DNSE live plane) | 2026-07-07 | Opus 4.8, reviewed by Fable 5 |
| [seeker-flying-bird](projects/seeker-flying-bird.md) | `Android-Apps/Seeker-flying-bird` (Compose-Multiplatform game, Android+iOS+NestJS) | 2026-07-07 | Opus 4.8, reviewed by Fable 5 |
| [kids-minecraft-lite-v4](projects/kids-minecraft-lite-v4.md) | `Android-Apps/kids-minecraft-lite-v4` (LibGDX kids' game — code is v5) | 2026-07-07 | Opus 4.8, reviewed by Fable 5 |

No row for the repo you're in? Run [DISTILL.md](DISTILL.md) — ideally on the strongest
model available — then add the row.

## Order of operations (any project)

1. **Bootstrap:** the repo's own `CLAUDE.md`/`AGENTS.md` (always authoritative — this skill NEVER overrides them) + its session-memory index if one exists + the matching `projects/<slug>.md` §0.
2. **Before acting:** OPERATING-MANUAL §1 — what is actually being asked? Especially when the request presumes something is "wrong": verify the presupposition first.
3. **While working:** follow the project map's flow sections; check its trap table before inventing a diagnosis. No map → work from the manual alone and note candidate traps as you hit them.
4. **Before handing over:** OPERATING-MANUAL §6 (attack the conclusion) + the 5-question self-test. Communicate per §7: answer → reasoning → risk.

## Non-negotiables this skill exists to protect

- Green gates ≠ done. Verify behavior on the journey you touched, in the real runtime.
- Numbers reconcile to EXTERNAL ground truth, never to a re-derivation of the same code.
- Class-of-bug → rule + mechanical audit, never a one-site patch.
- Say out loud what is verified vs inferred vs assumed.

## Maintenance

- Project maps are dated snapshots — the repo's own rulebook wins on conflict; fix the map to match, never the reverse.
- New paid-for gotcha (cost ≥ one session) → append to that project's trap table. Append-only.
- New repo distilled → new `projects/<slug>.md` + index row here. Commit + push (`~/.conan-agent-skills` is the source of truth; `~/.claude/skills/` holds symlinks).
