## Researched refinements (sharp checks worth singling out)

These notes supplement, but never replace, the current official policy. Re-check the
linked Apple/Google source at submission time; store policies and console surfaces move.

- **3.1.1(a) external purchase links are scoped by storefront.** On the **United States storefront**, the prohibition on buttons/external links/calls-to-action to non-IAP purchase does not apply, and no entitlement is required there — a 2025 change made to comply with a U.S. court order (Epic v. Apple). Everywhere else, the StoreKit External Purchase Link Entitlement or the Music Streaming Services Entitlement permits such a link, but each entitlement is valid only in the specific storefronts Apple lists for it; outside the US storefront and outside entitlement-covered storefronts, no such buttons/links/CTAs are allowed. Re-check the current storefront list before submission — it can change independently of the guideline text.
- **4.3 value bar.** Apple’s current guideline names established categories that need a meaningfully different or improved experience and says low-effort apps that do not add value may be removed. Show the actual differentiator in the binary and marketing assets; do not rely on a rejection-frequency ranking, because Apple does not publish one.
- **3.1.2 disclosure must live in the binary, "clearly and conspicuously."** Apple reproduces the subscription terms from the **app**, not App Store Connect. The minimum inline set on the paywall: title, period, price/period, the "auto-renews unless cancelled ≥24h before period end" sentence, trial length + conversion sentence (where a trial exists), and tappable Terms + Privacy links. Hiding any of these only inside a Terms sheet is the common miss. A subscription whose "ongoing value" isn't demonstrable (a one-time content drop sold as a sub) is a separate, harder 3.1.2 reject — use a non-consumable for those.
- **Verify links as an anonymous visitor.** A Support/Privacy URL that errors, hits a login wall, points to a private repo, or resolves to the wrong public page is a release blocker. Use the fail-closed [URL-live recipe](verification-recipes.md), then inspect every reported final URL in a private browser session. **Check the live App Store Connect value, not only the repo copy** — manual edits can make them differ.
- **Restore must call `AppStore.sync()` only behind the button** (never on launch) and re-read **`Transaction.currentEntitlements`** — not `Transaction.all` (which includes refunded/revoked) — taking only `.verified` results with `revocationDate == nil`. Never show a custom Apple-ID/password field.
- **Every restore tap needs visible feedback in every screen that hosts the button.** A `Task { await store.restore() }` that discards the result is a gap: `.nothingToRestore` often clears the error state, so the user sees a spinner stop and *nothing*. Capture the outcome and alert (restored / nothing / failed) regardless of entitlement state.
- **Background modes ↔ real tasks (2.5.4).** Declaring `processing` in `UIBackgroundModes` with no `BGProcessingTaskRequest` (or `fetch` with no `BGAppRefreshTaskRequest`) is flagged. Every `BGTaskScheduler` id must also be in `BGTaskSchedulerPermittedIdentifiers` and registered before launch finishes, or you get **ITMS-90771** at upload.
- **Notifications: stay functional + consent-clean (4.5.4 / 5.1.2).** Reminder content only — no Pro upsell / "rate us" / ads in notifications. The app must stay **fully usable with notification permission DENIED**. `.timeSensitive` is fine; `.critical` needs the (separately-approved) Critical Alerts entitlement — don't request `.criticalAlert` without it.
- **Privacy label must match actual collection and use.** Apple defines collection by whether data is transmitted off-device such that the developer or partner can access it beyond the time needed to service the request in real time. Audit app flows plus third-party partners, their documented behavior, and privacy manifests; the presence of networking or an SDK alone does not settle the answer. Also add an **in-app** link to the same privacy policy (Settings/About), not just the ASC field.
- **Screenshots: real UI, exact specs.** PNG/JPEG, RGB, **no alpha channel**, exact accepted sizes; verify with `sips`/`file`. Reconcile the submission guide's count/order/filenames against the actual files (they drift after renames).
- **Single source of truth for listing copy (2.3.7).** Name (≤30) / subtitle / promo / keywords / description must come from ONE canonical file and match byte-for-byte everywhere; `diff` the artifacts before pasting into ASC.

## Sources

- App Store Review Guidelines (the page carries no revision date; Apple presents it as a living document — re-read at submission time) — https://developer.apple.com/app-store/review/guidelines/
- App Previews — stay within the app, no device frames/hands — https://developer.apple.com/app-store/app-previews/
- Screenshot specifications — App Store Connect Help — https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Manage app privacy (privacy policy URL and app/third-party disclosure responsibility) — https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/
- App Privacy Details (Apple’s definition of collection) — https://developer.apple.com/app-store/app-privacy-details/
- User Privacy and Data Use (ATT, tracking definition, purpose strings) — https://developer.apple.com/app-store/user-privacy-and-data-use/
- Restore IAP with StoreKit 2 (`AppStore.sync` + `currentEntitlements`) — https://tanaschita.com/20231009-restore-in-app-purchases-storekit/
- `BGTaskScheduler` — https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler

### Policy-update reading (refresh at submission)

- Auto-renewable Subscriptions (in-app presentation requirements) — https://developer.apple.com/app-store/subscriptions/
- Updated guidelines now available — 3.1.1/3.1.1(a)/3.1.3/3.1.3(a) external-purchase-link changes for the US storefront, May 1 2025 — https://developer.apple.com/news/?id=9txfddzf
- Updated Apple Developer Program License Agreement and App Review Guidelines now available — most recent guideline revision (1.2, 4.3(a)/(b), 4.5.3), June 8 2026 — https://developer.apple.com/news/?id=a233fmpw
