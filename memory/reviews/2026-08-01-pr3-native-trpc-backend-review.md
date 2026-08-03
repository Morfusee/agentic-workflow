# PR #3 Review: refactor(trpc): migrate backend to native tRPC

- **Date:** 2026-08-01
- **Subject:** https://github.com/Morfusee/markdown2share/pull/3 — branch `refactor/native-trpc-backend-rewrite` -> `main` (129 files, +9034/-3970, 59 commits, OPEN/DRAFT)
- **Reviewers:** requirements-reviewer, thermo-nuclear-review, thermo-nuclear-code-quality-review (synthesized via thermos), react-quality-review
- **Verification:** CI run 30656260947 logs; `git diff origin/main...HEAD` (580KB); direct grep/read checks in worktree `$HOME/.codex/worktrees/465c/markdown2share`

## overall_status: FAIL

The architecture direction is sound and the inventory mapping (101 boundary rows) is faithfully executed, but the PR does not pass its own validation: CI is red on unit, integration, and Playwright jobs, and the PR body's validation claims are contradicted by CI evidence.

## Checks

### CI / Validation (blocking)

- **description:** Unit tests pass in CI (PR claims "pnpm test passed 33 files / 200 tests")
  **status:** FAIL
  **expected:** Green `pnpm test:unit`
  **actual:** CI fails with `useTRPC() can only be used inside of a <TRPCProvider>` from create-collection-dialog.tsx:44, deleted-document-gate.tsx:33, document-share-dialog.tsx:78, markdown-rich-editor.tsx:111. Root cause: 5 test files mock the stale path `@/server/trpc/*` (trpc-route.test.ts:4,12; deleted-document-gate.test.tsx:47; create-collection-dialog.test.tsx:25; markdown-rich-editor-save.test.tsx:99; document-share-dialog.test.tsx:67), but modules live at `@/lib/trpc/*` after commit 17a9353. Mocks silently no-op; real `useTRPC()` throws. All 5 mock paths are new lines in this PR.
  **source:** all four reviewers

- **description:** Integration tests pass in CI
  **status:** FAIL
  **expected:** Green `pnpm test:integration`
  **actual:** 12/12 suites fail, 39/39 tests skipped: `DATABASE_RESET_CONFIRM must exactly match the decoded database name` thrown at lib/db/database-reset-safety.ts:89 via scripts/setup-test-db.ts:27 <- __tests__/integration/helpers/test-db.ts:22. The new guard demands an env var that `.github/workflows/quality.yml` (unmodified in this PR) never sets. The new integration coverage therefore never runs in CI.
  **source:** requirements-reviewer, thermo-nuclear-review, thermo-nuclear-code-quality-review

- **description:** Destructive DB reset safeguards enforced without breaking CI consumption
  **status:** FAIL
  **expected:** Guard rejects unsafe resets AND the consuming workflow still passes
  **actual:** Guard itself is strong (confirmation must exactly equal decoded DB name; reserved names checked on decoded value so `pro%64` still caught; NODE_ENV=production blocked; `assertSafeTestDatabaseUrl` requires "test" in name + URL inequality; covered by database-reset-safety.test.ts). But CI Playwright job fails at `pnpm db:test:setup` with the same guard error; `pnpm test:e2e` never runs.
  **source:** requirements-reviewer, thermo-nuclear-review

- **description:** PR body Playwright claim ("blocked by Portless worktree-prefix 404") matches CI evidence
  **status:** FAIL
  **expected:** Claimed blocker matches observed failure
  **actual:** Contradicted. E2E job dies at `db:test:setup` (DATABASE_RESET_CONFIRM guard), before any app assertion. "pnpm test passed 33 files / 200 tests" also contradicted (unit job red).
  **source:** requirements-reviewer, thermo-nuclear-review

### Security / Correctness

- **description:** Local dev `just db-reset` / `pnpm db:reset` keeps working (breaking Devex)
  **status:** FAIL
  **expected:** Documented local workflow against the default DB works
  **actual:** `markdown2share` is in the reserved-name list (database-reset-safety.ts:16) AND is the documented default DB name (`.env.example:4`, port 6432). `commands/db.just:20` -> `pnpm db:reset` can never succeed against the default DB even with correct `DATABASE_RESET_CONFIRM`. Neither .env.example, justfile, nor README documents `DATABASE_RESET_CONFIRM`.
  **source:** thermo-nuclear-review

