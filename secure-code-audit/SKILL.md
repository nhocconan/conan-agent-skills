---
name: secure-code-audit
description: Portable application-security audit using open-source tooling — OWASP Top 10 code review, secret scanning, dependency/CVE audit, and insecure-default detection. Use when the user asks for a "security scan/review/audit", before making a repo public or shipping a release, after adding auth/upload/payment/API code, or when handling secrets, user data, or third-party input. Produces severity-ranked findings with concrete fixes. No proprietary or cloud tools required.
---

# Secure Code Audit

A repeatable, vendor-neutral security pass any repo can run locally. Four layers: **secrets**, **dependencies**, **static analysis (SAST)**, and a **manual OWASP review**. Prefer tools already installed; otherwise note the one-line install. Never exfiltrate code to a third-party service without the user's explicit OK — local execution does not imply zero network access. Inspect scanner telemetry, rule downloads, and credential-verification behavior. Keep secret values redacted.

## 1. Secret scanning (run first — leaked creds are the highest-severity, fastest win)
- Working tree AND full history: a redacted gitleaks scan or TruffleHog with credential verification disabled (check installed flags).
- Look for: API keys, tokens, JWTs, private keys, DB/LDAP passwords, cloud creds, `.env` committed by accident.
- If a real secret is found in history: say plainly it must be **rotated** (history rewrite does not unleak it from clones/caches), then offer to scrub history. Add the path to `.gitignore` and commit a `.env.example` instead.

## 2. Dependency / CVE audit
- JS/TS: `npm audit --omit=dev` / `pnpm audit`. Python: `pip-audit`. Go: `govulncheck ./...`. Multi-ecosystem: `osv-scanner scan -r .` (v2 form; v2's migration guide makes `osv-scanner <dir>` a shortcut for `osv-scanner scan source <dir>` and does not document whether the bare v1 `-r` form still parses — use the subcommand). Containers/images: `trivy fs .` or `trivy image <img>`.
- Triage by reachability and severity — a critical CVE in a transitive, unused path is lower priority than a high in your request path. Pin/upgrade; record anything intentionally deferred with the reason.

## 3. Static analysis (SAST)
- General: `semgrep --config auto` (or `p/owasp-top-ten`, `p/secrets`, framework packs like `p/react`, `p/nextjs`, `p/django`). Semgrep's registry rules moved to the Semgrep Rules License v1.0 in December 2024 — not open source: internal use allowed, reuse in a competing product or SaaS is not. **`opengrep`** is a fork of Semgrep CE v1.100.0 under LGPL 2.1 (same rule syntax, SARIF out). Both claims read 2026-09-15 from [docs.semgrep.dev/faq/comparisons/opengrep](https://docs.semgrep.dev/faq/comparisons/opengrep); re-verify there before relying on either.
- Language linters: `bandit -r .` (Python), `eslint` with `eslint-plugin-security` / `eslint-plugin-no-unsanitized` (JS), `gosec ./...` (Go).
- Tune out false positives with inline ignores + a short justification; don't silence a whole rule globally without saying why.

## 4. Manual OWASP Top 10 review — **the 2025 list** (what tools miss — focus here)
Read `sections/owasp-top-10-2025.md` for the ten categories and what to check in each.
Numbering follows [OWASP Top 10:2025](https://top10.owasp.org/2025), verified 2026-09-15;
OWASP renumbers each release, so confirm the list before quoting a category id in a
report. Two categories are new in 2025 and are the ones most often skipped: **A03 Software
Supply Chain Failures** and **A10 Mishandling of Exceptional Conditions**. SSRF is no
longer standalone — OWASP rolled it into A01; check it there.

## 5. LLM / AI features (chatbots, RAG, agents, AI dashboards — check explicitly)
Classic SAST misses these; review manually wherever the app calls a model (OWASP LLM Top 10):
- **Prompt injection**: retrieved documents, user uploads, and third-party content fed to a model are DATA, not instructions — never let them override the system prompt's authority (delimit clearly, instruct the model to treat them as untrusted, strip/flag instruction-like content in RAG chunks).
- **Tool-call authorization**: every tool an LLM can invoke re-checks authn/authz server-side with the END USER's identity — the model must not be able to reach rows/actions the user can't. No raw-SQL or shell tools without strict scoping/allow-listing. Treat tool args like any untrusted input.
- **RAG tenancy**: retrieval queries are scoped by tenant/org id at the store level (filter in the vector/DB query, not post-hoc in the prompt); one tenant's documents must never surface in another's context.
- **Output handling**: model output rendered as text/sanitized markdown — never `dangerouslySetInnerHTML`/`v-html` on it, never `eval`, never auto-clicking links it generates (XSS/markdown-image exfiltration).
- **Secrets & PII**: no credentials or hidden business logic in system prompts (assume prompts leak); don't log full prompts/completions containing user PII; API keys server-side only, never shipped to the client.
- **Denial-of-wallet**: rate-limit + max-token-cap every model endpoint per user/org; cap agent loop iterations; meter and alert on spend.

## File-upload & multi-tenant (common in data apps — check explicitly)
- Validate type by content not just extension; cap size; store outside web root or in object storage with scoped access; scan/disarm where feasible; never trust the client filename for paths (path traversal).
- Multi-tenant: every query is scoped by tenant/org id server-side; no way to read another tenant's rows by changing an id.

## Output
Findings table: **severity (Critical/High/Medium/Low) → OWASP/CWE → file:line → impact → fix**. Lead with anything exploitable now (exposed secret, missing authz, injection). For audit-only requests, report findings without edits. Apply scoped fixes only when requested; credential rotation and history rewriting need explicit authority. End with the exact commands you ran so the audit is reproducible.
