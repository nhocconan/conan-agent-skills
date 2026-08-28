## Step 4 — App Preview video (Apple) / promo video (Play)

> ⚠️ **The App Preview VIDEO must NOT contain device frames** (Apple Guideline
> 2.3.4 — *"the app preview includes device images and/or device frames… revise
> the app preview to only use video screen captures of the app"*). This is the
> **opposite** of screenshots: marketing **screenshots** may sit in a tilted
> device mockup (Step 3), but the **video** must be a *full-bleed screen
> capture* — the app fills the whole frame, no bezel, no phone, no gradient
> margin. Text/caption/narration overlays are explicitly allowed; device frames
> are not. A real first-submission rejection (June 2026) came from exactly this:
> the old "Ken-Burns over a framed device on a brand gradient" preview was fine
> as screenshots but illegal as a video. **Don't reuse `device_mockup()` in the
> video.**

Templates: `preview_clips.py` (the no-frame renderer + the same voiceover
engine) and `example_preview.py` (a thin config calling
`render_preview_from_media(scenes, media_dir, icon, out_path, W, H)`). It builds:
brand intro card → real captures full-bleed with a sticker caption overlaid on
top → outro card, 0.5s crossfades, optional voiceover. Scene kinds:
- **`clip`** — a real screen recording (.mp4), shown full-bleed, caption on top.
- **`still`** — a real full-screen screenshot, gentle Ken Burns (1.00→1.05 zoom),
  caption on top. Use for calm screens you can't record with motion.
- **`card`** — generated brand card (icon + name + tagline); intro/outro only.

**Capture native (1320×2868); the renderer outputs the video at 886×1920.**
Native captures are the *screenshot* size — the renderer downscales them for the
video (still a true screen capture, just not 1:1). Do NOT output the video at
1320×2868: the App Preview slot rejects that size (see spec below).
```bash
xcrun simctl status_bar booted override --time 09:41 --batteryState charging \
  --batteryLevel 100 --cellularBars 4 --wifiBars 3 --dataNetwork wifi
# LIVE clip — recordVideo is VARIABLE-FRAME-RATE: a static screen records as a
# ~0s clip, so you need on-screen motion (clock hand, ring, list).
# Launch FIRST and let it SETTLE, THEN record. Recording the launch catches the
# springboard (other apps + the tap) — that reads as "not showing the app in
# use" (another 2.3.4 angle). Capture the app only:
xcrun simctl launch booted <bundle-id> -uiScreenshots -uiTab 0
sleep 3.5                                    # settle on the hero screen
xcrun simctl io booted recordVideo --codec h264 --force segments/home.mp4 &
REC=$!; sleep 9; kill -INT $REC              # SIGINT finalizes the mp4
# (Tip: `xcrun simctl uninstall booted <id>` junk apps too, so even a stray
#  springboard frame is clean.)
# CALM screens — a screenshot is cleaner than a frozen recording; the renderer
# adds the motion via Ken Burns:
xcrun simctl io booted screenshot segments/stills/settings.png
```
One live "hero" clip (the signature screen) plus screenshots for the rest is a
reliable mix on a headless simulator (no idb/tap-injection needed). Reuse a
trimmed tail of the hero clip (`ffmpeg -ss 3 -i home.mp4 -c copy home_b.mp4`) if
two scenes show it, so they don't replay an identical opening.

**Accurate metadata (Guideline 2.3):** only caption a scene with a feature it
*visibly shows*. "Widgets & Siri" over a plain home screen is a rejection risk;
so is a "Lock Screen countdown" caption over the Settings page (a real June 2026
near-miss). For surfaces you can't screen-record on a headless sim — Lock Screen
/ Live Activity / widget / Siri (`simctl` has no lock command, and osascript UI
automation needs Accessibility) — **don't fake them in the VIDEO.** Either drop
the claim there and caption what's on screen, or — better — sell them in a
**STILL**: App Store *screenshots* may be composited, so a faithful render of a
real feature is compliant in a still even though it's illegal in the video.
Build the still from the shipping design (e.g. reproduce the Live Activity layout
on a Lock Screen) and use the GENUINE SF Symbols, exported via AppKit so glyphs
are real, not approximations:
```swift
// swift render.swift  → tint a template symbol with .sourceAtop, save PNG
let cfg = NSImage.SymbolConfiguration(pointSize: 240, weight: .bold)
let img = NSImage(systemSymbolName: "figure.walk", accessibilityDescription: nil)!
            .withSymbolConfiguration(cfg)!     // draw → fill .sourceAtop → PNG
```
A real, capturable extra surface (e.g. Dynamic Island while backgrounded) can go
in the video; everything else lives in the stills. Same accuracy rule as Step 1.

**Google Play** takes the promo as a **YouTube link**, not a file upload:
render a vertical 1080×1920 mp4, upload it to YouTube (unlisted is fine), and
paste the URL in the listing. Play is lenient on length (no 30s cap) and on
device frames, but keep it tight.

**Apple App Preview spec (verified June 2026 — recheck if rejected):**
- **Render at 886×1920** (portrait) / 1920×886 (landscape) — accepted across the
  6.5"/6.7"/6.9" iPhone App Preview slots. **Do NOT upload 1320×2868** (that's
  the *screenshot* size): the App Preview slot rejects it — *"The app preview
  dimensions should be: 886 × 1920px or 1920 × 886px"* (real June 2026 upload
  error). .mp4/.mov/.m4v, **30 fps**, **15–30 s**, ≤500 MB.
