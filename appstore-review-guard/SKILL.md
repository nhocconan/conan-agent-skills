---
name: appstore-review-guard
description: >-
  Use when about to submit or resubmit to the App Store / Google Play, and after any
  rejection ("App Store reject", "app got rejected", "guideline 3.1.1/2.3.4/2.1/4.x",
  "before I submit", "App Review", "pre-submission check", "resubmit"). Compliance
  gate against repeat rejections: missing Restore Purchases, device frames in preview
  videos, metadata promising unshipped features, debug hooks in release, unused
  permission strings, missing privacy policy URL; records cause + fix in the rejection
  ledger.
---

# App Store Review Guard

Apple doesn't publish rejection-frequency data, so no claim about the "most
common" rejection is verifiable — but every rejection logged in this skill's own
ledger was an **avoidable, mechanical mistake**, not a subtle judgement call: a
required thing that existed in the code but wasn't reachable in the state the
reviewer was in. This skill is a checklist built to catch that failure mode,
plus a **rejection ledger** you append to after every real rejection so the same
mistake never ships twice.

**Golden rule:** the reviewer is a busy human on one device looking for reasons
to bounce you. Every required affordance must be **obvious, reachable in the
state they'll be in, and labelled the way they expect.** "It's technically in
there" is how you get rejected.

**The failure mode to hunt:** every rejection in the ledger is a required thing
that existed in the code but was **not reachable in the state the reviewer was
in.** Check reachability, not existence.

## How to use this skill

1. **Before any submission/resubmission:** read the ledger, then run the
   platform checklist top to bottom. Anything unchecked is a blocker.
2. **After a rejection:** read Apple's message, find the guideline number, fix
   the code/metadata, then append a ledger row.
3. **Verify, don't assume.** Code-level items get a grep recipe run against the
   actual repo. UI items get driven in the **exact state the reviewer reaches**
   (fresh install, post-purchase, trial-ended).

## Section index — Read each section when its situation applies

This skill is a decision-tree skeleton. Read a section in full at its step; do
not work from memory. Paths are relative to this skill's directory.

| When | Read this section |
|------|-------------------|
| starting any submission, resubmission, or rejection response — always first | `sections/rejection-ledger.md` |
| running the Apple pre-submission checklist (3.1.1, 3.1.2, 2.1, 2.3, 5.1, 4.3, 2.3.1/2.5, 4.5.4, 4.0) | `sections/apple-checklist.md` |
| the target is Google Play — policy, Play Protect, binary hygiene, listing | `sections/play-checklist.md` |
| the app sells restorable IAP, or the rejection cites 3.1.1 — the full Restore Purchases pattern with code | `sections/restore-purchases.md` |
| producing or reviewing App Preview video / marketing screenshots, or the rejection cites 2.3.4 | `../store-screenshots/sections/preview-video.md` |
| verifying any code- or metadata-level item — the curl/grep recipes that turn a checkbox into a fact | `sections/verification-recipes.md` |
| you want the sourced policy notes and submission-time refresh links | `sections/research-notes.md` |

**Append after every rejection**, per `sections/rejection-ledger.md`. A rejection
that leaves no ledger row will be paid for a second time.

## Related

`store-screenshots` — produces the compliant screenshots and preview video.
`mobile-app-playbook` — the shipping process this gate sits inside.
