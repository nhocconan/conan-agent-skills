## Pre-submission checklist

Group by guideline area. ☐ = must verify every submission.

### 3.1.1 — In-App Purchase & payments
- ☐ A **distinct, clearly-labelled "Restore Purchases" button** exists and is reachable in **every** entitlement state — fresh install, mid-trial, **after purchase**, and after trial-ended. Not gated behind `!isPro`. Not auto-restore-only.
- ☐ It lives where reviewers look: **Settings** (canonical) **and** the paywall. Don't rely on the paywall alone — it often hides post-purchase.
- ☐ "Restore" wording is unambiguous: a backup/import feature must **not** be the only thing called "Restore" (rename it "Restore from file" / "Import").
- ☐ Restore actually calls the platform restore (`AppStore.sync()` on StoreKit 2 / `restorePurchases()` on Play Billing) and gives user feedback on success/failure.
- ☐ Purchase failures show user-facing feedback (no dead button).
- ☐ Nothing is **sold that isn't implemented** (paywall feature list == shipped features). "Planned" features only as clearly-labelled future notes, never in the buy list.
- ☐ **Scope the external-purchase-link rule by storefront, not blanket.** On the **United States storefront**, Guideline 3.1.1(a) does **not** prohibit buttons, external links, or other calls-to-action to non-IAP purchase methods, and no entitlement is required there. Outside the US storefront, such buttons/links/CTAs are prohibited **unless** the app holds a StoreKit External Purchase Link Entitlement or Music Streaming Services Entitlement for that specific storefront (those entitlements only cover the storefronts Apple lists for them). Check the current entitlement-covered storefront list before submitting — don't assume the US rule travels with the build.
- ☐ Non-consumable: don't use "free trial" wording that implies an auto-renewing subscription. An app-managed trial is fine if described as one-time.

### 3.1.2 — Auto-renewable subscription disclosure
> Reviewers reproduce subscription terms from the **binary**, not just App Store
> Connect. If the disclosure is incomplete in-app, you get 3.1.2 even when ASC is
> correct. Apple requires it "clearly and conspicuously".
- ☐ The paywall shows, **inline (not only inside a Terms sheet)**: subscription **title**, **length/period**, **price per period**, and a one-line **auto-renew disclosure** ("Automatically renews unless cancelled at least 24 hours before the end of the current period").
- ☐ **Free-trial terms** are stated where a trial is offered: trial length, what happens at conversion (paid subscription begins), and that you can cancel during the trial. Don't show a "free trial" badge without the conversion sentence.
- ☐ **Terms of Use / EULA** and **Privacy Policy** are reachable from the paywall as tappable links (sheets or external URLs that return 200).
- ☐ If you offer **multiple cadences** (weekly/monthly/yearly/lifetime), each plan's price + period is shown; a plan with no trial must not be captioned as having one.
- ☐ Don't sell a subscription whose **"ongoing value"** Apple can't see — a subscription that unlocks a static one-time deliverable (e.g. a one-off content drop) is a common 3.1.2 reject. The Pro entitlement must deliver continuing value (unlimited use, ongoing features).

