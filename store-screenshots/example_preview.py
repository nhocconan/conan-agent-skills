#!/usr/bin/env python3
"""Apple App Store preview video (886x1920, 6.9"/6.5" slots) from
appstore/screenshots/raw/. Renderer + voiceover docs: preview_core.py.

  VO_BACKEND=kokoro VO_VOICE=af_heart \\
    ~/.venvs/tts-kokoro/bin/python scripts/gen_app_preview.py
"""
import os
from store_frames import AMBER, CORAL, INK, INK_TOP, TEAL, TEAL_DEEP
from preview_core import render_preview

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "appstore", "screenshots", "raw")
ICON = os.path.join(ROOT, "ios", "HourlyMove", "Resources",
                    "Assets.xcassets", "AppIcon.appiconset", "icon-1024.png")
OUT = os.path.join(ROOT, "appstore", "preview", "app-preview-6.9.mp4")

SCENES = [
    dict(kind="card", dur=3.5, title="HOURLY MOVE",
         sub="Stand up. Stretch. Every hour.", bg=(INK_TOP, INK),
         vo="Sitting all day quietly wears you down."),
    dict(kind="shot", dur=4.5, raw="tab0.png", head="SITTING ALL DAY?",
         bg=(CORAL, AMBER), drift=-1,
         vo="Hourly Move shows your next stand-up break at a glance."),
    dict(kind="shot", dur=4.5, raw="tab1.png", head="YOUR HOURS, YOUR RULES",
         bg=(INK_TOP, INK), drift=1,
         vo="Set your own pace, from minutes to hours, weekdays and weekends."),
    dict(kind="shot", dur=4.5, raw="tab2.png", head="SEE YOURSELF MOVE",
         bg=(TEAL, TEAL_DEEP), drift=-1,
         vo="Then watch every break add up."),
    dict(kind="shot", dur=4.5, raw="tab3.png", head="NO ADS. NO ACCOUNT.",
         bg=(AMBER, CORAL), drift=1,
         vo="No ads. No account. It all stays on your iPhone."),
    dict(kind="card", dur=3.5, title="HOURLY MOVE",
         sub="Move more, starting this hour.", bg=(INK_TOP, INK),
         vo="Move more, starting this hour."),
]

render_preview(SCENES, RAW, ICON, OUT, 886, 1920, max_total=29.5)
