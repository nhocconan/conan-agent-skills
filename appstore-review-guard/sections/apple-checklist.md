## Pre-submission checklist

Group by guideline area. ☐ = must verify every submission.

### 3.1.1 — In-App Purchase & payments
- ☐ A **distinct, clearly-labelled "Restore Purchases" button** exists and is reachable in **every** entitlement state — fresh install, mid-trial, **after purchase**, and after trial-ended. Not gated behind `!isPro`. Not auto-restore-only.
- ☐ It lives where reviewers look: **Settings** (canonical) **and** the paywall. Don't rely on the paywall alone — it often hides post-purchase.
- ☐ "Restore" wording is unambiguous: a backup/import feature must **not** be the only thing called "Restore" (rename it "Restore from file" / "Import").
- ☐ Restore actually calls the platform restore (`AppStore.sync()` on StoreKit 2 / `restorePurchases()` on Play Billing) and gives user feedback on success/failure.
- ☐ Purchase failures show user-facing feedback (no dead button).
- ☐ Nothing is **sold that isn't implemented** (paywall feature list == shipped features). "Planned" features only as clearly-labelled future notes, never in the buy list.
- ☐ No mention of external/web purchasing or other payment methods for digital goods.
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
- ☐ **Every URL in the listing returns HTTP 200 anonymously** — Support, Privacy, Marketing, any URL in review notes (e.g. a takedown contact). Run the [URL-live recipe](sections/verification-recipes.md) against the **repo listing files** to collect every URL, then curl each as an anonymous visitor (no auth cookie). A 404/redirect-to-login/private-repo URL is an automatic 2.1/5.1.1 reject. **Don't trust the repo's copy as the source of truth** — cross-check against the live App Store Connect value; they drift apart after manual edits. (See ledger #3.)
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
- ☐ **Privacy policy URL is set** in App Store Connect (required for any app with an account or IAP; safe to always provide).
- ☐ App Privacy "nutrition label" matches reality. If "Data Not Collected" is claimed in-app, there must be **no network/analytics/tracking SDK** in the binary.
- ☐ `Info.plist` contains **only the permission usage strings the app actually uses.** A stray `NS*UsageDescription` invites "why do you need this?" questions. No `NSUserTrackingUsageDescription` unless ATT is actually used.

### 4.3 — Spam / "apps that do not add value" (Design)
> Top single reason for rejection (~28%). Apple **tightened 4.3 on June 9 2026** —
> see [researched refinements](sections/research-notes.md).
> Once flagged, a note sticks to the developer's file; subsequent submissions get
> harder. Hardest on **saturated categories** (video players, timers, calculators,
> matchstick puzzles, notes).
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
