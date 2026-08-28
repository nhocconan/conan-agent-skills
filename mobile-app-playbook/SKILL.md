---
name: mobile-app-playbook
description: >-
  End-to-end operating playbook for building and shipping a top-chart-quality
  Android + iOS app or game — the full thinking process of a senior orchestrator model,
  written so worker-tier models can execute it. Covers: defining the
  quality bar with numbers, architecture choice (KMP/Compose Multiplatform seams, platform
  traps), game-feel/UX standards, retention meta-systems, monetization that survives store
  policy, the verification discipline (fake-green traps, per-stage gates, bot-verified
  difficulty), store submission, ASO, and post-launch LiveOps. Trigger when: building a new
  mobile app/game, upgrading one to "top of market" quality, planning a mobile release,
  auditing a mobile app for quality/retention/ASO, or when the user says "world-class app",
  "SOTA mobile", "top chart", "lên top chart", "build app chuẩn thế giới", "chuẩn bị release
  app", "làm game mobile", "submit app", "improve retention", "tăng rating", "ASO",
  "monetization plan".
---

# Mobile App Playbook — build through store, top-chart bar

> Written by Claude Fable 5 (2026-07) as a capability handoff: the complete thinking
> process for taking a mobile app/game from "works" to "top of market", distilled from
> real shipped projects (a cross-platform arcade game that went through Play closed
> testing, a real Play rejection, a working IAP + ads stack, and an iOS CMP port).
> Every rule here was either paid for with a real failure or verified on a real release.
>
> Companion skills (use them at the step that names them): `appstore-review-guard`
> (pre-submission gate + rejection ledger), `store-screenshots` (listing assets),
> `bug-class-audits` (class-not-instance fixes), `senior-operator` (how to think under
> ambiguity; per-repo maps).

---

## How to use this skill

1. Read §0 (the bar) and §OP (orchestration) first — they shape every other step.
2. **§0, §OP and §5 apply at ALL times**; §1–§4 are the build ladder, and §6–§8
   (in `reference/launch-and-growth.md`) are the launch ladder — open that file once
   the build is real.
   Locate your project on the ladder — you almost never start at §1: audit the existing
   app against each phase's checklist and enter at the first phase with unchecked boxes.
3. Each phase ends with a **gate** — objective checks, not vibes. Do not advance
   through an open gate; the cost of skipping compounds silently.
4. When a step fails in a new way, generalize the failure into a rule and append it to
   your project's own failure catalog (modeled on §9). Only promote a rule into THIS
   file's §9 once it is fully project-agnostic — this file never carries project detail.

**Router — symptom → section:**

| You're here because… | Go to |
| --- | --- |
| Starting a new app/game, or scoping a big upgrade | §0 → §1 |
| App works but feels cheap / "not juicy" | §2 |
| D1 retention weak (players quit in the first session) | §2 (the hook/onboarding is the problem, not meta-systems) |
| D1 fine but D7/D30 weak (no reason to return) | §3 |
| Ads/IAP planning, or a policy question | §4 |
| Got rejected by a store | §4.2 + `reference/launch-and-growth.md` §6 + `appstore-review-guard` |
| Agent/CI says green but the app is broken | §5 |
| Preparing to submit / resubmit | `reference/launch-and-growth.md` §6 |
| Good app, low installs or low rating | `reference/launch-and-growth.md` §7 |
| Live app: what now? | `reference/launch-and-growth.md` §8 |

---

## Section index — Read each section when its situation applies

This skill is a decision-tree skeleton: the phases live in `reference/` and are
read at the step that needs them, not up front. Read a section in full before
working its phase; do not work from memory of the router table alone.

| When | Read this section |
|------|-------------------|
| starting a project or scoping an upgrade — defining the quality bar in numbers (§0) | `reference/define-the-bar.md` |
| day-0 stack choice, the seams that decide survival, backend (§1) | `reference/architecture.md` |
| the app works but feels cheap; juice, retry loop, onboarding, platform polish (§2) | `reference/game-feel-ux.md` |
| D1 is fine but D7/D30 is weak — retention meta-systems (§3) | `reference/retention.md` |
| planning ads/IAP, answering a policy question, or auditing money correctness (§4) | `reference/monetization.md` |
| any verification question — fake green, the per-stage gate, bot-verified difficulty (§5). Applies at ALL times | `reference/verification.md` |
| the build is real: store submission gates and the staged-rollout dwell ladder (§6), ASO as a product surface — listing, keywords, review-prompt policy, localization (§7), running the app as a service afterwards — LiveOps cadence, crash/ANR budgets, rating recovery (§8) | `reference/launch-and-growth.md` |
| a step failed in a new way and you want the generalized scars behind these rules (§9) | `reference/failure-catalog.md` |

§0, §5 and the orchestration rules below apply at all times. §1–§4 are the build
ladder; §6–§8 the launch ladder.

## §OP. Orchestration — spend model capacity like money

The full fleet discipline (tier routing, parallel DAG, briefs, scored verification,
integration) lives in **`agent-orchestration`** — that skill is the single source; read
it when staffing any multi-workstream build. What's specific to mobile work:

- **The natural cut** is per module or per layer (engine / UI / backend / assets). Two
  agents editing the same Gradle module is merge hell — one writer per module, worktrees
  when they must overlap.
- **Briefs quote the traps from §9** (this file's failure catalog) that apply to the
  workstream, plus "implement, do NOT commit".
- **Verification inherits the fake-green traps of §5** — the orchestrator re-runs the
  build/test itself, on device/emulator where the check is behavioral, and reviews the
  diff hunk by hunk before committing atomically.
- Anything learned mid-workstream goes into the spec of the next one.

---

---

## The pre-ship self-test (run before calling anything "done")

1. **The bar:** which §0 number does this change move, and how will I see it move?
2. **The gate:** did EVERY §5.2 command run at HEAD, exit-code-checked, by me (not an agent's claim)?
3. **The journey:** did I watch the real app do the changed thing on a real device/simulator?
4. **The money/policy:** if this touches payment, ads, or declarations — did I re-run the §4 matrix and cross-check the consoles?
5. **The next model:** is what I learned written where the next (possibly weaker) model will find it — spec, checklist, or failure catalog?

If any answer is "no" or "sort of", the work isn't done. The flinch is the signal.
