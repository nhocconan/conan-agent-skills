## Guideline 3.1.1 — Restore Purchases (the pattern)

A frequent avoidable IAP rejection. Guideline 3.1.1 itself says only that you "make sure you have a restore mechanism for any restorable in-app purchases" (read 2026-10-02); App Review's rejection message typically adds:

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
