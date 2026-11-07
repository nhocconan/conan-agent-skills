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

from preview_clips import render_preview_from_media

os.environ.setdefault("VO_BACKEND", "none")  # silent by default; set kokoro/say/openai for narration

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
# Only put a feature claim on a scene that visibly SHOWS it (accurate metadata):
# e.g. don't caption "Siri" unless Siri is on screen.
SCENES = [
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
]

# App Preview sets accept video dimensions distinct from screenshot dimensions.
render_preview_from_media(SCENES, MEDIA, ICON, OUT, 886, 1920, max_total=29.5)
