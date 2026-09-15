# Skill audit — 2026-09-15

Supersedes the 2026-09-08 audit. Scope: all 32 first-party skill entrypoints, the
orchestration suite's supporting sections, and the validators. This is a source, fact,
and behavior review. It is not a certification of universal performance, nor proof that
any skill works against a live third-party service.

## What changed structurally

**Routing became harness-conditional.** The previous policy named one model as the global
lead. That was wrong for an operator who runs the same library from three CLIs: it told a
Claude or agy session to defer final approval to a model it could not reach. The lead slot
now belongs to whichever provider's harness is running, leads are never substituted across
harnesses, and a session that cannot reach its own lead reports final review as pending.
Per-harness tables, model IDs, prices, retirement dates, effort parameters and subagent
mechanics live only in [routing](agent-orchestration/sections/routing.md).

Files asserting lead ownership fell from 10 to 7
(`git grep -l "final quality" -- '*.md'`, excluding vendored copies); the survivors are the
two routing-relevant frontmatter descriptions and five pointers, not five separate policies. `delegate-run` dropped from 76
to 43 lines by deleting text that restated `agent-orchestration` rather than adding to it.
`agent-orchestration` dropped `§` section numbering entirely; references now use filenames
and heading text, which survive insertion.

## Model facts, verified 2026-09-15

Every ID, price, context limit and retirement date in the routing tables was read from the
vendor's own model or deprecation page on this date, and the three claims that changed a
decision were re-checked independently:

- **No generally available Gemini 3.x Pro reasoning model exists.** Gemini 3.1 Pro has
  been in Preview since 2026-02-19. Every agy role therefore runs a Flash-family model,
  with the lead and builder separated by `thinking_level` rather than by model tier.
- **Claude Code's subagent model precedence changed at CLI 2.1.251** —
  `CLAUDE_CODE_SUBAGENT_MODEL` no longer overrides the per-invocation parameter and
  frontmatter. A configuration written against an older build routes differently than its
  author intended.
- **`spawn_agent` and `fork_turns` are not in OpenAI's published Codex CLI reference.**
  They are attested in the issue tracker and in the installed binary's own tool text. The
  skill now labels them observed behavior rather than documented API.

Concurrency and depth limits, resume primitives, and lane-enforcement keys were read from
the installed Claude Code 2.1.272 and Codex CLI 0.154.0 binaries, not from memory. The
previous claim that the concurrency ceiling "includes the lead slot" was false on both.
The agy definition format comes from published documentation; the installed agy 1.2.3 was
probed only for `agy models`, `agy --help` and one `--model` call during final review, and
no subagent definition was run.

## Corrections to shipped content

| Skill | Defect | Correction |
| --- | --- | --- |
| secure-code-audit | OWASP Top 10 numbered against the 2021 list | Renumbered to Top 10:2025; added the two new categories (A03 Software Supply Chain Failures, A10 Mishandling of Exceptional Conditions); SSRF kept as a check under A01, into which OWASP rolled it |
| appstore-review-guard | Blanket ban on external purchase links | Scoped to storefront: Guideline 3.1.1(a) does not prohibit them on the United States storefront, and entitlements cover specific others |
| appstore-review-guard | Privacy policy scoped to apps with accounts or IAP | 5.1.1(i) requires it for every app, in App Store Connect metadata and within the app |
| appstore-review-guard | No account-deletion coverage anywhere | Added 5.1.1(v): an app supporting account creation must offer deletion inside the app; a support email or web-only form does not satisfy it |
| interactive-course-builder | "44px targets" filed under WCAG 2.2 AA | 24×24 is the 2.5.8 AA minimum; 44px is a house rule, now labelled as one |
| secure-code-audit | `osv-scanner -r .` (v1 form) | v2 subcommand form; the docs do not say whether the bare form still parses, and the skill says so rather than guessing |

Stale counts, uncitable statistics and machine-specific facts were removed or replaced with
measured values carrying their measurement date. Private operator transcripts and dated
project rejections were converted into the rules they illustrate; the rejection ledger keeps
every lesson and drops the identifiers.

## Enforcement

Three rules that existed only as prose are now checked mechanically by
`skill-miner/validate_skills.py`: section citations must resolve to a real heading, model
IDs outside the routing policy must be justified, and house-style banned terms are reported.
`context_budget.py` previously measured only `SKILL.md`, so growth moved into `sections/`
was invisible; on-demand references are now budgeted too. CI gained the two test suites
`AGENTS.md` requires but the workflow never ran.

## Verification and limitations

Structural validation covers frontmatter, reference resolution, cross-reference targets and
context ceilings. It does not establish that a skill produces good output.

Not done: no live store submission, no production deployment, no browser journey, no private
history mining, no real-account restore. `osv-scanner`, `semgrep` and `opengrep` claims are
documentation-verified, not executed. Apple and Google policy pages are living documents —
re-check them at submission rather than trusting this date. Upstream installers still pin a
moving branch (`ref = main`), so this is not a fully pinned supply chain; `refsync.py` still
rewrites `version:` as the wrapper's own revision, and recording the upstream commit remains
an open code change rather than a documentation fix.

The CI additions pass on macOS and have not been observed on ubuntu-latest.

## Maintenance bar

Keep a skill only when it changes a decision the base agent would otherwise get wrong, and
has a distinct trigger boundary. Prefer updating an existing skill to adding a near-duplicate.
On a model release, deprecation, rejected ID, or a retirement date within 90 days, re-verify
against vendor pages and the active schema. Re-read harness concurrency, depth and resume
mechanics after any CLI upgrade — they are build-specific and this audit dates them.
