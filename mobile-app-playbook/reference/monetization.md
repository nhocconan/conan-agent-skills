## §4. Monetization that survives store policy

### 4.1 The model that keeps a casual game clean

- Ads: banner (menu only, never gameplay), interstitial (frequency-capped: not before
  minute 2, not on first death, cooldown ≥ 90s), rewarded (player-initiated only:
  revive, double coins, unlock trial). Rewarded is the only ad players like — build
  the economy so they want it.
- IAP: price-test a lifetime "remove ads" offer; no genre-wide best price is established here. State whether optional rewarded ads remain before purchase, and honor that promise.
- Soft currency: an earn-only economy can reduce purchase complexity, but does not establish an exemption from gambling or loot-box rules. Review the actual mechanics and distribution regions.

### 4.2 The policy traps (each of these is a real rejection class)

- **Families/child-audience trap (Play):** your Target-audience declaration, your ad
  SDK configuration (TFCD/TFUA flags, max ad content rating), and your actual content
  must agree. Declaring or "appealing to" under-13 pulls you into the ads-format
  section of the Play Families Policies (rejections cite it as "Families ad format
  requirements"): [ads interfering with normal use, including rewarded ads, must be closeable after 5 seconds](https://support.google.com/googleplay/android-developer/answer/9893335); non-interfering placements may persist longer. Apply the same protections to unknown-age users in mixed-audience apps; use certified SDKs for these users. "Appeals to
  children" is judged by Google from the app's look, not your intent: cartoon/cute
  characters, bright simple visuals, young actors in assets, child-oriented wording
  ("for everyone, including kids" in a brief is already a Families signal). If your
  art style is cute/cartoonish and you want 13+, declare 13+ explicitly, rate
  accordingly, configure ads PG/13+ — and expect Google may still classify you as
  child-appealing; have the Families-compliant ad config as the documented fallback.
  Decide 13+ vs Families BEFORE configuring ads, then make console declaration ⇔ code
  config ⇔ rating questionnaire all match. Mismatch = rejection loop.
- **Restore Purchases (3.1.1):** checked by `appstore-review-guard`; design it into the paywall in §2, not at submission.
- **Ads in review:** replace demo units/test-device debug settings before publication; use [test ads](https://developers.google.com/admob/android/test-ads) on development devices. Verify production configuration and consent/no-fill behavior; do not force an ad to appear by bypassing consent or audience rules.
- **Data safety / privacy labels:** reconcile the binary's SDK traffic with each
  store's collection/sharing definitions and the SDK's disclosure guidance. Audit
  analytics and ad SDKs explicitly; do not infer disclosures from the SDK name alone.
- **Consent stack:** Google publisher products require a [Google-certified TCF CMP](https://support.google.com/admob/answer/13554116) for personalized ads in the EEA, UK and Switzerland. With UMP, refresh consent information and check [`canRequestAds()`](https://developers.google.com/admob/android/privacy) before requests; a denied consent choice does not automatically prohibit every ad mode. On iOS, obtain ATT permission before tracking/IDFA access; privacy labels must match actual behavior.
- **Accounts imply deletion:** Apple's requirement includes automatically created guest accounts. Play applies its [app-account definition and creation-flow scope](https://support.google.com/googleplay/android-developer/answer/13327111), with an in-app deletion path plus a web resource. Do not equate a device identifier with an app account; inspect the actual account flow. Ship required deletion alongside account creation (`appstore-review-guard`).

### 4.3 Money correctness (silent-failure class — verify hardest here)

- Server verifies every receipt/transaction (Play Developer API / App Store Server API);
  client-side grant is a placebo.
- **Unit/decimal discipline:** store amounts in the smallest unit with the AUTHORITATIVE
  decimals of the asset. Real failure: a token had 6 decimals on-chain; code assumed 9;
  every real payment was rejected as underpaid. Verify decimals against the source of
  truth (the chain / the store API), not against another file in the same repo.
- **Entitlement restore across reinstall/device-change/account-relink** is a first-class
  flow with its own tests: pay → uninstall → reinstall → restore; pay → new device →
  restore; pay under system A → migrate to system B (schema v1 → v2) → restore. The
  migration case is the one everyone misses: users who paid BEFORE a schema change must
  still restore afterward.
- Idempotency: the same receipt replayed twice grants once.

**Gate §4:** the full money matrix (each product × purchase/restore/refund × platform)
executed against the REAL sandbox (StoreKit sandbox, Play internal testing), server
logs showing verification, plus the §4.2 declarations cross-checked in both consoles.

---
