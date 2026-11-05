---
name: tenant-scope-integrity
description: Make active scope — organisation, tenant, workspace, brand, project, store — a hard precondition for every write, persisted UI state, and visible on screen. Prevents cross-scope uploads/connectors/bulk deletes, silent picker resets, and treating no selection as "all" on destructive paths. Use for multi-tenant/workspace/brand features, especially imports, connectors, bulk actions/deletes, or "sai brand", "nhầm org", "data của khách khác", "wrong tenant", "it reset to default", "scope".
---

# Tenant-Scope Integrity

Scope constrains writes, visible state and available capabilities. `metric-integrity`
covers read-query filters; `secure-code-audit` covers authorization vulnerabilities.

## The five invariants

1. **Every write carries an explicit scope, passed in, never inferred.** The scope on an
   insert, update, delete or upsert comes from the request as a required parameter. Not
   from a session default, not from "the user's first organisation", not from the last
   value a module-level variable happened to hold. A write handler that can run without a
   scope argument will eventually run without one.
2. **No scope selected is a defined state, and it is never "all" for a write.** Decide and
   document what an unscoped context means: for reads it may legitimately mean an
   aggregate across everything the caller may see; for any write, connector binding, or
   delete it means *refuse*, with a message naming what to select.
3. **A scoped write may only touch rows in that scope.** The scope belongs in the WHERE
   clause of every update and delete and in the values of every insert — enforced at the
   layer closest to the database, not in the caller. Where the database supports it, make
   it structural (row-level security, a scoped connection, a repository that cannot be
   constructed without a scope) so a new call site inherits the guarantee instead of
   re-implementing it.
4. **Deduplication, upsert and "replace existing" keys are scope-prefixed.** This is where
   the cross-tenant overwrite actually happens: a natural key that is unique globally
   instead of per scope (an SKU, an external ID, an email, a slug, a filename) makes one
   tenant's import collide with another's rows. Every uniqueness constraint, upsert
   conflict target and idempotency key in a multi-tenant table includes the scope column.
5. **The selected scope is visible and persisted.** Show it where the work happens, not
   only in a header menu. Persist the operator's choice across navigation, reload and the
   next session, and restore it — a picker that silently returns to a default is how
   someone imports into the wrong tenant while believing otherwise. When the persisted
   scope is no longer permitted, say so and ask; do not fall back to a default silently.

## Where it breaks, in order of frequency

- **Import and upload flows** — the file is chosen inside a scope but the ingest job is
  enqueued without it, or with the *user's* default rather than the *screen's* scope.
  Carry the scope with the job payload and re-validate it in the worker; the job may run
  hours later under a different session.
- **Connectors and integrations** — an external account is bound at the wrong level, so
  one tenant's credentials pull data into another's tables. Bind the connection to the
  scope, and make the sync target a property of the connection rather than of whoever
  triggered it.
- **Background jobs, schedulers, webhooks and retries** — they have no session. Anything
  they touch must derive its scope from the record or the payload, never from ambient
  state. A retried job must resolve to the same scope as the original.
- **Bulk and destructive actions** — "delete all", "replace existing", "re-sync" run over
  whatever the query returns. Confirm against a counted, scope-named preview: *"delete 412
  rows in brand A"*, not "delete all rows".
- **Admin and support surfaces** — impersonation and cross-tenant tooling are exactly the
  code paths where the scope argument is optional. They need it most, plus an audit trail.
- **Caches and derived tables** — a cache key or a materialised aggregate without the
  scope in it serves one tenant's numbers to another. Same rule as uniqueness keys.

## Reviewing an existing surface

For products with organisation types, plans or feature flags, derive navigation,
connector choices and metric catalogues from the same server-enforced capability
policy as execution. Hidden menus alone do not block direct requests or background
jobs. Test an allowed and a denied role/type, then switch scope and reload to catch
stale menus, caches and permissions. Unknown capabilities must not enable features.

Server-side authorization of the requested scope and forged-ID tests: see
`secure-code-audit`. Here, run those same cases through jobs, object-storage keys and
caches.

Enumerate every write path into the scoped tables (route handlers, jobs, scripts,
migrations, seeds, admin tools) and check each for: scope required, scope in the WHERE
clause, scope in the uniqueness key. A script that inserts directly, outside the
application layer, is the usual survivor of this audit — the one-off ingest script written
under time pressure. Where a provenance or routing column was added later, check every writer sets it (see
`resilient-data-harvest` MIGRATION.md).

When the same fix lands at more than one call site, escalate to `bug-class-audits`: write
the rule down and add a mechanical audit that fails on a write to a scoped table without
its scope column.

- Per-scope behaviour is configuration or a registered extension, never per-customer conditionals in core code.

## Output

Report the write paths audited and the verdict per invariant, the uniqueness/upsert keys
checked, the persistence behaviour of the scope selector, and any path left unscoped with
the reason. Where a fix landed at multiple sites, name the rule and the audit that now
enforces it.
