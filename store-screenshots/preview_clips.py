#!/usr/bin/env python3
"""App Store App Preview renderer from REAL captures — NO device frames.

Apple Guideline 2.3.4 requires the App Preview *video* to be a full-screen
screen capture of the app (textual/narration overlays are allowed, device
frames are NOT). This renderer composites:

  card  — a generated brand card (gradient + app icon + title + subtitle)
  clip  — a real screen recording (.mp4), shown full-bleed, with a caption
  still — a real full-screen screenshot, gentle Ken Burns, with a caption

The captured media must already be at the output resolution (e.g. 1320x2868,
an accepted 6.9" App Preview size) so nothing is letterboxed or framed.

Voiceover reuses preview_core's backends via VO_BACKEND (unset = silent track).
Requires ffmpeg. Method notes: ~/.claude/skills/store-screenshots.
"""
import math
import os
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from store_frames import F_BOLD, WHITE, _vgrad, paste_with_shadow, sticker
from preview_core import (FADE, FPS, VO_BACKEND, VO_PAD, circular_icon,
                          _probe_dur, synth_line)


def _card_base(scene, icon_path, W, H):
    """Full-frame (W x H) brand card: gradient + app icon + title + subtitle."""
    base = _vgrad(W, H, *scene["bg"]).convert("RGBA")
    glow = Image.new("L", (W, H), 0)
    gr = int(W * 0.55)
    ImageDraw.Draw(glow).ellipse([W - gr, -gr // 2, W + gr, gr + gr // 2], fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.12))
    base = Image.composite(Image.new("RGBA", (W, H), WHITE + (255,)),
                           base, glow).convert("RGBA")
    icon = circular_icon(icon_path, int(W * 0.34))
    paste_with_shadow(base, icon, ((W - icon.width) // 2, int(H * 0.26)),
                      blur=40, dy=18, opacity=120)
    title = sticker(scene["title"], int(W * 0.092), angle=-2.0)
    base.alpha_composite(title, ((W - title.width) // 2, int(H * 0.55)))
    f_sub = ImageFont.truetype(F_BOLD, int(W * 0.046))
    d = ImageDraw.Draw(base)
    tw = d.textlength(scene["sub"], font=f_sub)
    d.text(((W - tw) / 2 + 3, int(H * 0.635) + 3), scene["sub"],
           font=f_sub, fill=(0, 0, 0, 90))
    d.text(((W - tw) / 2, int(H * 0.635)), scene["sub"], font=f_sub,
           fill=WHITE + (255,))
    return base.convert("RGB")


def caption(text, W, frac=0.072, angle=-2.0):
    """White brand sticker sized to the frame width, with a soft drop shadow,
    returned as one RGBA image (so it can be alpha-faded as a unit)."""
    size = int(W * frac)
    while True:
        card = sticker(text, size, angle=angle)
        if card.width <= W * 0.88 or size <= 24:
            break
        size -= 4
    pad = int(size * 0.6)
    out = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad),
                    (0, 0, 0, 0))
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sil = Image.new("RGBA", card.size, (0, 0, 0, 95))
    shadow.paste(sil, (pad, pad + int(size * 0.18)), card)
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.22))
    out.alpha_composite(shadow)
    out.alpha_composite(card, (pad, pad))
    return out


def _ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(1.0, max(0.0, t)))


def _fade_alpha(img, a):
    if a >= 0.999:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


def _kenburns(img, local_t, dur, W, H, drift=0.0, z0=1.0, z1=1.05):
    """Gentle zoom (and slight lateral drift) into a full-frame still."""
    z = z0 + (z1 - z0) * _ease(local_t / dur)
    vw, vh = int(W / z), int(H / z)
    cx = W / 2 + drift * (W * 0.012) * (local_t / dur)
    cy = H / 2
    x0 = min(max(0, cx - vw / 2), W - vw)
    y0 = min(max(0, cy - vh / 2), H - vh)
    return img.crop((int(x0), int(y0), int(x0) + vw, int(y0) + vh)) \
              .resize((W, H), Image.LANCZOS)


def _extract_clip(clip_path, tmp, key, W, H):
    """Decode a screen recording to a full-res frame sequence at FPS."""
    d = os.path.join(tmp, f"clip_{key}")
    os.makedirs(d, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", clip_path, "-vf",
         f"fps={FPS},scale={W}:{H}:flags=lanczos",
         os.path.join(d, "f%05d.png")], check=True, capture_output=True)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".png"))


