# Optional model-assisted layer: OpenAI Codex Security

`cs` (npm `@openai/codex-security`, 0.10.0 checked 2026-11-15) sends source to a model
provider. Run it only after the user approves, for this run, the target paths, the
auth source and a budget. Existing credentials are not consent. If any check below
fails, report `AI scan: not run (<reason>)` and finish layers 1–4 anyway.

1. **Preflight.** `cs --version` equals the pin, and `cs login status --json` with
   `OPENAI_API_KEY`/`CODEX_API_KEY` unset reports `"authenticated": true` (an env key alone
   also does). The agent never runs `cs login` or sets a key. cs refuses a group-writable
   state parent (umask 0002): set `CODEX_SECURITY_STATE_DIR` to a 700 dir under a 700
   parent. Show the user the `--dry-run --json` scope, model and limit first (no model call).
2. **Auth decides who pays.** Always pass `--auth` explicitly:
   - `--auth chatgpt` draws on the subscription's Codex allowance, which is shared with
     Codex CLI usage.
   - `--auth api-key` bills API credit.

   Without `--auth`, a non-interactive run prefers `OPENAI_API_KEY` from the environment
   over the stored login.
3. **Scope.** Use one of these forms:
   - repository: `cs scan . --path <src dirs>`, never data, fixtures or private folders;
   - committed changes: `--diff <base>`, which needs a clean checkout;
   - local edits: `--working-tree`.

   `--path` excludes `--diff`/`--working-tree`. Add
   `--max-cost <USD> --fail-on-severity high --json --output-dir <private dir outside the repo> --codex analytics.enabled=false`,
   plus `--knowledge-base <file>` for the project's security policy or threat model.
   `--mode deep` only when the user names it.
4. **Limits are estimates.** In-flight requests can overshoot `--max-cost`.
   `--validate`, `cs validate`, `cs patch` and post-scan prompts are not cost-tracked,
   so each needs its own approval, and none runs unattended.
5. **Exit codes.** `0` completed below the threshold; `1` findings at or above it; `2`
   or a signal exit (130/143) is not run, never clean. That includes a cyber-policy refusal
   (`SCAN_FAILED`, "flagged for possible cybersecurity risk"): the account needs Trusted
   Access for Cyber or Daybreak, the operator's application; never rephrase to get past it.
   Read exclusions in `scan-manifest.json`; a zero-finding report can still skip scope.
6. **Findings are leads.** Add them to the findings table with `source: codex-security`.
   Deduplicate by mechanism and path against secrets, dependency and SAST output. A
   finding counts only after you trace it to `file:line` in the current tree. Model
   agreement is not proof.

Keep cs out of `verify`, hooks, pre-commit and required CI checks. A paid,
nondeterministic scan would make those gates flaky, and their budget would have no
owner. A scheduled workflow needs an explicit policy decision with all of these:
- a pinned action SHA;
- `contents: read` permissions;
- `max-cost`;
- `fail-on-severity: none`;
- no secrets on fork PRs.

Install the CLI globally at an exact version (`npm i -g @openai/codex-security@<ver>`)
after checking its registry signatures, not as a project dependency. As a dependency it
would add about 120 packages to the lockfile and to image inputs, and every audit gate
would then cover that tree.
