## Researched refinements (sharp checks worth singling out)

These came out of researching current (guidelines revised **Nov 13 2025**; **4.3 tightened Jun 9 2026**) reviewer behaviour — the non-obvious ways the "obvious" items still fail:

- **The 4.3 "value" bar moved up (Jun 9 2026).** Apple expanded **4.3 Spam** to "apps that do not add value to the App Store" and can now **remove already-published apps** for low engagement in saturated categories — not just reject new ones. This is the single most common reject (~28% in 2026 surveys). Hardest hit: **video players, timers, calculators, notes, matchstick puzzles**. For a utility app, the differentiator must be *visible in the first screenshot*, and review notes should argue *why it exists*, not just *how to test it*. Once a reviewer leaves a 4.3 note on your developer file, future submissions get scrutinized harder — avoid the first flag at all costs. (Sources: 9to5Mac, MacRumors, MediaNama — Jun 2026.)
- **2026 reject leaderboard.** Community/App-figure data puts the top reasons at **4.3 Spam ≈28%**, then **2.1 Completeness** (bugs/broken links/missing demo), **5.1.1 Privacy** (policy URL dead / label ≠ binary), **3.1.2 Subscription disclosure**, and **IP.6.1 metadata** (trademarked art/names in icon/screenshots/description — fixable *without* a new build). Design your pre-flight around this order, not alphabetical.
- **3.1.2 disclosure must live in the binary, "clearly and conspicuously."** Apple reproduces the subscription terms from the **app**, not App Store Connect. The minimum inline set on the paywall: title, period, price/period, the "auto-renews unless cancelled ≥24h before period end" sentence, trial length + conversion sentence (where a trial exists), and tappable Terms + Privacy links. Hiding any of these only inside a Terms sheet is the common miss. A subscription whose "ongoing value" isn't demonstrable (a one-time content drop sold as a sub) is a separate, harder 3.1.2 reject — use a non-consumable for those.
- **Verify links as an anonymous visitor.** A Support/Privacy URL that 404s, hits a login wall, or points to a **private** repo is a routine reject. `curl -s -o /dev/null -w '%{http_code}' -L <url>` must return `200` with **no auth**; also open in a private window. **Check the LIVE App Store Connect value, not the repo's copy** — repo listing files drift out of sync (ledger #3: copy pointed Support/Privacy/Legal at the **backend API host** which serves only JSON routes; the real pages lived on the marketing host). Use the [URL-live recipe](sections/verification-recipes.md) to collect *every* URL from the repo, not just the ones you remember.
- **Restore must call `AppStore.sync()` only behind the button** (never on launch) and re-read **`Transaction.currentEntitlements`** — not `Transaction.all` (which includes refunded/revoked) — taking only `.verified` results with `revocationDate == nil`. Never show a custom Apple-ID/password field.
- **Every restore tap needs visible feedback in every screen that hosts the button.** A `Task { await store.restore() }` that discards the result is a gap: `.nothingToRestore` often clears the error state, so the user sees a spinner stop and *nothing*. Capture the outcome and alert (restored / nothing / failed) regardless of entitlement state.
- **Background modes ↔ real tasks (2.5.4).** Declaring `processing` in `UIBackgroundModes` with no `BGProcessingTaskRequest` (or `fetch` with no `BGAppRefreshTaskRequest`) is flagged. Every `BGTaskScheduler` id must also be in `BGTaskSchedulerPermittedIdentifiers` and registered before launch finishes, or you get **ITMS-90771** at upload.
- **Notifications: stay functional + consent-clean (4.5.4 / 5.1.2).** Reminder content only — no Pro upsell / "rate us" / ads in notifications. The app must stay **fully usable with notification permission DENIED**. `.timeSensitive` is fine; `.critical` needs the (separately-approved) Critical Alerts entitlement — don't request `.criticalAlert` without it.
- **Privacy label must match the binary.** "Data Not Collected" requires zero network/analytics/ad/tracking code, no `NSUserTrackingUsageDescription`, no ATT prompt, no SKAdNetwork. Also add an **in-app** link to the same privacy policy (Settings/About), not just the ASC field.
- **Screenshots: real UI, exact specs.** PNG/JPEG, RGB, **no alpha channel**, exact accepted sizes; verify with `sips`/`file`. Reconcile the submission guide's count/order/filenames against the actual files (they drift after renames).
- **Single source of truth for listing copy (2.3.7).** Name (≤30) / subtitle / promo / keywords / description must come from ONE canonical file and match byte-for-byte everywhere; `diff` the artifacts before pasting into ASC.

## Sources

- App Store Review Guidelines (revised Nov 13 2025) — https://developer.apple.com/app-store/review/guidelines/
- App Previews — stay within the app, no device frames/hands — https://developer.apple.com/app-store/app-previews/
- Screenshot specifications — App Store Connect Help — https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Manage app privacy (privacy policy URL required; "Data Not Collected") — https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/
- User Privacy and Data Use (ATT, tracking definition, purpose strings) — https://developer.apple.com/app-store/user-privacy-and-data-use/
- Restore IAP with StoreKit 2 (`AppStore.sync` + `currentEntitlements`) — https://tanaschita.com/20231009-restore-in-app-purchases-storekit/
- `BGTaskScheduler` — https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler

### 2026 rejection-frequency & guideline-update research (added Jun 22 2026)

- Apple tightens 4.3 — "apps that do not add value", removal of published low-engagement apps — https://9to5mac.com/2026/06/09/apple-tightens-app-review-guidelines-against-apps-that-do-not-add-value-to-the-app-store/ and https://www.macrumors.com/2026/06/09/app-store-guidelines-low-quality-apps/ and https://www.medianama.com/2026/06/223-apple-remove-app-store-apps-low-engagement/
- Auto-renewable Subscriptions (in-app presentation requirements) — https://developer.apple.com/app-store/subscriptions/
- App Review Guideline updates (news feed, incl. 3.1.2(a) changes) — https://developer.apple.com/news/?id=xqk627qu
- Adapty 2026 checklist (subscription disclosure table) — https://adapty.io/blog/how-to-pass-app-store-review/
- RevenueCat – Ultimate Guide to App Store Rejections — https://www.revenuecat.com/blog/growth/the-ultimate-guide-to-app-store-rejections/
- App Store rejection reasons index (2026 heatmap: 4.3, 2.1, 5.1.1 dominant) — https://pushmyapp.ai/blog/app-store-rejection-reasons
