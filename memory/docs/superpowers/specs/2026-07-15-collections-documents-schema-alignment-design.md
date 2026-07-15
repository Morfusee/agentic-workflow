# Collections and Documents Schema Alignment Design

**Date:** 2026-07-15

**Status:** Approved design; implementation pending spec review

## Goal

Align the collections, documents, and resource-assignment schema with the
queries and workflows already used by the Markdown feature, while keeping
root-level documents as a supported first-class case.

This is development-only work. The database will be dropped and recreated, so
no new Drizzle migration will be generated.

## Context and findings

The current application already supports documents without a collection:

- the new-document route accepts no `collectionId`;
- document creation omits `collectionId` when it is absent;
- the library queries root documents with `isNull(documents.collectionId)`;
- Playwright fixtures insert root documents directly.

The unused `getDefaultCollectionId` helper creates a collection only to give a
root document a parent. That behavior is not needed and conflicts with the
actual data model.

The resource assignment indexes currently include `roleId` in their unique
keys. This permits multiple roles for the same user and resource. The sharing
service compensates by deleting all document assignments before inserting the
new role. Multiple assignments can also duplicate library query rows.

The collections and documents list queries filter active rows, scope by a
parent or collection, and order by `updatedAt` and `id`, but the schema only
provides single-column indexes for those paths.

## Design decisions

### Root documents

`documents.collectionId` remains nullable with no default value.

When a document is created without a collection:

1. the service skips collection lookup and ownership validation;
2. the document is inserted with a null `collectionId`;
3. the document owner receives the direct document role;
4. no collection is created.

The seeded `Default` collection remains because it is intentional demo data.
It is not a fallback parent for runtime root-document creation.

### Schema indexes and constraints

Keep resource names and document titles non-unique because the application
addresses resources by UUID and has no product rule requiring unique names.

Update the schema as follows:

- replace the collection parent lookup index with an active composite index on
  `(parent_id, updated_at, id)`;
- add an active composite document index on
  `(collection_id, updated_at, id)`;
- add an active document ordering index on `(updated_at, id)` for shared
  document listing;
- replace the `user_roles` collection uniqueness rule with `(user_id,
  collection_id)`;
- replace the `user_roles` document uniqueness rule with `(user_id,
  document_id)`.

The resource-scope check remains the authority that exactly one of
`collection_id` and `document_id` is populated. The nullable column in each
unique index is therefore safe: rows of the relevant scope have a non-null
resource identifier, while assignments for the other scope do not conflict.

### Service and action behavior

`collections.service.ts` will remove the unused default collection constant and
`getDefaultCollectionId` function. Existing checks for active resources and
authorization stay in services because they are business rules involving soft
deletion and the current user.

`document-sharing.service.ts` will update an existing document assignment for
the same user and document, or insert one when none exists. The database
unique key remains the final guard against duplicate assignments.

No server action payload or error-boundary contract changes are required.

### Types

Database row and insert types will be exported from the schema modules using
Drizzle `$inferSelect` and `$inferInsert`. Feature types remain focused on
their projections:

- `MarkdownDraft` is a `Pick` of the document select type;
- collection breadcrumbs and library items are `Pick`-based projections of
  the collection select type;
- document library items are `Pick`-based projections of the document select
  type plus their derived literal fields;
- service input types reuse the relevant insert fields and add the actor/user
  fields required by the workflow.

### Seeds

Seed role assignments will use the new user/resource conflict targets.

Seed data will distinguish these cases:

- omitted `collectionName`: use the existing seeded `Default` collection;
- `collectionName: null`: create the document at the root level;
- a string `collectionName`: use that seeded collection.

An explicit root-level seed document will cover the supported null-parent case.
Existing collection-backed demo documents remain unchanged.

## Files in scope

- Modify `nextjs/lib/db/schema/collections.ts`.
- Modify `nextjs/lib/db/schema/documents.ts`.
- Modify `nextjs/lib/db/schema/permissions.ts`.
- Modify `nextjs/features/markdown/services/collections.service.ts`.
- Modify `nextjs/features/markdown/services/document-drafts.service.ts`.
- Modify `nextjs/features/markdown/services/document-library.service.ts` only
  if the new assignment uniqueness removes a duplicate workaround needed by
  the final query shape.
- Modify `nextjs/features/markdown/services/document-sharing.service.ts`.
- Modify `nextjs/features/markdown/types/collection.type.ts`.
- Modify `nextjs/features/markdown/types/markdown.type.ts`.
- Modify `nextjs/lib/db/seed-data.ts`.
- Modify `nextjs/lib/db/seed.ts`.
- Use the existing tests and direct development-database checks for root
  document creation and assignment uniqueness. Do not modify migration-replay
  test setup as part of this change.

Do not add a migration file or modify the existing user-owned migration work.

## Non-goals

- Do not make `collectionId` non-null.
- Do not create a default collection during runtime document creation.
- Do not introduce slugs or name/title uniqueness.
- Do not add repository abstractions or move existing service boundaries.
- Do not redesign collection inheritance or the permission model.
- Do not change the public server-action result contract.

## Validation

Use `pnpm exec drizzle-kit push` against the dropped development database
because no migration is being added. The existing `pnpm db:reset` and
integration setup replay migration files and therefore do not apply these new
indexes; do not use them as schema verification for this change unless the
test database has first been prepared with the current schema through a
separate direct push. Verify:

1. a root document can be created without increasing the user’s collection
   count;
2. a collection-backed document still validates and saves normally;
3. a user cannot accumulate two roles on one document or collection;
4. collection and document library queries return no duplicate resource rows;
5. seed data remains idempotent and includes the explicit root document;
6. `pnpm lint` and the unit test suite pass;
7. the direct-push development database can be seeded successfully;
8. `git diff --check` passes and the final diff contains no migration or
   unrelated changes.

## Risks and rollback

The schema reset removes existing development data by design. If the stricter
resource-assignment indexes expose duplicate rows, the seed/reset path can be
rerun after clearing the database. Runtime behavior can be rolled back by
restoring the schema indexes and the previous sharing upsert logic; no
migration rollback is required because this change is development-only.
