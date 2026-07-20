# markdown2share — Service Layer Review

**Date:** 2026-07-20
**Source repo:** markdown2share (`nextjs/features/*/services`)
**Scope:** `collections.service.ts`, `document-drafts.service.ts`, `document-publishing.service.ts`, `document-sharing.service.ts`, `library.service.ts` (+ direct collaborators)

---

# Service Layer Review — `features/*/services`

## Verdict up front

Your instinct is right, but the two biggest problems aren't naming — they're:

1. **App-side work the database should do** (N+1 breadcrumb loop, JS merge-sort of two half-result-sets, `max()+1` revision numbering with a race window).
2. **Names that describe one caller instead of the function** (`findCollectionForBreadcrumb` is the worst offender — it's used by four different flows, none of which are "finding for a breadcrumb").

Findings are ordered by severity within each file. Line numbers included.

---

## 1. `collections.service.ts`

### 1a. `findCollectionForBreadcrumb` — misleading name, wrong home (L24)

This is a generic "fetch collection core fields by id, excluding soft-deleted." Its callers: breadcrumb builder, `createCollection` parent validation, `deleteCollection` permission check, and `createMarkdownDraft` in the documents feature. Three of four callers have nothing to do with breadcrumbs. A reader in `document-drafts.service.ts` sees `findCollectionForBreadcrumb(collectionId)` and reasonably asks "what breadcrumb?"

**Fix:** rename to `findCollectionById` (or `findCollectionSummary` if you want to signal the narrow column set). One-word change, four call sites, big readability win.

### 1b. `createCollectionRecord` vs `createCollection` — split that buys nothing (L64, L167)

- The `Record` suffix signals "raw repository insert" per your own architecture boundary doc — but this function runs a transaction and assigns an owner role. That's business workflow, i.e. service logic wearing a repository name.
- `createCollection` is a 15-line wrapper: validate parent, delegate. The split exists only because tests call `createCollectionRecord` directly.

**Fix:** collapse into one public `createCollection({ name, parentId, userId })`. If tests need a lower-level insert, that's what a `repositories/` module is for — currently this feature has none, and this function is pretending to be one.

### 1c. `getCollectionBreadcrumbsForPath` — N+1 loop, the exact thing you asked to eliminate (L112)

For a path of depth *n* this fires:
- *n* × `findCollectionForBreadcrumb` queries, **plus**
- *n* × `canAccessCollection`, which itself is 4–5 round trips (`findApplicationRole`, `findCollectionScope`, `findHighestResourceRole`/`findHighestAssignedRole`, `findRequiredResourceRole`).

So a 3-deep path ≈ **15 sequential round trips**. You already have the right pattern in this same file — `deleteCollection`'s recursive CTE. The whole chain fetch, ordering, and parent-linkage validation is one query:

```sql
with recursive chain as (
  select id, name, owner_id, parent_id, 0 as depth
  from collections
  where id = $1 and deleted_at is null        -- root of the path
  union all
  select c.id, c.name, c.owner_id, c.parent_id, chain.depth + 1
  from collections c
  join chain on c.parent_id = chain.id        -- or walk down by matching path ids
  where c.deleted_at is null
)
select * from chain order by depth;
```

Walk the known id array with `where id = any($ids)` and verify linkage in JS from *one* result set, or recurse properly. Either way: 1 query for the data. Permission semantics need a product decision (check every node vs. check deepest node only — currently every node), but even keeping per-node checks, the *fetches* collapse.

Secondary nits in this function:
- **L151–154:** `href` is built by `breadcrumbs.map(...).concat(...).join("/")` inside the loop — O(n²) string building. Accumulate an `idPath: string[]` and join once per item.
- **L138:** parent-chain mismatch returns `INVALID_INPUT`. From the caller's perspective a broken/forged path is `NOT_FOUND`. Minor, but it changes what the UI shows.

### 1d. `findFirstOwnedCollection` — dead public API (L41)

Zero call sites anywhere in the repo. Exported, tested-by-nobody, maintained-by-everyone-who-reads-the-file. **Delete it** (confirm with the team first — maybe an in-flight branch uses it).

### 1e. `deleteCollection` — mostly good, two nits (L202)

The recursive CTE doing documents+collections soft-delete in one statement is exactly right — this is the pattern the rest of the codebase should copy. But:

- The final `select count(*) ... as collection_count, document_count` result is **discarded** (L254–256). Either return the counts (`ok({ collectionCount, documentCount })`) or delete the final SELECT and the two `returning id` clauses. Dead computation in SQL is still dead code.
- **L210–223:** returns `err()` from inside a transaction callback. Your own `code-style.md`/AGENTS contract says never return `err()` from a tx callback — throw and convert after rejection. Here no writes precede the returns so nothing can half-commit, but the file then uses *two different error idioms* (throw+catch in `createCollectionRecord`, return-err in `deleteCollection`). Pick one; the contract already picked for you.

### 1f. Micro-nits

- **L1:** top-level `and`, `eq` imports are unused — the `findFirst` callbacks destructure their own. Lint should be catching this.
- **L22:** `CollectionId = Pick<Collection, "id">` — a one-field Pick. `{ id: string }` reads better and doesn't pretend there's more shape.
- **L17:** `CollectionLookup` — vague name; it's the breadcrumb/summary column set. `CollectionSummary`.

---

## 2. `document-drafts.service.ts` — the most over-abstracted file

### 2a. `getEditableMarkdownDraft` / `getViewableMarkdownDraft` — copy-paste twins (L101, L115)

Twelve lines each, differing in exactly one string literal (`"edit"` vs `"view"`). This is abstraction-by-duplication: two public names where one parameterized private function + two thin exports (or one export taking a permission) does the job:

```ts
async function findDraftForUser(
  { documentId, userId }: DraftQuery,
  permission: "edit" | "view",
  db: DbExecutor,
) { /* fetch once, check once, return Result */ }
```

Whether you keep two public names is a taste call; the duplicated body is not.

### 2b. Validation order is backwards everywhere — cheap checks after expensive ones

Repeated pattern across this file and `document-publishing.service.ts`:

- `updateMarkdownDraft` (L152): `!(await documentExists(documentId, db)) || !isUuid(documentId)` — hits the DB **before** the free UUID check, and `documentExists` already returns `false` for non-UUIDs, so the `isUuid` half is unreachable in the failing direction. Just `if (!isUuid(documentId)) return err(NOT_FOUND)` first.
- `deleteMarkdownDraft` (L233–243): `documentExists` (DB) → `canAccessDocument` (4–5 queries) → `isUuid` (free). The `isUuid` at L241 is **provably dead code**: `documentExists` returns `false` for non-UUID input, so execution never reaches L241 with an invalid UUID. Delete it, and reorder survivors: isUuid → exists → permission.

### 2c. Double-fetching the document (L92–98, L152–157)

`documentExists()` fetches the document row. `canAccessDocument()` immediately fetches it again via `findDocumentScope`. That's 2 queries for the same row, and it happens in `getDocumentAccess`, `updateMarkdownDraft`, and `deleteMarkdownDraft`. Fetch the scope once, derive `exists` from it, and pass the row into the permission check (or accept one combined query in the permissions layer). With the permission check's own 4–5 queries, `updateMarkdownDraft` currently burns **~7 round trips before it writes anything**.

### 2d. The revision-publish block — duplicated, racy, and mis-named (L179–219)

Two problems stacked:

1. **It's a verbatim duplicate of `publishDocumentDraft`'s core** (publishing service L93–119): `max(revisionNumber)` → insert revision with `max+1` → update `latestPublishedRevisionId`. Same 25 lines in two files.
2. **`max()+1` in app code is a race.** Two concurrent saves both read max=5, both insert 6 — you get a collision or duplicate depending on constraints. Push it into the database:

```sql
insert into document_revisions (document_id, revision_number, markdown, title_snapshot, published_by_user_id, published_at)
select $1, coalesce(max(revision_number), 0) + 1, $2, $3, $4, now()
from document_revisions
where document_id = $1
returning id;
```

One statement, atomic under the transaction. (A unique constraint on `(document_id, revision_number)` should exist regardless — verify it does.)

3. **Naming:** `updateMarkdownDraft` silently *publishes a new revision* when the doc was previously published. "Update a draft" that publishes is a side effect a reader will not expect. Extract the shared block as `insertNextRevision(tx, ...)` (or one SQL statement as above) and make the branch loud: a comment at minimum, ideally a name like `updateDraftAndRepublish` — though the cleaner fix is the extracted helper used by both call sites.

Also **L180–186 vs L214–219**: the identical return-object literal is built twice. Select `latestPublishedRevisionId is not null` as a boolean `wasPublished` in the RETURNING clause, branch on that, build the result once.

### 2e. `saveMarkdownDraft` — fine façade, loose type (L35, L129)

Dispatching on presence of `documentId` is fine, but the input type is a bag of optionals. Make it a discriminated union so `createMarkdownDraft` stops re-narrowing:

```ts
type SaveMarkdownDraftInput =
  | { documentId: string; markdown: string; title: string; userId: string }
  | { collectionId?: string | null; markdown: string; title: string; userId: string };
```

### 2f. `createMarkdownDraft` — array-returning transaction dance (L281–311)

The tx callback returns the whole `.returning()` array, then the outer code does `const [document] = await db.transaction(...)` and a dead `if (!document)` check (L307 — unreachable, the tx already threw at L299). Return the single row from the callback (`return createdDocument`) and drop both checks. Also **L299** throws a raw `Error` while `updateMarkdownDraft` throws `DocumentError(NOT_FOUND)` for the identical impossible case — inconsistent; per your contract both are "impossible" throws, so align them.

### 2g. Duplicate input-type declarations

`GetMarkdownDraftQuery` (L43) and `DeleteMarkdownDraftInput` (L48) are structurally identical (`{documentId, userId}`), and `PublishDocumentDraftInput` in the publishing service is a third copy of the same shape. One named `DocumentUserInput` (or similar) in `types/` — or inline them all. Three names for one shape is the abstraction smell you were sensing.

---

## 3. `document-publishing.service.ts`

### 3a. `getPublishedDocument` — two queries that are one JOIN (L35–57)

Fetch doc → check `latestPublishedRevisionId` → fetch revision by that id. This is a textbook join:

```ts
db.select({...revisionCols})
  .from(documents)
  .innerJoin(documentRevisions, eq(documentRevisions.id, documents.latestPublishedRevisionId))
  .where(and(eq(documents.id, documentId), isNull(documents.deletedAt)))
```

One round trip, and it deletes the `doc.latestPublishedRevisionId!` non-null assertion (L54) — the `!` only exists because the knowledge "this can't be null" lives across two queries. This is your "use the database" thesis in miniature.

### 3b. `PublishDocumentDraftInput` reused for unpublish (L128–129)

`unpublishDocumentDraft({ ... }: PublishDocumentDraftInput)` — the type name lies about the operation. Rename the shared shape (`DocumentPublishInput` covers both directions) or inline.

### 3c. `unpublishDocumentDraft` silently no-ops on missing/deleted docs (L140)

Every sibling returns `NOT_FOUND` for a missing document; this one updates without `isNull(deletedAt)` in the WHERE and without `.returning()`, so unpublishing a deleted or nonexistent id returns `ok(null)`. Either intentional (say so in a comment) or a hole — add `.returning({ id: documents.id })` and map empty → `NOT_FOUND` for consistency.

### 3d. Permission-before-validation ordering (L72–76, L132–137, L153–158)

Same disease as drafts: `canAccessDocument` (4–5 queries) runs **before** the free `isUuid` check. Cheap guards first, always.

### 3e. The `max+1` race and duplication from §2d

Applies here identically — `publishDocumentDraft` should call the same extracted `insertNextRevision` as the drafts flow.

---

## 4. `document-sharing.service.ts`

### 4a. `hasDocumentPermission` — pure indirection, and not even used consistently (L45–52)

A one-line wrapper around `canAccessDocument` that only narrows the permission union type. It adds a hop for the reader and zero behavior — and then `getDocumentMembers` (L162) bypasses it and calls `canAccessDocument` directly, so it doesn't even deliver consistency. **Delete the wrapper**, call `canAccessDocument` everywhere.

### 4b. `getDocumentMembers` selects a column it throws away (L37, L166–173)

`listDocumentMembers` selects `roleId`, the mapper strips it. Don't select it. Trivial, but it's the "soft on the eyes" thing you asked about — every discarded field is a reader asking "where does roleId get used?" and searching for nothing.

### 4c. Anonymous inline input types repeated 3× (L55–65, L102–110, L122–132)

Your house style names service input types. Three inline object literals with `actorUserId`/`targetUserId` repeated. Name them (`InviteMemberInput`, `RemoveMemberInput`, `ChangeMemberRoleInput`) in `types/sharing.type.ts` next to `MemberInfo`.

### 4d. Possible business-rule hole in `removeUserFromDocument` (L101)

The check is `canAccessDocument(actor, "revoke")` — it validates the *actor*, never the *target*. Nothing stops removing the document **owner's** role. Maybe the policy layer guards this downstream; I couldn't confirm from these files. Flagging, not asserting — verify before changing behavior.

### 4e. Sequential independent lookups (L72–87)

`findUserByEmail` and `findRoleByName` don't depend on each other — `Promise.all` them. Better yet, per your DB-first rule: the upsert can take the role id from a subquery (`insert into user_roles ... select $user, $doc, id from roles where name = $role on conflict ...`), folding the role lookup into the write. The `Promise.all` is the lazy 80% win.

---

## 5. `library.service.ts` — the DB-capabilities poster child

### 5a. `getInfiniteLibraryItems` — merge-sort in JS that SQL does for free (L123–148)

Current flow: two queries each fetching `limit+1`, concat, **sort in JavaScript**, slice. You're shipping 2× the needed rows over the wire and reimplementing `ORDER BY ... LIMIT` in app code. This is one query:

```sql
select * from (
  select 'document' as type, d.id, d.title, null as description,
         case when d.latest_published_revision_id is null then 'draft' else 'published' end as status,
         d.updated_at
  from documents d join user_roles ur on ur.document_id = d.id
  where ur.user_id = $1 and d.deleted_at is null and ...
  union all
  select 'collection', c.id, c.name, c.description, 'collection', c.updated_at
  from collections c join user_roles ur on ur.collection_id = c.id
  where ur.user_id = $1 and c.deleted_at is null and ...
) items
where (updated_at, id) < ($cursorUpdatedAt, $cursorId)   -- keyset pagination, one clause
order by updated_at desc, id desc
limit $limit + 1;
```

Benefits beyond elegance:
- One cursor clause instead of `getDocumentLibraryCursorClause`/`getCollectionLibraryCursorClause` twins in `library.helpers.ts` (which are themselves copy-paste differing only in table reference — a `(updated_at, id) < (...)` tuple comparison makes both obsolete).
- `compareLibraryItemsByUpdatedAtAndId` becomes dead code.
- `hasMore` falls out of `rows.length > limit` exactly as now.

Correctness note: the current JS merge is actually *correct* (each side pre-sorted with limit+1 guarantees the merged top-N), so this is a simplification/efficiency rewrite, not a bug fix. Don't oversell it as one.

### 5b. Inconsistent where-clause construction (L54–68 vs L87–105)

`listDocumentLibraryRows` builds its where with a nested ternary expression; `listCollectionLibraryRows` pushes into a mutable `SQL[]`. Same file, same job, two styles. If you take 5a this evaporates; otherwise standardize on the clauses-array (it reads top-to-bottom).

### 5c. Unused imports (L1)

`lt` and `or` are imported but unused in this file (they're used in the helpers). Lint catch.

### 5d. Naming nits

- `getInfiniteLibraryItems` — "Infinite" describes one UI consumer (infinite scroll). Industry-standard for what this returns is cursor pagination: `listLibraryItemsPage` or `paginateLibraryItems`. Low priority, but it matches your `findCollectionForBreadcrumb` complaint — functions named after their caller.
- `InfiniteLibraryItemsResult.limit` (L42) — echoes back what the caller passed in. Unless a consumer needs it, drop it. (Grep says check `queries/` consumers before removing.)

### 5e. `normalizePage` in `library.helpers.ts` — dead code with a live test (helpers L16)

No production caller; only its own unit test references it. A test testing dead code is worse than no test — it signals the function matters. Delete both, or wire up the paginated (non-infinite) query type that `PaginatedLibraryQuery` clearly anticipated... which is itself currently unused. YAGNI: delete all three, re-add when the UI needs offset pagination.

### 5f. Possible duplicate rows via `userRoles` join

If a user can hold multiple roles on one document (e.g. an editor role and a viewer role row simultaneously), the join in `listDocumentLibraryRows` produces duplicate items. Verify a unique constraint on `(user_id, document_id)` exists in the schema; if not, add `distinct` — or better, the constraint.

---

## Cross-cutting summary

| Smell | Where | Fix |
|---|---|---|
| Function named after one caller | `findCollectionForBreadcrumb`, `getInfiniteLibraryItems` | Rename to what it does |
| N+1 / loops over queries | breadcrumbs (≈15 round trips @ depth 3) | Recursive CTE (pattern already in `deleteCollection`) |
| JS merge-sort over two partial sets | `getInfiniteLibraryItems` | `UNION ALL` + keyset `LIMIT` |
| `max()+1` race, duplicated ×2 | drafts L188, publishing L95 | Single `insert ... select coalesce(max,0)+1`, extracted once |
| Copy-paste function pairs | editable/viewable drafts; cursor-clause helpers | Parameterize the one differing value |
| Dead code | `findFirstOwnedCollection`, `normalizePage`, `roleId` select, `isUuid` at drafts L241, discarded CTE counts | Delete |
| Cheap checks after expensive ones | isUuid after permission/exists checks, 5 places | Guard order: free → DB → permission |
| Double-fetch same row | `documentExists` + `canAccessDocument` | Fetch scope once, reuse |
| One-line indirection wrapper | `hasDocumentPermission` | Inline it |
| Two error idioms in tx callbacks | collections throw+catch vs return-err | Contract says throw; align |

**What NOT to touch:** the `deleteCollection` recursive CTE approach (exemplary), the `Result`/error-code discipline (consistent with your contract), the `DbExecutor` parameter threading (enables the transaction composition you're already doing).

**Suggested execution order** (risk-ascending): 1) deletions + renames + import cleanup, 2) guard-order fixes, 3) extract `insertNextRevision` with the atomic SQL, 4) `getPublishedDocument` join, 5) breadcrumbs CTE, 6) library UNION ALL. Items 1–3 are small mechanical diffs; 5–6 deserve their own PRs with the existing integration tests as the safety net.
