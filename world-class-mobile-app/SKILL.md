---
name: world-class-mobile-app
description: >-
  End-to-end operating playbook for building and shipping a world-class (top-chart quality)
  Android + iOS app or game — the full thinking process of a senior orchestrator model,
  written so weaker/cheaper models (Opus, Sonnet) can execute it. Covers: defining the
  quality bar with numbers, architecture choice (KMP/Compose Multiplatform seams, platform
  traps), game-feel/UX standards, retention meta-systems, monetization that survives store
  policy, the verification discipline (fake-green traps, per-stage gates, bot-verified
  difficulty), store submission, ASO, and post-launch LiveOps. Trigger when: building a new
  mobile app/game, upgrading one to "top of market" quality, planning a mobile release,
  auditing a mobile app for quality/retention/ASO, or when the user says "world-class app",
  "SOTA mobile", "top chart", "lên top chart", "build app chuẩn thế giới", "chuẩn bị release
  app", "làm game mobile", "submit app", "improve retention", "tăng rating", "ASO",
  "monetization plan".
---

# World-Class Mobile App — the full playbook

> Written by Claude Fable 5 (2026-07) as a capability handoff: the complete thinking
> process for taking a mobile app/game from "works" to "top of market", distilled from
> real shipped projects (a cross-platform arcade game that went through Play closed
> testing, a real Play rejection, a working IAP + ads stack, and an iOS CMP port).
> Every rule here was either paid for with a real failure or verified on a real release.
>
> Companion skills (use them at the step that names them): `appstore-review-guard`
> (pre-submission gate + rejection ledger), `store-screenshots` (listing assets),
> `bug-class-audits` (class-not-instance fixes), `senior-operator` (how to think under
> ambiguity; per-repo maps).

---

## How to use this skill

1. Read §0 (the bar) and §OP (orchestration) first — they shape every other step.
2. **§0, §OP and §5 apply at ALL times**; §1–§4 and §6–§8 are the sequential ladder.
   Locate your project on the ladder — you almost never start at §1: audit the existing
   app against each phase's checklist and enter at the first phase with unchecked boxes.
3. Each phase ends with a **gate** — objective checks, not vibes. Do not advance
   through an open gate; the cost of skipping compounds silently.
4. When a step fails in a new way, generalize the failure into a rule and append it to
   your project's own failure catalog (modeled on §9). Only promote a rule into THIS
   file's §9 once it is fully project-agnostic — this file never carries project detail.

**Router — symptom → section:**

| You're here because… | Go to |
| --- | --- |
| Starting a new app/game, or scoping a big upgrade | §0 → §1 |
| App works but feels cheap / "not juicy" | §2 |
| D1 retention weak (players quit in the first session) | §2 (the hook/onboarding is the problem, not meta-systems) |
| D1 fine but D7/D30 weak (no reason to return) | §3 |
| Ads/IAP planning, or a policy question | §4 |
| Got rejected by a store | §4.2 + §6 + `appstore-review-guard` |
| Agent/CI says green but the app is broken | §5 |
| Preparing to submit / resubmit | §6 |
| Good app, low installs or low rating | §7 |
| Live app: what now? | §8 |

---

## §0. Define the bar with numbers, or you will polish forever

"World-class" is not a feeling. Before touching code, write down the target numbers.
For a casual/arcade mobile game in 2026, top-of-market means roughly:

| Dimension | Table-stakes | Top-chart |
| --- | --- | --- |
| D1 / D7 / D30 retention | 30% / 10% / 4% | 45%+ / 20%+ / 8%+ |
| Crash-free sessions | 99.5% | 99.8%+ |
| Android vitals | below "bad behavior" thresholds | green on ALL vitals (user-perceived crash < 1.09% overall / 8% per device model, ANR < 0.47% / 8% per model, excessive partial wake locks < 5% of sessions — 28-day windows; Play demotes visibility above them, per developer.android.com/topic/performance/vitals — re-verify thresholds there, they evolve) |
| Time-to-fun (install → first core-loop moment) | < 60s | < 20s, zero mandatory reading |
| Frame rate | stable 60fps on 5-year-old devices | 120Hz on ProMotion/high-Hz Android |
| Input latency (tap → visible response) | < 100ms | < 50ms, with haptic + audio confirm |
| Store rating | ≥ 4.0 | ≥ 4.5 with in-app review prompt wired |
| Store conversion (listing view → install) | genre median | above median via screenshot story + video |

