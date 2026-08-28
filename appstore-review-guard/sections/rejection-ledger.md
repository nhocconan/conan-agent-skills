# Rejection ledger

Read this before running any checklist (a repeat of a logged rejection is the
likeliest failure), and **append to it after every real rejection** — guideline,
what the reviewer saw, root cause, the fix, and the new permanent checklist item
that makes it unrepeatable. The ledger is the point of this skill; keep it growing.

> Real rejections this account/app has hit. Each one is now also a checklist
> item. **Append here after every new rejection.**

| # | Date | Guideline | What the reviewer saw | Root cause | Fix shipped |
|---|---|---|---|---|---|
| 1 | 2026-06-17 | **2.3.4** Accurate Metadata (previews) | App Preview **video** showed a device frame / bezel | Video pipeline reused the still-image `device_mockup()`; previews must be full-bleed screen capture | Preview re-rendered full-bleed from real captures (no mockup); marketing screenshots may keep frames, the **video may not**. Also dropped an unshipped "Widgets & Siri" claim. See `store-screenshots` skill. |
| 2 | 2026-06-21 | **3.1.1** In-App Purchase (Restore) | App offers restorable IAP but no distinct **"Restore Purchases"** button; auto-restore on launch ≠ acceptable | The only Restore control lived inside the paywall's purchase section, gated `proUnlockEnabled && !isPro` → it **vanished once purchased**, and Settings had no IAP-restore button (only a same-named "Restore from file" backup button, which misleads) | Added a distinct, always-present "Restore purchases" button in **Settings → Pro plan** (gated only on `proUnlockEnabled`) and a dedicated always-visible Restore section in the **Paywall**; restore returns a precise outcome (restored / nothing-to-restore / failed) with an alert. See [3.1.1 deep-dive](sections/restore-purchases.md). |
| 3 | 2026-06-22 | **2.1 / 5.1.1** Broken listing URLs (pre-submission catch) | Support / Privacy / Legal URLs in the listing copy returned **HTTP 404** — the app's marketing site never hosted those pages, and the copy wrongly pointed them at the **backend API host** (which serves JSON routes only, no static pages) | Listing copy was written against the backend subdomain (`<api-host>/privacy`) instead of the marketing host; the marketing site had the app's sibling pages but not this app's | Created `<marketing-host>/<app-slug>/{index,privacy,terms,support}.html` on the marketing host (same template as the sibling app) and **repointed every listing/review-notes URL** (`en-US.md`, `listing.html`, `SUBMISSION-GUIDE.md`, `docs/APPSTORE.md`, localized copy) to `<marketing-host>/<app-slug>/*`. The backend subdomain is now referenced **only** where review notes explain the gateway. Caught by the [URL-live recipe](sections/verification-recipes.md) before submit — no rejection, but it *would* have been a clean 2.1/5.1.1 reject. |
| 4 | 2026-07-08 | **Play: Families Policy — Families Ad Format Requirements** (a cartoon-mascot casual game) | "**Unclosable ads**: Ads interfere with app use and can't be closed after 5 seconds" — reviewer hit a full-screen AdMob creative (game-over interstitial or rewarded) not closable within 5s | App got scoped into **Families Policy** (target-audience declaration in Play Console included an under-13 group, or Google's "appeals to children" determination — cartoon-animal mascot, content rating Everyone), while the binary's ad config was built for 13+: `TAG_FOR_CHILD_DIRECTED_TREATMENT_UNSPECIFIED` + `MAX_AD_CONTENT_RATING_PG` untagged requests → AdMob free to serve long unskippable/playable creatives that violate Families ad-format rules | Align declaration ⇔ ad config. EITHER declare 13+ only (no under-13 group ticked, matches shipped config, no new build) OR fully comply with Families (TFCD=TRUE, `MAX_AD_CONTENT_RATING_G`, AdMob app marked child-directed, Families Self-Certified SDK version, new build). Permanent rule: **never ship a 13+ ad config while the console declaration puts the app in Families scope** — cross-check the Target audience page against `RequestConfiguration` before every Play submit. |

**Pattern across both:** a required thing existed in the code but was **not
reachable in the state the reviewer was in.** That's the failure mode to hunt.

---

## Enriching this skill (do this after every rejection)

1. Add a row to the [rejection ledger](sections/rejection-ledger.md): date, guideline, what they saw, root cause, fix.
2. Add a permanent ☐ item to the matching [checklist](sections/apple-checklist.md) section so it's checked forever after.
3. If it's code-detectable, add a [grep recipe](sections/verification-recipes.md).
4. If new, research the current guideline text (Apple updates them) before writing the fix — link the source below.

---
