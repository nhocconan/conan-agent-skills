---
name: repo-hygiene-scrub
description: Repo secret/privacy hygiene — proper .gitignore, secret and internal-data scanning, and emergency git-history rewrite when something sensitive was committed. Use when creating a repo, making a repo public, committing reference/customer material, or when secrets/internal files leaked into git.
---

# Repo Hygiene & Scrub

The user has committed HR documents, customer data dumps, and tool artifacts by accident, then needed history rewrites. Prevent first; scrub fast when needed.

## When creating or first committing a repo
1. `.gitignore` by detected stack (node_modules, .next, dist, .env*, *.log) PLUS the user's recurring offenders:
   - `.playwright-mcp/`, `logs/`, `*.log`
   - `private/` (his analysis scratch space — never committed)
   - `refs/` and `*.zip` when they contain customer/HR-provided material (confirm before ignoring if refs are needed by code)
   - backups/, image caches, generated sample data
2. `.env.example` committed at repo root; real `.env` ignored. Demo/seed credentials documented in README only — **never rendered in public login forms**.
3. Commits authored as `Tien Le <nhocconan@gmail.com>`.

## Before making a repo public (full scrub)
- Scan working tree AND full history (`git log -p`, or `gitleaks`/`trufflehog` if available) for: API keys, tokens, passwords, JWTs, LDAP/bind credentials, internal hostnames (`*.local`, internal IPs), employee names/emails, company-internal terms that must be genericized.
- Replace internal terms with demo equivalents consistently (code, docs, seeds, screenshots).
- Verify git author identity on all commits is the user's personal identity.

## Emergency: sensitive content already pushed
1. Confirm scope: which paths, which commits (`git log --oneline --follow -- <path>`).
2. Add the paths to `.gitignore` first.
3. Rewrite: `git filter-repo --path <path> --invert-paths` (preferred) or interactive rebase for a recent single commit.
4. Force-push **only after telling the user exactly what will be rewritten** and getting confirmation; remind them any other clones need re-cloning.
5. Verify: `git log --all -- <path>` returns nothing; re-scan history for the secret string itself (it may exist in other files).
6. If an actual credential leaked, say plainly: rotate it — history rewrite does not unleak it from caches/forks.
