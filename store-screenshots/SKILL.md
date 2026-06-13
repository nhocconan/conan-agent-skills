---
name: store-screenshots
description: Turn raw app screenshots into high-converting App Store / Play Store marketing screenshots and App Preview videos — outcome-driven copywriting (not feature lists), story-sequenced, branded device-frame graphics and Ken Burns preview videos generated via PIL/ffmpeg. Trigger when the user asks for store screenshots, listing screenshots, ASO screenshot copy, an App Store preview video, or to "make screenshots better / eye-catching".
---

# Store screenshots & previews that convert

70% of a store screenshot is copywriting. Raw UI captures with no text — or text
that lists features — read like patch notes to someone who hasn't bought in yet.
This skill produces **story-sequenced marketing screenshots** (big outcome
headline + framed device mockup on a branded background) and a matching
**App Preview video**.

## Step 1 — Write the copy FIRST (before any pixels)

**Rule: describe what changes for the user, never the feature.**

| ✗ Feature (patch notes) | ✓ Outcome (reason to download) |
|---|---|
| Customizable dashboard | See everything that matters, at a glance |
| Workout tracking | You'll never forget what you lifted again |
| Dark mode support | Easy on your eyes, day and night |
| Multiplayer mode | Challenge your friends |

Specificity makes the promise real: "Productivity app" is invisible;
"Never lose a meeting note again" is a download.

**The hand test:** cover the UI with your hand and read only the text across all
screenshots. It must tell a story, in order. If the screenshots work in any
sequence, you have a catalog, not a story.

**The sequence (5 screenshots, each does ONE job, one short message each):**
1. **Name the pain** — their frustration before your app ("Buried in notes you'll never find again?")
2. **State the shift** — life after the app ("Everything you capture, organized automatically.")
3. **Show proof** — real numbers/users/result ("Used by 10,000 developers."). *Never invent numbers.* A v1 with no users substitutes its strongest verifiable claim (reliability, privacy, offline, free).
4. **Feature delivery #1** — the capability that delivers the promise from #2
5. **Feature delivery #2** — second strongest capability (privacy/no-ads is a great closer)

Headline ≤ 4 words per line, ≤ 2 lines, ALL CAPS works well. Optional subline
≤ 12 words. If a screen needs two sentences, split it into two screenshots.
Only claim what the app verifiably does on that platform (e.g. don't claim
"rings on silent" if the platform build lacks the entitlement).

## Step 2 — Capture raw screens

One clean raw capture per slide, content matching the headline. Keep raws in
`<assets>/screenshots/raw/`; generated finals go in `<assets>/screenshots/`.

**iOS simulator recipe** (gives App Store-native sizes for free):
```bash
xcrun simctl boot "iPhone 17 Pro Max"        # 6.9" → captures are 1320×2868
xcrun simctl status_bar booted override --time "9:41" --batteryLevel 100 \
  --batteryState charged --cellularBars 4 --wifiBars 3
xcrun simctl uninstall booted <bundle-id>    # fresh state so seeds apply
xcrun simctl install booted <path>.app
xcrun simctl launch booted <bundle-id> -uiScreenshots -uiTab 0   # etc.
xcrun simctl io booted screenshot raw/tab0.png   # use an ABSOLUTE output path
```
Android: emulator + `adb exec-out screencap`; set the clock with
`adb shell cmd alarm set-time <epoch-millis>` (no root needed).

**Add a DEBUG-only `-uiScreenshots` launch arg to the app** (pattern that pays
for itself): skip onboarding, seed realistic demo data **including data active
on the capture day** (e.g. a Weekend profile so a Saturday capture isn't
empty), select the seasonally-correct default, and report permissions as
granted so "Turn on notifications"-style banners stay out of marketing shots.

## Step 3 — Generate the screenshot frames

Templates next to this SKILL.md: copy `store_frames.py` (shared renderer) plus
`example_screenshots.py` (per-store config) into the project's scripts dir.
Edit the `SLIDES` list (raw file, headline lines, subline, background
gradient, alternating tilt) and call `render_slides(SLIDES, raw_dir, out_dir, W, H)`.

Canvas sizes (the renderer scales its layout to any of these):
- **Google Play:** 1080×1920 (9:16 — required for promotion placements)
- **Apple App Store 6.9" slot:** 1320×2868 (capture on iPhone 17 Pro Max and
  it's already native; Apple auto-scales down for smaller slots)

