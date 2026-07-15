# Markdown2Share Database Schema Split Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) to implement this plan task-by-task with review checkpoints.

**Goal:** Split the monolithic Drizzle schema into readable domain modules without changing exported identifiers, database structure, consumer imports, or runtime behavior.

**Architecture:** Replace nextjs/lib/db/schema.ts with nextjs/lib/db/schema/. Keep table declarations grouped by domain, centralize all Drizzle relations in relations.ts, and expose the complete existing schema through index.ts. Configure Drizzle Kit to discover the module files with the MIHC-style glob while preserving @/lib/db/schema and ./schema import resolution.

**Tech Stack:** TypeScript 5, Drizzle ORM 0.45, Drizzle Kit 0.31, PostgreSQL, Next.js 16, pnpm.

---

### Task 1: Extract domain table declarations

**Files:**

- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/auth.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/collections.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/documents.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/permissions.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/oauth.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/audit-log.ts
- Source: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema.ts

- [ ] Step 1: Create the auth module with the existing table definitions

Create auth.ts with the Drizzle imports needed by users, sessions, accounts, and verifications. Move the existing declarations from schema.ts:16-116 unchanged. The module must export exactly users, sessions, accounts, and verifications. Do not rewrite any table body, column, index, default, or constraint.

- [ ] Step 2: Create the collection module

Create collections.ts with the existing collections declaration from schema.ts:118-144. Use the existing AnyPgColumn annotation for the self-referencing parentId callback and import users from ./auth:

