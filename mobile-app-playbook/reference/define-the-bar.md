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