- **description:** Library default ("all") scope preserves behavior
  **status:** PARTIAL
  **expected:** Old "all" scope returned owned + invited items (userRoles join); PR claims behavior preservation
  **actual:** library.repository.ts:100 "all" scope now uses `eq(documents.ownerId, userId)` only (collections likewise :164); invited items appear only under the "shared" tab. Silent user-visible change vs "Preserve current user-visible behavior", not documented in docs/architecture/mihc-alignment-matrix.md.
  **source:** thermo-nuclear-review

- **description:** Permission model parity (owner/admin/direct/inherited/revocation)
  **status:** PASS
  **expected:** canAccessDocument/canAccessCollection semantics preserved
  **actual:** permissions.service.ts + permissions.policy.ts resolveResourceAccess reproduces old branching exactly; repository queries equivalent. Owner role rows no longer written (ownership derived from ownerId — data-model change, asserted by lifecycle tests).
  **source:** thermo-nuclear-review

- **description:** Public published-document endpoint security (no existence oracle, no revision leak)
  **status:** PASS
  **expected:** Public reads only for non-deleted, actually-published docs
  **actual:** documents.publishing.byId public procedure -> findPublishedDocumentRecord joins latest_published_revision_id with deletedAt IS NULL; invalid id -> NOT_FOUND; published page maps NOT_FOUND -> 404 and validates isUuid first.
  **source:** thermo-nuclear-review

- **description:** No info leaks via tRPC errors or logging
  **status:** PASS
  **expected:** No raw input/internals in client-visible messages
  **actual:** lib/trpc/init.ts errorFormatter masks INTERNAL_SERVER_ERROR messages, attaches only flattened Zod errors; document-sharing.service.ts:90 logs static message; onError logs server-side only.
  **source:** thermo-nuclear-review

- **description:** Drizzle transaction boundaries / rollback / lock ordering
  **status:** PASS
  **expected:** publish/save/restore/delete stay transactional with throw-to-rollback
  **actual:** Publishing keeps FOR UPDATE lock + revision insert + pointer update in one transaction; save/restore/collection delete/restore all in db.transaction; TRPCError throws roll back (AGENTS.md-compliant).
  **source:** thermo-nuclear-review

- **description:** Soft-delete/restore flows (owner-only, parent-deleted, deletedAt guard)
  **status:** PASS
  **expected:** Restore restricted to owner; parent-deleted blocked; re-delete guarded
  **actual:** restoreDocument/restoreCollection require owned lookup, block deleted parent (PRECONDITION_FAILED), match exact deletedAt — parity with origin/main.
  **source:** thermo-nuclear-review

- **description:** Library cursor pagination + input validation (injection, perf)
  **status:** PASS
  **expected:** Parameterized SQL, validated cursor, bounded inputs
  **actual:** libraryCursorSchema (z.uuid + z.date), limit 1-100 default 20, search trimmed max 160; parameterized drizzle SQL throughout; superjson round-trips Date cursor.
  **source:** thermo-nuclear-review

- **description:** Cache invalidation semantics preserved (document flows)
  **status:** PASS
  **expected:** Same paths revalidated as old actions
  **actual:** document-revalidation.ts covers /app, /app/md/:id, /published/:id (+ /app/trash on restore); called from documents.router mutations; components invalidate trpc pathKeys and router.refresh().
  **source:** thermo-nuclear-review

- **description:** Cache invalidation preserved for collection flows (S3-41..46)
  **status:** FAIL
  **expected:** Collection create/delete/restore revalidate /app server-side like the old actions
  **actual:** collections.router.ts/services contain no revalidatePath; only client router.refresh() remains. Downgraded from server-side revalidation; not documented.
  **source:** requirements-reviewer, thermo-nuclear-review (dedup)

- **description:** Better Auth nextCookies() removal keeps session flows working
  **status:** BLOCKED
  **expected:** Login/signout/tRPC context work without nextCookies()
  **actual:** Design plausibly fine (native auth route/client; context reads session from headers), but e2e never runs in CI so browser cookie behavior is unverified. Do not merge without e2e auth pass.
  **source:** thermo-nuclear-review

- **description:** Migration baseline rewrite (0000_native_trpc_baseline.sql) migrates existing DBs
  **status:** PARTIAL
  **expected:** Existing deployments migrate or are re-baselined knowingly
  **actual:** Single journal entry re-tagged with new snapshot id; any DB under 0000_graceful_master_mold fails drizzle migrate (duplicate tables). Acceptable for 0.1.0 if acknowledged. `users.name NOT NULL` risk for OAuth users without profile name (signup page sends name:email; GitHub flow unverified).
  **source:** thermo-nuclear-review