def render_preview_from_media(scenes, media_dir, icon_path, out_path, W, H,
                              cap_y_frac=0.052, max_total=29.5):
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="preview-clips-")
    stem = os.path.splitext(os.path.basename(out_path))[0]
    try:
        # 1. Voiceover first — clip lengths drive scene durations.
        vo_clips = []
        if VO_BACKEND:
            print(f"synthesizing voiceover via '{VO_BACKEND}'...")
            for k, s in enumerate(scenes):
                if not s.get("vo"):
                    continue
                wav = os.path.join(tmp, f"vo{k}.wav")
                synth_line(s["vo"], wav, out_dir, stem, k)
                vo_clips.append((k, wav, _probe_dur(wav)))
                s["dur"] = max(s["dur"], round(_probe_dur(wav) + VO_PAD + 0.4, 2))

        # 2. Prepare per-scene frame providers.
        for k, s in enumerate(scenes):
            cap = caption(s["head"], W) if s.get("head") else None
            s["_cap"] = cap
            if cap is not None:
                s["_cap_pos"] = ((W - cap.width) // 2, int(H * cap_y_frac))
            if s["kind"] == "card":
                s["_card"] = _card_base(s, icon_path, W, H)
            elif s["kind"] == "still":
                s["_img"] = Image.open(
                    os.path.join(media_dir, s["src"])).convert("RGB").resize(
                        (W, H), Image.LANCZOS)
            elif s["kind"] == "clip":
                s["_frames"] = _extract_clip(
                    os.path.join(media_dir, s["src"]), tmp, k, W, H)

        starts, t0 = [], 0.0
        for s in scenes:
            starts.append(t0)
            t0 += s["dur"] - FADE
        total = starts[-1] + scenes[-1]["dur"]
        if total > max_total:
            print(f"WARNING: {total:.1f}s exceeds the {max_total}s ceiling — "
                  "trim narration.")
        n_frames = int(total * FPS)
        print(f"{total:.1f}s, {n_frames} frames")

        def scene_frame(s, lt):
            if s["kind"] == "card":
                img = _kenburns(s["_card"], lt, s["dur"], W, H, z1=1.035)
                return img.convert("RGBA")
            if s["kind"] == "still":
                img = _kenburns(s["_img"], lt, s["dur"], W, H,
                                drift=s.get("drift", 0), z1=1.05)
            else:  # clip
                idx = min(int(lt * FPS), len(s["_frames"]) - 1)
                img = Image.open(s["_frames"][idx]).convert("RGB")
            img = img.convert("RGBA")
            if s.get("_cap") is not None:
                a = min(1.0, lt / 0.4)
                img.alpha_composite(_fade_alpha(s["_cap"], a), s["_cap_pos"])
            return img

        for i in range(n_frames):
            t = i / FPS
            active = [(k, s) for k, s in enumerate(scenes)
                      if starts[k] <= t < starts[k] + s["dur"]]
            k, s = active[0]
            img = scene_frame(s, t - starts[k])
            if len(active) > 1:  # crossfade into next
                k2, s2 = active[1]
                nxt = scene_frame(s2, t - starts[k2])
                a = (t - starts[k2]) / FADE
                img = Image.blend(img, nxt, min(1.0, a))
            img.convert("RGB").save(os.path.join(tmp, f"f{i:05d}.png"))

        # 3. Audio: lay each VO clip ~0.3s into its scene, mix, normalize.
        if vo_clips:
            inputs, filters, labels = [], [], []
            for j, (k, wav, _d) in enumerate(vo_clips):
                inputs += ["-i", wav]
                delay_ms = int((starts[k] + 0.3) * 1000)
                filters.append(f"[{j + 1}]adelay={delay_ms}|{delay_ms}[d{j}]")
                labels.append(f"[d{j}]")
            mix = (";".join(filters) + ";" + "".join(labels) +
                   f"amix=inputs={len(vo_clips)}:normalize=0,"
                   f"loudnorm=I=-16:TP=-1.5:LRA=11,"
                   f"apad,atrim=0:{total:.3f},aresample=48000[a]")
            audio_args = inputs + ["-filter_complex", mix, "-map", "[a]"]
        else:
            audio_args = [
                "-f", "lavfi", "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000", "-map", "1:a"]

        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", os.path.join(tmp, "f%05d.png"), *audio_args,
            "-shortest", "-map", "0:v", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-crf", "18", "-c:a", "aac", "-b:a", "256k",
            "-ac", "2", out_path], check=True, capture_output=True)

        # Self-verify the voiceover actually landed: a forgotten/failed
        # VO_BACKEND silently ships a mute "preview" (the #1 way that happens).
        # If narration was requested but the track is effectively silent, FAIL
        # the build instead of writing a useless file. `VO_BACKEND=none` opts
        # out (a silent stereo track is still spec-valid for Apple).
        if VO_BACKEND and VO_BACKEND != "none" and vo_clips:
            probe = subprocess.run(
                ["ffmpeg", "-i", out_path, "-af", "volumedetect", "-f", "null",
                 "-"], capture_output=True, text=True)
            m = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", probe.stderr)
            if m and float(m.group(1)) < -50:
                raise SystemExit(
                    f"VOICEOVER MISSING: {out_path} mean volume {m.group(1)} dB "
                    f"— narration didn't render (check VO_BACKEND='{VO_BACKEND}' "
                    "and that the synth venv is on PATH).")
            print(f"voiceover OK (mean volume {m.group(1) if m else '?'} dB)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", out_path)
