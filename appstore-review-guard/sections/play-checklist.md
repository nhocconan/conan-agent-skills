## Google Play — pre-submission checklist

Use the actual Play policy notice and submitted artifact to diagnose a flag.
Visible wallet/signing symbols alone do not prove why Play Protect flagged a build;
obfuscation is not a policy-compliance fix.

### Play Protect / binary hygiene
- ☐ Review release optimization: if R8/resource shrinking is enabled, keep rules cover reflection, engines and SDKs; test the optimized artifact. Check applicable [DEX optimization thresholds](https://developer.android.com/google/play/vitals); minification is not a universal upload requirement or malware remediation.
- ☐ Verify the delivered APK with `apksigner verify --verbose`; apps targeting API 30+ need v2+ signing on Android 11+ ([Android requirement](https://developer.android.com/about/versions/11/behavior-changes-11#minimum-signature-scheme)). Validate the AAB and Play-generated APKs when using Play App Signing.
- ☐ `targetSdkVersion` meets the [current floor](https://support.google.com/googleplay/android-developer/answer/11926878): phone new apps/updates ≥ API 36 from 2026-08-31; existing phone apps ≥ API 35 for availability to new users on newer OS versions. Wear/Automotive/TV/XR have separate floors; check the applicable table.
- ☐ **Permissions audit**: nothing high-risk without justification (`READ_SMS`, `SYSTEM_ALERT_WINDOW`, `REQUEST_INSTALL_PACKAGES`, accessibility). Every permission in the manifest maps to a visible feature.
- ☐ No executable dex/JAR/.so downloads outside Google Play. Check [Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/9888379) for interpreted-code exceptions and restrictions; dynamic loading is not universally forbidden.
- ☐ Automate the applicable release checks (optimized-build smoke test, signing and artifact validation) so a misconfigured build can't ship.

### Listing & policy
- ☐ **Data safety form matches the binary** (Play's version of the privacy label) — declared collection/sharing = actual SDK behaviour.
- ☐ Billing: reconcile owned purchases with `queryPurchasesAsync()` when connecting/returning to the foreground ([integration guide](https://developer.android.com/google/play/billing/integrate)). An explicit Restore control can help users, but do not gate reconciliation on it or import Apple's button pattern as a Play policy requirement.
- ☐ Promo video is a [YouTube link](https://support.google.com/googleplay/android-developer/answer/9866151) — public/unlisted, embeddable, no age restriction or ads. Portrait/landscape both supported; 30 seconds is the autoplay window, not an upload-duration cap.
- ☐ If rejected/flagged: check Play Console pre-launch report first; `bundletool validate`; appeal false positives with a plain-language description of the legitimate functionality.

---
