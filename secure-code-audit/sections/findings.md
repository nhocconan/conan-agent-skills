# Findings: triage, run record, closing

- **Triage.** A scanner hit becomes a finding only after you trace it to the current code.
  Record dismissed hits with their reason: a test fixture, a documented public dev key that
  production refuses, or an advisory already fixed in the installed build (for example a
  vendor tarball outside the registry). Mark heuristic dismissals that you did not read one
  by one.
- **Run record.** For each layer, record tool and version, scope (refs/paths) and `EXIT=<n>`,
  or `not run: <reason>`. A missing tool is never a clean layer. A scanner's findings exit
  (gitleaks and osv-scanner use 1) is not an execution failure.
- **Severity.** Rank by reachability. A DoS advisory in a dev-only linter fed repository
  globs is Low. Defer it with a reason instead of making an out-of-scope major bump.
- **Closing.** Mark a finding `fixed` only after you re-trace its exploit path, and the
  equivalent paths, on the current tree. Use `fixed | still_vulnerable | inconclusive`.
  "The scanner stopped reporting it" or "tests pass" is not enough.
