## Researched refinements (sharp checks worth singling out)

These notes supplement, but never replace, the current official policy. Re-check the
linked Apple/Google source at submission time; store policies and console surfaces move.
Checklist items (3.1.1(a) storefront scope, 4.3, 3.1.2 disclosure, anonymous URL check, Restore, privacy label) live in `apple-checklist.md` and `restore-purchases.md`.

- **Restore internals (beyond the checklist).** Call `AppStore.sync()` only behind the button, never on launch. Re-read `Transaction.currentEntitlements`, not `Transaction.all` (includes refunded/revoked); accept only `.verified` with `revocationDate == nil`. Never show a custom Apple-ID/password field.
- **Background modes ↔ real tasks (2.5.4).** Match each declared mode to implemented work. Check task types, permitted identifiers and registration against the selected BackgroundTasks API, then verify scheduling on the submitted build; a plist declaration alone does not prove valid background behavior or a particular upload error.
- **Notifications (4.5.4 / 5.1.2).** The app must function with notification permission denied. Promotional pushes require explicit marketing opt-in in the app and an in-app opt-out; ordinary push permission alone is insufficient. Critical Alerts need Apple's entitlement; use time-sensitive delivery only for qualifying content.
- **Screenshots: real UI, exact specs.** PNG/JPEG, RGB, **no alpha channel**, exact accepted sizes; verify with `sips`/`file`. Reconcile the submission guide's count/order/filenames against the actual files (they drift after renames).
- **Single source of truth for listing copy (2.3.7).** Name (≤30) / subtitle / promo / keywords / description must come from ONE canonical file and match byte-for-byte everywhere; `diff` the artifacts before pasting into ASC.

## Sources

- App Store Review Guidelines (the page carries no revision date; Apple presents it as a living document — re-read at submission time) — https://developer.apple.com/app-store/review/guidelines/
- App Previews — stay within the app, no device frames/hands — https://developer.apple.com/app-store/app-previews/
- Screenshot specifications — App Store Connect Help — https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Manage app privacy (privacy policy URL and app/third-party disclosure responsibility) — https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/
- App Privacy Details (Apple’s definition of collection) — https://developer.apple.com/app-store/app-privacy-details/
- User Privacy and Data Use (ATT, tracking definition, purpose strings) — https://developer.apple.com/app-store/user-privacy-and-data-use/
- `AppStore.sync()` — https://developer.apple.com/documentation/storekit/appstore/sync()
- `Transaction.currentEntitlements` — https://developer.apple.com/documentation/storekit/transaction/currententitlements
- `BGTaskScheduler` — https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler

### Policy-update reading (refresh at submission)

- Auto-renewable Subscriptions (in-app presentation requirements) — https://developer.apple.com/app-store/subscriptions/
- Updated guidelines now available — 3.1.1/3.1.1(a)/3.1.3/3.1.3(a) external-purchase-link changes for the US storefront, May 1 2025 — https://developer.apple.com/news/?id=9txfddzf
- For later guideline revisions, use the living guidelines and Apple's current news; an older announcement does not establish the latest policy.
