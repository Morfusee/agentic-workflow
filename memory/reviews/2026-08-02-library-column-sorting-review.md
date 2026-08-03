# Review: feat/library-column-sorting

Date: 2026-08-02
Overall status: **FAIL**

Scope:
- Branch `feat/library-column-sorting` vs `main` (`git diff main...HEAD`, 3 commits, 14 files).
- Changed files: `docs/plans/2026-08-01-library-column-sorting.md`, `nextjs/code-style.md`, `nextjs/app/globals.css` (cosmetic teal theme tokens), `nextjs/features/library/*` (repositories/library.repository.ts, schemas/library.schema.ts, services/library.service.ts, types/library.type.ts, utils/library.helpers.ts, components/markdown-files-table.tsx, components/markdown-files-table-columns.tsx), tests (library.router.test.ts, library.service.test.ts, markdown-files-table.test.tsx, library.helpers.test.ts).
- Requirements source: `docs/plans/2026-08-01-library-column-sorting.md`.
- Reviewers: requirements-reviewer, thermos (synthesized from thermo-nuclear-review + thermo-nuclear-code-quality-review), react-quality-review.
- Verification run during review: `pnpm typecheck` PASS; `pnpm lint` 0 errors / 24 warnings (pre-existing); unit `markdown-files-table.test.tsx` 3/3 PASS; integration tests not re-run (DB-backed).

## Checks

### requirements-reviewer (overall: PASS, confidence: high)

- Sort keys restricted to `name`/`updated`; meta.sort only on Name and Updated columns.
  status: PASS
  expected: `LibrarySortBy = "name" | "updated"`; sort metadata only on Name and Updated.
  actual: `library.type.ts:6`, `library.schema.ts:3`, columns file: sort meta only on Name (:82) and Updated (:108); Status (:101) and Actions (:129) carry none.
- URL-backed sort state via `useDataTableSort` with `sortableColumns: ["name","updated"]`, defaults `updated`/`desc`.
  status: PASS
  expected: Hook initialized with exact options; sort fed to query input and DataTable provider; `sortable` on Table.
  actual: `markdown-files-table.tsx:41-48` (hook + startTransition), :65-66 (query input), :171/:179 (provider state/actions), :187 (sortable).
- Cursor records sortBy/sortDirection + last row primary value + id; mismatched cursor rejected.
  status: PASS
  expected: Discriminated cursor type/schema; superRefine rejects mismatch; service guards direct callers.
  actual: `library.type.ts:9-21`, `library.schema.ts:6-19,31-44`, `library.service.ts:60-65`; router tests assert BAD_REQUEST + cursor field error.
- PostgreSQL owns cursor comparison and final ordering; no JS comparator.
  status: PASS
  expected: Drizzle operators on aliased union; no localeCompare/Array.sort.
  actual: `unionAll` (`library.repository.ts:16`), keyset clause + order + limit (:237-266); JS comparator deleted from helpers; grep confirms no JS comparator in feature.
- Repository fetches limit+1 globally; service slices and derives nextCursor from last returned row.
  status: PASS
  actual: `library.service.ts:68-86`; `rows.length > limit && lastItem` guard.
- Public invalid values and cursor/order mismatches are Zod BAD_REQUEST; collections keep description, documents do not gain it; internal LibraryRow has nullable description.
  status: PASS
  actual: `toLibraryItem` (`library.service.ts:18-51`); `sql<string|null>`null`` projection (`library.repository.ts:82`); router test asserts shape (:671-677).
- Direct service calls normalize defaults to `updated`/`desc`.
  status: PASS
  actual: `normalizeLibrarySort` (`library.helpers.ts:18-23`); service test asserts `{}` equals explicit updated/desc.
- Name sorting uses DB collation consistently; case-insensitive out of scope.
  status: PASS
  actual: `libraryItems.title` with gt/lt/eq; no lower/citext/collation added.
- `id` is deterministic secondary key following the selected direction.
  status: PASS
  actual: `.orderBy(order(primaryColumn), order(libraryItems.id))` and eq-tie id compare use same direction helper.
