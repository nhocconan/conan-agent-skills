## §4b. Worker modes and return contracts

A brief names a **mode**. The mode is the behavioral contract a worker holds itself to;
it replaces a persona with something checkable. Six modes cover nearly every node
(distilled from the task-mode set shipped in Grok's marketplace, tightened to our gates):

| Mode | The worker will | The worker will not | Stops when |
| --- | --- | --- | --- |
| **investigate** | separate observed symptom from inferred cause; trace inputs, state, ownership; rank hypotheses by evidence and cheap falsification | edit product code until one mechanism explains the evidence | cause + proof are named, or the exact blocker is |
| **build** | derive observable acceptance + explicit non-goals; trace the entry point through the layers that own the invariants; deliver one coherent end-to-end path; reuse the fitting seam | add modes, providers, config, extensibility, polish the acceptance did not ask for; force the work into one file or a local patch | the focused proof passes; reports only material omissions |
| **patch** | reproduce first when cheap; change the narrowest layer that owns the wrong behavior; add only the regression proof relevant to the task | clean up, rename, or abstract outside the fix | the failure is fixed and the regression proof + nearest gate pass |
| **refactor** | define the behavior-preservation boundary and the proof *before* moving anything; move one ownership boundary at a time; keep every intermediate state buildable | mix feature change into the move; grow deps or config | the same proof passes after and the requested structure exists |
| **migrate** | map readers, writers, data shape, compatibility window; define forward *and* rollback; expand → migrate → verify → contract; make retries idempotent | perform a destructive contraction implicitly; run destructive steps without separate authorization (see the repo's data-protection rule) | the requested stage passes |
| **verify** | translate acceptance into the smallest sufficient proof set; run focused checks before wide gates; distinguish pass / fail / unavailable / blocked exactly | edit product code; add polish or unrelated tests once criteria pass | the proof is complete; reports commands, results, unresolved risk |

Put the mode on the first line of the brief (`MODE: patch`). A worker that drifts out of
its mode ("while I was there I also…") has produced a diff the lead must re-scope, which
costs more than the drift saved.

### Return contracts — the shape of what comes back

A subagent's return lands in the lead's context verbatim. Prose from a scout costs the
lead 2,000 tokens per delegation; the same finding in a fixed shape costs 700, and is
greppable. Demand the shape in the brief and reject returns that ignore it.

**Scout** (investigate / survey — read-only):
```
<Header>:
- path:line — `symbol` — note ≤ 12 words
totals: <counts>
```
or `No match.` — file-path first, line attached, symbols backticked.

**Builder** (build / patch / refactor / migrate):
```
<path:line-range> — <change ≤ 10 words>      (one line per file touched)
gate: <cmd> → EXIT=<n>, marker: <the positive marker, verbatim>
unverified: <what could not be checked, and why>   |   assumptions: <…>
```
or a terminal first token: `too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.`
— any of which the lead treats as a re-scope, not a retry.

**Verifier / reviewer** (verify, or any review lens):
```
[P1] Imperative finding title — path/to/file:line  (confidence N/10, lens: security)
  <one paragraph: the affected scenario and why the behavior is wrong>
  quote: `<the verbatim line(s) that motivate the finding>`
…
totals: P0 n · P1 n · P2 n · P3 n
```
or `No findings.` — never an invented finding to fill the page. Priorities: P0 release
blocker · P1 urgent defect · P2 ordinary defect · P3 low-impact but worth fixing. Flag
only what is discrete, actionable, *introduced by the change*, demonstrable from the code,
and something the author would fix if told. Pre-existing problems, intentional behavior
changes, and style nits are not findings. Structured JSON (`TEMPLATES.md` §2) when the
result feeds a merge.

All three drop the compressed shape for plain language on security warnings and
irreversible-action confirmations — ambiguity there is worse than a few tokens.
