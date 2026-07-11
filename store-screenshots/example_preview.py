#!/usr/bin/env python3
"""Apple App Store App Preview video — built from REAL screen captures, NO
device frames (Guideline 2.3.4). Renderer + voiceover docs: preview_clips.py.

Capture the media first (see SKILL.md Step 4):
  segments/home.mp4            a LIVE screen recording (needs on-screen motion —
                               recordVideo is variable-frame-rate, so a static
                               screen yields a ~0s clip; a moving clock/ring/list
                               works). One live "hero" clip is usually enough.
  segments/stills/*.png        full-screen screenshots for the calmer screens
                               (animated with a gentle Ken Burns in the renderer)

  VO_BACKEND=kokoro VO_VOICE=af_heart \\
    ~/.venvs/tts-kokoro/bin/python scripts/gen_app_preview.py
"""
import os
import subprocess

from store_frames import INK, INK_TOP
from preview_clips import render_preview_from_media

os.environ.setdefault("VO_BACKEND", "kokoro")  # never ship a silent "preview"

ROOT = os.path.join(os.path.dirname(__file__), "..")
MEDIA = os.path.join(ROOT, "appstore", "preview", "segments")
ICON = os.path.join(ROOT, "ios", "YourApp", "Resources",  # adapt to your project
                    "Assets.xcassets", "AppIcon.appiconset", "icon-1024.png")
OUT = os.path.join(ROOT, "appstore", "preview", "app-preview-6.9.mp4")

# Reuse the same recording's tail as a second segment so two scenes that show
# the hero screen don't replay an identical opening.
HOME_B = os.path.join(MEDIA, "home_b.mp4")
if not os.path.exists(HOME_B):
    subprocess.run(["ffmpeg", "-y", "-ss", "3.0", "-i",
                    os.path.join(MEDIA, "home.mp4"), "-c", "copy", HOME_B],
                   check=True, capture_output=True)

# kind="clip"  → full-bleed real recording + caption (no frame)
# kind="still" → full-screen screenshot + gentle Ken Burns + caption
# kind="card"  → generated brand card (intro/outro only)
# Only put a feature claim on a scene that visibly SHOWS it (accurate metadata):
# e.g. don't caption "Siri" unless Siri is on screen.
SCENES = [
    dict(kind="card", dur=3.0, title="STAND TIMER",
         sub="Your hourly nudge to move.", bg=(INK_TOP, INK),
         vo="Long days in a chair quietly wear you down."),
    dict(kind="clip", dur=3.6, src="home.mp4", head="SITTING ALL DAY?",
         vo="Stand Timer shows your next stand-up break at a glance."),
    dict(kind="still", dur=3.6, src="stills/profiles.png",
         head="YOUR HOURS, YOUR RULES", drift=1,
         vo="Set your own pace, from minutes to hours, weekdays and weekends."),
    dict(kind="still", dur=3.4, src="stills/history.png",
         head="SEE YOURSELF MOVE", drift=-1,
         vo="Watch every stand-up add up."),
    # Caption only what's ON SCREEN. The Settings screen shows themes, so
    # "MAKE IT YOURS" is honest. To actually sell a Lock Screen / Live Activity /
    # widget you CAN'T screen-record (no simctl lock), don't fake it in the
    # VIDEO — put a faithful render in a STILL instead (stills may be composited;
    # see SKILL.md Step 4 "unshowable surfaces").
    dict(kind="still", dur=3.8, src="stills/settings.png",
         head="MAKE IT YOURS", drift=1,
         vo="Pick your theme and keep everything on your terms."),
    dict(kind="clip", dur=3.6, src="home_b.mp4", head="NO ADS. NO ACCOUNT.",
         vo="No ads, no account. It all stays on your iPhone."),
    dict(kind="card", dur=3.0, title="STAND TIMER",
         sub="Move more, starting this hour.", bg=(INK_TOP, INK),
         vo="Move more, starting this hour."),
]

# OUTPUT SIZE = 886x1920 (App Preview), NOT 1320x2868 (that's the SCREENSHOT
# size — App Store Connect's iPhone App Preview slot REJECTS it: "dimensions
# should be 886 × 1920px or 1920 × 886px", a real June 2026 upload error).
# 886x1920 is accepted across the 6.5"/6.7"/6.9" preview slots. The renderer
# downscales the native 1320x2868 captures to fit (the ~0.3% aspect delta is
# imperceptible); it's still a real screen capture, just not 1:1.
render_preview_from_media(SCENES, MEDIA, ICON, OUT, 886, 1920, max_total=29.5)
