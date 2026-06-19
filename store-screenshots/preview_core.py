#!/usr/bin/env python3
"""Shared App Preview / promo video renderer (Ken Burns scenes + sticker
captions + brand cards + optional voiceover). Used by gen_app_preview.py
(Apple, 886x1920) and gen_play_preview.py (Play, 1080x1920).

Voiceover backends via VO_BACKEND (unset = silent stereo track, still valid):
  say | kokoro | piper | openai | file   (see store-screenshots SKILL.md)
Method: ~/.claude/skills/store-screenshots. Requires ffmpeg.
"""
import json
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from store_frames import (F_BLACK, F_BOLD, WHITE, _vgrad, device_mockup,
                          paste_with_shadow, sticker)

FPS = 30
FADE = 0.5          # crossfade seconds
OVER = 1.30         # scene canvases are rendered larger to allow zooming

VO_BACKEND = os.environ.get("VO_BACKEND", "").strip().lower()
if VO_BACKEND == "none":      # explicit opt-in to a silent track
    VO_BACKEND = ""
VO_VOICE = os.environ.get("VO_VOICE", "")
VO_PAD = 0.6        # seconds of breathing room after each narration line

_KPIPE = None


def _probe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def synth_line(text, wav_path, out_dir, stem, index):
    """Render one narration line to a 48k mono wav via the chosen backend."""
    global _KPIPE
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
        import soundfile as sf
        voice = VO_VOICE or "af_heart"
        if _KPIPE is None:
            # Prefer kokoro-onnx (no torch/spacy — installs on modern Python);
            # fall back to the torch `kokoro` package if that's what's present.
            try:
                from kokoro_onnx import Kokoro
                model = os.environ.get("KOKORO_MODEL", os.path.expanduser(
                    "~/.venvs/tts-kokoro/models/kokoro-v1.0.onnx"))
                voices = os.environ.get("KOKORO_VOICES", os.path.expanduser(
                    "~/.venvs/tts-kokoro/models/voices-v1.0.bin"))
                _KPIPE = ("onnx", Kokoro(model, voices))
            except ImportError:
                from kokoro import KPipeline
                _KPIPE = ("torch", KPipeline(lang_code="a"))
        kind, pipe = _KPIPE
        if kind == "onnx":
            audio, sr = pipe.create(text, voice=voice, speed=1.0, lang="en-us")
        else:
            audio, sr = None, 24000
            for _, _, a in pipe(text, voice=voice):
                audio = a
        raw = wav_path + ".raw.wav"
        sf.write(raw, audio, sr)
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
        src = os.path.join(out_dir, "vo", f"{stem}-{index}.wav")
        if not os.path.exists(src):
            raise SystemExit(f"file backend: missing {src}")
        subprocess.run(["ffmpeg", "-y", "-i", src, "-ar", "48000", "-ac", "1",
                        wav_path], check=True, capture_output=True)
    else:
        raise SystemExit(f"unknown VO_BACKEND={VO_BACKEND!r}")


def circular_icon(icon_path, size):
    icon = Image.open(icon_path).convert("RGB").resize((size, size),
                                                        Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(icon, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def compose_scene(scene, raw_dir, icon_path, W, H):
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
        icon = circular_icon(icon_path, int(cw * 0.40))
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
        device = device_mockup(os.path.join(raw_dir, scene["raw"]),
                               int(cw * 0.74))
        paste_with_shadow(base, device, ((cw - device.width) // 2,
                                         int(ch * 0.27)),
                          blur=40, dy=24, opacity=130)
    return base.convert("RGB")


def _ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def _frame_of(canvas, local_t, dur, W, H, drift=0):
    """Slow zoom 1.00→1.10 across the scene plus a slight lateral drift."""
    z = 1.0 + 0.10 * _ease(local_t / dur)
    cw, ch = canvas.size
    vw, vh = int(W * OVER / z), int(H * OVER / z)
    cx = cw / 2 + drift * (cw * 0.02) * (local_t / dur)
    cy = ch / 2 - (ch * 0.015) * (local_t / dur)
    x0 = min(max(0, cx - vw / 2), cw - vw)
    y0 = min(max(0, cy - vh / 2), ch - vh)
    return canvas.crop((int(x0), int(y0), int(x0) + vw, int(y0) + vh)) \
                 .resize((W, H), Image.BILINEAR)


def render_preview(scenes, raw_dir, icon_path, out_path, W, H, max_total=29.5):
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="preview-")
    stem = os.path.splitext(os.path.basename(out_path))[0]
    try:
        # 1. Voiceover first — clip lengths drive scene durations.
        vo_clips = []  # (scene_index, wav_path, duration)
        if VO_BACKEND:
            print(f"synthesizing voiceover via '{VO_BACKEND}'...")
            for k, s in enumerate(scenes):
                if not s.get("vo"):
                    continue
                wav = os.path.join(tmp, f"vo{k}.wav")
                synth_line(s["vo"], wav, out_dir, stem, k)
                dur = _probe_dur(wav)
                vo_clips.append((k, wav, dur))
                s["dur"] = max(s["dur"], round(dur + VO_PAD + 0.4, 2))

        canvases = [compose_scene(s, raw_dir, icon_path, W, H) for s in scenes]
        starts, t0 = [], 0.0
        for s in scenes:
            starts.append(t0)
            t0 += s["dur"] - FADE
        total = starts[-1] + scenes[-1]["dur"]
        if total > max_total:
            print(f"WARNING: {total:.1f}s exceeds the {max_total}s ceiling — "
                  "trim narration lines.")
        n_frames = int(total * FPS)
        print(f"{total:.1f}s, {n_frames} frames")

        for i in range(n_frames):
            t = i / FPS
            active = [(k, s) for k, s in enumerate(scenes)
                      if starts[k] <= t < starts[k] + s["dur"]]
            k, s = active[0]
            img = _frame_of(canvases[k], t - starts[k], s["dur"], W, H,
                            s.get("drift", 0))
            if len(active) > 1:  # crossfade into the next scene
                k2, s2 = active[1]
                nxt = _frame_of(canvases[k2], t - starts[k2], s2["dur"], W, H,
                                s2.get("drift", 0))
                a = (t - starts[k2]) / FADE
                img = Image.blend(img, nxt, min(1.0, a))
            img.save(os.path.join(tmp, f"f{i:05d}.png"))

        # 2. Audio: lay each VO clip ~0.3s into its scene, mix, normalize.
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
            "-i", os.path.join(tmp, "f%05d.png"), *audio_args,
            "-shortest", "-map", "0:v", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-crf", "18", "-c:a", "aac", "-b:a", "256k",
            "-ac", "2", out_path], check=True, capture_output=True)

        # 3. Self-verify the audio actually landed. A voiceover run that comes
        # out silent means the narration was dropped — fail loudly instead of
        # shipping a mute "preview with voice".
        det = subprocess.run(
            ["ffmpeg", "-i", out_path, "-af", "volumedetect", "-f", "null", "-"],
            capture_output=True, text=True)
        mean = None
        for line in det.stderr.splitlines():
            if "mean_volume:" in line:
                mean = float(line.split("mean_volume:")[1].split("dB")[0])
        if VO_BACKEND and (mean is None or mean < -50):
            raise SystemExit(
                f"VOICEOVER MISSING: {out_path} rendered with VO_BACKEND="
                f"'{VO_BACKEND}' but mean_volume={mean} dB (silent). "
                "The narration did not make it into the file.")
        print(f"audio check: mean_volume={mean} dB"
              + ("" if VO_BACKEND else " (silent track — no VO_BACKEND set)"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", out_path)
