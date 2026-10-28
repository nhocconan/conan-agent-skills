# Anti-slop catalogue

## Contents
- Clusters
- Concrete tells
- Content
- Rule of use

Derived from the Anthropic `frontend-design` plugin's calibration list plus tells seen in
review. A hit is a default, not a crime: it must be a choice the brief or brand justifies.

## Clusters
1. Warm cream background (near #F4F1EA), high-contrast serif display, terracotta/clay accent
   (near #D97757).
2. Near-black background with a single acid-green or vermilion accent.
3. Broadsheet: hairline rules, zero radius, dense newspaper columns.
4. SaaS-card kit: identical rounded cards, one radius everywhere, same soft grey shadow
   under each, gradient washes as decoration.
5. Template chrome: tracked ALL-CAPS eyebrow over every heading; meta strings joined by
   middle dots; "WORD - fragment" labels; tinted near-black (#0B0B0B, #111) for black;
   monospace for small labels; "->" appended to link and button text.

## Concrete tells
- Purple/blue-to-pink gradient hero or gradient text on the headline.
- One word of the headline in italic, bold or accent colour.
- Big number + small label + gradient accent as the hero by reflex.
- 01 / 02 / 03 numbering on content that is not a sequence.
- Three equal feature cards with icon, title, one line; the same row repeated per section.
- Fade-and-slide-up on every section, hover lift on every card.
- Glassmorphism / blur panels with no depth reason; decorative blobs, orbs, grids.
- Emoji or generic icon-in-circle as the only visual; stock-looking illustration.
- Subtitle that restates the title; a section header for one sentence; decorative boxes
  carrying no information.
- Fake social proof: invented logos, "10,000+ users", placeholder testimonials, lorem ipsum,
  "John Doe".
- Default font stack for the whole page (Inter/Roboto/Arial) when a brand font exists.
- Everything centred; no alignment decision.
- Buttons: two equal-weight CTAs competing; label "Submit" / "Learn more".
- Mixed-language chrome: English section labels/kickers ("Attention Engine", "First Party Data")
  on a page localized to another language.
- A visual that encodes nothing (concentric arcs, abstract bars) inside a card that claims a
  story; each card visual must show its own mechanism.
- Copy that sells instead of saying what it is; "seamless", "unlock", "supercharge",
  "revolutionize"; headings in Title Case Everywhere.

## Content
Product facts must trace to docs or code. Do not claim capabilities the product lacks (for
example autonomous execution or causal impact). No real-customer names, numbers or logos
without a source. Straight quotes where the project's rules require them.

## Rule of use
Run the list on the plan (section 2 of SKILL.md) and again on the rendered page. For each
hit, either change it or record the one-line reason it is a deliberate choice.

The builder's own pass is not the gate: builders mark their own page PASS on every line while
eight tracked-caps eyebrows and middot strings are still on screen (observed 2026-10-27). The
gate is a second reader on full-page screenshots (both themes, narrow width) who COUNTS:
uppercase-tracked labels, middot/arrow meta strings, numbered lists that are not sequences,
foreign-language labels, decorative-only visuals. Report the counts, not adjectives. Spend
boldness in one place; remove one accessory before leaving the house.
