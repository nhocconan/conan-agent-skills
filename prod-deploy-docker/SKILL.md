---
name: prod-deploy-docker
description: Production deployment readiness and step-by-step deploy guide for projects running Docker Compose behind Traefik. Use when deploying to production, creating/editing docker-compose.prod.yml, after schema or dependency changes, or when the user asks "how to deploy", "build down up", or reports prod-only failures.
---

# Prod Deploy — Docker Compose

All of the user's production apps run **fully inside Docker Compose behind a Traefik balancer** on a remote Linux host. The user deploys by: `git pull` → `docker compose -f docker-compose.prod.yml build` → `down` → `up -d`. Everything must be ready after exactly that — never instruct host-level commands.

## Conventions
- `docker-compose.prod.yml` lives at the **repo root** and on prod it may be gitignored/customized — **never modify or assume you can change the prod copy**; if local changes are needed, say so explicitly.
- DB runs in a container, not exposed to the host. All scripts/migrations run **inside containers** (`docker compose -f docker-compose.prod.yml run --rm ...`).
- Migrations / `prisma db push` run automatically in the container `CMD` on start — never tell the user to run them manually as a separate step.
- `.env` / `.env.example` at repo root (not inside app/), with a `scripts/` generator for secret values at deploy time. Never bake secrets into images, scripts, or git.

## Pre-deploy checklist (run BEFORE telling the user to deploy)
1. **Prod build passes locally**: build the actual prod images (`docker compose -f docker-compose.prod.yml build` or the Dockerfile prod target). Next.js prod builds catch type errors dev mode hides — this has broken prod repeatedly.
2. **Migrations are additive and safe** against existing prod data. Test against a restored prod backup if available, never only an empty DB.
3. **DATA SAFETY**: start/seed logic must detect existing data and **never re-seed or erase**. Any script that could touch existing prod data needs an explicit `--yes` guard and a backup step first.
4. Verify locale/timezone/currency behavior is config-driven (per bot/org), not hard-coded — prod serves multiple languages.
5. Everything tested per `verify-before-done`.

## Output to the user (every deploy)
Give one copy-pasteable block, e.g.:
```bash
git pull
docker compose -f docker-compose.prod.yml --env-file .env.prod build
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```
Plus, only if needed: one-off container commands (re-index, re-promote, backfill) with exact `run --rm` syntax, and what to verify in the UI afterwards.

## Always state when rebuild is required
If the change touched any of: schema (Prisma/Drizzle), package.json/lockfile, Dockerfile, docker-compose.prod.yml, or scripts referenced by `CMD` — explicitly tell the user: **"Rebuild container trên prod: build → down → up"**. New models WILL throw on prod until rebuilt.
