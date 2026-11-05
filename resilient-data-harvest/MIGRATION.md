# Migration and sync precedence

Read from `SKILL.md` when moving records between systems or when a re-sync could overwrite a manual edit.

## Migrations: preserve, don't recreate

Moving records between systems (tickets, users, content) has extra invariants:

- **Preserve identity and history** — original author, original timestamps, the original
  id recorded on the target record for traceability.
- **Timestamps the target overwrites** (a modified-at column the platform always stamps) need an
  explicit post-pass to restore. Expect this; check it rather than assume it.
- **Suppress notifications.** A migration that emails thousands of users is unrecoverable.
  Disable notification on every write, verify on one record before the bulk run.
- **Dry-run into a scratch instance first**, diff against the source, then run for real.
- When the operator can grant DB access, **prefer generating a reviewable script over
  performing hidden writes** — reversibility beats speed.

## A second sync must not clobber a human edit

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