- all/trash combine selects; shared retains document-only select.
  status: PASS
  actual: shared `documentQuery.as("library_items")` (:173-180); trash/default union both branches.
- Out of scope respected: no dnd/reorder, no sortable Status/Actions metadata, no client-side re-sort, existing permission/scope/search/trash/membership predicates preserved.
  status: PASS
  actual: predicates byte-identical vs main; diff scoped to plan files + directly related cleanup.
- Tests exist for router validation/order/cursor, service mixed-resource pagination + equal-key tiebreaks + direct defaults, component query-input/sort wiring.
  status: PASS
  actual: exact plan assertions present in all three spec files (e.g., equal-name 3-item walk, cursor shape, re-key on name/asc).

### thermos (synthesized: thermo-nuclear-review PASS high + thermo-nuclear-code-quality-review PASS high; overall: PASS, confidence: high)

- unionAll rewrite preserves owner/collection/shared/trash/ancestor/search predicates and membership semantics.
  status: PASS
  expected: All scope predicates from main reproduced in union branches.
  actual: Byte-identical predicates verified (source: both), e.g., `library.repository.ts:118-227`.
- Cursor predicate correctness for both directions and both sort keys with id tiebreaker; gt/lt matches asc/desc; no NULL-key hazard.
  status: PASS
  actual: `library.repository.ts:237-266`; both updatedAt columns `.notNull()`; predicate and ORDER BY share collation (self-consistent keyset).
- limit+1 global fetch: no off-by-one, gap, or duplicate risk.
  status: PASS
  actual: `library.service.ts:67-86`; strict keyset inequality; equal-key walks covered in tests.
- Shared-scope path orders and paginates correctly.
  status: PASS
  actual: document-only select routed through same `selectLibraryRows` (:173-180).
- Public item shape: internal nullable description does not leak onto documents.
  status: PASS
  actual: `toLibraryItem` mapping; router test asserts shape.
- Cursor mismatch rejected at both boundaries (router superRefine BAD_REQUEST; service internal throw).
  status: PASS
- DB collation vs previous JS comparison: default updated/desc equals main behavior; name sort new and deliberate.
  status: PASS
- useDataTableSort URL integration and infinite query re-keying correct (initialCursor null resets on sort change; stale cursors rejected server-side).
  status: PASS
- Devex: no env/script/port changes.
  status: PASS
- Feature leaks: none (no flags/gates in diff).
  status: PASS
- File-size: no file pushed past 1000 lines (largest changed: library.router.test.ts ~660; library.repository.ts 267).
  status: PASS
- Spaghetti growth: cursor clause is one minimal 16-line keyset expression; scope branches preserve pre-existing structure; change de-duplicates cursor/order/limit formerly duplicated across 6 query sites.
  status: PASS
- Boundary/type cleanliness: no any/unknown in production; internal LibraryRow alignment justified; subquery typing verified sound by typecheck.
  status: PASS
- Canonical-layer reuse: `useDataTableSort`, `normalizeLimit`, `DEFAULT_LIBRARY_PAGE_SIZE` reused; bespoke cursor helpers deleted, not duplicated.
  status: PASS
- Abstractions earn their keep: `selectLibraryRows` (3 call sites) consolidates prior duplication; `toLibraryItem` necessary boundary mapping; `normalizeLibrarySort`/`getLibraryCursor` conventional.
  status: PASS
- Orchestration: single union query replaces 2 queries + JS concat/sort/slice — genuine simplification, pagination now exact across mixed set.
  status: PASS
notes:
- Minor: `selectLibraryRows` receives full `query` but reads only `query.cursor`; default sort values hard-coded in 3 places (schema :28-29, helpers :20-21, table :44-45).
- Trash view: "Deleted" column header becomes sortable but sorts by `updatedAt` while cells display `deletedAt` (`markdown-files-table-columns.tsx:105-114`) — UX mismatch; default trash order unchanged from main.
- globals.css teal-token change confirmed in branch diff (cosmetic, no risk).
- Pre-existing (not regression): shared-scope innerJoin could duplicate a document with multiple role rows; unchanged from main.
- Transient: in-flight old-shape cursors ({id, updatedAt}) now fail validation instead of silently restarting — expected per plan; cursors live in React Query state only, self-heals on reload.

