---
name: excel-data-reconcile
description: Reconcile system numbers against customer-provided Excel/PPTX business data and formulas (GMV/NMV-style metrics, enrichment mappings). Use when a customer sends raw data files, when system totals don't match the customer's numbers, when extracting business formulas from documents, or when generating sample/derived Excel files.
---

# Excel Data Reconcile

For projects where customers hand over Excel/PPTX/PDF files containing raw data and implicit business formulas (e.g. BLO GMV/NMV, ECI enrichment). Weeks were lost re-litigating formulas and chasing mismatches. This skill prevents that.

## 1. Formula source of truth — FIRST, before any code
- Read **every sheet of every file**, including embedded images in PPTX/PDF (read the images — formulas often only exist in screenshots).
- Extract every formula/filter rule into `docs/FORMULA-REFERENCE.md` with exact citation: file → sheet → column letters → status filter values (verbatim, including Vietnamese diacritics variants).
- Once the user confirms a formula, it is FROZEN. Never re-derive or "correct" it from your own reasoning. If raw data seems to contradict it, report the discrepancy with cell-level evidence and ASK — do not silently change the calculation.
- Name DB columns/variables generically (`nmv`, not `nmv_blo`) — the same system serves other customers later.

## 2. Independent recompute before trusting the system
- Write a standalone script (prefix `claude_`, output into `private/`, never committed) that recomputes the metrics straight from the raw files using the frozen formulas.
- Compare three ways: raw-file recompute vs. system vs. customer's own numbers — **per day, per platform**, not just monthly totals. A matching total can hide offsetting errors.
- For each mismatch report: file, sheet, the specific orders/rows, which side differs, and the most likely formula/filter cause.

## 3. Generating Excel files
- Derived/sample files must have **100% identical column names and data types** as the originals, drawn from real source rows with realistic diversity (not all one marketplace, not synthetic).
- Files must open cleanly in MS Office 365 on Mac — verify no repair prompt. Use proper library options for: data filters (real AutoFilter dropdowns like the customer's files), Vietnamese titles/UTF-8, date cells as dates.
- Add new sheets to a copy; never overwrite the customer's original files. Never commit bulk-generated files.

## 4. Upload/ingest validation
- After implementing an upload path, round-trip test with the actual customer file: upload → check row counts match the file (investigate any "partial success") → spot-check 5+ specific orders end to end against the raw cells.
- Duplicate/overlap handling (re-uploaded days) must upsert safely, never double-count or wipe.

## Cardinal rule
When the user says the numbers are wrong, they almost always are. Investigate from the raw file inward; never defend the system's number without cell-level proof.
