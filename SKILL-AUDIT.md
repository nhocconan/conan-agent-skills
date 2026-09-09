# Skill audit — 2026-09-08

Reviewed all 32 first-party skill entrypoints and the supporting resources involved
in the findings below. The collection is useful as a library, not as a requirement
to load every skill for every task. This is a source and behavior review, not a
certification of universal “SOTA” performance or production safety.

## Model and operating policy

GPT-6 Astra owns planning, architecture, integration, and final output quality.
GPT-5.6 Terra implements scoped work; GPT-5.6 Luna handles simple checked work.
Claude Fable 5.1, Opus 5, Sonnet 5, and Haiku 4.5 can collaborate where supported.
Exact IDs, official sources, freshness checks, and unavailable-model behavior live
in [routing](agent-orchestration/sections/routing.md). Skills do not switch the
current runtime model. A non-Astra session must leave final Astra review pending
unless the user explicitly chooses another lead.

The updated bootstrap template selects Astra for future applications of the profile.
No global configuration, active load-out, or running session was changed by this audit.

## Necessity and boundaries

Core means useful for the general development profile, not automatically invoked.
Conditional skills remain available for their domain. Maintenance skills are used
for explicit setup or maintenance work. No skill was deleted. The headless `core`
profile now contains 12 skills; workstation profiles retain their broader selection.

| Skill | Use | Review result |
| --- | --- | --- |
| agent-orchestration | Core | Canonical Astra ownership, tiered workers, bounded review, actual harness semantics |
| delegate-run | Core | Existing authority persists; proportional delegation and evidence-based handoff |
| senior-operator | Core | Retain evidence and project maps; remove competing model tables and append-only folklore |
| bug-class-audits | Core | Confirm common invariant before broad fixes; scope repairs and test enforcement |
| metric-integrity | Core | Retain formula/filter/timezone checks; proposed business definitions need owner input |
| tenant-scope-integrity | Core | Preserve write scope; check server authorization and forged/cross-tenant IDs |
| dev-env-lifecycle | Core | Track actual owned resources; preserve files when ownership is unclear |
| remote-host-access | Core | Retain layered diagnosis; allow firewall REJECT as a refusal cause; protect management access |
| resilient-data-harvest | Core | Respect access limits, durable checkpoints, manual challenges, restricted payload retention |
| secure-code-audit | Core | Report-only scope; redacted secrets; local scanners can still use the network |
| docs-sync | Core | Follow existing doc format; preserve required historical evidence |
| coding-env-bootstrap | Core / maintenance | Future Astra default; explain install authority and moving-dependency limitations |
| a11y-audit | Conditional UI | Distinguish WCAG requirements, AAA extras, and house conventions; scoped conformance claims |
| admin-crud-standards | Conditional admin UI | Preserve legitimate zero rows; avoid automatic privileged screens/migrations; remove stale version claim |
| anti-slop-review | Conditional prose | Evidence and clarity; style heuristics do not prove truth or AI authorship |
| appstore-review-guard | Conditional mobile release | Correct policy/URL checks, privacy interpretation, and local links; no rejection-rate predictions |
| backtest-integrity | Conditional quant | Annualize sampled returns, not rebalance cadence; remove unsupported survivorship reassurance |
| browsing-web | Conditional browser | User-selected/project-approved available browser; portable optional upstream paths |
| demo-data-craft | Conditional demo | Synthetic-first option; authorization for real clones; no “clean grep proves anonymity” claim |
| design-qa | Conditional visual review | Review-only stays read-only; fixes do not imply commits |
| interactive-course-builder | Conditional education | Keep tested template workflow; centralized model routing; course-specific design conventions |
| investigating-bugs | Conditional diagnosis | Retain evidence-first investigation and scoped delegation |
| mobile-app-playbook | Conditional mobile/game | Retain domain references; centralized Astra ownership; game/stack targets are project-specific |
| reference-parity | Conditional rebuild | Inventory and evidence; agreed parity does not override security, accessibility, or rights |
| shipping-changes | Conditional shipping | Respect repository branches/protections and explicit shipping authority |
| store-screenshots | Conditional store assets | Current Apple slot guidance, supported fallback sizes, honest silent-preview default |
| web-perf-audit | Conditional performance | Distinguish lab evidence from percentile-based field outcomes |
| web-qa | Conditional functional QA | Keep report-only default; remove automatic commits and rigid browser prohibition |
| agent-session-backup | Maintenance | Fix paired transcript export; preserve safe merge; skip transcript symlinks; disclose lossy cwd filter |
| autonomous-loops | Maintenance / recurring work | Discover actual scheduling APIs; monitoring stability differs from failed improvement loops |
| ref-skills | Maintenance | Review/apply distinction, source/version evidence, curated load-out preservation |
| skill-miner | Maintenance | Repo review does not authorize private history mining; raw digests need restricted handling |

## Verification and limitations

Local validation covers frontmatter, resolvable public references, and unchanged
context ceilings. Isolated tests cover installer/load-out behavior, read-only
budget reporting, frontmatter/reference validation, and backup/restore transcript
round trips, no-overwrite, dry-run, and symlink boundaries. Final command results
for this tree: 35 tests pass (7 backup, 12 skill validation/budget, 16 bootstrap),
32 skills validate with zero errors/warnings, all unchanged context ceilings pass,
and the skill-creator validator accepts all 32 entrypoints. `git diff --check`
passes. A separate Astra reviewer approved the scoped changes after reproducing
and rechecking the restore-path defect. These results are not permanent proof of
future runs. Restore guards cover static selected-root/descendant checks, not
adversarial filesystem races or symlink aliases above the selected roots.

No live store submission, production deployment, browser journey, private-history
mining, or real-account restoration was executed. Claude collaborator availability
was documented from official sources, not tested through this OpenAI-only surface.
Historical author attributions and the specialized TTS model remain unchanged.

Upstream installers still include moving branches and `@latest` dependencies;
this audit does not turn them into a fully pinned supply chain. Controlled hosts
should use approved pinned dependencies and disable automatic network installation.
Mobile growth targets, writing conventions, and course layouts are domain guidance,
not universal standards. Refresh vendor policies before each actual submission.

## Maintenance bar

Keep a skill only when it changes useful decisions beyond the base agent and has a
distinct task boundary. Prefer updating an existing skill over adding a near-duplicate.
On model or tool changes, verify official documentation and the active schema, then
exercise representative success, failure, and unavailable-tool scenarios. Structural
validation alone cannot establish output quality. Revisit conditional skills based on
observed project use; do not claim every specialty is necessary for every developer.
