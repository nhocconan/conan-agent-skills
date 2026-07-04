---
name: demo-data-craft
description: Build convincing, safe demo/seed data for product demos — masked clones of real tenants (joins survive, secrets scrubbed), synthetic story-shaped seed data, demo orgs with env-gated forcing, and screenshot/capture seeding. Use when preparing any demo, showcase, sales environment, seeded dev/e2e data, or marketing capture; when the user says "demo", "seed data", "chuẩn bị demo", "mask the data", or asks for a populated environment. Demo data must be internally consistent and never mutate the source system.
---

# Demo Data Craft

A demo lives or dies on its data: empty screens kill the story, fabricated-looking numbers
kill trust, and a leaked real customer name kills the deal. Three tiers of demo data, in
descending realism — pick per goal, and obey the shared rules at the bottom.

## Tier 1 — Masked clone of a real tenant (highest realism; for sales/demo servers)

Clone → mask → export → restore. Never touch the source.

- **Never mutate the source DB.** Clone into a scratch database (`pg_dump | psql`), mask on
  the scratch, export the artifact, drop the scratch.
- **Discover tenant tables dynamically** (every table with the tenant/org id column) — a
  hardcoded table list goes stale the day someone adds a feature and the new table leaks
  unmasked.
- **Mask uniformly so joins survive.** Two token classes: DISPLAY columns get the pretty
  replacement ("Brand A", "Org DEMO"); IDENTIFIER-shaped columns (slugs, `%_id`, handles,
  URLs, codes, keys) get the same slug-safe token applied EVERYWHERE, so
  `oldshop-lzd → branda-lzd` still joins across tables. One scrub pass over all text/jsonb
  columns; skip secret-shaped columns (ciphertext/iv/hash) and handle them explicitly.
- **Product/content names too**: token-swapping the brand still leaves googleable product
  titles in payloads, line items, video titles. Rename per-entity ("Brand A {category} NN")
  including inside raw JSON payloads; exclude bronze/raw-staging tables from the export
  entirely (not rendered, full of raw text, and it shrinks the artifact).
- **Secrets**: NULL real credentials in the export; on restore, write FAKE blobs encrypted
  with the demo environment's own key so the UI shows "configured/active" without any real
  secret in the artifact. Purge audit logs, tokens, DSAR/PII tables. Verify **zero residue**
  of the real names with a final grep over every text column.
- **Demo users**: fixed roles (owner/operator/viewer) with a documented password; drop real
  accounts from the export.

## Tier 2 — Synthetic story data (for products without a rich real tenant)

- **Seed the story, not random rows.** Decide the narrative first ("TikTok is the problem",
  "anomaly engine fires", "returning customers grew") and shape the data so the screens the
  demo walks through actually show it. Random data produces flat, meaningless charts.
- **Internally consistent**: attach rates plausible (not 100%), breakdowns sum to totals,
  history deep enough for every widget (a 13-month synthetic history so trend/anomaly
  features fire, weekly records so time toggles work). Anchor magnitudes to real aggregates
  where known — an impossible total is a bug even in a demo (see `metric-integrity`).
- **Pin the demo period** if screens assume one (and document it — "do not change to
  `now()` or screens go blank"), or generate relative-to-today so the demo never rots.
- Make the seed **one command, idempotent, documented** next to the login credentials.

## Tier 3 — Capture-time seeding (screenshots/videos/QA)

A DEBUG-only launch arg (`-uiScreenshots` pattern) that: skips onboarding, seeds realistic
demo content **valid on the capture day**, selects the seasonally-correct defaults, and
reports permissions as granted so no permission banners pollute captures. Details live in
`store-screenshots` (Step 2); e2e-seeded accounts are the same idea for tests.

## Shared rules (all tiers)

- **Env-gated demo forcing, inert by default.** Flags like `DEMO_FORCE_CONNECTORS_HEALTHY`
  short-circuit at read time (list endpoints stamp healthy, ping short-circuits), gated on
  an env var that is unset everywhere except the demo box. Never fake state by writing
  future dates into data — read-time gates survive time passing.
- **Shared external tokens: disable auto-sync** in demo/dev (`syncEnabled: false`) so the
  demo worker can't throttle production APIs.
- **Self-bootstrapping bring-up**: the canonical start is ONE command (`docker compose up
  -d` / one seed script) that is safe to re-run — first boot seeds, later boots skip.
  Reset = documented one-liner (`down -v && up -d`, or delete the store file).
- **Write the runbook**: bring-up, login creds, demo period, reset, known gaps — the demo
  will be run by someone else (or by you, months later).

## Output

Deliver: the seeding/masking script(s) committed where they belong, the runbook, and a
verification pass — walk the actual demo path in a browser/device and confirm every screen
in the story is populated and consistent. An unverified demo environment is not done.