Per slide the renderer draws: vertical brand-gradient background + soft glow →
rotated white "sticker" headline boxes (heavy font, ink text, drop shadow) →
subline → device mockup (rounded corners, dark bezel, ±2.5° alternating tilt,
drop shadow) bleeding off the bottom edge. Design rules — keep them:
- Supersample ×2, LANCZOS downscale.
- Use the app's own brand palette; alternate background colors between slides
  so the row pops in search results, but stay in-brand.
- Headline must survive thumbnail size: check legibility at ~25% zoom.
- Device bleeds off the bottom — full phones look like a catalog.

## Step 4 — App Preview video (Apple) / promo video (Play)

Template: `preview_video.py` (PIL frames → ffmpeg). It builds: brand intro
card (icon + name sticker + tagline) → one Ken Burns scene per raw capture
(slow 1.00→1.10 zoom + slight drift, sticker caption on brand gradient) →
outro card with a call-to-action line, 0.5s crossfades throughout.

**Apple App Preview spec (verified June 2026 — recheck if rejected):**
- iPhone 6.9"/6.5" portrait: **886×1920**, .mp4/.mov/.m4v, **30 fps**,
  **15–30 s**, ≤500 MB.
- **A stereo audio track is required** (256kbps AAC, 44.1/48 kHz) — a silent
  `anullsrc` stereo track satisfies it:
  `ffmpeg -framerate 30 -i f%05d.png -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -shortest -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -b:a 256k out.mp4`
- Verify with ffprobe: codec h264, 886×1920, 30/1, aac 2ch, duration 15–30.
- Captions are fine, but footage must be (or be composed from) real app UI.

Keep the video's captions the same voice/sequence as the screenshots — the
listing reads as one story.

### Voiceover (optional, allowed, recommended for polish)

Apple permits a narration track; `preview_video.py` supports a pluggable
backend via `VO_BACKEND` (unset = silent stereo track, still valid). Write one
short `vo` line per scene that mirrors its caption; the script synths each line,
**lets clip length drive scene duration** (so audio never gets cut off), lays
clips ~0.3s into each scene, mixes, and `loudnorm`-normalizes — then stays
inside the 15–30s window (warns if narration pushes past 30s).

Pick a voice source (decision order for a free, license-clean, published asset):

| Backend | Quality | Cost / setup | Local? | Notes |
|---|---|---|---|---|
| `kokoro` | Excellent | `pip install kokoro soundfile` + espeak-ng; ~330MB weights | Yes | **Apache-2.0 → safe for commercial listings.** Best free pick. `VO_VOICE=af_heart` etc. |
| `piper` | Good | Piper binary + a `.onnx` voice (`VO_VOICE=<path>`) | Yes | Lighter than Kokoro; MIT voices available |
| `say` | OK | zero install; **download a Premium voice** in System Settings (defaults sound robotic) | Yes | `VO_VOICE="Ava (Premium)"`. Fine for a draft |
| `openai` | Excellent | `OPENAI_API_KEY`, model `gpt-4o-mini-tts` (~1¢) | No | **NOT covered by the "free shared-traffic" token tier** — that tier is text models only; TTS bills at standard rates |
| `file` | — | drop `vo/<stem>-<i>.wav` per scene | Yes | Use your own recorded voice — most authentic |

Avoid **edge-tts** (Microsoft's free no-key neural voices) for a *published*
asset: it's online and its ToS scopes it to Edge's read-aloud feature. Great for
throwaway drafts only. (voice-pro and similar all-in-one tools lean on it, plus
F5-TTS/CosyVoice for zero-shot cloning if you want a *custom* voice — heavier,
GPL.)

Add a music bed only if you have a license for the track (ffmpeg can duck it
under the VO with `sidechaincompress`); never grab a random song.

## Step 5 — Verify

- View every output image and 3–4 extracted video frames
  (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 check.png`); check text fits, no
  glyph boxes (e.g. ≠ missing from a font), sticker doesn't cover key UI.
- Hand test again on the finals; ffprobe the video against the spec table.
- With voiceover: confirm the track isn't silent —
  `ffmpeg -i out.mp4 -af volumedetect -f null -` should report a mean_volume
  around −16 dB, not −91 dB. Listen that no line is clipped at a scene cut.
- Play: PNG/JPEG ≤ 8 MB, sides 320–3840 px, 2–8 phone screenshots.
- Don't claim anything the app can't verifiably do (store rejection / trust).
