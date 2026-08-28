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
