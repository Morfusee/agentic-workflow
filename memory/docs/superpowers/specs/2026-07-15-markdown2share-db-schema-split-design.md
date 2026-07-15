# Markdown2Share Database Schema Split Design

**Date:** 2026-07-15

**Repository:** `$HOME/Documents/Programming/markdown2share`

## Context

`nextjs/lib/db/schema.ts` currently contains all Drizzle table definitions and
all Drizzle relations for authentication, markdown content, permissions, OAuth,
and audit logging. The file is 706 lines long, which makes individual domains
hard to inspect and increases the cost of changing one area safely.

The local MIHC repository provides the desired structural precedent: a
`schema/` directory with focused table modules, a separate `relations.ts`, and
an `index.ts` that re-exports the complete schema.

## Goal

Split the database schema into focused domain modules that are easier to read
and maintain while preserving the current database structure, exported table
names, import paths, and runtime behavior.

## Design

Create `$HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/` with
the following modules:

| File | Responsibility | Tables |
| --- | --- | --- |
| `auth.ts` | Better Auth persistence | `users`, `sessions`, `accounts`, `verifications` |
| `collections.ts` | Collection hierarchy | `collections` |
| `documents.ts` | Markdown documents and revisions | `documents`, `documentRevisions` |
| `permissions.ts` | Roles and scoped resource permissions | `roles`, `resourcePermissionRequirements`, `userRoles`, `userRoleRevocations` |
| `oauth.ts` | OAuth provider persistence | `oauthClients`, `oauthRefreshTokens`, `oauthAccessTokens`, `oauthConsents` |
| `audit-log.ts` | Authentication and resource audit records | `auditLog` |
| `relations.ts` | All Drizzle relation declarations | Existing relation exports, unchanged |
| `index.ts` | Public schema entrypoint | Re-exports every table and relation module |

Domain modules may import table definitions from other domain modules when a
foreign-key callback requires them. Relations remain centralized in
`relations.ts`, matching the MIHC organization and avoiding duplicate relation
definitions across table modules.

The existing `nextjs/lib/db/schema.ts` file will be removed. The new directory
entrypoint will preserve these existing import forms without consumer changes:

```ts
import * as schema from "@/lib/db/schema";
import { documents } from "@/lib/db/schema";
```

Existing exported identifiers, table names, column definitions, indexes,
constraints, foreign-key behavior, and relation names will remain unchanged.

## Drizzle configuration

Update `nextjs/drizzle.config.ts` to point Drizzle Kit at the split schema
modules using the MIHC-style glob:

```ts
schema: "./lib/db/schema/*.ts",
```

The Drizzle client and seed imports will continue to resolve `./schema` and
`@/lib/db/schema` through `schema/index.ts`.

## Documentation

Update the stale source-of-truth link in
`nextjs/code-style.md` from `lib/db/schema.ts` to
`lib/db/schema/index.ts`. No product or architecture behavior changes are
introduced.

## Non-goals

- Do not rename exported tables or relations.
- Do not change SQL table names, columns, constraints, indexes, or relations.
- Do not generate or modify database migrations.
- Do not change database client behavior or consumer imports.
- Do not refactor unrelated authentication, markdown, or permission code.

## Validation

1. Run `pnpm lint` from `nextjs/` to verify all TypeScript imports and schema
   types.
2. Run `pnpm db:generate` in a disposable validation state or inspect its
   output to confirm Drizzle Kit recognizes the split modules without
   producing a schema change.
3. Run the relevant schema/database tests if available, followed by
   `git diff --check`.
4. Confirm the final diff contains only the schema split, Drizzle config,
   and the corrected documentation link, while preserving pre-existing user
   changes elsewhere in the repository.

## Risks and mitigations

The primary risk is a circular or incomplete module import caused by foreign
key callbacks. Keep table definitions in domain modules, use the existing
`AnyPgColumn` annotations for cross-module/self-referential callbacks where
needed, and let `relations.ts` import all domain modules after they are
defined. TypeScript compilation and Drizzle Kit schema discovery provide
coverage for missing or incorrectly exported tables.
