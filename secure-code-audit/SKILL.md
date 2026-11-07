---
name: secure-code-audit
description: >-
  Use when the user asks for a "security scan/review/audit", before making a repo
  public or shipping a release, after adding auth/upload/payment/API code, or when
  handling secrets, user data, or third-party input. Whole-repo application-security
  audit with open-source tools — secret scanning incl. history, dependency CVEs, SAST,
  OWASP Top 10, LLM-feature checks; severity-ranked findings with fixes. For only the
  pending branch diff, use the harness's built-in diff security review (Claude Code:
  /security-review).
---

# Secure Code Audit

For a branch-only audit, use an available harness review tool or inspect the diff and
affected callers directly. Claude's `/security-review` is optional; its absence on
Codex or agy does not prevent the same security checks.

A repeatable, vendor-neutral security pass any repo can run locally. Four layers: **secrets**, **dependencies**, **static analysis (SAST)**, and a **manual OWASP review**. Prefer tools already installed; otherwise note the one-line install. Never exfiltrate code to a third-party service without the user's explicit OK — local execution does not imply zero network access. Inspect scanner telemetry, rule downloads, and credential-verification behavior. Keep secret values redacted.

## 1. Secret scanning (run first — leaked creds are the highest-severity, fastest win)
- Working tree AND all available refs: `gitleaks git --redact --log-opts="--all" .` and `gitleaks dir --redact .` ([Gitleaks usage](https://github.com/gitleaks/gitleaks#usage)). Record shallow/missing history. TruffleHog needs both `git file://<absolute-repo-path> --no-verification` and `filesystem <repo-path> --no-verification`; its output can contain raw secrets, so capture privately and redact before reporting ([usage](https://github.com/trufflesecurity/trufflehog#usage)).
- Look for: API keys, tokens, JWTs, private keys, DB/LDAP passwords, cloud creds, `.env` committed by accident.
- If a real secret is found in history: say plainly it must be **rotated** (history rewrite does not unleak it from clones/caches), then offer to scrub history. Add the path to `.gitignore` and commit a `.env.example` instead.

## 2. Dependency / CVE audit
- JS/TS: `npm audit` / `pnpm audit` (include build/dev dependencies; use `--omit=dev` only for an explicitly production-only pass). Python: `pip-audit`. Go: `govulncheck ./...`. Multi-ecosystem: `osv-scanner scan source -r .` ([source scanning](https://google.github.io/osv-scanner/usage/scan-source)). Containers/images: `trivy fs .` or `trivy image <img>`.
- Triage by reachability and severity — a critical CVE in a transitive, unused path is lower priority than a high in your request path. Pin/upgrade; record anything intentionally deferred with the reason.

## 3. Static analysis (SAST)
- General: `semgrep scan --config <reviewed-local-rules> --metrics=off` for local rules. Registry packs require network access; `--config auto` also sends the project URL to the registry, even though `--metrics=off` disables usage metrics ([CLI reference](https://docs.semgrep.dev/cli-reference)). Opengrep is an alternative engine; verify the selected engine and rule-pack licenses separately before reuse or redistribution.
- Language linters: `bandit -r .` (Python), `eslint` with `eslint-plugin-security` / `eslint-plugin-no-unsanitized` (JS), `gosec ./...` (Go).
- Tune out false positives with inline ignores + a short justification; don't silence a whole rule globally without saying why.

## 4. Manual OWASP Top 10 review — **the 2025 list** (what tools miss — focus here)
Read `sections/owasp-top-10-2025.md` for the ten categories and what to check in each.
Numbering follows [OWASP Top 10:2025](https://top10.owasp.org/2025);
OWASP renumbers each release, so confirm the list before quoting a category id in a
report. Two categories are new in 2025: **A03 Software
Supply Chain Failures** and **A10 Mishandling of Exceptional Conditions**. SSRF is no
longer standalone — OWASP rolled it into A01; check it there.

## 5. LLM / AI features
If the app calls a model, read `sections/llm-features.md` (OWASP LLM Top 10, 2025 edition).

## File-upload & multi-tenant (common in data apps — check explicitly)
- Validate type by content not just extension; cap size; store outside web root or in object storage with scoped access; scan/disarm where feasible; never trust the client filename for paths (path traversal).
- Multi-tenant: every query is scoped by tenant/org id server-side; no way to read another tenant's rows by changing an id.
- A client-supplied tenant/scope ID is verified server-side against the caller's membership, never trusted. Test with a forged scope ID and a cross-tenant resource ID; check paths that bypass RLS (service-role/admin clients, `SECURITY DEFINER` functions, raw SQL, background jobs).

## Output
Findings table: **severity (Critical/High/Medium/Low) → OWASP/CWE → file:line → impact → fix**. Lead with anything exploitable now (exposed secret, missing authz, injection). For audit-only requests, report findings without edits. Apply scoped fixes only when requested; credential rotation and history rewriting need explicit authority. End with the exact commands you ran so the audit is reproducible.
