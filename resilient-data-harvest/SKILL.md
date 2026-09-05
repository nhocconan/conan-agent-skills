---
name: resilient-data-harvest
description: Build data-collection runs that survive contact with reality — browser scraping, paged API pulls, and system-to-system migrations. Covers human-paced request rhythm and block/CAPTCHA avoidance, write-as-you-go checkpointing so a dropped connection costs one item not the whole run, resume-from-partial, endpoint/schema drift detection, data-quality gates before ingest, and the rule that the harvester script or skill gets updated the moment reality changes. Use when scraping a logged-in site, pulling a paginated API, backfilling or re-syncing a connector, migrating tickets/records between systems, or when the user says "lấy data", "scrape", "crawl", "backfill", "bị block", "CloudFlare", "chạy lại từ đầu".
---

# Resilient Data Harvest

A harvest is not code that runs once. It is code that runs again next week, against a
source that changed, over a connection that will drop. Every rule here comes from a run
that failed at hour three.

## 1. Checkpoint per item — never per run

**Write each completed unit to disk before starting the next one.** Page, record, day,
ticket — whatever the unit is. Then keep a manifest of what is done.

- Manifest of processed unit keys + an output file (or one file per unit).
- The run is **idempotent and resumable**: on start, read the manifest, skip what's done,
  continue. Re-running a completed harvest is a no-op, not a duplicate.
- Never hold the whole result set in memory to write at the end. A crash at 95% then
  costs 95%. *"Xong cái nào thì write ra file lưu cho chắc chứ."*

## 2. Move at human speed

Sources that notice a bot escalate: rate-limit → CAPTCHA → CloudFlare challenge → ban.
Getting banned costs far more than going slow.

- **Pace deliberately** and state the pacing in the run log so it can be checked. If the
  plan says 4–8s per page, the log must show 4–8s per page — a claimed pace that the
  timestamps contradict is the bug.
- **Serialize.** Do not fan out concurrent requests at one source to "go faster". One
  worker, steady rhythm. *"đừng có flood quá nhiều request vô cùng lúc nó chặn."*
- **Jitter** the interval; a metronome is itself a signature.
- **Back off on the first warning sign** (429, a challenge page, a sudden empty result),
  don't push through it.
- Slow is the point. There is no deadline that beats losing the account.

## 3. Use the real session

For a logged-in source, drive the operator's already-authenticated browser rather than
re-implementing auth or re-solving login. Two consequences that have both bitten:

- **State the profile/session requirement up front.** If the harvest needs a specific
  browser profile, say so before starting — don't fail silently ten minutes in because
  the operator was browsing in a different profile.
- **Don't stop to ask for what you already have.** If the operator has said the browser
  is open and logged in, proceed. Halting to re-confirm burns their time and tokens.

When a challenge does appear, solve it in that live session rather than aborting the run.

## 4. Detect drift, don't paper over it

The source will change shape without telling you.

- **Assert the schema** on every unit: expected fields present, types right, row count in
  a sane band. A silent shape change that yields empty columns is the worst outcome —
  it looks like success and poisons everything downstream.
- **Compare against the last run.** A field that was 100% populated and is now 0% is
  drift, not data. Volume that halves is drift, not a slow week.
- **Fail loudly, with the payload.** Log the raw response that broke the parse. A drift
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

Store the raw payload alongside the parsed output. Re-parsing beats re-harvesting.

## 6. The harvester is a living artifact

**Whenever reality changes, the script/skill changes in the same session.** New endpoint,
new pacing, a new challenge type, a new quality trap — it goes into the harvester before
the run is called done. Otherwise the next run rediscovers it from scratch and the
operator has to say it again. *"Trong quá trình lấy data có gì lỗi cần sửa thì cần cập
nhật skill... Đừng để tao nhắc hoài nha."*

Every harvester ships with:

- a **dry-run / small-N mode** to prove the path end-to-end cheaply;
- a **reset + reload** command, so a bad pull can be redone without hand-surgery;
- a note of the last-verified date and the last-known-good response shape.

## 7. Migrations: preserve, don't recreate

Moving records between systems (tickets, users, content) has extra invariants:

- **Preserve identity and history** — original author, original timestamps, the original
  id recorded on the target record for traceability.
- **Timestamps the target overwrites** (a `date_mod` the platform always stamps) need an
  explicit post-pass to restore. Expect this; check it rather than assume it.
- **Suppress notifications.** A migration that emails thousands of users is unrecoverable.
  Disable notification on every write, verify on one record before the bulk run.
- **Dry-run into a scratch instance first**, diff against the source, then run for real.
- When the operator can grant DB access, **prefer generating a reviewable script over
  performing hidden writes** — reversibility beats speed.

## 8. A second sync must not clobber a human edit

The moment a record can be written by both a sync and a person, precedence is a design
decision — and if it is not made explicitly, the next re-sync makes it for you by
overwriting the correction someone was asked to make.

- **Record provenance on every row, from the first writer.** A column saying which path
  produced this value (`source`/`transport`: automated sync, manual edit, import,
  backfill) plus when. Add it before the second writer exists, and stamp it in *every*
  writer — a one-off script that leaves it NULL makes its rows indistinguishable from
  pre-column history, permanently.
- **State the precedence rule and enforce it in the writer.** Usually: a human edit wins
  until the upstream value changes again, or wins outright. Either is defensible; silence
  is not. Full re-syncs and reprocessing runs obey the same rule as incremental ones —
  "resync" is where this breaks.
- **Make the sync's write conditional, not wholesale.** Update only fields the sync owns,
  and only when the row is not human-owned; never `DELETE`-then-`INSERT` a table that
  carries human edits.
- **Show the origin in the UI** where the value can be edited, so the operator knows
  whether what they are looking at will survive the night.

## Companions

`agent-orchestration` §4 — the plan-file/resume discipline this shares.
`metric-integrity` — what happens downstream if harvested numbers are wrong.
`demo-data-craft` — when the requirement is fabricated data, not harvested data.