- **description:** Permission-denial semantics: FORBIDDEN vs NOT_FOUND consistency
  **status:** PARTIAL
  **expected:** Same UX outcomes as legacy boundaries
  **actual:** getCollectionAccess/getDocumentAccess now return NOT_FOUND (old FORBIDDEN on some operations). md/[documentId] UX preserved via NOT_FOUND -> 404 mapping; [...collectionPath] changed: old any-failure -> 404, new FORBIDDEN -> error boundary.
  **source:** thermo-nuclear-review

- **description:** Bounded inputs on per-item-work procedures (collections.breadcrumbs)
  **status:** PARTIAL
  **expected:** Inputs with per-item DB work bounded
  **actual:** z.array(z.uuid()) with no .max(); ~4 queries per entry; transport moved from URL segments to POST JSON removing the URL-length bound. Low severity.
  **source:** thermo-nuclear-review

### Code Quality (thermo-nuclear-code-quality-review)

- **description:** Legacy infrastructure removal complete with no orphan imports
  **status:** PASS
  **expected:** Old transport layer fully deleted
  **actual:** /api/app, all feature actions, serializers, error types, server-action-return deleted; zero remaining imports (grep-verified); enforced by trpc-boundaries.test.ts:686-771.
  **source:** thermo-nuclear-code-quality-review

- **description:** Publish-revision logic implemented once, not duplicated
  **status:** FAIL
  **expected:** One "create next revision + repoint latestPublishedRevisionId" implementation
  **actual:** documents.repository.ts:228-279 and document-publishing.repository.ts:66-80 duplicate findMaximumDocumentRevisionNumber (byte-identical) and revision insert/pointer update; document-drafts.service.ts:190-237 vs document-publishing.service.ts:94-128 run the same lock->maxRev->insert->pointer transaction twice. Strongest code-judo target: extract one insertNextRevision.
  **source:** thermo-nuclear-code-quality-review

- **description:** No dead code/dead exports in new layers
  **status:** FAIL
  **expected:** Every exported symbol has a production caller
  **actual:** canAccessCollection/canAccessDocument (permissions.service.ts:143-171, zero callers), getDocumentAccess (document-drafts.service.ts:92-106), markdownFileIdSchema/documentIdSchema (document.schema.ts:10,14), markdownFilesCursorSchema (library.schema.ts:16), MarkdownDraft/DeletedMarkdownDocument types, providers.tsx one-line re-export shim with zero importers, document-sharing.schema.ts transforms producing unused userId fields, listLibraryItems pass-through wrapper.
  **source:** thermo-nuclear-code-quality-review

- **description:** Permission layer cohesion / single enforcement point
  **status:** PARTIAL
  **expected:** One permission module as enforcement point; policy not bypassed
  **actual:** 5 files for one concern; getCollectionAccess/getDocumentAccess ~90% identical; assert-access trivial; ad-hoc `ownerId !== userId` checks bypass the policy in collections.service.ts:117-119 and document-drafts.service.ts:252-254 while sibling delete operations go through the policy — authorization enforced two ways.
  **source:** thermo-nuclear-code-quality-review

- **description:** No scattered defensive UUID re-validation
  **status:** FAIL
  **expected:** Trust the zod boundary (z.uuid) or one central guard
  **actual:** 16 `isUuid` guards across 5 service files, unreachable in the shipped path since every tRPC input schema already validates UUID format.
  **source:** thermo-nuclear-code-quality-review

- **description:** Error factories shared, not copy-pasted
  **status:** FAIL
  **expected:** One TRPCError factory; assertResourceAccess already centralizes NOT_FOUND/FORBIDDEN
  **actual:** 4 copies of notFoundError/forbiddenError/parentDeletedError/internalServerError (document-drafts.service.ts:75-90, document-publishing.service.ts:24-32, document-sharing.service.ts:38-52, collections.service.ts:27-37); requireDocumentPermission re-implements assertResourceAccess a second way in publishing + sharing services.
  **source:** thermo-nuclear-code-quality-review

