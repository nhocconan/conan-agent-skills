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
