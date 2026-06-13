#!/usr/bin/env python3
"""Apple App Store preview video (886x1920 portrait, 30fps, ~25s, H.264 +
stereo AAC — App Store Connect requires a stereo audio track).

Composes Ken Burns-style scenes from the raw simulator captures in
appstore/screenshots/raw/ with sticker captions, brand intro/outro cards and
crossfades. Output: appstore/preview/app-preview-6.9.mp4 (works for the 6.9"
and 6.5" preview slots — both accept 886x1920).

Voiceover (optional): set VO_BACKEND to add narration. When unset the audio is
a silent stereo track (still spec-valid).
  VO_BACKEND=say     macOS `say` (zero install; set VO_VOICE, use a Premium
                     voice — defaults sound robotic). Local, free.
  VO_BACKEND=kokoro  Kokoro-82M via `pip install kokoro` (Apache-2.0, local,
                     Apple Silicon). Recommended for the published asset.
  VO_BACKEND=piper   Piper CLI on PATH (VO_VOICE = path to .onnx voice). Local.
  VO_BACKEND=openai  OpenAI /v1/audio/speech (needs OPENAI_API_KEY; NOT covered
                     by the free shared-traffic tier — billed at TTS rates).
  VO_BACKEND=file    Pre-recorded per-scene clips named vo/<out-stem>-<i>.wav.
Each scene's on-screen caption and its `vo` line stay in lockstep — one story.

Requires ffmpeg. Method: ~/.claude/skills/store-screenshots.
"""
import json
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

VO_BACKEND = os.environ.get("VO_BACKEND", "").strip().lower()
VO_VOICE = os.environ.get("VO_VOICE", "")
VO_PAD = 0.6        # seconds of breathing room after each narration line
MAX_TOTAL = 29.5    # stay inside Apple's 30s ceiling

SCENES = [
    dict(kind="card", dur=3.5, title="HOURLY MOVE",
         sub="Stand up. Stretch. Every hour.", bg=(INK_TOP, INK),
         vo="Sitting all day quietly wears you down."),
    dict(kind="shot", dur=4.5, raw="tab0.png", head="SITTING ALL DAY?",
         bg=(CORAL, AMBER), drift=-1,
         vo="Hourly Move shows your next stand-up break at a glance."),
    dict(kind="shot", dur=4.5, raw="tab1.png", head="YOUR HOURS, YOUR RULES",
         bg=(INK_TOP, INK), drift=1,
         vo="Set your own hours and pace, for weekdays and weekends."),
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


def _probe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def synth_line(text, wav_path, stem, index):
    """Render one narration line to a 48k mono wav via the chosen backend."""
    if VO_BACKEND == "say":
        aiff = wav_path + ".aiff"
        cmd = ["say", "-o", aiff]
        if VO_VOICE:
            cmd += ["-v", VO_VOICE]
        subprocess.run(cmd + [text], check=True)
        subprocess.run(["ffmpeg", "-y", "-i", aiff, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
        os.remove(aiff)
    elif VO_BACKEND == "piper":
        if not VO_VOICE:
            raise SystemExit("piper backend needs VO_VOICE=<path-to-.onnx voice>")
        raw = wav_path + ".raw.wav"
        subprocess.run(["piper", "--model", VO_VOICE, "--output_file", raw],
                       input=text, text=True, check=True)
        subprocess.run(["ffmpeg", "-y", "-i", raw, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
        os.remove(raw)
    elif VO_BACKEND == "kokoro":
        import soundfile as sf  # noqa: lazy, only when used
        from kokoro import KPipeline
        global _KPIPE
        try:
            _KPIPE
        except NameError:
            _KPIPE = KPipeline(lang_code="a")  # American English
        voice = VO_VOICE or "af_heart"
        audio = None
        for _, _, a in _KPIPE(text, voice=voice):
            audio = a
        raw = wav_path + ".raw.wav"
        sf.write(raw, audio, 24000)
        subprocess.run(["ffmpeg", "-y", "-i", raw, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
        os.remove(raw)
    elif VO_BACKEND == "openai":
        import urllib.request
        key = os.environ["OPENAI_API_KEY"]
        body = json.dumps({
            "model": "gpt-4o-mini-tts", "voice": VO_VOICE or "alloy",
            "input": text, "response_format": "wav"}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/audio/speech", data=body,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"})
        raw = wav_path + ".raw.wav"
        with urllib.request.urlopen(req) as r, open(raw, "wb") as f:
            f.write(r.read())
        subprocess.run(["ffmpeg", "-y", "-i", raw, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
        os.remove(raw)
    elif VO_BACKEND == "file":
        src = os.path.join(OUT_DIR, "vo", f"{stem}-{index}.wav")
        if not os.path.exists(src):
            raise SystemExit(f"file backend: missing {src}")
        subprocess.run(["ffmpeg", "-y", "-i", src, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
    else:
        raise SystemExit(f"unknown VO_BACKEND={VO_BACKEND!r}")


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
    tmp = tempfile.mkdtemp(prefix="preview-")
    stem = os.path.splitext(os.path.basename(OUT))[0]
    try:
        # 1. Voiceover first — clip lengths drive scene durations.
        vo_clips = []  # (scene_index, wav_path, duration)
        if VO_BACKEND:
            print(f"synthesizing voiceover via '{VO_BACKEND}'...")
            for k, s in enumerate(SCENES):
                if not s.get("vo"):
                    continue
                wav = os.path.join(tmp, f"vo{k}.wav")
                synth_line(s["vo"], wav, stem, k)
                dur = _probe_dur(wav)
                vo_clips.append((k, wav, dur))
                # A scene must outlast its line (+ lead-in + tail).
                s["dur"] = max(s["dur"], round(dur + VO_PAD + 0.4, 2))

        canvases = [compose_scene(s) for s in SCENES]
        starts = []
        t0 = 0.0
        for s in SCENES:
            starts.append(t0)
            t0 += s["dur"] - FADE
        total = starts[-1] + SCENES[-1]["dur"]
        if total > MAX_TOTAL:
            print(f"WARNING: {total:.1f}s exceeds Apple's 30s ceiling — "
                  "trim narration lines.")
        n_frames = int(total * FPS)
        print(f"{total:.1f}s, {n_frames} frames")

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

        # 2. Audio track: lay each VO clip ~0.3s into its scene, mix, normalize.
        # The image sequence is input 0, so wav inputs start at index 1.
        if vo_clips:
            inputs, filters, labels = [], [], []
            for j, (k, wav, _dur) in enumerate(vo_clips):
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
            "-i", os.path.join(tmp, "f%05d.png"),
            *audio_args,
            "-shortest", "-map", "0:v", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-crf", "18", "-c:a", "aac", "-b:a", "256k",
            "-ac", "2", OUT], check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