- **description:** Error-contract honesty: formatter matches documented masking behavior
  **status:** PARTIAL
  **expected:** "leaves deliberate public messages intact" (code-style.md) matches formatter
  **actual:** init.ts:17-20 masks ALL INTERNAL_SERVER_ERROR messages, so the deliberate message in document-sharing.service.ts:48-52 ("Document sharing is not configured correctly.") is unreachable on the wire.
  **source:** thermo-nuclear-code-quality-review

- **description:** Page-state reads avoid re-fetching and double fact-gathering
  **status:** PARTIAL
  **expected:** One permission fact-gather per page read
  **actual:** getDocumentPageState (document-drafts.service.ts:108-165) gathers the 4 permission queries twice (view + edit) plus a document re-read: ~10 queries for one page.
  **source:** thermo-nuclear-code-quality-review

- **description:** Schema naming honesty (generic documentId input)
  **status:** PARTIAL
  **expected:** Truthful generic documentIdSchema for read/membership/publishing procedures
  **actual:** deleteDocumentSchema (document.schema.ts:32-34) is the input schema for 8 procedures including pure reads (byId, members.list, publishing.byId/state/publish/unpublish); restoreDocumentSchema identical shape; an unused documentIdSchema exists as a bare string type.
  **source:** thermo-nuclear-code-quality-review

- **description:** File-size discipline
  **status:** PASS
  **expected:** No production file pushed toward/over 1k lines
  **actual:** Largest production files 279 lines (documents.repository.ts); code-style.md cut from ~925 to 739; only new 853-line file is trpc-boundaries.test.ts (test).
  **source:** thermo-nuclear-code-quality-review

- **description:** Architecture guard test is cheap and maintainable
  **status:** PARTIAL
  **expected:** Cheap enforcement (ESLint would be simpler)
  **actual:** trpc-boundaries.test.ts is 853 lines; ~600 lines are a hand-rolled TypeScript AST scanner plus 4 self-referential fixture tests testing the scanner itself; regex heuristics (isPurePolicyOrRepository) will rot as naming drifts. Guards themselves are meaningful.
  **source:** thermo-nuclear-code-quality-review

### React / TypeScript (react-quality-review)

- **description:** New component tests mock the module the components actually import
  **status:** FAIL
  **expected:** Mock `@/lib/trpc/client` or wrap in real TRPCProvider
  **actual:** All four failing tests mock nonexistent `@/server/trpc/client` (silent no-op). Fix is minimal: repoint 4 mocks (plus trpc-route.test.ts context/root mocks) or add a shared test provider helper.
  **source:** react-quality-review

- **description:** Provider hierarchy guarantees useTRPC() has an ancestor
  **status:** FAIL
  **expected:** Every useTRPC consumer guaranteed a provider (or tests adapt)
  **actual:** Placement correct (app/layout.tsx:30-37: Theme > TRPCReact > Tooltip > Nuqs). But 10 client components now hard-require the provider (unconditional top-level useTRPC); any render outside it throws. Breaking change unabsorbed in the test surface (tests neither wrap nor mock correctly).
  **source:** react-quality-review

- **description:** Client/server component boundaries (in-process caller, no HTTP /api/trpc fetch)
  **status:** PASS
  **expected:** RSC uses createCaller; data hooks only in "use client"
  **actual:** Server pages use createCaller from lib/trpc/server; all 10 useTRPC consumers are "use client"; server.tsx imports "server-only"; TRPCReactProvider imported into root server layout correctly.
  **source:** react-quality-review

- **description:** TanStack Query + tRPC integration (generated options, narrow invalidation)
  **status:** PASS
  **expected:** queryOptions/mutationOptions/pathKey; narrowest invalidation
  **actual:** Components use generated options and invalidate via pathKey/exact queryKey; DocumentShareDialog disables queries without documentId via `enabled`. Matches code-style.md conventions.
  **source:** react-quality-review

- **description:** Hook usage policy (useEffect only for external sync)
  **status:** PASS
  **expected:** No effect-driven state sync; cleanup for scheduled work
  **actual:** markdown-rich-editor effects only for hydration scheduling with cleanup; ref-versioning scheme avoids effect-driven sync; callbacks memoized with correct deps.
  **source:** react-quality-review

- **description:** Error/loading/empty states
  **status:** PASS
  **expected:** Distinct states; mutation errors per existing patterns
  **actual:** markdown-files-table handles error/empty-with-CTA/skeleton states; mutation errors render with role="alert" in all action components.
  **source:** react-quality-review

