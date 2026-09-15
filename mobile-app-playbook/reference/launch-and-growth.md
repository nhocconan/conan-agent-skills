# Launch & growth reference

Loaded when the app is built and you are shipping it. Everything here is post-build:
getting through review, ranking in the store, and operating the app as a service.

## Contents
- §6. Store submission — pre-submission gates, staged rollout ladder, dwell rules
- §7. ASO — listing, keywords, review prompts, localization
- §8. Post-launch — LiveOps cadence, crash/ANR budgets, rating recovery

---

## §6. Store submission

Run the `appstore-review-guard` skill before EVERY submit/resubmit — it holds the live
checklist and the rejection ledger for the review-risk items (Restore Purchases, listing
URL liveness, debug/QA hooks, data-safety/privacy declarations, preview-video framing).
Items that sit outside that guard's scope:

- The TestFlight / internal-testing build is actually played through the core loop on a
  real device before submit — a build that installs is not a build that was tested.
- Store questionnaires (content rating, target audience, data safety, export/encryption)
  are answered from the BINARY's truth, not from hope — and re-answered after adding any
  SDK, because the SDK changes the truthful answer.
- Version/versionCode strictly increasing across every release track; release
  keystore/cert custody documented; R8/minify ON with tested proguard rules; app size
  sanity-checked against the last release.
- Never write store-console navigation paths from memory in docs/guides — consoles
  re-organize yearly. Verify against current official docs, link the deep URL, and add
  "type the page name into the console search box" as fallback.

**Rollout ladder (don't skip rungs):** internal testing → closed testing → (optional
but recommended) a geo-limited **soft launch** to validate the §0 retention numbers
with real users BEFORE the global push and any ASO spend → production with **staged
rollout** (Play lets you set the percentage manually and never auto-increases it; a
common convention is 5–10% → 25% → 50% → 100% — iOS phased release, by contrast, ramps
automatically over 7 days), with written halt criteria tied to the §0 vitals numbers
(e.g. "halt below 99.5% crash-free"). Dwell before each increase: hold at least 24–48h
AND until the new build has enough installs for the vitals read to mean something
(rule of thumb: ~1k+ sessions for crash-rate direction; retention reads need ~1–2k
installs and, for D7, seven days of calendar — don't promote on a same-day D7 guess).
Read the Play pre-launch report on every track promotion — it's free device-farm QA.

**Gate §6:** appstore-review-guard checklist green on both platforms; a dry-run build
installed from the store track (internal testing / TestFlight) on a real device and
played end-to-end, including one real sandbox purchase + restore.

---

## §7. ASO — ranking is a product surface, not an afterthought

- **Title/subtitle/keywords:** title = brand + strongest keyword (30 chars);
  iOS subtitle (30) and keyword field (100, comma-separated, no spaces, no duplicates
  of title words); Play short description (80) is both keyword surface and conversion
  copy. Research actual search volume (competitor titles are free research: what words
  do the top 10 in genre share?).
- **Screenshot story:** first 2 screenshots decide conversion — they must show the core
  loop + the hook as OUTCOME copy ("One tap. Don't die.") not feature lists. Sequence:
  hook → gameplay proof → depth (collection/dailies) → social proof. Use `store-screenshots`
  for the production pipeline; sizes/specs change — verify current-year requirements before
  rendering.
- **Video:** Play promo video + iOS App Preview (full-bleed, real capture, first 5s
  carry the message — most views are muted + truncated).
- **Ratings engine:** wire the platform in-app review APIs at the moment of earned
  delight: new best score, level-set complete, streak milestone — NEVER after a death,
  never on first session, never more than once per version. Quotas (verified 2026):
  iOS hard-caps at 3 prompts per 365 days per user and silently ignores extras; Play's
  quota is deliberately undocumented and may silently no-op — so the call must always
  be fire-and-forget, gated by your own policy (sessions ≥ 3, days-since-install ≥ 2,
  ≥ 60 days between prompts). This single feature moves rating from 4.0 → 4.5 over
  months; rating gates both ranking and conversion.
- **Localization:** localize the LISTING first (top 5–10 locales for your genre) — it's
  cheap and moves ranking per-locale; localize the app itself only for locales that
  convert. A one-tap game may need almost no in-app text — that's an ASO advantage,
  keep it that way.
- **Events/LiveOps surfaces:** iOS in-app events and Play promotional content are free
  featuring real estate tied to your daily-challenge/seasonal cadence (§8).
- **Custom store listings (Play):** per-country/per-audience listings once you know your
  top acquisition segments.

**Gate §7:** listing copy A/B plan written; every claim in the listing is true of the
shipped binary (screenshot count of levels/characters matches code constants); review
prompt fires in a debug walkthrough at the designed moment and never at a forbidden one.

---

## §8. Post-launch — the app is now a service

- **Watch the vitals dashboards daily for the first 2 weeks** (Android vitals, Xcode
  Organizer/App Store Connect metrics): crash-free %, ANR, hang rate, battery. Play
  DEMOTES ranking on bad vitals; this is an ASO input, not just hygiene.
- Respond to every review < 24h in launch month (responses are ranked/visible and
  convert fence-sitters; on Play they can flip a 1★ to 4★).
- LiveOps cadence sustainable by ONE person: weekly = new daily-challenge modifier or
  mission rotation (config-only, no release); monthly = a content drop (character/
  level pack) with an in-app event on both stores; quarterly = a feature.
- Remote-config kill-switches for: each ad format, each experimental feature, anti-cheat
  thresholds. Deploy-day rule: config values that gate money or fairness get re-checked
  against production (they live in the DB, not the repo — a code read tells you nothing).
- Keep the rejection ledger and the §9-style failure catalog growing; feed each new scar
  back into the relevant checklist so the NEXT release is cheaper.

---
