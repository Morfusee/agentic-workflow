# WYSIWYG Plate Branch Review

overall_status: FAIL

## Review Scope

- Subject: current branch `feat/wysiwyg-plate` reviewed against `main`.
- Diff scope: `git diff main...HEAD` and changed files from `git diff main...HEAD --name-only`.
- Branch commits reviewed: `main..HEAD`.
- Provider context: none supplied.
- Explicit requirements or acceptance criteria: none supplied; requirements checks infer intent only from commit messages, changed files, tests, and implementation behavior.
- Verification: `pnpm test` failed. 14 passed, 1 failed, 4 skipped/not run. The first markdown document workflow timed out waiting for `locator("#editor-mode")` in `e2e/markdown-documents.spec.ts` lines 70-72.
- Exclusions: unchanged files and whole-repository review outside branch-scoped changed-file context.

## Reviewers

- requirements-reviewer
- react-quality-review

## Aggregate Notes

- Both reviewer results complied with the required reviewer contract and stayed read-only.
- Both reviewers independently identified the same blocking functional defect: save/revalidation targets `/app/md/{id}/edit`, but the changed App Router files define `/app/md/[documentId]` without an `/edit` child route.
- Aggregate status is `FAIL` because multiple accepted checks failed.

## Checks

### requirements-reviewer: Explicit Acceptance Criteria Available

- status: BLOCKED
- expected: A provider ticket, PRD, prompt, or explicit acceptance criteria defining required behavior.
- actual: No provider ticket or explicit acceptance criteria were supplied; requirements had to be inferred from `git log --oneline main..HEAD`, changed files from `git diff main...HEAD --name-only`, branch tests, and implementation behavior.

### requirements-reviewer: Markdown Editor Document Routes Are Consistent

- status: FAIL
- expected: New and existing Markdown documents should navigate to routes that exist in the changed App Router files.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx` line 279 redirects new saved documents to `/app/md/${savedDocument.id}/edit`, and `features/markdown/actions/document-draft.action.ts` lines 73-74 revalidate `/app/md/${result.document.id}/edit`; changed route files define `/app/md`, `/app/md/new`, and `/app/md/[documentId]` through `app/(auth)/app/md/page.tsx`, `app/(auth)/app/md/new/page.tsx`, and `app/(auth)/app/md/[documentId]/page.tsx`, with no matching `/edit` route.

### requirements-reviewer: Rich Markdown Editor Saves And Reloads Documents

- status: FAIL
- expected: Creating a document from `/app/md/new`, saving Markdown, refreshing, and switching back to Markdown mode should preserve the saved Markdown.
- actual: `e2e/markdown-documents.spec.ts` lines 20-28 assert save, refresh, and exact Markdown retrieval; `pnpm test` failed with the first markdown-documents test timing out waiting for `locator("#editor-mode")` in `switchToMarkdownMode` at lines 70-72.

### requirements-reviewer: Markdown File Listing Opens And Deletes Documents

- status: PARTIAL
- expected: Files on `/app` should link to editable document pages and row actions should delete files from the list.
- actual: `features/markdown/components/markdown-files-table.tsx` links rows to `/app/md/${row.original.id}` and wires `DocumentRowActions`, while `features/markdown/services/document-draft.service.ts` soft-deletes accessible documents; however, saved-document navigation still targets `/app/md/[id]/edit`, and the markdown document workflow suite did not complete after the first failure.

### requirements-reviewer: Slug Removal Reflected In Schema, Migrations, And Seed Data

- status: PASS
- expected: Removing document and collection slugs should remove schema fields, drop persisted columns/indexes, and stop seed data from depending on slugs.
- actual: `lib/db/schema.ts` removes `collections.slug`, `documents.slug`, and slug unique indexes; `lib/db/migrations/0005_third_blindfold.sql` drops slug constraints/indexes/columns; `lib/db/seed-data.ts` and `lib/db/seed.ts` seed collections/documents by names/titles without slug values.

### requirements-reviewer: Signup Supports Optional Display Usernames

- status: PASS
- expected: Signup should no longer require a user-entered full name while auth supports optional display usernames.
- actual: `features/auth/schemas/signup.schema.ts` validates email/password/confirmPassword only; `app/(public)/signup/page.tsx` submits `name: data.email`; `lib/auth/index.ts` defines optional `displayUsername`; login/signup tests passed in the `pnpm test` run.

### react-quality-review: Editor Post-Save Route Matches Implemented Route

- status: FAIL
- expected: After saving a new document, the client should navigate to an existing editor route that renders `MarkdownRichEditor` and exposes `#editor-mode`.
- actual: `app/(auth)/app/md/[documentId]/page.tsx` defines the editor at `/app/md/[documentId]`, but `features/markdown/components/editor/markdown-rich-editor.tsx` line 279 redirects new saves to `/app/md/${savedDocument.id}/edit`, and `features/markdown/actions/document-draft.action.ts` lines 74 and 109 revalidate `/edit`. No `app/**/edit/**/*.tsx` route exists. `pnpm test` failed with the first markdown document test timing out waiting for `#editor-mode`.