Two consequences of writing these down:

- **Every proposed feature must name the number it moves.** "Add achievements" is not a
  plan; "achievements + streak calendar to move D7 from 12% → 18%" is.
- **The numbers force instrumentation.** If you can't measure D1 or time-to-fun, the
  first workstream is analytics, not features. Minimum event set: first_open,
  first-core-loop-moment (this timestamps time-to-fun), session_start/end, death/retry
  (or task complete/abandon), purchase, ad_impression, plus a crash-reporting SDK wired
  day 1 — D1/D7/D30 and every §0 number derive from these.

**Gate §0:** a one-page doc exists (suggested home: `docs/BAR.md`, or the project's map
file if you use `senior-operator`) with: target numbers, the core loop in one sentence,
the differentiator in one sentence ("why this and not the #1 in genre"), and the
platform list. If you cannot state the differentiator, stop — more polish will not fix
an undifferentiated product.

---

## §OP. Orchestration — spend model capacity like money

The strongest model available should do exactly four things: **decide, review, verify,
and write the tricky 10%**. Everything else is delegated.

| Work | Model tier | Why |
| --- | --- | --- |
| Codebase survey, feature inventory, doc reading | cheap (Sonnet-class), parallel read-only agents | breadth, no judgment calls |
| Web research (store policy, specs, benchmarks) | cheap, with "flag UNVERIFIED" instruction | facts either verify or don't |
| Implementation of a specified workstream | mid (Opus-class) | needs competence, not final judgment |
| Documentation, changelogs, store copy drafts | cheap→mid | review catches drift |
| Architecture decisions, diff review, gate verification, risk calls | strongest available | this is where wrong = expensive |

The loop that works (per workstream):

1. Orchestrator writes a **tight spec**: files in scope, exact acceptance checks, the
   traps from §9 that apply, "implement, do NOT commit".
2. Implementation agent works in the repo (worktree if parallel agents touch the same
   modules).
3. Orchestrator **verifies with its own commands** (never trusts the agent's claim of
   green — agents inherit the fake-green traps of §5), reviews the diff hunk by hunk,
   then commits atomically with explicit paths.
4. Anything learned goes into the spec of the next workstream.

Parallelize only what verifies independently. Two agents editing the same Gradle module
= merge hell; one agent per module or per layer (engine / UI / backend / assets) is the
natural cut.

---

## §1. Architecture — choose for the 90% you can't see yet

### 1.1 Stack choice (day 0, hard to reverse)

- **Game, 2D, needs iOS + Android, team is Kotlin-first** → Kotlin Multiplatform +
  Compose Multiplatform. Proven: full engine + ViewModels + UI in `commonMain`, thin
  platform hosts. You get ONE deterministic engine for both stores.
- **Game, 3D or physics-heavy** → Unity/Godot; don't fight it with app toolkits.
- **App (not game)** → native SwiftUI + Compose, or KMP for the logic layer only.
  Flutter is fine but you inherit its release-cycle risk on new OS versions.
- Whatever you choose, the test is: **can one codebase produce a deterministic result
  on both platforms?** Daily challenges, leaderboards, and anti-cheat all die if the
  answer is no.

### 1.2 The seams that decide whether the codebase survives

- **Platform seam:** one interface (e.g. `StorePlatform`) injected at startup carrying
  every platform/flavor difference (store channel, feature flags like crypto content,
  haptics/audio/IAP controllers). GameCore/business logic must never `#ifdef` by
  platform — it asks the seam.
- **Time seam:** `currentEpochMillis()` as expect/actual. Never `System.currentTimeMillis()`
  in shared code.
- **Randomness seam:** the engine takes a seed; identical seed ⇒ identical run,
  bit-for-bit, on both platforms. This is what makes daily challenges fair,
  replays/ghosts possible, and difficulty bot-testable (§5.4).
- **KMP trap (paid for repeatedly):** JVM unit tests pass while iOS is broken, because
  `java.lang.*` leaked into `commonMain` (Math, UUID, String.format, synchronized,
  Dispatchers.IO). **Rule: every stage runs the iOS framework link task**
  (`:<your-kmp-module>:linkDebugFrameworkIosSimulatorArm64` — find yours with
  `./gradlew tasks | grep linkDebugFramework`) — it is the only gate that catches this
  class. Replacements: `kotlin.math`, `kotlin.uuid.Uuid` (needs
  `@OptIn(ExperimentalUuidApi::class)` on Kotlin < 2.4; stable from 2.4), `Mutex`,
  expect/actual.
