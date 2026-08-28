## Google Play — pre-submission checklist

Same philosophy, different scanner: Play review is more automated, and **Play
Protect** does static pattern-matching on the binary. Real rejection basis: a
crypto-adjacent build flagged as suspicious purely because unobfuscated
wallet/signing symbols were visible in the bytecode.

### Play Protect / binary hygiene
- ☐ **R8/ProGuard on for release**: `isMinifyEnabled = true` + `isShrinkResources = true` + a real `proguard-rules.pro` (keep rules for the engine, reflection paths, SDKs). Unobfuscated financial/crypto symbols (`signAndSendTransactions`, `Base58`, wallet classes) pattern-match malware signatures.
- ☐ **v2+ APK signing** (`enableV2Signing = true` minimum; v3 for key rotation). v1-only is rejected. Verify alignment: `zipalign -c 4 app.apk`.
- ☐ `targetSdkVersion` meets Play's current floor (rises yearly — check the current requirement at support.google.com/googleplay/android-developer/answer/11926878; as of 2026-08: new apps/updates ≥ API 36 from 2026-08-31, existing apps ≥ API 35 to stay visible to new users).
- ☐ **Permissions audit**: nothing high-risk without justification (`READ_SMS`, `SYSTEM_ALERT_WINDOW`, `REQUEST_INSTALL_PACKAGES`, accessibility). Every permission in the manifest maps to a visible feature.
- ☐ No dynamic code loading (`DexClassLoader` on downloaded code, remote `.so`) — all code bundled at build time.
- ☐ Wire these as **automated pre/post-build checks in the release script** (verify R8 on, proguard file non-trivial, signing scheme, alignment) so a misconfigured build can't ship.

### Listing & policy
- ☐ **Data safety form matches the binary** (Play's version of the privacy label) — declared collection/sharing = actual SDK behaviour.
- ☐ Billing: same "distinct Restore purchases button" rule as 3.1.1 (`queryPurchasesAsync()` behind an explicit control).
- ☐ Promo video is a **YouTube link** (vertical 1080×1920 is fine; Play tolerates device frames and >30s, but keep the same story as the screenshots).
- ☐ If rejected/flagged: check Play Console pre-launch report first; `bundletool validate`; appeal false positives with a plain-language description of the legitimate functionality.

---
