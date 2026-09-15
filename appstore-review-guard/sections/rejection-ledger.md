# Rejection ledger

Read this before running any checklist (a repeat of a logged rejection is the
likeliest failure), and **append to it after every real rejection** — guideline,
what the reviewer saw, root cause, the fix, and the new permanent checklist item
that makes it unrepeatable. The ledger is the point of this skill; keep it growing.

> Illustrative rejection **patterns** distilled from real submissions — dates and
> project-specific identifiers stripped so this stays a public, reusable checklist
> rather than a private incident log. Each pattern is now also a checklist item.
> **Append a new generalized pattern here after every new rejection.**

| # | Guideline | What the reviewer saw | Root cause | Fix shipped |
|---|---|---|---|---|
| 1 | **2.3.4** Accurate Metadata (previews) | App Preview **video** showed a device frame / bezel | The video pipeline reused the same rendering path as the still-image marketing mockups; previews must be full-bleed screen capture | Preview re-rendered full-bleed from real captures (no device mockup); marketing screenshots may keep frames, the **video may not**. Also dropped an unshipped feature claim from the listing. See `store-screenshots` skill. |
| 2 | **3.1.1** In-App Purchase (Restore) | App offers restorable IAP but no distinct **"Restore Purchases"** button; auto-restore on launch ≠ acceptable | The only Restore control lived inside the paywall's purchase section, gated on the app's premium-unlock check → it **vanished once purchased**, and Settings had no IAP-restore button (only a same-named "Restore from file" backup button, which misleads) | Added a distinct, always-present "Restore purchases" button in **Settings → Pro plan** (visible regardless of entitlement state) and a dedicated always-visible Restore section in the **Paywall**; restore returns a precise outcome (restored / nothing-to-restore / failed) with an alert. See [3.1.1 deep-dive](restore-purchases.md). |
| 3 | **2.1 / 5.1.1** Broken listing URLs (pre-submission catch) | Support / Privacy / Legal URLs in the listing copy returned **HTTP 404** — the app's marketing site never hosted those pages, and the copy wrongly pointed them at the **backend API host** (which serves JSON routes only, no static pages) | Listing copy was written against the backend subdomain instead of the marketing host that actually hosted the static pages | Hosted the missing pages on the marketing host and **repointed every listing/review-notes URL** (localized copy included) to the marketing host; the backend subdomain is now referenced **only** where review notes explain the gateway. Caught by the [URL-live recipe](verification-recipes.md) before submit — no rejection, but it *would* have been a clean 2.1/5.1.1 reject. |
| 4 | **Play: Families Policy — Families Ad Format Requirements** (a cartoon-mascot casual game) | "**Unclosable ads**: Ads interfere with app use and can't be closed after 5 seconds" — reviewer hit a full-screen ad creative (game-over interstitial or rewarded) not closable within 5s | App got scoped into **Families Policy** (target-audience declaration in Play Console included an under-13 group, or Google's "appeals to children" determination — cartoon-animal mascot, content rating Everyone), while the binary's ad config was built for 13+ (Google Mobile Ads `RequestConfiguration` left at `TAG_FOR_CHILD_DIRECTED_TREATMENT_UNSPECIFIED` + `MAX_AD_CONTENT_RATING_PG`) → the ad SDK was free to serve long unskippable/playable creatives that violate Families ad-format rules | Align declaration ⇔ ad config. EITHER declare 13+ only (no under-13 group ticked, matches shipped config, no new build) OR fully comply with Families (`TAG_FOR_CHILD_DIRECTED_TREATMENT_TRUE`, `MAX_AD_CONTENT_RATING_G`, AdMob app marked child-directed, Families Self-Certified SDK version, new build). Permanent rule: **never ship a 13+ ad config while the console declaration puts the app in Families scope** — cross-check the Target audience page against `RequestConfiguration` before every Play submit. |

**Pattern across both:** a required thing existed in the code but was **not
reachable in the state the reviewer was in.** That's the failure mode to hunt.

---

## Enriching this skill (do this after every rejection)

1. Add a generalized row to the [rejection ledger](rejection-ledger.md): guideline, what they saw, root cause, fix — strip dates and project-specific identifiers (app names, flag/variable names, hostnames) so the row reads as a reusable pattern.
2. Add a permanent ☐ item to the matching [checklist](apple-checklist.md) section so it's checked forever after.
3. If it's code-detectable, add a [grep recipe](verification-recipes.md).
4. If new, research the current guideline text (Apple updates them) before writing the fix — link the source below.

---