- **Flavor discipline:** if you ship store variants (e.g. Play build vs sideload build
  with extra SDKs), the store flavor must provably NOT contain the other flavor's SDKs
  (Play scans for them), and both flavors build + test at every stage.
- **iOS host minimum:** for CMP, `Info.plist` needs `CADisableMinimumFrameDurationOnPhone` —
  Compose Multiplatform's renderer fatal-errors at launch without it (a CMP check, not
  an Apple rule; Apple would merely cap you at 60Hz) — and the Xcode project should be
  generated (xcodegen) so it's reviewable text, not a binary pbxproj war.

### 1.3 Backend

- A game backend earns its existence with exactly: auth (anonymous-first), leaderboard,
  server-side IAP receipt verification, remote config, anti-cheat validation. Resist
  everything else at v1.
- Server-verified IAP is non-negotiable the day you charge money (§4.3).
- Remote config from day 1 (even a JSON column) — difficulty tuning, ad gating, and
  kill-switches must not require a store release.

**Gate §1:** both platforms build from one logic codebase; seed-determinism test passes
(two engine runs, same seed, identical event stream); platform seam exists; iOS link
task is in the standard build command; flavors verified clean.

---

## §2. Game feel & UX — the invisible 40% of "quality"

Players can't name frame pacing or input latency, but they uninstall over them. This is
where top-chart games actually differ from clones.

### 2.1 The juice checklist (each item is small; the sum is the product)

- [ ] Tap feedback < 50ms: sprite reacts same frame; sound + light haptic within 1 frame.
- [ ] Squash & stretch on the player character (jump/fall/land).
- [ ] Death: hit-stop (60–100ms freeze), screen shake, particle burst, then slow-mo or
      cut — never an instant modal.
- [ ] Score: number pops with scale bounce; milestone scores get color/sound escalation.
- [ ] Near-miss feedback (passed close to an obstacle): subtle whoosh/spark — it creates
      "skill feel" for free.
- [ ] Ambient motion in menus (parallax, floating particles, staggered card entrances) —
      a static menu reads as dead.
- [ ] Every button: pressed-state scale (≈0.95) + haptic tick.
- [ ] Transitions: no hard cuts between screens; 150–250ms slide/fade, but **interruptible**
      — a player who taps through must never wait for an animation.
- [ ] Sound design: separate SFX for tap, score, milestone, coin, death, unlock, purchase,
      button. Music ducks under death/result stingers. Respect the mute switch (iOS) and
      audio-focus (Android).
- [ ] Haptics: Core Haptics patterns on iOS (not just UIImpactFeedbackGenerator spam),
      VibrationEffect on Android; settings toggle; NEVER haptic on every frame.

### 2.2 The retry loop is the product

For any run-based game: death → retry must be **< 2 seconds and one tap**, with the run
summary readable at a glance. Every 100ms and every extra tap here costs real retention.
An interstitial ad must never race the result screen (frame-order bug class: ad covering
the result the same frame it appears) and must never appear on the FIRST death of a session.

### 2.3 Onboarding

- Playable within one tap of launch. Tutorial = the first level teaching by doing
  (ghost hand, one instruction word), not screens of text.
- First session must reach a "one more try" moment inside 90 seconds — instrument it.
- All permission prompts deferred until the feature needs them; never at first launch.

### 2.4 Platform polish checklist

- [ ] Safe areas correct on notch/Dynamic Island/home-indicator AND small devices (SE class).
- [ ] 120Hz: request high refresh rate explicitly (CADisplayLink preferred range / Android
      frame-rate API); interpolate world rendering at display Hz even if simulation ticks fixed.
- [ ] Predictive back (Android 14+), back never exits the app from a sub-screen.
- [ ] SplashScreen API (Android) / launch storyboard (iOS) matching the menu's first frame —
      no white flash, no double-splash.
- [ ] Dark-appropriate status bar, display cutout modes, landscape either fully supported
      or fully locked (half-support is worse than none).
- [ ] Text scaling: UI survives 1.3× font scale; touch targets ≥ 44pt/48dp.
- [ ] Reduced-motion setting respected for screen shake / parallax (a11y + motion sickness).
- [ ] Offline-first: the game plays with zero network; online features degrade with a
      quiet retry, never a blocking dialog.

