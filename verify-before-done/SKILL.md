---
name: verify-before-done
description: Mandatory self-QA before claiming any web-app task is done. Use whenever finishing a feature, fix, or UI change in any web project — start the dev server, walk the changed pages in a real browser, run the production build, and only report done with evidence. Trigger on "test it", "make sure it works", "đảm bảo ngon lành", or before any "done" claim.
---

# Verify Before Done

Iron rule: **never claim a task is done without running the app and seeing the change work.** Compiling, type-checking, or "the code looks correct" is NOT verification. The user has been burned dozens of times by untested "done" claims and will check personally — every bug they find that you should have found destroys trust.

## Procedure

1. **Start the environment**
   - Use the project's `scripts/start-dev.sh` if present. It must return control to the terminal (background the servers). If start-dev is broken, fixing it IS part of the task.
   - Each project has its own port block (e.g. LMS=3940x, chatbot=3950x, ECI=3960x, REDACTED_INTERNAL=3000). Check existing scripts/docker-compose before assuming.

2. **Walk every changed page in a real browser** (browse/playwright skill)
   - Visit each affected URL as the actual user role (admin AND normal user if both touched).
   - Click through the full flow, not just load the page. Submit forms, upload the sample file, run the filter.
   - Take screenshots at each step; check the browser console and server logs for errors.

3. **The recurring-bug checklist** (these exact bugs shipped repeatedly — check them every time)
   - Dark mode AND light mode: no text/legend/chart-series blending into the background.
   - Filters (marketplace, date, category) must update EVERY chart/table/number below them, not just some.
   - Date pickers: month navigation, week spanning two months, "last week" = full Mon–Sun, persisted date range survives page navigation (cookie/URL).
   - Date-only data: never display `00:00:00`; timezone must follow bot/org locale, never hard-coded.
   - i18n: switching language updates ALL visible strings; progress/state is preserved across the switch.
   - Lists: pagination present and consistent (same items-per-page everywhere), empty/zero rows not rendered as junk.
   - Layout: no overflowing text, broken alignment, leftover blank space between sections, two-line buttons.
   - Error messages must be VISIBLE to the user — a blocked action with a hidden message is a bug.

4. **Build like production**
   - Run the production build (`pnpm build` / `next build` / the prod Dockerfile target). Type errors that only surface in prod builds have broken deploys repeatedly.
   - If schema changed, confirm migrations run cleanly on a copy of real data, not just an empty DB.

5. **Report with evidence**
   - State exactly what was tested, at which URLs, with which accounts, and attach screenshots.
   - If anything was NOT tested, say so explicitly — never imply full coverage.
   - If tests fail, report the failure honestly; never claim done with known issues.

## Related
For list/CRUD pages also run the checklist in `admin-crud-standards`. For prod deployment readiness use `prod-deploy-docker`.
