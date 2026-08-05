# PR #9 Review — Recursive Collection Authorization

- **Date:** 2026-08-05
- **Subject:** `feat/recursive-collection-authorization` (PR #9)
- **URL:** https://github.com/Morfusee/markdown2share/pull/9
- **Base:** `main` (merge-base `309e8c5`) → `HEAD` (`a09b42f`), 7 commits, 26 files, +2444 / -65
- **overall_status:** FAIL

## Reviewers

- `requirements-reviewer` (medium confidence)
- `thermos` (security/correctness + code quality, high confidence)
- `react-quality-review` (high confidence)

## Review scope

Branch-scoped diff `git diff main...HEAD` only (saved at
`$HOME/AppData/Local/Temp/opencode/pr9.diff`). Requirements sourced from
`docs/plans/2026-08-04-recursive-collection-authorization-ticket.md` (Authorization
Contract, Implementation Requirements, all 22 Acceptance Criteria, Non-Goals) and
`docs/plans/2026-08-04-recursive-collection-authorization-implementation-plan.md`
(execution constraints, Task specs, exit criteria). Read-only review; no files modified.

## Verification run locally

- `pnpm lint`: 0 errors (23 warnings, all pre-existing in files untouched by this branch)
- `pnpm typecheck`: exit 0
- `pnpm test:unit`: 28 files / 262 tests passed
- `pnpm test:integration`: **BLOCKED locally** — requires Postgres on port 6432 (not running). PR claims 42 files / 328 tests passed; all integration-based findings rest on static inspection of implementation + test assertions.

## Checks

- description: AC1–AC21 recursive authorization contract (nearest-assignment precedence, exact ownership, revocation exceptions, derived-ancestry moves, delete/restore persistence, Shared root/nested discovery, topmost-root de-duplication, breadcrumbs at shared subtree roots, bounded set-based SQL, non-goal 1: no MCP/closure table/copied roles/move UI)
  status: PASS
  expected: Nearest assignment wins regardless of rank; revocation blocks only inherited roles; Shared discovery == authorization with stable sorting/pagination/shapes
  actual: `findNearestCollectionRole` orders ancestry by depth (permissions.repository.ts:80-105); depth-0 vs deeper split (permissions.service.ts:77-79); policy gates inherited behind `!isRevoked` (permissions.policy.ts:51); Shared helpers pass unions through `selectLibraryRows`; nested pages authorized once per page (library.service.ts:44-52). Behavioral PASSes are static-inspection-based (integration DB unavailable). [requirements-reviewer]

- description: AC22 — lint/typecheck/unit/focused-integration verification commands pass
  status: PARTIAL
  expected: All verification commands exit 0
  actual: lint 0 errors, typecheck clean, 262 unit tests pass (verified). Integration suite could not run locally (no Postgres); PR's "42 files / 328 tests" claim unverified. [requirements-reviewer]

- description: Ticket non-goal #2 / plan exit criterion — no collection sharing-management UI or collection member CRUD; no application code outside the planned permission/collection/library boundaries
  status: FAIL
  expected: No sharing-management UI or member CRUD per ticket Non-Goals; exit criterion "no application code outside the planned permission, collection, and library boundaries"
  actual: The PR adds a full collection-sharing feature beyond the ticket: members router (collections.router.ts:1990-2040), `collection-sharing.service.ts` (2170-2273), `collection-members.repository.ts`, `collection-share-dialog.tsx`, `collection-member-list.tsx`, `collection-invite-form.tsx`, `collection-sharing.schema.ts`, plus document-sharing component edits. Deliberate scope expansion; does not corrupt the recursive-auth contract. [requirements-reviewer]

- description: SQL injection / parameterization of all raw SQL (recursive CTEs, shared-listing fragments)
  status: PASS
  expected: All user/query-controlled values bound via placeholders
  actual: Every raw SQL fragment uses Drizzle `sql` template parameters (permissions.repository.ts:80-105; library.repository.ts:252-332). No concatenated input found. [thermos]

- description: Recursive CTE termination/cycle safety
  status: PARTIAL
  expected: CTEs terminate; a parent cycle must not hang the query
  actual: Anchor/depth/deleted_at semantics correct, but all three new CTEs use `UNION ALL` with no `CYCLE` clause or depth cap — a `parent_id` cycle would loop forever (app-wide hang). No current API can create a cycle (no move API; create requires owning the parent), so latent. One-line hardening: add `CYCLE` clause. [thermos]

- description: Shared-listing SQL set semantics — every listed row must be viewable; revocation blocks inherited access
  status: FAIL
  expected: Listing equals `resolveResourceAccess` semantics: a listed child must be a resource the caller can actually view; revoked inherited documents hidden
  actual: `listSharedCollectionRows` (library.repository.ts:461-499) lists ALL direct children with zero access predicate, and the document branch uses `canDiscoverSharedDocument` (310-332) whose `or not exists (revocation...)` branch discloses any non-revoked document regardless of actual access. Only gate is one parent-level `assertResourceAccess(view)` (library.service.ts:44-52). Latent today because mixed-ownership trees are unreachable via current APIs (create requires owning the parent; no move/transfer), but the model explicitly supports mixed ownership and any future move/transfer/editor-creation feature turns it into a real leak. Root document branch also omits the revocation filter (consistent only because direct-role keeps view). [thermos]

- description: Authorization logic — nearest precedence, revocation interaction, branch isolation, owner/admin exceptions, delete/restore
  status: PASS
  expected: Nearest lower-rank shadows farther higher-rank; revocation nulls inherited; roles never cross branches; owner/admin bypass; deleted subtree denied, restore reinstates
  actual: Depth-ordered resolution, revocation+direct-role interaction, branch isolation, differently-owned-descendant denial, and subtree delete/restore persistence all verified by non-vacuous integration assertions. No privilege expansion across unrelated trees. [thermos]

- description: Share procedure authorization / input validation / escalation
  status: PASS
  expected: Only admin/owner can share; only editor/viewer assignable; no admin grant; arbitrary collectionId denied
  actual: `roleName` is `z.enum(["editor","viewer"])` (collection-sharing.schema.ts:17); invite/changeRole/remove gated on collection share/revoke requirements (min admin) via `assertResourceAccess` (collection-sharing.service.ts:214-254); cross-user access → FORBIDDEN. Minor: no guard against target==actor/target==owner, but harmless (owner is always highest). [thermos]

- description: Error handling — native TRPC codes, no raw SQL leaks
  status: PASS
  expected: UNAUTHORIZED/NOT_FOUND/FORBIDDEN/BAD_REQUEST with masked internals
  actual: protectedProcedure → UNAUTHORIZED; `assertResourceAccess` → NOT_FOUND/FORBIDDEN; zod → BAD_REQUEST. One unreachable bare `new Error` in library.repository.ts:456. [thermos]

- description: Pagination / sorting / cursor stability across the mixed union
  status: PASS
  expected: Stable (sortKey, id) tie-break; limit+1 lookahead; no duplicate keys
  actual: `selectLibraryRows` orders by (title|updatedAt, id) with limit+1; unique `user_collection`/`user_document` indexes prevent dup union rows; equal-name pagination tested. [thermos]

- description: Performance — no per-row permission calls / N+1
  status: PARTIAL
  expected: Listings are single set-based statements; no per-result authorization loop
  actual: No JS-level N+1 (one SQL per listing; single `getCollectionAccess` per page). But `listSharedRootRows` evaluates a correlated recursive CTE per candidate row (O(N×depth)), and the outer LIMIT has no guaranteed pushdown into union branches; nested listing pays 2 correlated EXISTS per document. Acceptable at personal scale; re-flag as Shared grows. [thermos]

- description: Architecture boundaries (AGENTS.md) — pure policy, repository SQL ownership, no MCP
  status: PARTIAL
  expected: Policies pure; repositories own SQL; one source of truth for "what grants view"
  actual: `permissions.policy.ts` stays pure; no MCP/HTTP added. Concern: library repository embeds authorization semantics in SQL (library.repository.ts:252-332) that duplicate — and have already diverged from — `resolveResourceAccess` (nested-child filter vs `getDocumentAccess`; no-revocation branch vs policy). Two sources of truth for the view predicate is the root maintainability risk. [thermos]

- description: React Effect Usage Policy / derived state (code-style.md)
  status: PASS
  expected: No useEffect for derived state; derive during render; minimal local state
  actual: Zero useEffect/useMemo/useCallback in changed components; `members`/`canShare` derived during render; query gated with `enabled: open`. [react-quality-review]

- description: Share-flow correctness (invalidation, pending/loading, errors, double-submit)
  status: PARTIAL
  expected: Narrow invalidation + library.list pathKey; mutation error surfaces; controls disabled while pending
  actual: Invalidation correct (`invalidateQueries` on generated queryKey + `trpc.library.list.pathKey()`, collection-share-dialog.tsx:71-79); double-submit guarded (invite disabled while isInviting). Gaps: changeRole/remove mutations surface no error to the user (failed remove leaves the AlertDialog open silently); role Select not disabled while a role change is pending. Mirrors pre-existing document dialog. [react-quality-review]

- description: Role/email handling, owner display, empty states, label consistency
  status: PASS
  expected: Validated email + role; owner non-removable; labels capitalized consistently; empty state present
  actual: Email trimmed client + `z.email()` server (collection-invite-form.tsx:70; collection-sharing.schema.ts:17); duplicate invites upsert via `onConflictDoUpdate`; owner rendered as "Owner" badge and exempt from select/remove; `SHARING_ROLE_OPTIONS` centralizes lowercase values + capitalized labels; document sharing components updated consistently. [react-quality-review]

- description: Dialog UX / a11y (open/close, focus, escape, reset-on-reopen)
  status: PASS
  expected: Controlled dialog; primitive owns focus/escape; confirmation state reset between opens
  actual: Fully controlled (`open`/`onOpenChange`); `removeTarget` resets on close and after remove; invite form resets on success via `key={inviteResetKey}`. Stale email persists across close/reopen, identical to established document dialog. [react-quality-review]

- description: Props/typing conventions (`[ComponentName]Props`, no `any`, schema reuse)
  status: PARTIAL
  expected: Named `Props` types per code-style.md; narrow types; no duplicated schemas
  actual: No `any`; types strict and narrow. Gaps: `CollectionMemberList` types props inline (collection-member-list.tsx:32-41) while sibling `CollectionInviteForm` uses named props; `changeCollectionMemberRoleSchema` re-declares `z.enum(["editor","viewer"])` instead of reusing `sharingRoleSchema` (collection-sharing.schema.ts:30). [react-quality-review]

- description: Permission-aware UI (reflect effective access; hide what the user cannot do)
  status: PARTIAL
  expected: Actions hidden/disabled when the current user lacks access, matching the document-sharing pattern
  actual: Role selects/remove suppressed for non-sharers via server-gated `members.list`. Gaps: "Share" menu item always rendered (collection-row-actions.tsx:78-81) so a viewer sees a FORBIDDEN error pane instead of a form (document version gates on explicit isOwner/canEdit props); `CollectionMemberList` lacks a `currentUserId` prop, so a non-owner sharer can change their own role from the UI (DocumentMemberList guards this). [react-quality-review]

- description: Test quality — dangerous paths verified, non-vacuous
  status: PASS
  expected: Behavior-focused assertions on precedence, revocation, branch isolation, denial, lifecycle
  actual: document-member-list.test.tsx asserts tooltip disclosure, callback args incl. lowercase "viewer", and empty state via RTL role/text queries (not a snapshot). Integration suites assert real DB rows for the precedence/revocation/lifecycle paths and would fail loudly rather than pass vacuously. No unit tests for the new collection-sharing components (integration coverage for members router/service is thorough). [react-quality-review / thermos]

## Notes

- The core recursive-authorization contract (AC1–AC21) is implemented faithfully per static inspection; the two FAIL checks do not touch the resolver itself.
- **FAIL 1 (scope):** the bundled collection-sharing feature contradicts the ticket's Non-Goal #2 and the plan's boundary exit criterion. Decide whether this expansion is intentional product work; if so, the ticket/plan should be amended to keep the contract authoritative.
- **FAIL 2 (latent authz gap):** Shared nested child listing has no per-row access predicate and `canDiscoverSharedDocument` discloses any non-revoked document. Not exploitable with today's APIs (mixed-ownership trees unreachable), but the SQL has already diverged from `resolveResourceAccess`; harden before any move/transfer/editor-creation feature lands.
- **Hardening:** add `CYCLE` clause or depth cap to all new recursive CTEs (one-line defense against future move features).
- **UX gaps:** changeRole/remove mutations have no error surface; Share action not permission-gated in the row actions; member list lacks the self-role-change guard.
- **Process gap:** integration-test claims (42 files / 328 tests) were not re-verifiable locally (Postgres down). Re-run `pnpm test` with the test DB before merge, and record the `EXPLAIN (ANALYZE, BUFFERS)` output from Task 5 somewhere in-repo (currently only referenced in the PR body).
- Minor: cosmetic line-collapse at library.router.test.ts:331 (`{    const db = getDb();`); lint/typecheck still pass.

## Aggregate status rationale

Two accepted FAIL checks (scope expansion beyond ticket non-goal; latent Shared-listing authorization divergence) → overall **FAIL** per orchestration rules, despite the recursive-authorization core passing. Reviewers did not disagree on any evidence; thermos was preferred on the technical divergence (stronger file-level evidence).