### react-quality-review (overall: PARTIAL, confidence: high)

- Sort wiring: hook usage, query input, re-keying with initialCursor null.
  status: PASS
  actual: `markdown-files-table.tsx:41-48,65-70`; typed via `parseAsStringLiteral`.
- Provider wiring: sort state/actions, `sortable` prop.
  status: PASS
  actual: `markdown-files-table.tsx:171,179,187`.
- Column sort metadata restricted to Name/Updated only — RUNTIME EFFECT of `sortable` flag on Status header.
  status: FAIL
  expected: Only Name and Updated render sortable headers; Status renders plain header (plan: "Status and Actions receive no sort metadata").
  actual: Status is `columnHelper.accessor("status")` with no `meta.sort` (`markdown-files-table-columns.tsx:85-102`); shared `getSortKey` falls back to `accessorKey` ("status") (`data-table.tsx:99-101`); with `sortable` enabled the Status header renders a sort button with ArrowUpDown icon and hover affordance whose click is a silent no-op (`onSort("status")` rejected at `use-data-table.tsx:196`). Users see a sortable-looking header that does nothing. Fix (branch-local): `meta: { sort: { enabled: false } }` on the Status column; shared getSortKey already honors `enabled === false` (`data-table.tsx:96`).
- Accessibility of sortable headers.
  status: PARTIAL
  expected: Keyboard-operable, sort state announced to assistive tech.
  actual: Native buttons inside th, keyboard operable; but no `aria-sort`/`aria-pressed`/`aria-label` on headers or buttons — direction conveyed only by aria-hidden icon. Gap lives in shared `data-table.tsx` (not in branch diff; pre-existing infra this branch activates) — flagged as follow-up, not branch failure. Dead Status button (FAIL above) also exposes a meaningless button to assistive tech.
- TypeScript quality: strict typing, discriminated unions, no any/unknown leaks, validated narrowing.
  status: PASS
  actual: `LibraryCursor` discriminated union mirrored by `z.discriminatedUnion`; `toLibraryItem` throws on impossible status/type combos; typecheck clean; test-only casts confined to specs.
- Testing quality: hoisted mocks, query-input/re-keying and provider wiring assertions, regression-sensitive.
  status: PASS
  actual: `markdown-files-table.test.tsx` 3 tests; mutation+rerender re-key check; 3/3 pass; dropping wiring fails corresponding test.
- Performance: no new re-render hazards; stable query keys; sort fully server-side.
  status: PASS
- Adherence to nextjs/code-style.md: naming, co-location, no effect-driven state sync, scoped diff.
  status: PASS
notes:
- Pre-existing shared-component gap activated by this feature: no aria-sort on sortable headers — follow-up in shared block.
- Sorting is desktop-only (mobile `responsive` rendering has no headers) — consistent with shared design.
- Pre-existing cast `fileColumns as unknown as ColumnDef<unknown, unknown>[]` (`markdown-files-table.tsx:168`) untouched by branch.

## Aggregate status determination

- Any accepted FAIL check → overall FAIL.
- The single accepted FAIL (dead sortable Status header) is branch-local, cheaply fixable, and contradicts the plan's "no sortable Status" intent at the runtime-affordance level. Everything else passes across all reviewers; both thermo-nuclear reviews agree PASS (no unresolved conflicts).
- Secondary actionable note: trash "Deleted" header sorts by updatedAt while displaying deletedAt.

## Follow-ups

1. Fix Status header dead sort affordance: add `meta: { sort: { enabled: false } }` to the Status column (or require explicit sort meta in shared component).
2. Decide trash-scope "Deleted" column: sort by `deletedAt` in trash or disable sortable there.
3. Optional follow-up (shared infra, out of branch scope): aria-sort/aria-pressed on sortable headers.
