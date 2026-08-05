# ART-001A Article Category Governance Design

**Date:** 2026-08-05  
**Repository:** `mmdc-v3`  
**Task:** ART-001A — Establish Article Category governance  
**Status:** Approved for implementation planning

## Purpose

Establish the Payload CMS data and governance foundation for root Article Categories and one direct-child Subcategory level. The work supports later Article authoring without implementing Article records or any public Category archive behavior.

ART-001A owns the authoring model, validation, redirect-history persistence, migration, generated types, fixtures, and automated tests. ART-001B remains responsible for public archive routes, redirect resolution, archive qualification, Article counts, pagination, navigation, SEO, and sitemap behavior.

## Confirmed decisions

- Payload `_status` provides the only editorial states: `draft` and `published`. No additional archive-approval state is added.
- Draft records may omit archive-governance fields. Publishing an active record requires the complete governance set.
- `owner` relates to the existing `users` collection. It records accountability and does not grant exclusive editing permission.
- All authenticated Payload editors may see Article Categories and their owners. The public API does not expose the collection in this ticket.
- The archive onward-path contract recognizes `programs`, `pathfinder`, `qualified_taxonomy`, and `offering` as the complete governed intent set. Only `programs` and `pathfinder` are selectable now because they need no target collection.
- ART-001A does not create Offering, Goal, Skill, Career Role, Topic, Article, or other deferred collections. It adds no temporary onward target field.
- Published path changes are recorded in a minimal shared redirect registry. HTTP redirect handling remains deferred.
- Validation is implemented as small domain functions connected through thin Payload hooks. A separate persistence service is unnecessary because Payload Admin, REST, GraphQL, and Local API writes must all pass through collection hooks.

## Collection design

### Article Categories

Add the `article-categories` Payload collection with versioning and drafts enabled.

| Field | Shape and rule |
| --- | --- |
| `code` | Required text, unique, trimmed, immutable after creation. |
| `name` | Required text used as the public name and Admin record title. |
| `slug` | Required unique text, normalized to lowercase ASCII kebab case. |
| `landingIntro` | Optional in drafts; trimmed; unique when present; at most 240 Unicode code points. Empty input is stored as absent rather than an empty string. |
| `parent` | Optional single relationship to `article-categories`. No value means a root Category; one root parent means a Subcategory. |
| `displayOrder` | Required non-negative integer used as the governed stable order, with immutable `code` available as the later deterministic tie-breaker. |
| `owner` | Optional while drafting; single relationship to `users`; required to publish an active record. |
| `reviewedAt` | Optional date while drafting; required and current to publish an active record. |
| `reviewDueAt` | Optional date while drafting; required, after `reviewedAt`, and in the future to publish an active record. |
| `archiveOnwardPath` | Optional group while drafting. A published active record requires a complete valid group. |
| `status` | Required select with `active` and `archived`; defaults to `active`. This is separate from Payload `_status`. |

`archiveOnwardPath` contains:

- `heading`: trimmed text of at most 80 Unicode code points;
- `summary`: trimmed text of at most 180 Unicode code points;
- `intent`: a governed select. Admin currently offers only `programs` and `pathfinder`.

A shared intent module documents the complete four-intent contract. `qualified_taxonomy` and `offering` remain unavailable to both Admin and API writes until their canonical target collections are registered. The group stores no raw URL, public action label, image, layout, style, card array, or temporary target.

### Redirect registry

Add a minimal `redirects` Payload collection for automatically recorded path history:

| Field | Shape and rule |
| --- | --- |
| `sourcePath` | Required normalized canonical-origin path; unique. This is the historical path that moved. |
| `destination` | Required relationship to the current Article Category record, not a raw destination URL. |
| `redirectType` | Locked value `permanent`; the later resolver owns the exact HTTP response status. |
| `reason` | Controlled value `slug_change` or `parent_change`. |
| `createdBy` | Relationship to the authenticated user when available. |

Payload supplies creation and update timestamps. Editors may inspect redirect history if needed, but routine create, update, and delete operations are not exposed in Admin. Category hooks create records through the Local API in the originating request context.

Pointing historical sources to the Category identity avoids redirect chains: a future resolver derives the destination from the Category's current canonical path. A unique source constraint prevents competing redirect destinations.

## Architecture and file boundaries

The planned implementation uses these focused units:

- `src/collections/ArticleCategories.ts`: Payload fields, Admin configuration, access, drafts, and hooks.
- `src/collections/Redirects.ts`: redirect-history schema and restricted access.
- `src/lib/article-categories/validation.ts`: pure value, publication, date, lifecycle, immutability, and hierarchy rules.
- `src/lib/article-categories/hooks.ts`: Payload hook adapters and related-record lookups.
- `src/lib/article-categories/paths.ts`: canonical root/Subcategory path derivation and historical-path comparison.
- `src/lib/article-categories/archiveOnwardPath.ts`: complete intent contract and currently available intents.
- `src/test/fixtures/articleCategories.ts`: reusable synthetic Category inputs for this ticket and later Article tests.

The collection configuration stays declarative. Validation functions accept explicit values and loaded relationship facts so most rules can be tested without booting Payload. Hooks own database reads and translate failures into clear Payload validation errors.

## Validation behavior

### Identity and value validation

- The database and Payload field configuration enforce unique `code`, `slug`, and non-empty `landingIntro` values.
- Update hooks compare `code` with the persisted original and reject any change.
- Slugs accept lowercase ASCII letters and digits separated by single hyphens. Leading, trailing, duplicate, or uppercase separators are rejected after normalization rules are applied consistently.
- Character limits count Unicode code points with `Array.from(value).length`, not UTF-16 code units.
- Display order must be a whole number greater than or equal to zero.

### Hierarchy validation

