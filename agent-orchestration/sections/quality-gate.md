## §5. Astra's quality gate

### Evidence before acceptance

Astra owns the final decision after reading the combined diff and relevant
artifacts. Capture the actual command exit status and output; avoid pipelines
that hide failures (or explicitly preserve status). A screenshot proves visible
state, an HTTP status proves reachability, and neither alone proves a complete
user journey. Match evidence to the claim.

Re-run load-bearing checks on the integrated tree. Workers' checks help localize
failures but do not replace integration verification.

For corpus audits, require separate counts for enumerated, parsed and actually
content-reviewed artifacts. A generated queue or truncated tool output is not a
completed semantic review. Resume unread portions before claiming exhaustive coverage.

### Independent review

Use a fresh reviewer for complex or consequential changes. Give it the criteria
and raw artifacts, without the builder's verdict. Select lenses by actual risk:
security for permissions/tenancy/input boundaries, data safety for migrations,
performance for hot paths, and design/accessibility for UI behavior.

Findings require a specific scenario, relevant path/lines, and evidence of failure
or a clearly explained violated invariant. Distinguish confirmed defects,
unverified concerns, and unavailable checks. Confidence scores may prioritize
investigation; they are not calibrated probabilities and never authorize a fix.
Do not discard a potentially severe concern solely because its score is low.

Deduplicate by failure mechanism and affected path. Agreement among models is
supporting evidence, not independent proof when they share assumptions.

### Bounded review and repair

Route fixes to the original builder when useful; Astra may fix them directly
when that is simpler or the worker has failed. Reviewers remain read-only.
After two failed attempts on one check, Astra diagnoses the failure and changes
the approach. Limit review cycles to three before re-planning; do not silently
accept outstanding material defects.

Astra resolves technical disagreements from evidence. Ask the user for a missing
preference or authority, not to arbitrate routine builder/reviewer disputes.

### Stop condition

Finish when acceptance checks pass and material concerns are resolved or honestly
reported as limitations. Expand review only for new evidence, missing coverage,
or explicit exhaustive-audit scope. Do not require repeated empty waves, fixed
reviewer counts, or additional tests based only on diff line count.

Before reporting completion, Astra checks scope alignment, integration behavior,
evidence, remaining risks, and that the actual lead model is known.
If Astra review is unavailable, mark it pending rather than claiming approval.