**Gate §2:** run the app on the oldest device/simulator you support and the newest;
film both; watch the film at 0.5× speed looking for: dropped frames on death, layout
jumps, uninterruptible animations, any moment where a tap does nothing visible. Fix
what the film shows. (A film review catches what code review structurally cannot.)

---

## §3. Retention meta-systems — the difference between a toy and a product

Ship these in this order; each multiplies the previous. (Diagnosing a LIVE app: walk
this same ladder top-down and enter at the first rung that's missing or half-built —
the order doubles as the priority order for retrofits.)

1. **Progression skeleton:** levels/worlds OR endless with milestones. Numbers must be
   visible (level N, best score, % to next unlock).
2. **Collection:** characters/skins with rarity tiers, earned via play (see §4 for why
   earn-only currency keeps you compliance-safe). 8–12 at launch is enough if the last
   2 are aspirational.
3. **Daily challenge:** same seed for all players per day (needs §1.2 determinism),
   own leaderboard, streak counter. This is the single highest-ROI retention feature
   in the genre.
4. **Streaks + daily reward calendar:** escalating 7-day cycle, grace day (one missed
   day doesn't reset — reduces rage-quit), notification opt-in AFTER the player has a
   streak worth protecting (day 2–3, never day 0).
5. **Leaderboards:** global + friends; weekly reset tier gives everyone a chance;
   server-validated (§1.3) with plausibility anti-cheat (score vs time played vs input
   count) — a poisoned leaderboard is worse than none.
6. **Achievements:** map them to the platform systems (Game Center / Play Games) — they
   are free re-engagement surfaces and count toward platform featuring.
7. **Missions/quests (daily ×3, weekly ×1):** rotate objectives that push players into
   underused features ("score 10 with character X").

Re-engagement notifications: max 1/day, streak-protection and daily-challenge-reset
only, deep-link straight into the relevant screen, and the settings screen has a
per-category toggle. Anything more aggressive trades D30 for uninstalls.

**Gate §3:** a new player's first 7 days have a scripted reason to return each day —
write the 7-day storyboard down and check each day has one.

---

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

## §5. Verification discipline — where projects actually die

The bugs that kill releases are the ones your gates don't cover. These rules exist
because each was paid for:

### 5.1 Fake green (the worst class)

Piping a build through `tail`/`head`/`grep` makes the exit code the PIPE's exit code.
A missing SDK produced "BUILD SUCCESSFUL"-looking output for SIX stages once; nothing
had compiled. **Rule: never pipe build commands. Redirect to a log
(`> build.log 2>&1; echo EXIT=$?`), then check BOTH the exit code and a positive marker
(`BUILD SUCCESSFUL`, test counts) in the log.** An agent claiming green counts for
nothing until the orchestrator has re-run the command itself (§OP).

### 5.2 The per-stage gate (run ALL of it, every stage, no exceptions)

For a KMP/CMP project the minimum is: unit tests for EVERY flavor × the assemble for
EVERY flavor × the iOS framework link × (if backend touched) backend lint+test+build.
The stage isn't done until all are green AT HEAD — not green on the files you think
you touched.

**Bootstrap on a cold repo (do this FIRST, before any change):** derive the concrete
gate and freeze it into a script so you never re-derive it wrong. Recipe:
`./gradlew projects` (module list) → `./gradlew tasks | grep -E "test.*UnitTest|assemble|linkDebugFramework"`
(the real task names, including every flavor) → check `package.json`/`Makefile`/CI
config for the backend/web halves → write the full command list into `scripts/verify.sh`
with the §5.1 exit-code discipline baked in → run it once on a clean HEAD to prove the
baseline is green. From then on, "the gate" = that script, and any new module/flavor
must be added to it in the same PR that introduces it.

### 5.3 Behavior verification outranks green gates

Green gates prove you didn't break what the gates cover. After any UI/flow change:
launch the real app (emulator/simulator), traverse the changed journey, screenshot it.
Where simulator input automation is unavailable (common on iOS: no idb, no Accessibility
permission), build a **debug-only capture harness** into the app: launch args select a
screen, skip tutorials/prompts, autopilot gameplay. It pays for itself the first week
— and it must be compiled out of release builds (§6 debug-hook rule).

### 5.4 Bot-verify game difficulty (genre-specific but generalizes)

Hand-tuning difficulty is guessing. Write a headless bot that plays the real engine
thousands of runs across the whole level range, and assert invariants: every level
reachable, no level with median-death-at-zero, gap/reaction-time floors ≥ human limits,
difficulty monotonic where designed. This converts "feels hard" into a regression test —
and it once caught levels that were mathematically impossible.

### 5.5 Determinism as a test target

Same seed ⇒ identical obstacle/event IDs across two runs of the engine. Assert it in CI.
The day this silently breaks, daily challenges stop being fair and nobody notices for weeks
(silent × wide blast radius = highest risk class).

### 5.6 Class, not instance

Any bug that greps to more than one call site, or whose shape you've seen before, gets:
fix every site + a written rule + a mechanical audit script wired into pre-push.
See `bug-class-audits`.

**Gate §5:** the project has a single mirror command (`verify.sh` or equivalent) that
runs the full §5.2 set; the fake-green rule is followed in every script; a behavior
check on the touched journey is recorded (screenshot/film) for the stage.

---

## §6. Store submission

Run the `appstore-review-guard` skill before EVERY submit/resubmit — it holds the live
checklist and the rejection ledger. Summary of the invariants, roughly ordered by
rejection risk (missing Restore and dead policy URLs are near-automatic rejects; the
rest are frequent but reviewer-dependent):

- iOS: Restore Purchases reachable in every entitlement state (3.1.1 — near-automatic
  reject); no placeholder screens; App Preview video full-bleed (no device frames —
  2.3.4 plus Apple's App Preview specs); TestFlight build actually played to the core
  loop before submit.
- Every URL in the listing (privacy policy, terms, support) returns HTTP 200 anonymously —
  curl them from a clean session, and curl the URL DECLARED IN THE CONSOLE, not the one
  you think is declared.
- Store questionnaires (content rating, data safety, target audience, encryption) answered
  from the BINARY's truth, not from hope — and re-checked after adding any SDK.
- If the app has accounts: in-app account deletion reachable, plus Play's web deletion
  URL declared (§4.2) — reviewers check this.
- Debug/QA hooks (capture harness, autopilot, test menus) compiled out of release.
- Version/versionCode strictly increasing; release keystore/cert custody documented;
  R8/minify ON with tested proguard rules; app size sanity-checked against last release.
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

## §9. Failure catalog — generalized scars (why half these rules exist)

| Failure (real, generalized) | Rule it produced |
| --- | --- |
| Six "green" build stages; nothing had compiled (SDK missing; exit code was `tail`'s) | §5.1 never pipe builds; check exit code + positive marker |
| JVM tests green, iOS won't link (`java.lang.*` in shared code) | §1.2 iOS link task in every stage gate |
| CMP iOS app crashed at launch (missing frame-duration plist key) | §1.2 iOS host minimum |
| Play rejection: Families ad-format violation after audience declaration drifted from ad config | §4.2 declaration ⇔ code ⇔ rating must agree, decided up front |
| Every real token payment rejected: code assumed 9 decimals, asset had 6 | §4.3 verify decimals against the authoritative source |
| Paying users couldn't restore after account-system migration (v1 rows not mapped to v2) | §4.3 restore matrix includes schema-migration case |
| Interstitial covered the result screen on the same frame | §2.2 ad never races result UI |
| Daily challenge unfair: obstacle IDs differed between two runs of the same engine | §5.5 determinism is a CI assertion |
| "Impossible" levels shipped; players stuck at median-death-zero | §5.4 bot-verified difficulty invariants |
| Docs gave store-console menu paths from memory; console had been redesigned | §6 verify nav against current docs + deep link + search fallback |
| Declared a policy URL "dead, needs infra work" after curling the wrong host | §6 curl the URL actually declared in the console |
| Screenshots grabbed mid-entrance-animation looked broken | §5.3 behavior checks wait for settle; know your UI's timing |

---

## The pre-ship self-test (run before calling anything "done")

1. **The bar:** which §0 number does this change move, and how will I see it move?
2. **The gate:** did EVERY §5.2 command run at HEAD, exit-code-checked, by me (not an agent's claim)?
3. **The journey:** did I watch the real app do the changed thing on a real device/simulator?
4. **The money/policy:** if this touches payment, ads, or declarations — did I re-run the §4 matrix and cross-check the consoles?
5. **The next model:** is what I learned written where the next (possibly weaker) model will find it — spec, checklist, or failure catalog?

If any answer is "no" or "sort of", the work isn't done. The flinch is the signal.
