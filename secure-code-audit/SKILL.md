---
name: secure-code-audit
description: Portable application-security audit using open-source tooling — OWASP Top 10 code review, secret scanning, dependency/CVE audit, and insecure-default detection. Use when the user asks for a "security scan/review/audit", before making a repo public or shipping a release, after adding auth/upload/payment/API code, or when handling secrets, user data, or third-party input. Produces severity-ranked findings with concrete fixes. No proprietary or cloud tools required.
---

# Secure Code Audit

A repeatable, vendor-neutral security pass any repo can run locally. Four layers: **secrets**, **dependencies**, **static analysis (SAST)**, and a **manual OWASP review**. Prefer tools already installed; otherwise note the one-line install. Never exfiltrate code to a third-party service without the user's explicit OK — all default tools here run locally.

## 1. Secret scanning (run first — leaked creds are the highest-severity, fastest win)
- Working tree AND full history: `gitleaks detect --no-banner` or `trufflehog git file://. --only-verified`.
- Look for: API keys, tokens, JWTs, private keys, DB/LDAP passwords, cloud creds, `.env` committed by accident.
- If a real secret is found in history: say plainly it must be **rotated** (history rewrite does not unleak it from clones/caches), then offer to scrub history. Add the path to `.gitignore` and commit a `.env.example` instead.

## 2. Dependency / CVE audit
- JS/TS: `npm audit --omit=dev` / `pnpm audit`. Python: `pip-audit`. Go: `govulncheck ./...`. Multi-ecosystem: `osv-scanner -r .`. Containers/images: `trivy fs .` or `trivy image <img>`.
- Triage by reachability and severity — a critical CVE in a transitive, unused path is lower priority than a high in your request path. Pin/upgrade; record anything intentionally deferred with the reason.

## 3. Static analysis (SAST)
- General: `semgrep --config auto` (or `p/owasp-top-ten`, `p/secrets`, framework packs like `p/react`, `p/nextjs`, `p/django`).
- Language linters: `bandit -r .` (Python), `eslint` with `eslint-plugin-security` / `eslint-plugin-no-unsanitized` (JS), `gosec ./...` (Go).
- Tune out false positives with inline ignores + a short justification; don't silence a whole rule globally without saying why.

## 4. Manual OWASP Top 10 review (what tools miss — focus here)
- **A01 Broken Access Control**: every endpoint/server action/route checks authn AND authz server-side; object-level checks (can THIS user touch THIS record — IDOR); admin-only routes gated by role, not just hidden in the UI.
- **A02 Cryptographic Failures**: secrets in env/secret-manager not code; passwords hashed with bcrypt/argon2 (never MD5/SHA1/plain); TLS enforced; no sensitive data in logs/URLs/error messages.
- **A03 Injection**: parameterized queries / ORM (no string-built SQL); no `eval`/shell interpolation of user input; output encoding to stop XSS; `dangerouslySetInnerHTML`/`v-html` only on sanitized content (DOMPurify).
- **A04 Insecure Design**: rate-limiting on auth/expensive endpoints; server-side validation of every input (client validation is UX, not security); sane file-upload limits & type checks.
- **A05 Security Misconfiguration**: debug off in prod; security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy); CORS not `*` with credentials; default/admin creds removed; stack traces not shown to users.
- **A06 Vulnerable Components**: covered by step 2 — keep deps current, drop unmaintained ones.
- **A07 Auth Failures**: session/JWT expiry & rotation; secure+httpOnly+sameSite cookies; no user-enumeration in login/reset; MFA where it matters; OAuth `state` checked.
- **A08 Integrity Failures**: verify integrity of CI/build artifacts & third-party scripts (SRI); no untrusted deserialization.
- **A09 Logging/Monitoring**: security events (auth, access denials) logged WITHOUT logging secrets/PII; logs tamper-evident.
- **A10 SSRF**: server-side fetches of user-supplied URLs are allow-listed and blocked from internal/metadata addresses (169.254.169.254, localhost, RFC1918).

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
Findings table: **severity (Critical/High/Medium/Low) → OWASP/CWE → file:line → impact → fix**. Lead with anything exploitable now (exposed secret, missing authz, injection). Apply the safe fixes; list the ones needing the user's decision. End with the exact commands you ran so the audit is reproducible.