For every parent change, hooks load only the candidate parent and any direct children needed to prove the two-level invariant.

- A root Category has no parent.
- A Subcategory has exactly one parent, and that parent must itself have no parent.
- A Category cannot select itself.
- A root with existing children cannot become a Subcategory because doing so would create a third level.
- Reparenting a Subcategory is allowed only to another root.

These rules reject self-parenting, cycles, and all third-level nesting regardless of whether the write comes from Admin, REST, GraphQL, or Local API. Parent picker filtering improves Admin usability but is never the sole enforcement mechanism.

### Draft, publication, and lifecycle validation

Core identity fields remain required for a usable draft, but drafts may omit `landingIntro`, `owner`, review dates, and `archiveOnwardPath`.

Publishing an active Category requires:

- a non-empty unique `landingIntro`;
- a valid `owner` relationship;
- `reviewedAt` no later than the current time;
- `reviewDueAt` later than `reviewedAt` and later than the current time;
- a complete onward heading, summary, and currently available intent.

An archived record remains stored for history and relationships. Editors can archive an existing record even if its review is overdue; archiving does not force a fake review-date extension. Routine Category deletion is denied so lifecycle changes use `archived` instead.

## Redirect data flow

Redirects are created only for paths that were actually published. Draft-only slug and parent experiments create no redirect.

On a publish or update, the hooks compare the last published Category version with the newly published canonical path:

1. Derive the previous published root or Subcategory path.
2. Derive the new path from the new slug and current root relationship.
3. If the paths differ, create a permanent redirect record from the old path to the Category identity.
4. When a published root slug changes, repeat the comparison for each direct child that has a published version because each child's archive path also moves.
5. Reject a new canonical path that conflicts with another record's canonical path or with a redirect owned by another Category.
6. If a Category returns to one of its own historical paths, remove that now-obsolete source redirect in the same request and create a redirect from the path that just moved. For example, moving `a` to `b` records `a`; moving back to `a` removes that redirect and records `b`.

Changing a Category parent never queries, stores, or mutates an Article URL. Article canonical identity is outside this collection and outside ART-001A.

## Payload Admin and access

- Use `name` as the Admin title.
- Use clear singular and plural labels: `Article Category` and `Article Categories`.
- Show `code`, `name`, `parent`, `status`, `_status`, and `updatedAt` in the default list columns.
- Group fields so identity, hierarchy, archive governance, and lifecycle are understandable to editors.
- Add concise descriptions explaining immutable code, root versus Subcategory selection, owner accountability, review dates, and the onward path.
- Filter the parent relationship picker to root Categories and exclude the current record where Payload context permits. Server hooks remain authoritative.
- Authenticated users may create, read, and update Categories. Routine delete is denied.
- Redirect records are system-managed and are not ordinary editor-authored content.

Fine-grained roles, owner-only editing, public API access, and public rendering permissions are not introduced by this ticket.

## Fixtures and tests

Reusable synthetic fixtures cover:

- an incomplete draft root;
- a valid published root;
- a valid published direct-child Subcategory;
- an archived Category;
- deterministic unique codes, slugs, names, introductions, owners, dates, and display orders.

Tests follow TDD and are divided by responsibility:

1. Unit tests cover Unicode boundaries, slug rules, display order, date ordering/currentness, required publication fields, onward intent availability, code immutability, and pure hierarchy decisions.
2. Collection-configuration tests cover labels, list columns, drafts/versioning, relationship configuration, parent picker filtering, and available onward options.
3. Payload/PostgreSQL integration tests cover root and Subcategory creation, self-parent rejection, cycle rejection, third-level rejection, a root-with-children reparent rejection, unique indexes, incomplete draft saves, valid publication, invalid publication, archival of overdue records, deletion denial, redirect creation, child redirects after a root rename, and draft-only changes producing no redirects.
4. A regression assertion verifies Category parent and slug operations do not read or update Article records. Since ART-001A registers no Article collection, no Article URL field or mutation path can be introduced.

Integration fixtures use isolated unique identifiers and remove only their own records. Tests run against the repository's PostgreSQL-backed CI environment after migrations are applied.

## Migration and generated artifacts

After the collection definitions and tests are in place:

1. Register `ArticleCategories` and `Redirects` in `src/payload.config.ts`.
2. Run `pnpm generate:types` and commit the generated `src/payload-types.ts` changes without manual edits.
3. Run `pnpm migrate:create -- establish-article-category-governance`.
4. Commit the generated TypeScript migration and schema snapshot under `src/migrations/` and register the migration in `src/migrations/index.ts`.
5. Inspect the generated unique indexes, relationships, version tables, foreign keys, and down migration.
6. On a disposable PostgreSQL database, verify migrate up, down, and up again.

The migration is structurally reversible. Shared and production data is not used for migration verification.

## Verification gates

The implementation is complete only when:

- focused unit and integration tests pass;
- `pnpm generate:types` leaves no uncommitted generated-type drift;
- `pnpm format` and `pnpm check` pass;
- `pnpm build` passes;
- the migration succeeds on an empty database and its down/up cycle is verified on a disposable database;
- `git diff` contains only intentional ART-001A files and preserves all pre-existing user-owned work;
- no public archive route, Article model, Article preview, eligible-Article count, pagination, navigation link, SEO metadata, redirect resolver, or sitemap entry appears in the diff.

## Explicitly deferred

- Article records, ArticleBody, Article URLs, Article eligibility, and author models.
- Public Category and Subcategory routes or rendering.
- Archive Article membership, the three-eligible-Article gate, counts, pagination, child navigation, and onward-path rendering.
- Redirect HTTP resolution, canonical tags, sitemap changes, and internal-link updates.
- Offering and taxonomy collections and their onward target relationships.
- Public preview, search indexing, navigation, analytics, and SEO.