### react-quality-review: E2E Coverage Validates Changed Markdown Workflows

- status: FAIL
- expected: `pnpm test` should pass for the branch-scoped editor and document list workflows.
- actual: `pnpm test` failed. 14 passed, 1 failed, 4 skipped/not run. Failure: `e2e/markdown-documents.spec.ts` timed out waiting for `locator("#editor-mode")` in `switchToMarkdownMode` at lines 70-72.

### react-quality-review: Changed React/TypeScript Avoids Unsafe Any

- status: PARTIAL
- expected: Changed TS/TSX should avoid `any` and use typed child contracts or safe narrowing.
- actual: `components/ui/toggle-group.tsx` lines 65-68 clones children via `React.ReactElement<any>` and reads `(child.props as any).value`, weakening type safety in a shared UI primitive.

### react-quality-review: Changed List Rendering Uses Stable Keys

- status: PARTIAL
- expected: Dynamic list items should use stable, unique keys rather than array indexes unless the list is static.
- actual: `components/blocks/data-table/data-cell.tsx` lines 160-172 renders caller-provided menu items with `key={index}`, so reordering or insertion can preserve the wrong menu item state.

### react-quality-review: Icon-Only Controls Have Accessible Names

- status: PARTIAL
- expected: Icon-only buttons should expose an accessible label when their visual content is only an icon.
- actual: `components/blocks/data-table/data-table.tsx` lines 558-565 and 598-605 render clear-search icon buttons without `aria-label`; lines 610-617 render a filter icon button without visible text or `aria-label`.

### react-quality-review: Editor Primary Controls Expose Labels And Focus Semantics

- status: PASS
- expected: The editor mode selector, Markdown textarea, title input, and toolbar icon buttons should be labeled and keyboard-accessible.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx` labels the editor mode selector and Markdown textarea; `features/markdown/components/editor/editor-shell.tsx` labels the title input; `features/markdown/components/editor/editor-toolbar.tsx` gives toolbar icon buttons `aria-label`.

### react-quality-review: React Hooks And Scheduled Work Cleanup

- status: PASS
- expected: Hooks should be called unconditionally and scheduled work should be cancelled on unmount.
- actual: `features/markdown/components/editor/markdown-rich-editor.tsx` calls hooks at component top level and cleans up scheduled heading/tab conversion work in the unmount effect.

### react-quality-review: TypeScript Strict Mode Enabled

- status: PASS
- expected: The project should compile under TypeScript strict mode.
- actual: `tsconfig.json` has `"strict": true`.

## Reviewer Confidence

- requirements-reviewer: low, because no explicit acceptance criteria were supplied.
- react-quality-review: high.
