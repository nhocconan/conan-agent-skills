## §4. Monetization that survives store policy

### 4.1 The model that keeps a casual game clean

- Ads: banner (menu only, never gameplay), interstitial (frequency-capped: not before
  minute 2, not on first death, cooldown ≥ 90s), rewarded (player-initiated only:
  revive, double coins, unlock trial). Rewarded is the only ad players like — build
  the economy so they want it.
- IAP: one lifetime "remove ads" at $2.99–$4.99 typically converts best in genre
  (price-test via the stores' pricing experiments rather than trusting this number);
  it must remove
  interstitial+banner but KEEP rewarded (players consider rewarded a feature).
- Soft currency: **earn-only** (never purchasable with money) if you want to stay out
  of loot-box/gambling regulation entirely — document this stance; it also simplifies
  every store questionnaire.

### 4.2 The policy traps (each of these is a real rejection class)

- **Families/child-audience trap (Play):** your Target-audience declaration, your ad
  SDK configuration (TFCD/TFUA flags, max ad content rating), and your actual content
  must agree. Declaring or "appealing to" under-13 pulls you into the ads-format
  section of the Play Families Policies (rejections cite it as "Families ad format
  requirements"): ads serving children must be closeable within 5 seconds — stricter
  than the general-audience Ads policy's 15-second rule — plus certified ad SDKs only. "Appeals to
  children" is judged by Google from the app's look, not your intent: cartoon/cute
  characters, bright simple visuals, young actors in assets, child-oriented wording
  ("for everyone, including kids" in a brief is already a Families signal). If your
  art style is cute/cartoonish and you want 13+, declare 13+ explicitly, rate
  accordingly, configure ads PG/13+ — and expect Google may still classify you as
  child-appealing; have the Families-compliant ad config as the documented fallback.
  Decide 13+ vs Families BEFORE configuring ads, then make console declaration ⇔ code
  config ⇔ rating questionnaire all match. Mismatch = rejection loop.
- **Restore Purchases (Apple 3.1.1):** any non-consumable needs a reachable Restore
  button in EVERY entitlement state — missing it is an automatic reject.
- **Ads in review:** test ads must be un-shippable (build-type-gated), but real ads
  must show for reviewers — use real units with mediation test devices only on your
  own hardware.
- **Data safety / privacy labels:** must match the binary's actual SDK traffic
  (Play data-safety form, Apple nutrition labels). Ad SDKs = "data collected". An
  analytics SDK you forgot about is a rejection or a takedown later.
- **Consent stack (ads = consent obligations):** serving ads to EEA/UK users requires
  a Google-certified CMP gathering consent before the first ad request (in practice
  Google's UMP; missing it → limited ads + legal exposure); on iOS, ANY IDFA/tracking
  access requires the ATT prompt with an honest purpose string BEFORE access (skipping
  it → rejection or silent limited ads) — and the privacy labels (§ above) must agree
  with whatever the consent stack actually does.
- **Accounts imply deletion:** the moment your app has any account (§1.3 anonymous-first
  counts once it's linkable), Apple 5.1.1(v) and Play both require in-app account
  deletion, and Play additionally requires a web deletion URL declared in Data safety.
  Ship auth and deletion in the same release, never auth first.

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
