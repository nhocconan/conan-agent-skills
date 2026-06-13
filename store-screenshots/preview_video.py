#!/usr/bin/env python3
"""Apple App Store preview video (886x1920 portrait, 30fps, ~25s, H.264 +
silent stereo AAC — App Store Connect requires a stereo audio track).

Composes Ken Burns-style scenes from the raw simulator captures in
appstore/screenshots/raw/ with sticker captions, brand intro/outro cards and
crossfades. Output: appstore/preview/app-preview-6.9.mp4 (works for the 6.9"
and 6.5" preview slots — both accept 886x1920).

Requires ffmpeg. Method: ~/.claude/skills/store-screenshots.
"""
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from store_frames import (AMBER, CORAL, F_BLACK, F_BOLD, INK, INK_TOP, TEAL,
                          TEAL_DEEP, WHITE, _vgrad, device_mockup,
                          paste_with_shadow, sticker)

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "appstore", "screenshots", "raw")
ICON = os.path.join(ROOT, "ios", "HourlyMove", "Resources",
                    "Assets.xcassets", "AppIcon.appiconset", "icon-1024.png")
OUT_DIR = os.path.join(ROOT, "appstore", "preview")
OUT = os.path.join(OUT_DIR, "app-preview-6.9.mp4")

W, H = 886, 1920
FPS = 30
FADE = 0.5          # crossfade seconds
OVER = 1.30         # scene canvases are rendered larger to allow zooming

SCENES = [
    dict(kind="card", dur=3.5, title="HOURLY MOVE",
         sub="Stand up. Stretch. Every hour.", bg=(INK_TOP, INK)),
    dict(kind="shot", dur=4.5, raw="tab0.png", head="SITTING ALL DAY?",
         bg=(CORAL, AMBER), drift=-1),
    dict(kind="shot", dur=4.5, raw="tab1.png", head="YOUR HOURS, YOUR RULES",
         bg=(INK_TOP, INK), drift=1),
    dict(kind="shot", dur=4.5, raw="tab2.png", head="SEE YOURSELF MOVE",
         bg=(TEAL, TEAL_DEEP), drift=-1),
    dict(kind="shot", dur=4.5, raw="tab3.png", head="NO ADS. NO ACCOUNT.",
         bg=(AMBER, CORAL), drift=1),
    dict(kind="card", dur=3.5, title="HOURLY MOVE",
         sub="Move more, starting this hour.", bg=(INK_TOP, INK)),
]


def circular_icon(size):
    icon = Image.open(ICON).convert("RGB").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(icon, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def compose_scene(scene):
    """Static oversized canvas the per-frame zoom crops into."""
    cw, ch = int(W * OVER), int(H * OVER)
    base = _vgrad(cw, ch, *scene["bg"]).convert("RGBA")
    glow = Image.new("L", (cw, ch), 0)
    gr = int(cw * 0.55)
    ImageDraw.Draw(glow).ellipse([cw - gr, -gr // 2, cw + gr, gr + gr // 2],
                                 fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(cw * 0.12))
    base = Image.composite(Image.new("RGBA", (cw, ch), WHITE + (255,)),
                           base, glow).convert("RGBA")

    if scene["kind"] == "card":
        icon = circular_icon(int(cw * 0.40))
        paste_with_shadow(base, icon, ((cw - icon.width) // 2, int(ch * 0.24)),
                          blur=40, dy=18, opacity=120)
        title = sticker(scene["title"], int(cw * 0.085), angle=-2.0)
        base.alpha_composite(title, ((cw - title.width) // 2, int(ch * 0.55)))
        f_sub = ImageFont.truetype(F_BOLD, int(cw * 0.042))
        d = ImageDraw.Draw(base)
        tw = d.textlength(scene["sub"], font=f_sub)
        d.text(((cw - tw) / 2 + 3, int(ch * 0.645) + 3), scene["sub"],
               font=f_sub, fill=(0, 0, 0, 90))
        d.text(((cw - tw) / 2, int(ch * 0.645)), scene["sub"],
               font=f_sub, fill=WHITE + (255,))
    else:
        head_size = int(cw * 0.062)
        f = ImageFont.truetype(F_BLACK, head_size)
        d = ImageDraw.Draw(base)
        while d.textlength(scene["head"], font=f) > cw * 0.80:
            head_size -= 4
            f = ImageFont.truetype(F_BLACK, head_size)
        card = sticker(scene["head"], head_size, angle=-2.0)
        paste_with_shadow(base, card, ((cw - card.width) // 2, int(ch * 0.155)),
                          blur=18, dy=12)
        device = device_mockup(os.path.join(RAW, scene["raw"]), int(cw * 0.74))
        paste_with_shadow(base, device, ((cw - device.width) // 2,
                                         int(ch * 0.27)),
                          blur=40, dy=24, opacity=130)
    return base.convert("RGB")


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def frame_of(canvas, local_t, dur, drift=0):
    """Slow zoom 1.00→1.10 across the scene plus a slight lateral drift."""
    z = 1.0 + 0.10 * ease(local_t / dur)
    cw, ch = canvas.size
    vw, vh = int(W * OVER / z), int(H * OVER / z)
    cx = cw / 2 + drift * (cw * 0.02) * (local_t / dur)
    cy = ch / 2 - (ch * 0.015) * (local_t / dur)
    x0 = min(max(0, cx - vw / 2), cw - vw)
    y0 = min(max(0, cy - vh / 2), ch - vh)
    return canvas.crop((int(x0), int(y0), int(x0) + vw, int(y0) + vh)) \
                 .resize((W, H), Image.BILINEAR)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    canvases = [compose_scene(s) for s in SCENES]
    starts = []
    t0 = 0.0
    for s in SCENES:
        starts.append(t0)
        t0 += s["dur"] - FADE
    total = starts[-1] + SCENES[-1]["dur"]
    n_frames = int(total * FPS)
    print(f"{total:.1f}s, {n_frames} frames")

    tmp = tempfile.mkdtemp(prefix="preview-frames-")
    try:
        for i in range(n_frames):
            t = i / FPS
            active = [(k, s) for k, s in enumerate(SCENES)
                      if starts[k] <= t < starts[k] + s["dur"]]
            k, s = active[0]
            img = frame_of(canvases[k], t - starts[k], s["dur"],
                           s.get("drift", 0))
            if len(active) > 1:  # crossfade into the next scene
                k2, s2 = active[1]
                nxt = frame_of(canvases[k2], t - starts[k2], s2["dur"],
                               s2.get("drift", 0))
                a = (t - starts[k2]) / FADE
                img = Image.blend(img, nxt, min(1.0, a))
            img.save(os.path.join(tmp, f"f{i:05d}.png"))
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", os.path.join(tmp, "f%05d.png"),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-crf", "18", "-c:a", "aac", "-b:a", "256k",
            OUT], check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
