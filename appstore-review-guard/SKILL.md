---
name: appstore-review-guard
description: Pre-submission compliance gate for Apple App Store (and Google Play) that prevents repeat rejections. Run BEFORE every submit/resubmit, and AFTER any rejection to record the cause + fix in the rejection ledger. Catches the avoidable "silly" rejections — missing Restore Purchases (3.1.1), device frames in preview videos (2.3.4), metadata that promises unshipped features, debug/QA hooks shipping in release, unused permission strings, missing privacy policy URL. Triggers: "App Store reject", "app got rejected", "guideline 3.1.1/2.3.4/2.1/4.x", "before I submit", "pre-submission check", "resubmit", "App Review".
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

## How to use this skill

1. **Before any submission/resubmission:** run the [pre-submission checklist](#pre-submission-checklist) top to bottom. Anything unchecked is a blocker until resolved.
2. **After a rejection:** read Apple's message, find the guideline number, fix the code/metadata, then **append a row to the [rejection ledger](#rejection-ledger)** — guideline, what they saw, root cause, the fix, and a new permanent checklist item so it can't recur. The ledger is the whole point; keep it growing.
3. **Verify, don't assume.** For code-level items, run the [grep recipes](#fast-verification-recipes) against the actual repo. For UI items, drive the app in the **exact state the reviewer reaches** (fresh install, post-purchase, trial-ended).

---

## Rejection ledger

> Real rejections this account/app has hit. Each one is now also a checklist
> item. **Append here after every new rejection.**

| # | Date | Guideline | What the reviewer saw | Root cause | Fix shipped |
|---|---|---|---|---|---|
| 1 | 2026-06-17 | **2.3.4** Accurate Metadata (previews) | App Preview **video** showed a device frame / bezel | Video pipeline reused the still-image `device_mockup()`; previews must be full-bleed screen capture | Preview re-rendered full-bleed from real captures (no mockup); marketing screenshots may keep frames, the **video may not**. Also dropped an unshipped "Widgets & Siri" claim. See `store-screenshots` skill. |
| 2 | 2026-06-21 | **3.1.1** In-App Purchase (Restore) | App offers restorable IAP but no distinct **"Restore Purchases"** button; auto-restore on launch ≠ acceptable | The only Restore control lived inside the paywall's purchase section, gated `proUnlockEnabled && !isPro` → it **vanished once purchased**, and Settings had no IAP-restore button (only a same-named "Restore from file" backup button, which misleads) | Added a distinct, always-present "Restore purchases" button in **Settings → Pro plan** (gated only on `proUnlockEnabled`) and a dedicated always-visible Restore section in the **Paywall**; restore returns a precise outcome (restored / nothing-to-restore / failed) with an alert. See [3.1.1 deep-dive](#guideline-311--restore-purchases-the-pattern). |

**Pattern across both:** a required thing existed in the code but was **not
reachable in the state the reviewer was in.** That's the failure mode to hunt.

---

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

### 2.1 — App completeness
- ☐ No placeholder/lorem/"coming soon" content, no dead buttons, no broken links.
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

## Guideline 3.1.1 — Restore Purchases (the pattern)

This is the single most common avoidable IAP rejection. Apple's exact bar:

> Provide a **distinct "Restore" button** and initiate the restore when tapped.
> **Automatically restoring purchases on launch will not resolve this.**

**The trap that gets you rejected:** putting Restore only inside the paywall's
"buy" area, conditionally rendered. Reviewers test by **purchasing first**, then
looking for Restore — and your buy area (with the Restore button in it) is now
hidden because the user owns the product. Result: "no Restore button."

**The fix (StoreKit 2):**

```swift
// ProStore.swift — explicit, user-initiated restore with a precise outcome
enum RestoreOutcome: Equatable { case restored, nothingToRestore, cancelled, failed(String) }

@discardableResult
func restore() async -> RestoreOutcome {
    guard !isRestoring else { return .cancelled }
    isRestoring = true; defer { isRestoring = false }
    do { try await AppStore.sync() }                 // <-- the actual restore call
    catch {
        await refreshEntitlement()
        if let e = error as? StoreKitError, case .userCancelled = e { return .cancelled }
        return .failed("Couldn't restore. Make sure you're signed in to the App Store and try again.")
    }
    let owned = await currentEntitlementOwned()       // re-derive from Transaction.currentEntitlements
    onEntitlementChange?(owned)
    return owned ? .restored : .nothingToRestore
}
```

```swift
// Settings — a DISTINCT, ALWAYS-PRESENT button (gated only on IAP being on)
if AppConfig.proUnlockEnabled {
    Button("Restore purchases") { Task { lastOutcome = await proStore.restore() } }
    // show an alert for restored / nothingToRestore / failed (ignore cancelled)
}
```

Place it **both** in Settings (where reviewers look first) **and** as its own
always-visible section in the paywall — visible even after purchase. Confirm the
result with an alert so the action is never silent.

**Play Billing equivalent:** query `queryPurchasesAsync()` / call the billing
client's restore path behind an explicit "Restore purchases" button; same "must
be a real, distinct, tappable control" rule applies.

---

## Guideline 2.3.4 — Preview video & screenshots

Delegated to the **`store-screenshots`** skill, which already encodes:
- App Preview **video = full-bleed real capture, no device frame** (the 2.3.4 fix).
- Screenshots may use device frames; copy is outcome-first; the advertised USP must be **shown**.
- Correct upload sizes (iPhone preview 886×1920, screenshot 1320×2868, etc.).

When this guard flags a 2.3.x metadata risk, hand the asset work to
`store-screenshots`.

---

## Fast verification recipes

Run these against the repo before submitting (paths are examples; adapt):

```bash
# 3.1.1 — is there a Restore control NOT gated behind purchase state?
grep -rn "Restore purchases\|AppStore.sync\|restorePurchases" ios/ --include="*.swift"
#   → expect a button in Settings gated only on the IAP flag, plus an always-visible paywall section.

# 2.3.1 / 2.5 — every QA/launch-arg hook must be inside #if DEBUG
grep -rn "ProcessInfo.processInfo.arguments\|CommandLine\|-ui[A-Z]" ios/ --include="*.swift"
#   → each must sit within a #if DEBUG ... #endif; the vars they set default to inert.

# entitlements — nothing the app isn't approved for (e.g. AlarmKit, critical alerts, push)
find ios -name "*.entitlements" -not -path "*/build/*" -exec cat {} \;

# 5.1 — claims "no data collected" but talks to the network?
grep -rn "URLSession\|URLRequest\|Alamofire\|analytics\|firebase\|amplitude\|mixpanel" ios/ --include="*.swift" | grep -v build/

# 4.5.4 / background — BG task ids in code must be declared in Info.plist
grep -rn "BGTaskScheduler\|register(forTaskWithIdentifier" ios/ --include="*.swift"
#   → cross-check each id against Info.plist BGTaskSchedulerPermittedIdentifiers + UIBackgroundModes.

# Info.plist — only the usage strings you actually use
plutil -p ios/HourlyMove/App/Info.plist | grep -i "UsageDescription\|BackgroundModes\|BGTaskScheduler"
```

For UI affordances, **drive the real states** (don't trust static reads):
fresh install → mid-trial → **post-purchase** → trial-ended. The Restore button
must be visible and working in all four.

---

## Enriching this skill (do this after every rejection)

1. Add a row to the [rejection ledger](#rejection-ledger): date, guideline, what they saw, root cause, fix.
2. Add a permanent ☐ item to the matching [checklist](#pre-submission-checklist) section so it's checked forever after.
3. If it's code-detectable, add a [grep recipe](#fast-verification-recipes).
4. If new, research the current guideline text (Apple updates them) before writing the fix — link the source below.

---

## Researched refinements (sharp checks worth singling out)

These came out of researching current (guidelines revised **Nov 13 2025**) reviewer behaviour — the non-obvious ways the "obvious" items still fail:

- **Verify links as an anonymous visitor.** A Support/Privacy URL that 404s, hits a login wall, or points to a **private** repo is a routine reject. `curl -s -o /dev/null -w '%{http_code}' -L <url>` must return `200` with **no auth**; also open in a private window. **Check the LIVE App Store Connect value, not the repo's copy** — repo listing files drift out of sync (this app's `en-US.md` still held dead GitHub URLs while ASC actually used working `dep.app` ones; auditing the repo alone would have raised a false blocker *and* missed the real source of truth).
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
