---
name: appstore-review-guard
description: >-
  Pre-submission compliance gate for Apple App Store (and Google Play) that prevents repeat
  rejections. Run BEFORE every submit/resubmit, and AFTER any rejection to record the cause
  + fix in the rejection ledger. Catches the avoidable "silly" rejections — missing Restore
  Purchases (3.1.1), device frames in preview videos (2.3.4), metadata that promises
  unshipped features, debug/QA hooks shipping in release, unused permission strings, missing
  privacy policy URL. Triggers include "App Store reject", "app got rejected", "guideline
  3.1.1/2.3.4/2.1/4.x", "before I submit", "pre-submission check", "resubmit", "App Review".
---

# App Store Review Guard

Most App Store rejections are not subtle judgement calls — they're the same
short list of **avoidable, mechanical mistakes** that a checklist catches in
minutes. This skill is that checklist, plus a **rejection ledger** you append to
after every real rejection so the same mistake never ships twice.

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
| producing or reviewing App Preview video / marketing screenshots, or the rejection cites 2.3.4 | `sections/preview-video.md` |
| verifying any code- or metadata-level item — the curl/grep recipes that turn a checkbox into a fact | `sections/verification-recipes.md` |
| you want the researched sharp checks, 2026 rejection-frequency data, and sources | `sections/research-notes.md` |

**Append after every rejection**, per `sections/rejection-ledger.md`. A rejection
that leaves no ledger row will be paid for a second time.

## Related

`store-screenshots` — produces the compliant screenshots and preview video.
`mobile-app-playbook` — the shipping process this gate sits inside.
