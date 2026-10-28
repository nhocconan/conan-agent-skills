# Landing page path

## Contents
- Intake
- Structure
- Conversion rules
- Copy
- Build order
- Ship list
- What is not taken from upstream

Strategy half of upstream `landing-page-design` (summarized; see [../REF.md](../REF.md)).
Decide the offer before the look.

## Intake
One batch of questions, then assume-and-state for anything unanswered (one line each):
primary action, the offer, ideal visitor, top objections, traffic source (ad-only pages get
`noindex`), proof assets that actually exist, brand voice, mobile priority. Thesis: one offer,
one audience, one primary action.

## Structure
- **Above the fold**: headline (outcome + audience), subheadline, ONE primary CTA, one proof
  signal, a hero visual that is the most characteristic thing in the subject's world (a live
  or scripted product moment beats a stat strip).
- **Middle**: problem to solution, 3-5 benefits, how it works (about 3 steps), social proof.
- **Bottom**: FAQ of real objections (6-12), risk reversal, final CTA identical to the top one.
- **Tagline reveal**: one benefit statement of at least two lines, revealed word by word
  (muted to full) as it scrolls in.
- Layout type: A classic, B long-form story (offer needs education), C minimal, D comparison.
  Pick one and say why. Each section gets its own composition; identical card rows repeated
  down the page are a slop tell.

## Conversion rules
Specific numbers over adjectives; one action (no competing CTAs); proof next to the claim it
supports; objections get a section; navigation shrinks to what supports the action.

## Copy
CTA = verb + what you get ("Open the workspace", not "Submit"). Headline names the outcome.
Sentence case. No filler subtitle that restates the title. Copy goes through the project's
i18n source, source language first.

## Build order
Outline, hero copy, benefits, how it works, FAQ, SEO notes, layout choice, all as text and
shown before code. Then build hero, benefits, how it works, proof, FAQ, CTA. SEO/AEO: FAQ
structured data when the FAQ is real, one h1, descriptive meta, no keyword stuffing.

## Ship list
Real content only (no fake logos, reviews, counts); all states (hover, focus, disabled,
loading, error); responsive at 375px; one h1 and ordered headings; alt text; the motion rules
in [motion.md](motion.md) honoured; route allow-list and bundle budget checked when the
project has them (a new public route can be redirected by auth middleware until allow-listed).

## What is not taken from upstream
Its visual half (fixed font list, single typeface, no gradients, fixed dark hex list, hero
heading gradient, icon set, no hyphens in copy) is advisory. A brand with its own fonts,
gradients, accents, icons or a language that needs hyphens, dashes or diacritic-safe line
height keeps them. Keep from it only what the brand does not decide: type contrast through
scale, balanced wrapping (`text-wrap: balance` for headings, `pretty` for body), nested radius
= outer radius minus the gap, spacing from a fixed step scale, flat or quiet surfaces unless
the brand uses gradients.
