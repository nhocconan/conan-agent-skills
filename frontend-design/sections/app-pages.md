# App and dashboard page path

For utilitarian surfaces: dashboards, settings, admin, list/detail, tools. The user is here to
do a job repeatedly; the design serves scanning and acting.

- **No hero.** No marketing eyebrow, tagline or decorative banner. The page title says what
  the page is; the first screen is the work.
- **Hierarchy by job**: the primary answer or action first, filters in one predictable
  place (consistent across pages), secondary detail below or on demand.
- **Density**: tables and KPI rows are compact but breathing; one spacing scale; numbers
  right-aligned, tabular figures, units and period always shown.
- **KPI cards**: few, each answers a question; no card without a number or a state; do not
  give one-sentence content its own section header.
- **Charts**: one idea per chart, labelled, no collisions with legends, honest axes; use the
  project's chart package and theme.
- **Tables/lists**: pagination, search, filters, empty/loading/error states per
  `admin-crud-standards`.
- **Consistency over novelty**: same component, same padding, same placement across pages.
  Spend boldness only where it helps comprehension.
- **Copy**: user's vocabulary, sentence case, a verb on every action, the same name for an
  action through the whole flow, errors say what happened and how to fix it.
- **Numbers must be right**: any displayed metric goes through `metric-integrity`.
- Verify by operating it (filters, pickers, popovers), at 375px and in both themes.