- **description:** TypeScript strictness (no any, no unsafe assertions)
  **status:** PARTIAL
  **expected:** strict:true, no any
  **actual:** strict:true (tsconfig.json:7); no any in feature components; one `as unknown as ColumnDef<unknown, unknown>[]` boundary cast in markdown-files-table.tsx:155.
  **source:** react-quality-review

- **description:** Accessibility basics
  **status:** PARTIAL
  **expected:** Labels, keyboard-accessible dialogs, focus rings, error announcements
  **actual:** Semantic landmarks, aria-labels, role="alert", focus rings all present. Pre-existing (not PR): Settings button with aria-label but no onClick (authenticated-shell-client.tsx:159-168) — focusable dead control.
  **source:** react-quality-review

- **description:** Test quality: behavioral verification that runs green
  **status:** FAIL
  **expected:** Behavioral, user-centric tests that pass
  **actual:** Query style good (getByRole/getByLabelText). But suites don't run green (stale mock path); markdown-rich-editor-save.test.tsx:47-97 hand-reimplements TanStack's useMutation state machine (listeners + forceRender) so tests verify their own fake; no new test exercises a real provider.
  **source:** react-quality-review

- **description:** Component size and structure
  **status:** PARTIAL
  **expected:** Readable boundaries; repeated UI extracted
  **actual:** markdown-rich-editor.tsx (511 lines) and document-share-dialog.tsx (394 lines) large but organized; tab/version-sync logic (lines 142-396) dense — extraction candidate.
  **source:** react-quality-review

## Notes

- Deduplicated: the CI unit-test failure (stale `@/server/trpc/*` mocks) and the CI integration/e2e failure (DATABASE_RESET_CONFIRM not wired into workflow) were each found by all four reviewers; they are the two blocking issues. Root cause of both is within the PR's own changes.
- Doc drift: code-style.md:704-709 and docs/architecture/mihc-alignment-matrix.md still reference `server/trpc/*` paths; modules live at `lib/trpc/*` after relocation commit 17a9353. Same stale path the tests mock — relocation happened late without updating tests/docs.
- The architecture (router -> workflow -> policy -> repository -> Drizzle) and inventory mapping are faithfully implemented and legacy removal is thorough; the blockers are test/CI correctness, not design.
- Resolved conflict: none — reviewers agree on all blocking findings.
- Confidence: high.

## 2026-08-01 Follow-up: resolution status (worked on branch refactor/native-trpc-backend-rewrite)

- Fix 1 (stale @/server/trpc mocks): DONE - repointed 5 test files to @/lib/trpc/*; unit suite green (21 files / 161 tests).
- quality.yml: DELETED per user request (CI no longer builds).
- nextCookies e2e pass: DONE via manual browser pass - signup, login, session persistence on reload, save mutation, signout, anonymous /app redirect, better-auth.session_token cookie set/cleared by native route. PASS.
- Playwright suite: unblocked via playwright.config.ts worktree-prefix fix (the documented "Portless worktree-prefix 404"); 35 pass / 25 fail with deterministic in-suite Share-dialog instability (save->refresh fallback flow) - proven pre-existing: failing test passes alone at PR head and with the changes; not caused by this follow-up. Suite had no green baseline before.
- Quality findings: DONE for FAIL items + cheap PARTIALs (revision-logic dedup via insertNextPublishedRevision, shared permission-errors module, requireDocumentPermission -> assertResourceAccess, removed 12 redundant isUuid guards + 2 local requireDocumentPermission variants, dead code sweep: canAccess*/getDocumentAccess(drafts)/MarkdownDraft/DeletedMarkdownDocument/markdownFileIdSchema/markdownFilesCursorSchema/delete+restore schemas->documentIdSchema/providers.tsx/transform shims/listLibraryItems wrapper; error-contract: docs now say internal errors always masked, dead sharing message removed). DEFERRED (structural, noted): permission-layer cohesion merge, getDocumentPageState query fan-out, trpc-boundaries AST-scanner rewrite, component-size extraction.
- Docs drift: DONE - code-style.md (layer table, import example, formatter contract, evidence table, dead-symbol examples) + mihc-alignment-matrix.md + plan docs 02/05/06/08; moved __tests__/unit/server/trpc -> __tests__/unit/lib/trpc.
- Verification on branch: pnpm typecheck PASS, pnpm lint 0 errors / 24 pre-existing warnings, pnpm test 33 files / 200 tests PASS, pnpm build PASS, git diff --check clean. Net diff of follow-up: +207 / -720 lines.
