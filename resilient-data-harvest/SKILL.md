---
name: resilient-data-harvest
description: Resumable data collection — browser scraping, paged API pulls, backfills and system-to-system migrations — per-item checkpoints, pacing and challenge handling, resume-from-partial, drift detection, quality gate before ingest, harvester updated when reality changes. Use when scraping a logged-in site, pulling a paginated API, backfilling or re-syncing a connector, migrating tickets/records between systems, when a re-sync must not clobber a manual correction, or when the user says "lấy data", "scrape", "crawl", "backfill", "bị block", "CloudFlare", "chạy lại từ đầu".
---

# Resilient Data Harvest

Make collection resumable across crashes, source changes and interrupted connections.

## 1. Checkpoint per item — never per run

**Write each completed unit to disk before starting the next one.** Page, record, day,
ticket — whatever the unit is. Then keep a manifest of what is done.

- Manifest of processed unit keys + an output file (or one file per unit).
- The run is **idempotent and resumable**: on start, read the manifest, skip what's done,
  continue. Re-running a completed harvest is a no-op, not a duplicate.
- Never hold the whole result set in memory to write at the end. A crash at 95% then
  costs 95%. The unit of durability is the item, not the run.

## 2. Respect source limits

Use authorized sources; prefer a supported export/API.

- **Pace deliberately** and state the pacing in the run log so it can be checked. If the
  plan says 4–8s per page, the log must show 4–8s per page — a claimed pace that the
  timestamps contradict is the bug.
- **Serialize browser collection and sources with unknown limits.** For supported APIs
  with documented concurrency limits, use bounded workers under one shared rate budget,
  independent unit ownership and atomic checkpoints. Reduce concurrency on warnings.
- Honor `Retry-After`; jitter retries to avoid synchronized retry bursts, not to evade detection.
- **Back off on the first warning sign** (429, a challenge page, a sudden empty result),
  don't push through it.

## 3. Use the real session

Logged-in source: drive the operator's authenticated browser; session rules live in
`browsing-web` (**"Standing rules"**). On a CAPTCHA or access challenge, save progress and
hand it to the user; never bypass.

## 4. Detect drift, don't paper over it

The source will change shape without telling you.

- **Assert the schema** on every unit: expected fields present, types right, row count in
  a sane band. A silent shape change that yields empty columns is the worst outcome —
  it looks like success and poisons everything downstream.
- **Compare against the last run.** A field that was 100% populated and is now 0% is
  drift, not data. Volume that halves is drift, not a slow week.
- **Fail with a redacted sample.** Remove secrets and personal data from diagnostic output. A drift
  failure you can't reproduce from the log is a second run wasted.
- **Range-check the boundaries.** If the pull claims a date range, verify the returned
  data actually covers it — a truncated window that quietly returns stale rows reads as
  a successful run.

## 5. Quality gate before ingest

Harvested data lands in a staging area first. Promote only after:

- row counts and date coverage match what was requested;
- no unit is duplicated (the manifest is the authority);
- required fields are non-null at the expected rate;
- units that failed are listed explicitly — a partial harvest must **announce** it is
  partial, never present itself as complete.

Retain raw payloads only when necessary and authorized, with restricted access and a retention period. Write checkpoints atomically and lock concurrent resumes; never mark an item complete before its output is durable.

## 6. The harvester is a living artifact

**Whenever reality changes, the script/skill changes in the same session.** New endpoint,
new pacing, a new challenge type, a new quality trap — it goes into the harvester before
the run is called done. Otherwise the next run rediscovers it from scratch and the
operator has to say it again — and a rule that has to be re-stated every run is a rule
that was never recorded.

Every harvester ships with:

- a **dry-run / small-N mode** to prove the path end-to-end cheaply;
- a **reset + reload** command, so a bad pull can be redone without hand-surgery;
- a note of the last-verified date and the last-known-good response shape.

## Migration and sync

Moving records between systems, or a sync that can overwrite human edits (provenance
column, precedence rule): read `MIGRATION.md`.

## Companions

`agent-orchestration` — the plan-file/resume discipline this shares: see
`agent-orchestration/sections/tracking.md`, its **"Track and resume"** section.
