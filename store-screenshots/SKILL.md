---
name: store-screenshots
description: Turn raw app screenshots into high-converting App Store / Play Store marketing screenshots — outcome-driven copywriting (not feature lists), story-sequenced, with branded device-frame graphics generated via PIL. Trigger when the user asks for store screenshots, listing screenshots, ASO screenshot copy, or to "make screenshots better / eye-catching".
---

# Store screenshots that convert

70% of a store screenshot is copywriting. Raw UI captures with no text — or text
that lists features — read like patch notes to someone who hasn't bought in yet.
This skill produces **story-sequenced marketing screenshots**: big outcome
headline + framed device mockup on a branded background.

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

## Step 2 — Capture raw screens

One clean raw capture per slide, content matching the headline (status bar
clock set nicely, realistic seeded data, no debug UI). Keep raws in
`<assets>/screenshots/raw/`; generated finals go in `<assets>/screenshots/`.

## Step 3 — Generate the frames

Use the template `frame_screenshots.py` next to this SKILL.md: copy it into the
project's scripts dir, edit the `SLIDES` config (raw file, headline lines,
subline, background gradient, tilt) and the brand `PALETTE`. It renders, per
slide: vertical brand-gradient background + soft glow → rotated white
"sticker" headline boxes (heavy font, ink text, drop shadow) → subline →
device mockup (rounded corners, dark bezel, slight alternate tilt ±2.5°, drop
shadow) bleeding off the bottom edge.

Design rules baked into the template — keep them:
- Canvas **1080×1920** (9:16 — safe for Google Play promotion slots and usable
  cross-store; iPhone 6.7" equivalent is 1290×2796, same layout scales).
- Supersample ×2, LANCZOS downscale.
- Use the app's own brand palette; alternate background colors between slides
  so the row pops in search results, but stay in-brand.
- Headline must survive thumbnail size: check legibility at ~25% zoom.
- Device bleeds off the bottom — full phones look like a catalog.

## Step 4 — Verify

- View every output image; check text fits, no glyph boxes (e.g. ≠ missing
  from a font), sticker doesn't cover key UI.
- Hand test again on the finals.
- Play limits: PNG/JPEG ≤ 8 MB, sides 320–3840 px, 2–8 phone screenshots.
- Don't claim anything the app can't verifiably do (store rejection / trust).
