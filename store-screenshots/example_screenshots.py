#!/usr/bin/env python3
"""Apple App Store marketing screenshots (1284x2778, 6.5" slot — accepted on
its own; App Store Connect does NOT auto-convert between iPhone slots) from
appstore/screenshots/raw/ (iPhone simulator captures via
-uiScreenshots -uiSeedHistory -uiTab N; the renderer reframes any raw size).

Story order: pain -> control -> progress -> reliability -> privacy.
Renderer: store_frames.py; method: ~/.claude/skills/store-screenshots.
"""
import os
from store_frames import AMBER, CORAL, INK, INK_TOP, TEAL, TEAL_DEEP, render_slides

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "appstore", "screenshots", "raw")
OUT = os.path.join(ROOT, "appstore", "screenshots")

SLIDES = [
    dict(raw="tab0.png", out="01-pain.png",
         head=["SITTING", "ALL DAY?"],
         sub="One glance shows your next stand-up break.",
         bg=(CORAL, AMBER), tilt=-2.5),
    dict(raw="tab1.png", out="02-your-rules.png",
         head=["YOUR HOURS,", "YOUR RULES"],
         sub="Weekday and weekend profiles — windows, pace, lunch skips.",
         bg=(INK_TOP, INK), tilt=2.5),
    dict(raw="tab2.png", out="03-progress.png",
         head=["SEE YOURSELF", "MOVE"],
         sub="Every break counted, day by day.",
         bg=(TEAL, TEAL_DEEP), tilt=-2.5),
    dict(raw="onboarding.png", out="04-reliable.png",
         head=["ON TIME.", "EVERY TIME."],
         sub="Reminders that actually fire — never spammy.",
         bg=(INK_TOP, INK), tilt=2.5),
    dict(raw="tab3.png", out="05-private.png",
         head=["NO ADS.", "NO ACCOUNT."],
         sub="No internet at all — your data stays on your iPhone.",
         bg=(AMBER, CORAL), tilt=-2.5),
]

render_slides(SLIDES, RAW, OUT, 1284, 2778)
