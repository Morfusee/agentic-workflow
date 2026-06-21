# Branch Review: wysiwyg-plate

overall_status: FAIL

## Review Scope

- Subject: current branch `feat/wysiwyg-plate`
- Base comparison: `main...HEAD`
- Diff scope: branch-scoped changed files only
- Provider context: none provided
- Requirements context: review current branch changes against `main`; no external acceptance criteria provided
- Exclusions: no provider comments published; no code modified; no full-repository review beyond immediate changed-file context

## Reviewers

- requirements-reviewer
- thermos
- react-quality-review

## Checks

### requirements-reviewer: Markdown document save flow routes to an implemented edit page

- status: FAIL
- expected: Saving a new document should navigate to a route implemented by the branch, and cache revalidation should target that same route.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx:278-279` redirects new saves to `/app/md/${savedDocument.id}/edit`, and `features/markdown/actions/document-draft.action.ts:73-74` revalidates `/app/md/${result.document.id}/edit`; the branch only adds `app/(auth)/app/md/[documentId]/page.tsx`, which implements `/app/md/[documentId]`, not `/edit`.

### requirements-reviewer: Branch e2e tests align with implemented Markdown document routes

- status: FAIL
- expected: Tests should assert routes that the app implements.
- actual: `e2e/markdown-documents.spec.ts:21` and `e2e/markdown-documents.spec.ts:66` expect `/app/md/[id]/edit`, matching the incorrect redirect but not the added route file `app/(auth)/app/md/[documentId]/page.tsx`.

### requirements-reviewer: Markdown document CRUD enforces authentication and access checks

- status: PASS
- expected: Create/update/delete/edit document flows should require an authenticated user and prevent access to unauthorized or deleted documents.
- actual: `features/markdown/actions/document-draft.action.ts:62-67` and `features/markdown/actions/document-draft.action.ts:95-99` call `assertAuthenticated`; `features/markdown/services/document-draft.service.ts` access paths call `canAccessDocument`; `features/markdown/services/markdown.service.ts` filters `deletedAt` with `isNull`.

### requirements-reviewer: Changed files satisfy repository lint standards

- status: FAIL
- expected: Branch-scoped changed code should not introduce lint errors.
- actual: Reviewer-reported `pnpm lint` exited 1. Reported changed-file lint errors include `components/blocks/data-table/data-column-meta.ts:20`, `components/blocks/data-table/data-table-context.tsx:194`, `components/blocks/data-table/types.ts:4`, `components/blocks/data-table/use-data-table.tsx:52`, and `hooks/use-mobile.ts:12`.

### thermos: New-document save redirects to a route that the branch does not define

- status: FAIL
- expected: After saving a new Markdown document, the app should navigate to an existing editor route for that document.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx:278-280` redirects new documents to `/app/md/${savedDocument.id}/edit`, and `features/markdown/actions/document-draft.action.ts:73-75` revalidates the same `/edit` path. The branch contains `app/(auth)/app/md/[documentId]/page.tsx`, `app/(auth)/app/md/new/page.tsx`, and `app/(auth)/app/md/page.tsx`, but no `app/(auth)/app/md/[documentId]/edit/page.tsx` route.

### thermos: Destructive migrations drop persisted identifiers without a staged preservation path

- status: FAIL
- expected: Schema migrations that remove user/document identifiers should preserve or backfill data before dropping columns, or stage the removal so existing production data is not irreversibly lost.
- actual: `lib/db/migrations/0005_third_blindfold.sql:4-5` drops `collections.slug` and `documents.slug`; `lib/db/migrations/0006_loving_the_fallen.sql:1-2` drops `user.username`. The branch diff shows no migration that copies those values into replacement columns before dropping them.

### react-quality-review: Branch-scoped React/Next route consistency for the markdown editor save flow

- status: FAIL
- expected: Client navigation, cache revalidation, links, and E2E assertions should target an existing changed route.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx:278-279` redirects new documents to `/app/md/${savedDocument.id}/edit`, `features/markdown/actions/document-draft.action.ts:73-75` and `features/markdown/actions/document-draft.action.ts:108-109` revalidate `/app/md/{id}/edit`, and `e2e/markdown-documents.spec.ts` expects `/app/md/{id}/edit`; `features/markdown/components/markdown-files-table.tsx:69-72` links rows to `/app/md/${row.original.id}` and the added route is `app/(auth)/app/md/[documentId]/page.tsx`.

### react-quality-review: Accessibility semantics for the changed toggle group component

- status: FAIL
- expected: A group of `role="radio"` items should expose the correct radio-group semantics to assistive technologies.
- actual: `components/ui/toggle-group.tsx:57-63` renders the parent as `role="group"`, while `components/ui/toggle-group.tsx:91-97` renders each item as `role="radio"` with `aria-checked`; this changed component is used by `components/blocks/data-table/data-table.tsx`.

### react-quality-review: React hooks and client/server boundaries in changed React files

- status: PASS
- expected: Components using client hooks or browser globals should be client components, and server actions should remain server-only.
- actual: Changed hook/browser-using components include `"use client"` in `features/markdown/components/editor/markdown-rich-editor.tsx`, `features/markdown/components/document-row-actions.tsx`, `components/blocks/data-table/data-table.tsx`, `components/blocks/data-table/data-table-context.tsx`, `components/layout/authenticated-shell-client.tsx`, and `app/(public)/signup/page.tsx`; changed server action file declares `"use server"` in `features/markdown/actions/document-draft.action.ts`.

### react-quality-review: Test coverage evidence for changed React/TypeScript user flows

- status: PARTIAL
- expected: Changed critical editor and document-list flows should have executable coverage that would catch routing and interaction regressions.
- actual: `e2e/markdown-documents.spec.ts` adds save/reload/delete coverage, but the assertions currently encode the non-existent `/app/md/{id}/edit` route and there is no branch evidence of component/a11y tests for the new data table, toggle group, or editor controls.

## Notes

- Aggregate status is `FAIL` because multiple accepted checks failed.
- The strongest and repeated finding is the route mismatch: new-document save, revalidation, and E2E tests use `/app/md/{id}/edit`, while the branch implements `/app/md/{id}`.
- Reviewers agreed on the route mismatch. No reviewer-result conflicts required arbitration.
- Reviewer outputs were accepted after spot-checking cited files and route file presence.
