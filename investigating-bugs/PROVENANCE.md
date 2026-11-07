# Historical upstream provenance

## Archived wrap metadata

```yaml
mode: wrap
upstream: gstack
source: github:garrytan/gstack@5862765a20cd751b73e54fe85ffebd9e4da01e30:investigate/SKILL.md
tracking_source: github:garrytan/gstack@main:investigate/SKILL.md
version: 1.0.2
fingerprint: sha256:200b669d7cca41fd5dd38983fbfd87546e66941bb75d74dd33d7d27b19db1337
reviewed: 2026-11-07
```

The local skill formerly wrapped gstack's `investigate` (384 lines at the
accepted source above). This file preserves that wrap's source, tracking source,
revision, fingerprint and overrides as history; it is not an active REF manifest.

## Retirement

By upstream snapshot `6cf00aee9c0fdedc722f35c1f0032c3db9404104`, gstack had
removed `investigate`. Its
[retirement changelog](https://github.com/garrytan/gstack/blob/6cf00aee9c0fdedc722f35c1f0032c3db9404104/changelog.d/capy-gst-1717-retire-investigate.md)
records the retirement and replacement with direct cause checks and focused failing
tests. `investigating-bugs` now owns its diagnosis, pattern probes and proof procedure
locally. It does not read gstack files at runtime or track the removed path for drift.

## Why this exists

The former wrapper preserved Vietnamese triggers
("sao lại lỗi", "lại bị nữa"), reproduction-before-editing, independent proof and
the fix-the-class handoff after upstream shortened its diagnosis procedure.

Adapted from mattpocock/skills (diagnosing-bugs, commit 4ae2317, MIT).

## Retained local overrides

1. preserve reproduction before the fix; isolated diagnostic probes may test hypotheses
2. verify the presupposition first
3. verify by re-deriving, not recognising
4. escalate a repeated shape to bug-class-audits
5. fail-before/pass-after proof for the intended defect (SKILL step 8)

## Former upstream dependencies

- "How to work"
- "Recipes"

The former wrapper also routed to `investigate/sections/` (flake, polluter, race, eval-bisect, blast-radius).
The local diagnosis/proof procedure is self-contained. The accepted source replaces
Phases 1–5 with "How to work", "Recipes" and "Report". Local proof requirements
survive that shortening; Claude hooks, contract helpers and fixed permission thresholds
do not govern this wrapper.

## Accepted source review — 2026-11-07

The accepted source and markdown cache used the commit in `source` as a frozen
compatibility baseline; `tracking_source` checked the moving branch before retirement.
Reviewed entrypoint/section changes against the previous cache; local runtime,
evidence, authority and repository gates take precedence over upstream helpers.
