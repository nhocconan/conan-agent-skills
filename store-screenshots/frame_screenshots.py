#!/usr/bin/env python3
"""Generate Play Store marketing screenshots from raw app captures.

Reads playstore/screenshots/raw/*.png, writes story-sequenced 1080x1920
frames (gradient brand background + sticker headline + tilted device mockup)
to playstore/screenshots/. Method: ~/.claude/skills/store-screenshots.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "playstore", "screenshots", "raw")
OUT = os.path.join(ROOT, "playstore", "screenshots")

W, H = 1080, 1920
SS = 2  # supersample
w, h = W * SS, H * SS

INK = (0x15, 0x17, 0x1C)
INK_TOP = (0x23, 0x26, 0x30)
CORAL = (0xFF, 0x6B, 0x4A)
AMBER = (0xFF, 0xB0, 0x20)
TEAL = (0x3F, 0xB6, 0xA8)
TEAL_DEEP = (0x1C, 0x5F, 0x58)
WHITE = (255, 255, 255)

FONTS = "/System/Library/Fonts/Supplemental"
F_BLACK = os.path.join(FONTS, "Arial Black.ttf")
F_BOLD = os.path.join(FONTS, "Arial Bold.ttf")

# Story order: pain -> shift -> profiles -> reliability proof -> privacy.
SLIDES = [
    dict(raw="01-home.png", out="01-pain.png",
         head=["SITTING", "ALL DAY?"],
         sub="One glance shows your next stand-up break.",
         bg=(CORAL, AMBER), tilt=-2.5),
    dict(raw="03-editor.png", out="02-your-rules.png",
         head=["YOUR HOURS,", "YOUR RULES"],
         sub="Pick a window, set the pace, keep lunch quiet.",
         bg=(INK_TOP, INK), tilt=2.5),
    dict(raw="02-profiles.png", out="03-profiles.png",
         head=["WEEKDAYS ≠", "WEEKENDS"],
         sub="Profiles switch with your week — automatically.",
         bg=(TEAL, TEAL_DEEP), tilt=-2.5),
    dict(raw="05-settings.png", out="04-never-miss.png",
         head=["IMPOSSIBLE", "TO MISS"],
         sub="Exact alarms, on the minute — even on silent.",
         bg=(INK_TOP, INK), tilt=2.5),
    dict(raw="04-onboarding.png", out="05-private.png",
         head=["NO ADS.", "NO ACCOUNT."],
         sub="No internet at all — your data stays on your phone.",
         bg=(AMBER, CORAL), tilt=-2.5),
]


def vgrad(top, bottom):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        c = tuple(int(top[i] + (bottom[i] - top[i]) * y / (h - 1))
                  for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def rounded_mask(size, radius):
    m = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, size[0] * 2 - 1, size[1] * 2 - 1], radius * 2, fill=255)
    return m.resize(size, Image.LANCZOS)


def sticker(text, font_size, fg=INK, bg=WHITE, angle=-2.0):
    f = ImageFont.truetype(F_BLACK, font_size)
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    box = d.textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    px_, py_ = int(font_size * 0.42), int(font_size * 0.30)
    sw, sh = tw + 2 * px_, th + 2 * py_
    card = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, sw - 1, sh - 1], int(font_size * 0.18),
                         fill=bg + (255,))
    cd.text((px_ - box[0], py_ - box[1]), text, font=f, fill=fg + (255,))
    return card.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste_with_shadow(base, img, pos, blur, dy, opacity=110):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    silhouette = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    sh.paste(silhouette, (pos[0], pos[1] + dy), img)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh)
    base.alpha_composite(img, pos)


def device_mockup(raw_path, device_w):
    shot = Image.open(raw_path).convert("RGB")
    device_h = int(shot.height * device_w / shot.width)
    shot = shot.resize((device_w, device_h), Image.LANCZOS)
    r_in = int(device_w * 0.085)
    pad = int(device_w * 0.022)
    fw, fh = device_w + 2 * pad, device_h + 2 * pad
    frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle(
        [0, 0, fw - 1, fh - 1], r_in + pad, fill=(0x0A, 0x0B, 0x0E, 255))
    shot_rgba = Image.new("RGBA", shot.size, (0, 0, 0, 0))
    shot_rgba.paste(shot, (0, 0), rounded_mask(shot.size, r_in))
    frame.alpha_composite(shot_rgba, (pad, pad))
    return frame


def wrap(text, font, max_w, d):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


os.makedirs(OUT, exist_ok=True)
for slide in SLIDES:
    base = vgrad(*slide["bg"]).convert("RGBA")

    # Soft glow top-right so the gradient isn't flat.
    glow = Image.new("L", (w, h), 0)
    gr = int(w * 0.55)
    ImageDraw.Draw(glow).ellipse(
        [w - gr, -gr // 2, w + gr, gr + gr // 2], fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.12))
    base = Image.composite(
        Image.new("RGBA", (w, h), WHITE + (255,)), base, glow).convert("RGBA")

    margin = 64 * SS
    y = 78 * SS
    head_size = 92 * SS
    f_head = ImageFont.truetype(F_BLACK, head_size)
    d = ImageDraw.Draw(base)
    longest = max(slide["head"], key=lambda t: d.textlength(t, font=f_head))
    while d.textlength(longest, font=f_head) > w - 2 * margin - head_size:
        head_size -= 2 * SS
        f_head = ImageFont.truetype(F_BLACK, head_size)

    for i, line in enumerate(slide["head"]):
        card = sticker(line, head_size, angle=-2.0)
        paste_with_shadow(base, card, (margin + i * 18 * SS, y),
                          blur=10 * SS, dy=8 * SS)
        y += int(card.height * 0.86)

    y += 30 * SS
    f_sub = ImageFont.truetype(F_BOLD, 40 * SS)
    d = ImageDraw.Draw(base)
    for line in wrap(slide["sub"], f_sub, w - 2 * margin, d):
        d.text((margin + 2 * SS, y + 2 * SS), line, font=f_sub,
               fill=(0, 0, 0, 90))
        d.text((margin, y), line, font=f_sub, fill=WHITE + (255,))
        y += int(46 * SS * 1.25)

    device = device_mockup(os.path.join(RAW, slide["raw"]), int(w * 0.76))
    device = device.rotate(slide["tilt"], expand=True, resample=Image.BICUBIC)
    dx = (w - device.width) // 2
    dy_pos = max(y + 40 * SS, int(h * 0.345))
    paste_with_shadow(base, device, (dx, dy_pos), blur=22 * SS, dy=14 * SS,
                      opacity=130)

    final = base.convert("RGB").resize((W, H), Image.LANCZOS)
    final.save(os.path.join(OUT, slide["out"]))
    print("wrote", slide["out"])