- **No device frames / bezels** in the footage (2.3.4) — full-bleed only.
- **A stereo audio track is required** (256kbps AAC, 44.1/48 kHz) — a silent
  `anullsrc` stereo track satisfies it if you ship without voiceover.
- Verify with ffprobe: codec h264, **886×1920**, 30/1, aac 2ch, duration 15–30,
  and that no frame shows a phone bezel.

Keep the video's captions the same voice/sequence as the screenshots — the
listing reads as one story.

### Voiceover (optional, allowed, recommended for polish)

Apple permits a narration track; `preview_clips.py` supports a pluggable
backend via `VO_BACKEND`. Write one short `vo` line per scene that mirrors its
caption; the script synths each line, **lets clip length drive scene duration**
(so audio never gets cut off), lays clips ~0.3s into each scene, mixes, and
`loudnorm`-normalizes — then stays inside the 15–30s window (warns if narration
pushes past 30s).

**Default to voiced — don't ship a silent "preview".** Have the per-platform
config `os.environ.setdefault("VO_BACKEND", "kokoro")` so a bare
`python gen_*_preview.py` run still narrates; a forgotten `VO_BACKEND` is the
#1 way a mute video reaches the store. To deliberately ship a silent stereo
track (still spec-valid for Apple), pass `VO_BACKEND=none`. After encoding, the
renderer **self-verifies the audio**: if a voiced run comes out under −50 dB it
`raise`s `VOICEOVER MISSING` instead of writing a mute file — so a silent
result fails the build rather than slipping into the listing.

Pick a voice source (decision order for a free, license-clean, published asset):

| Backend | Quality | Cost / setup | Local? | Notes |
|---|---|---|---|---|
| `kokoro` | Excellent | see below; ~350MB model | Yes | **Apache-2.0 → safe for commercial listings.** Best free pick. `VO_VOICE=af_heart`/`af_bella`/`am_michael` etc. |
| `piper` | Good | Piper binary + a `.onnx` voice (`VO_VOICE=<path>`) | Yes | Lighter than Kokoro; MIT voices available |
| `say` | OK | zero install; **download a Premium voice** in System Settings (defaults sound robotic) | Yes | `VO_VOICE="Ava (Premium)"`. Fine for a draft |
| `openai` | Excellent | `OPENAI_API_KEY`, model `gpt-4o-mini-tts` (~1¢) | No | **NOT covered by the "free shared-traffic" token tier** — that tier is text models only; TTS bills at standard rates |
| `file` | — | drop `vo/<stem>-<i>.wav` per scene | Yes | Use your own recorded voice — most authentic |

**Installing Kokoro (use kokoro-onnx — `pip install kokoro` breaks on Python
3.13+ because spacy/blis won't compile):**
```bash
brew install espeak-ng                       # phonemizer backend
python3.13 -m venv ~/.venvs/tts-kokoro        # isolate; 3.13 has onnxruntime wheels
~/.venvs/tts-kokoro/bin/pip install kokoro-onnx soundfile pillow
# one-time model download into ~/.venvs/tts-kokoro/models/:
#   kokoro-v1.0.onnx + voices-v1.0.bin from the kokoro-onnx GitHub release
VO_BACKEND=kokoro VO_VOICE=af_heart ~/.venvs/tts-kokoro/bin/python example_preview.py
```
The `kokoro` backend prefers `kokoro_onnx` and falls back to the torch
`kokoro` package; set `KOKORO_MODEL`/`KOKORO_VOICES` to override model paths.
Run the generator with the venv's python so Pillow + kokoro-onnx are on the path.

Avoid **edge-tts** (Microsoft's free no-key neural voices) for a *published*
asset: it's online and its ToS scopes it to Edge's read-aloud feature. Great for
throwaway drafts only. (voice-pro and similar all-in-one tools lean on it, plus
F5-TTS/CosyVoice for zero-shot cloning if you want a *custom* voice — heavier,
GPL.)

Add a music bed only if you have a license for the track (ffmpeg can duck it
under the VO with `sidechaincompress`); never grab a random song.