~~~ts
import type { AnyPgColumn } from "drizzle-orm/pg-core";
import { index, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

import { users } from "./auth";
~~~

Export collections with its current table name, foreign keys, indexes, and updated timestamp behavior unchanged.

- [ ] Step 3: Create the document module

Create documents.ts with the existing documents and documentRevisions declarations from schema.ts:146-229. Import the dependencies used by their foreign-key callbacks:

~~~ts
import type { AnyPgColumn } from "drizzle-orm/pg-core";
import {
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";

import { collections } from "./collections";
import { oauthClients } from "./oauth";
import { users } from "./auth";
~~~

Keep both document tables in one module so the existing references between documents.latestPublishedRevisionId and documentRevisions remain local and do not introduce a new cross-file cycle.

- [ ] Step 4: Create the permissions module

Create permissions.ts with the existing declarations from schema.ts:231-345: roles, resourcePermissionRequirements, userRoles, and userRoleRevocations. Use the existing check and sql expressions exactly as written, and import the referenced tables:

~~~ts
import { sql } from "drizzle-orm";
import {
  check,
  index,
  integer,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core";

import { collections } from "./collections";
import { documents } from "./documents";
import { users } from "./auth";
~~~

- [ ] Step 5: Create the OAuth module

Create oauth.ts with the existing declarations from schema.ts:347-455: oauthClients, oauthRefreshTokens, oauthAccessTokens, and oauthConsents. Import users and sessions from ./auth; keep all OAuth column names, foreign keys, indexes, and nullable/default behavior unchanged.

- [ ] Step 6: Create the audit-log module

Create audit-log.ts with the existing auditLog declaration from schema.ts:457-482. Import users from ./auth and oauthClients from ./oauth; preserve the existing actor foreign keys and indexes exactly.

- [ ] Step 7: Verify the table export inventory before moving relations

Run from the repository root:

~~~powershell
rg -n "^export const" nextjs/lib/db/schema/*.ts
~~~

Expected table exports are exactly:

~~~text
users sessions accounts verifications
collections
documents documentRevisions
roles resourcePermissionRequirements userRoles userRoleRevocations
oauthClients oauthRefreshTokens oauthAccessTokens oauthConsents
auditLog
~~~

No relation declarations should exist in the new domain modules.

### Task 2: Centralize relations and preserve the public schema entrypoint

**Files:**

- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/relations.ts
- Create: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema/index.ts
- Delete: $HOME/Documents/Programming/markdown2share/nextjs/lib/db/schema.ts

- [ ] Step 1: Move all relation declarations into relations.ts

Create relations.ts with the existing relation declarations from schema.ts:484-706, unchanged. Use this import block so every table is loaded from its focused module:

~~~ts
import { relations } from "drizzle-orm";

import { auditLog } from "./audit-log";
import { accounts, sessions, users } from "./auth";
import { collections } from "./collections";
import { documentRevisions, documents } from "./documents";
import {
  oauthAccessTokens,
  oauthClients,
  oauthConsents,
  oauthRefreshTokens,
} from "./oauth";
import {
  resourcePermissionRequirements,
  roles,
  userRoleRevocations,
  userRoles,
} from "./permissions";
~~~

The relation exports must remain exactly: usersRelations, collectionsRelations, documentsRelations, documentRevisionsRelations, rolesRelations, resourcePermissionRequirementsRelations, userRolesRelations, userRoleRevocationsRelations, oauthClientsRelations, oauthRefreshTokensRelations, oauthAccessTokensRelations, oauthConsentsRelations, auditLogRelations, sessionsRelations, and accountsRelations.

- [ ] Step 2: Create the schema index

Create schema/index.ts with only this complete re-export surface:

~~~ts
export * from "./auth";
export * from "./collections";
export * from "./documents";
export * from "./permissions";
export * from "./oauth";
export * from "./audit-log";
export * from "./relations";
~~~

- [ ] Step 3: Remove the monolithic schema file

Delete nextjs/lib/db/schema.ts only after the new modules and index compile as a complete replacement. Do not modify imports in lib/db/index.ts, lib/db/seed.ts, lib/auth/index.ts, or tests; resolution of ./schema and @/lib/db/schema must now select schema/index.ts.

- [ ] Step 4: Verify the public export surface

Run:

~~~powershell
rg -n "lib/db/schema|from .*schema" nextjs --glob '!node_modules/**'
rg -n "^export \*" nextjs/lib/db/schema/index.ts
~~~

Expected: consumer import paths are unchanged, and index.ts re-exports all seven modules in the order shown above.

### Task 3: Update Drizzle discovery and documentation references

**Files:**

- Modify: $HOME/Documents/Programming/markdown2share/nextjs/drizzle.config.ts
- Modify: $HOME/Documents/Programming/markdown2share/nextjs/code-style.md

- [ ] Step 1: Point Drizzle Kit at the schema directory

Change only the schema path in drizzle.config.ts:

~~~ts
export default defineConfig({
  schema: "./lib/db/schema/*.ts",
  out: "./lib/db/migrations",
  dialect: "postgresql",
  dbCredentials: {
    url: databaseUrl,
  },
});
~~~

Preserve the existing dotenv import, database URL check, and all other configuration fields.

- [ ] Step 2: Correct the code-style source-of-truth link

In the source-of-truth table near the end of code-style.md, replace the link to lib/db/schema.ts with a link to lib/db/schema/index.ts. Do not reformat adjacent documentation.

### Task 4: Verify behavior and scope

**Files:**

- Inspect: working-tree diff and existing changed files
- Test: all available TypeScript, unit, and schema-discovery checks

- [ ] Step 1: Run TypeScript validation

From nextjs/, run:

~~~powershell
pnpm lint
~~~

Expected: tsc --noEmit exits successfully with no new schema import or type errors.

- [ ] Step 2: Run the unit suite

From nextjs/, run:

~~~powershell
pnpm test:unit
~~~

Expected: the existing unit suite passes without changes to test behavior.

- [ ] Step 3: Validate Drizzle schema discovery

From nextjs/, run:

~~~powershell
pnpm exec drizzle-kit generate
~~~

Expected: Drizzle Kit loads the split schema without errors. If it creates a new migration, inspect it immediately; the final diff must contain no migration changes because the table definitions are unchanged.

- [ ] Step 4: Check the final diff and preserve user work

From the repository root, run:

~~~powershell
git diff --check
git diff --stat
git status --short
~~~

Expected intentional changes are limited to the new schema modules, deletion of the old schema.ts, drizzle.config.ts, and the single documentation link. The pre-existing modifications to AGENTS.md, markdown actions/errors, permissions.service.ts, and untracked docs/schema files remain present and are not staged or reverted.

