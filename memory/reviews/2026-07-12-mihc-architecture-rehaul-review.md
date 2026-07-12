# Review: MIHC-Inspired Architecture Rehaul (Unstaged Changes)

**Date:** 2026-07-12
**Review Scope:** Unstaged working-tree changes (`git diff`) in markdown2share
**Reviewers:** requirements-reviewer, thermos, react-quality-review
**Overall Status:** **FAIL**

## Summary

The MIHC architecture rehaul implementation successfully removes the repository layer, splits broad services into focused services, migrates resource authorization to markdown permissions, and simplifies authentication guards. Contract freeze invariants (routes, action contracts, permission semantics, UI labels, database schema) are preserved. However, **1 security issue** remains (5 lint issues and 2 incomplete plan extractions addressed post-review).

---

## Checks

### Security

| # | Description | Status | Expected | Actual |
|---|-------------|--------|----------|--------|
| 1 | Permission check on `getDocumentMembers` (thermos) | **FAIL** | Document access verification before listing members | `share.action.ts:115` only calls `getCurrentUser()`; `document-sharing.service.ts:183-195` has zero permission checks. Any authenticated user can enumerate members of any document ID. |
| 2 | Permission checks on mutation paths | PASS | All mutations guard with appropriate permission | Save/edit/delete/publish/unpublish/share/revoke/create-collection all have proper guards via `canAccessDocument` or `requireDocumentPermission` |
| 3 | UUID validation before DB queries | PASS | `isUuid()` or `z.string().uuid()` on all foreign keys | All new services validate UUIDs before queries |
| 4 | Transaction consistency | PASS | Permission checks in transactions use same `DbExecutor` | All `DbExecutor` parameters threaded through to permission checks |
| 5 | Auth guards on routes | PASS | `requireCurrentUser` on auth routes, `redirectAuthenticatedUser` on public auth pages | All 9 app pages, 2 public layouts, and API route use correct guards |
| 6 | Soft-delete checks in queries | PASS | `isNull(deletedAt)` on read queries | All new service queries filter deleted records |
| 7 | Owner-lookup helpers missing `deletedAt` filter | PARTIAL | Defense-in-depth filtering | `permissions.service.ts:114,126` (findCollectionOwner, findDocumentOwner) omit `deletedAt` — low risk since callers have valid IDs |
| 8 | `publishDocumentDraft` lacks transaction wrapping | PARTIAL | Multi-step publication writes atomic | `document-publishing.service.ts:60-107` does select+insert+update without a transaction — same as old code, not a regression |
| 9 | SQL injection | PASS | No raw string interpolation | All queries use Drizzle parameterized builders |

### Requirements (Plan Compliance)

| # | Description | Status | Expected | Actual |
|---|-------------|--------|----------|--------|
| 10 | Task 7: Sharing UI split | PASS ~~(resolved)~~ | `document-invite-form.tsx` and `document-publish-controls.tsx` as separate files | Both created: `document-invite-form.tsx` (self-contained form), `document-publish-controls.tsx` (publish UI). `components/sharing/` now has all 4 files. |
| 11 | Task 9: `plate-elements.tsx` extraction | PASS ~~(resolved)~~ | Plate element/leaf renderers extracted to `plate-elements.tsx` | Created with 18 named exports. `plate-plugins.tsx` imports all renderers from `./plate-elements`. |
| 12 | Task 2: Auth guard renaming | PASS | No old helper matches | `assertAuthenticated`/`requireAuthentication`/`assertRole`/`requireRole`/`assertDocumentAccess` all zero matches |
| 13 | Task 3: Permissions colocation | PASS | `permissions.service.ts` with required exports; `authorization.service.ts` deleted | All exports present, zero `authorization.service` imports remain |
| 14 | Task 4: Collection/library service split | PASS | `collections.service.ts` and `document-library.service.ts`; no old imports | All required exports present, orphan imports zero |
| 15 | Task 5: Draft/publishing service split | PASS | `document-drafts.service.ts` and `document-publishing.service.ts`; no old imports | All required exports present, `markdown.service.ts` deleted, orphan imports zero |
| 16 | Task 6: Sharing service and type | PASS | `document-sharing.service.ts` and `sharing.type.ts` with `MemberInfo` | All exports present, `share.service.ts` deleted, orphan imports zero |
| 17 | Task 8: Library table/creation split | PASS | Column definitions and collection dialog extracted | `markdown-files-table-columns.tsx` and `create-collection-dialog.tsx` present and consumed |
| 18 | Task 10: Docs updated | PASS | `AGENTS.md` and `code-style.md` reflect new architecture | Both updated with focused services, removed repositories, auth vs authorization separation |
| 19 | Completion: No repository orphans | PASS | Zero repository imports or directories | All repository directories deleted, zero `repositories/` imports |
| 20 | Completion: Backend flows direct | PASS | `page/action → focused service → Drizzle` | All new services import `getDb` directly |
| 21 | Completion: No DB schema changes | PASS | No DDL, migration, or schema modifications | Zero changes to `lib/db/` or migration files |

### React/TypeScript Quality

| # | Description | Status | Expected | Actual |
|---|-------------|--------|----------|--------|
| 22 | Unused import: `MarkdownFileIdSchema` | PASS ~~(resolved)~~ | No unused imports | Import removed from `features/markdown/types/markdown.type.ts:1` |
| 23 | Unused import: `MarkdownErrorCode` | PASS ~~(resolved)~~ | No unused imports | Import removed from `features/markdown/actions/share.action.ts:7` |
| 24 | Unused import: `Trash2Icon` | PASS ~~(resolved)~~ | No unused imports | Import removed from `features/markdown/components/sharing/document-share-dialog.tsx:11` |
| 25 | Indentation drift | PASS ~~(resolved)~~ | Consistent 2-space indentation | Fixed `document-share-dialog.tsx:76-77` to use 2-space indentation |
| 26 | `as unknown as string` cast on Date | PASS ~~(resolved)~~ | Proper Date-to-ISO conversion | Replaced with `new Date(row.original.updatedAt).toISOString()` at `markdown-files-table-columns.tsx:89` |
| 27 | Module-level side effects | PARTIAL | No module-level `getQueryClient()` calls | `markdown-files-table-columns.tsx:20` and `document-share-dialog.tsx:65` call at import time — pre-existing pattern, not new damage |
| 28 | Component extraction correctness | PASS | All extractions preserve behavior, props, callbacks | `RichEditorPane`, toolbar primitives, `DocumentShareDialog`, columns, `CreateCollectionDialog` all 1:1 |
| 29 | `useMemo` on column definitions | PASS | Stable reference for DataTable | `markdown-files-table.tsx:67-70` correctly memoizes |
| 30 | `React.memo` with `displayName` | PASS | DevTools debugging support | `RichEditorPane.displayName` set at `rich-editor-pane.tsx:53` |
| 31 | Accessibility | PASS | aria-* attributes preserved | All aria-labels, aria-pressed, aria-busy, role=group, aria-hidden maintained |
| 32 | `useEffect` compliance | PASS | No unnecessary effects | Only legitimate effects: cleanup on unmount + deferred hydration |
| 33 | File naming conventions | PASS | kebab-case | All new component files follow convention |
| 34 | `tsc --noEmit` passes | PASS | Clean type-check | Exit code 0 |

---

## Notes

1. **CRITICAL**: `getDocumentMembersAction` (`share.action.ts:110-122`) exposes document membership to any authenticated user without a permission check. This must be fixed before deployment.

2. All Contract Freeze invariants (routes, action contracts, permission semantics, UI labels, database schema) are verified intact.
