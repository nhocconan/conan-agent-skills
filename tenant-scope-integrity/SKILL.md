---
name: tenant-scope-integrity
description: Make the active scope — organisation, tenant, workspace, brand, project, store — a hard precondition of every write, a persisted piece of UI state, and a visible fact on screen. Catches the class where data uploaded or connected while "inside" one scope lands in, overwrites, or deletes another's; where a scope picker silently resets to a default after navigation; and where "no scope selected" quietly means "all" on a destructive path. Use when building or reviewing any multi-tenant / multi-workspace / multi-brand feature, especially imports, connectors, bulk actions and deletes, or when the user says "sai brand", "nhầm org", "data của khách khác", "wrong tenant", "it reset to default", "scope".
---

# Tenant-Scope Integrity

In a multi-tenant product, scope is not a filter — it is an argument. Treating it as a
filter produces the worst bug this class has: an import performed "inside" brand A that
replaces brand B's data, discovered by the customer. Reads that leak across scope are a
privacy incident; writes that leak are unrecoverable without a restore.

`metric-integrity` covers whether a scope filter reaches every read query.
`secure-code-audit` covers isolation as an authorisation vulnerability. This skill covers
scope on the **write** path and as **UI state** — the two places both of those miss.

## The five invariants

1. **Every write carries an explicit scope, passed in, never inferred.** The scope on an
   insert, update, delete or upsert comes from the request as a required parameter. Not
   from a session default, not from "the user's first organisation", not from the last
   value a module-level variable happened to hold. A write handler that can run without a
   scope argument will eventually run without one.
2. **No scope selected is a defined state, and it is never "all" for a write.** Decide and
   document what an unscoped context means: for reads it may legitimately mean an
   aggregate across everything the caller may see; for any write, connector binding, or
   delete it means *refuse*, with a message naming what to select. The dangerous default
   is the silent one.
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

Enumerate every write path into the scoped tables (route handlers, jobs, scripts,
migrations, seeds, admin tools) and check each for: scope required, scope in the WHERE
clause, scope in the uniqueness key. A script that inserts directly, outside the
application layer, is the usual survivor of this audit — the one-off ingest script written
under time pressure. Where a column was added later to record provenance or routing, check
that **every** writer sets it; rows left NULL by the writers nobody updated are
indistinguishable from historic rows and will be mis-attributed forever.

When the same fix lands at more than one call site, escalate to `bug-class-audits`: write
the rule down and add a mechanical audit that fails on a write to a scoped table without
its scope column.

## Customisation without forking the core

When one customer's requirement pushes toward scope-specific behaviour, do not branch the
core path. Express the difference as configuration or a registered per-scope extension
loaded by the same code, so the shared path stays single. Per-customer conditionals inside
core logic are how a multi-tenant product becomes several products with one deployment.

## Output

Report the write paths audited and the verdict per invariant, the uniqueness/upsert keys
checked, the persistence behaviour of the scope selector, and any path left unscoped with
the reason. Where a fix landed at multiple sites, name the rule and the audit that now
enforces it.
