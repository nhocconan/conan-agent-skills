---
name: mobile-app-playbook
description: >-
  Operating playbook for building and shipping an Android + iOS app or game through store
  submission: quality bar in numbers, architecture seams, game feel, retention,
  monetization under store policy, verification gates, ASO, LiveOps. Trigger when:
  building a new mobile app/game, upgrading one to "top of market" quality, planning a
  mobile release, auditing a mobile app for quality/retention/ASO, or when the user says
  "world-class app", "SOTA mobile", "top chart", "lên top chart", "build app chuẩn thế
  giới", "chuẩn bị release app", "làm game mobile", "submit app", "improve retention",
  "tăng rating", "ASO", "monetization plan".
---

# Mobile App Playbook — build through store, top-chart bar

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

## §OP. Orchestration — spend model capacity like money

Fleet discipline, tier routing, briefs and integration live in
[`agent-orchestration`](../agent-orchestration/SKILL.md); the lead slot, model IDs and
tier table live in [`agent-orchestration/sections/routing.md`](../agent-orchestration/sections/routing.md).
Mobile-specific facts only:

- Natural cut: per module or layer (engine / UI / backend / assets); one writer per Gradle module.
- Briefs quote the applicable rows of `reference/failure-catalog.md`.
- Have the §5.2 gate re-run through a runner on the final tree; accept only its verdict, never the builder's (`reference/verification.md` §5.1).
- Escalate critical receipt verification, concurrency, and engine invariants to the harness lead.

---

## The pre-ship self-test (run before calling anything "done")

1. **The bar:** which §0 number does this change move, and how will I see it move?
2. **The gate:** did EVERY §5.2 command run at HEAD, exit-code-checked, by me (not an agent's claim)?
3. **The journey:** did I watch the real app do the changed thing on a real device/simulator?
4. **The money/policy:** if this touches payment, ads, or declarations — did I re-run the §4 matrix and cross-check the consoles?
5. **The next model:** is what I learned written where the next (possibly weaker) model will find it — spec, checklist, or failure catalog?

If any answer is "no" or "sort of", the work isn't done. The flinch is the signal.