### 2.1 — App completeness
- ☐ No placeholder/lorem/"coming soon" content, no dead buttons, no broken links.
- ☐ **Every public listing/review-notes URL works for an anonymous visitor** — Support, Privacy, Marketing, and any review-note link. Run the [URL-live recipe](verification-recipes.md) against the repo listing files, then open every final URL in a fresh private browser session and confirm the expected public page, not a login wall, generic landing page, private repo, or API response. Transport success alone is not enough. **Don't trust the repo's copy as the source of truth** — cross-check the live App Store Connect values; they can drift after manual edits. (See ledger #3.)
- ☐ App doesn't crash on launch on the **reviewer's device class** (they test iPad too — see 4.0).
- ☐ Demo account / reviewer notes provided if any gating exists.
- ☐ Every advertised feature actually works on this platform build.

### 2.3 — Accurate metadata
- ☐ **App Preview video is full-bleed** real screen capture — **no device frame/bezel** (2.3.4). (Marketing screenshots MAY use frames.)
- ☐ Screenshots show **real in-app UI** only; no features the build doesn't have.
- ☐ Listing copy promises nothing unshipped (cut "Widgets/Siri/etc." if not in this build).
- ☐ Preview video uploads at the **correct slot size** (iPhone App Preview: 886×1920 or 1920×886 — NOT the 1320×2868 screenshot size; ASC rejects the wrong one). iPad sizes per slot.
- ☐ The advertised USP is **demonstrated** in screenshots/video, not just claimed (Apple can reject "feature not shown").
- ☐ App name/subtitle/keywords aren't spammy or trademark-infringing (2.3.7).

### 5.1 — Privacy
- ☐ **Privacy policy URL is set in App Store Connect metadata AND linked within the app itself in an easily accessible manner** — Guideline 5.1.1(i) requires both placements for **every app**, regardless of whether it has an account or IAP.
- ☐ App Privacy answers match the app's and every integrated third party's actual data practices. For a "Data Not Collected" answer, inventory every data flow and apply Apple's definition of collection; a network call or SDK is a review signal, not proof by itself. Check vendor documentation and privacy manifests as well as runtime behavior.
- ☐ `Info.plist` contains **only the permission usage strings the app actually uses.** A stray `NS*UsageDescription` invites "why do you need this?" questions. No `NSUserTrackingUsageDescription` unless ATT is actually used.
- ☐ **If the app supports account creation, account deletion is offered *inside the app*** — Guideline 5.1.1(v): "If your app supports account creation, you must also offer account deletion within the app." A support email, a web-only form, or a "deactivate" toggle does not satisfy it; the path must be reachable from within the binary the reviewer runs. Walk it end to end on the submitted build. Play requires an equivalent in-app path plus a publicly reachable web deletion URL declared in the Play Console data-safety form, so ship both.

### 4.3 — Spam / "apps that do not add value" (Design)
> Apple’s current 4.3 rule rejects established app categories that do not offer a
> meaningfully different or improved experience, and identifies low-effort apps that
> do not add value to the App Store. Re-read the current guideline before submission;
> there is no official rejection-frequency ranking. See [policy notes](research-notes.md).
- ☐ The app has a **clear, demonstrable differentiator** vs. the obvious alternatives — and that USP is **shown** in screenshots/preview, not just claimed in copy. If a reviewer can name two apps that do the same thing, you're at risk.
- ☐ Not a reskin/template/cookie-cutter of another app under the same account (shared source, shared assets, near-identical UI). **Own every visual asset** (icon, screenshots, preview video); don't lift stock/copyrighted art into metadata (separate **IP.6.1** metadata reject — fixable without a new build, but still a reject).
- ☐ For a **new** account/app in a saturated category, the app clears a genuine usefulness bar, not just "it works". Reviewer notes should spell out *why this exists*, not just *how to test it*.
- ☐ No duplicate apps under the same Apple ID doing essentially the same job (consolidate, don't multiply).

### 2.3.1 / 2.5 — Hidden features, debug code, APIs
- ☐ **No debug/QA hook can activate in a release build.** Every launch-arg / test path is wrapped in `#if DEBUG`; the flags it sets default to inert.
- ☐ No hidden/undocumented features toggled by special input.
- ☐ No entitlements the app isn't approved for / doesn't use (e.g. don't ship `com.apple.developer.alarmkit`, critical-alerts, push `aps-environment` if unused).
- ☐ No private API usage.

### 4.5.4 / background — notifications & background modes
- ☐ Notifications serve the **core function** (reminders), not marketing/promotion. No promotional pushes without explicit opt-in.
- ☐ `interruptionLevel`/time-sensitive usage is justified by the feature.
- ☐ Every `BGTaskScheduler` identifier used in code is declared in `Info.plist` (`BGTaskSchedulerPermittedIdentifiers`) and the matching `UIBackgroundModes` are present.

### 4.0 — Design & device coverage
- ☐ App is **fully usable on iPad** if the binary targets iPad (reviewers test iPad Air/Pro). No iPhone-only layout that hides controls on a regular-width size class. **Both 2.3.4 and 3.1.1 above were reviewed on iPad** — test there.
- ☐ Supports the orientations it declares; no truncated/inaccessible controls; Dynamic Type / large text doesn't clip critical buttons.

---
