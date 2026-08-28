---
name: store-screenshots
description: Turn raw app screenshots into high-converting App Store / Play Store marketing screenshots and App Preview videos — outcome-driven copywriting (not feature lists), story-sequenced, branded device-frame screenshot graphics, and full-bleed no-device-frame App Preview videos (Apple Guideline 2.3.4) from real screen captures, generated via PIL/ffmpeg. Trigger when the user asks for store screenshots, listing screenshots, ASO screenshot copy, an App Store preview video, or to "make screenshots better / eye-catching".
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
xcrun simctl boot "iPhone 17 Pro Max"        # native raw is 1320×2868; the
                                             # renderer reframes to your target
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
- **Apple App Store iPhone:** App Store Connect has two iPhone slots and does
  **NOT** auto-convert between them — a file must exactly match the slot it's
  uploaded into, or you get *"The dimensions of one or more screenshots are
  wrong."*
  - **6.9" slot:** 1320×2868 or 1290×2796 (portrait), or the rotated landscape.
  - **6.5" slot:** 1284×2778 or 1242×2688 (portrait), or rotated.
  - You only need to fill **one** iPhone slot. **Default to the 6.5" size
    `1284×2778`** — it's accepted on its own and is the most broadly compatible.
    (Capturing on iPhone 17 Pro Max gives a native 1320×2868 raw, but the
    renderer reframes to whatever W×H you pass, so the raw size doesn't matter.)
- **Apple App Store iPad:** the 13"/12.9" slot. Use **`2048×2732`** (12.9",
  universally accepted). Native 13" captures are 2064×2752 — reframe to
  2048×2732 to avoid the same "wrong dimensions" rejection.

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

Only when a video is actually being produced: **read
`sections/preview-video.md` in full and follow it.** It carries the capture
recipe (variable-frame-rate traps, springboard-free launches), the Ken Burns
renderer, the ffmpeg assembly, and the optional Kokoro voiceover pipeline —
about 9KB that a screenshots-only run should never load.

Two rules are load-bearing enough to state here, because getting them wrong is a
rejection, not a retouch:

- **Apple 2.3.4: the preview video must be full-bleed real screen capture — no
  device frame, no bezel, no mockup.** Marketing screenshots may keep frames;
  the video may not. This is a logged rejection (`appstore-review-guard` ledger).
- **Never show the springboard or the launch tap** — that reads as "not showing
  the app in use", another 2.3.4 angle. Launch, let it settle, then record.

---

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
