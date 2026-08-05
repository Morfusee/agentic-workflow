# Review: PR #9 feat: recursive collection authorization

- Date: 2026-08-04
- Subject: PR #9 `feat/recursive-collection-authorization` -> `main`
- URL: https://github.com/Morfusee/markdown2share/pull/9
- Diff: `git diff main...FETCH_HEAD` (10 files, +1039 / -36, all under `nextjs/`)
- Reviewers: `requirements-reviewer`, `thermos` (thermo-nuclear-review + thermo-nuclear-code-quality-review synthesized)

## overall_status: PARTIAL

Reviewers disagree at the headline level (requirements-reviewer: PASS; thermos: PARTIAL).
Thermos carries stronger file-level evidence: the PR's own "depth-bounded" claim is
contradicted by the code (unbounded `union all` recursion, no cycle guard). Per the
conflict rule, the result with stronger file-level evidence wins. Overall: PARTIAL.
No FAIL-level defect was found; all PARTIALs are hardening/verification gaps, not
confirmed functional breakage.

## Checks

### requirements-reviewer (functional coverage vs PR requirements)

1. `findNearestCollectionRole` — single upward recursive CTE, set-based, nearest (depth) role, active-only.
   status: **PASS**
   actual: permissions.repository.ts `with recursive collection_ancestors(id,parent_id,depth)` seeded at target (depth 0), walks parents with `deleted_at is null`, `order by depth asc limit 1`.
   note: no explicit depth cap — bounded by tree height; cyclic parents would recurse to DB limit.
2. `getCollectionAccess` classifies depth-0 direct, depth>0 inherited.
   status: **PASS** — permissions.service.ts:84-87.
3. `getDocumentAccess` resolves inherited role from document's collection ancestry, keeps direct document role + revocation.
   status: **PASS** — permissions.service.ts:118-127; test asserts assignedRole + inheritedRole + isRevoked simultaneously.
4. Direct-over-inherited precedence preserved without policy change.
   status: **PASS** — `resolveResourceAccess` unchanged; `assignedRole ?? (isRevoked ? null : inheritedRole)`.
5. Breadcrumbs may start at authorized shared subtree root; adjacency still validated per later segment; inaccessible ancestors never loaded.
   status: **PASS** — collections.service.ts:54 guard change; router tests cover FORBIDDEN root and BAD_REQUEST non-adjacent.
6. Shared root lists topmost roots (excluding reachable-through-assigned-ancestor) + standalone shared docs.
   status: **PASS** — `hasNoAssignedCollectionAncestor` / `hasNoAssignedCollectionForDocument`; test asserts root = [rootCollection, sharedDocument].
7. Nested Shared pages list authorized immediate children with revocation filtering (owner/direct-role exceptions preserved).
   status: **PASS** — `canDiscoverSharedDocument` = owned OR no revocation OR direct view role; nested-branch test asserts direct-role exception.
8. Nested pages authorized once per page via the recursive contract.
   status: **PASS** — library.service.ts:43-49 gate through `getCollectionAccess` -> `findNearestCollectionRole`.
9. Native FORBIDDEN for `library.list` inaccessible `collectionId` + `scope:"shared"`.
   status: **PASS** — `assertResourceAccess` -> `forbiddenError()` TRPCError; router test asserts code + message.
10. Tests cover recursive lifecycle, truncated breadcrumbs, Shared discovery, pagination stability, native denial.
    status: **PASS** — new recursive-permissions.service.test.ts + updates; deep inheritance, precedence, ownership, branch isolation, moves (role rows unchanged), delete/restore, denial.
11. No new DB indexes required.
    status: **PASS** — no schema/migration/index DDL in diff.

QA scenarios:
12. Viewer on root grants descendant/document access at all depths; Shared lists only topmost root + direct docs.
    status: **PASS**
13. Lower-rank role on nearer descendant overrides higher-rank farther up.
    status: **PASS**
14. Document revocation removes it from Shared while directly assigned docs remain discoverable.
    status: **PARTIAL** — direct-role exception is tested; the pure-revocation branch (no direct role -> disappears from Shared listing) is implemented but not asserted in isolation (root test exclusion is via ancestor filter, not revocation).
15. Moving a subtree re-derives inherited access without copying role rows.
    status: **PASS** — move test asserts access flips and actor role rows unchanged.
16. Soft-deleted subtree denied; restored subtree accessible again.
    status: **PASS** — delete/restore test asserts `resourceExists: false` then restored with revocations intact.

### thermos (security/correctness + code quality, deduplicated)

17. Recursive CTE direction/depth/soft-delete/cycle-safety.
    status: **PARTIAL** (source: both)
    expected: depth-bounded + cycle-safe per PR claim.
    actual: direction, depth semantics, active filtering correct (permissions.repository.ts:81-105), BUT `union all` with no depth bound and no `cycle` guard (line 87) — contradicts "depth-bounded". A parent cycle would recurse to DB limit and 500 every access check on that subtree. Latent today (no move-parent API; child ownership requires same owner), and the codebase already guards cycles with `union` in `softDeleteCollectionTree` — authors know the pattern and did not apply it here.
18. `getCollectionAccess`/`getDocumentAccess` classification, precedence, ownership/revocation preservation.
    status: **PASS** (source: thermo-nuclear-review) — direct/inherited mapping correct; all precedence edges asserted by tests; no escalation beyond stated intent.
19. Revocation semantics — direct document role overrides a revocation row.
    status: **PARTIAL** (source: both)
    actual: `canDiscoverSharedDocument` keeps direct-grant docs visible despite revocation (library.repository.ts:310-330); policy keeps direct role effective. REVOKE of a directly-shared document is a no-op. Tests assert this as intended, so not a code defect — but a sharp footgun: operators expecting REVOKE to strip access will be surprised. Contract should be stated explicitly.
20. Shared root/nested listing — authorization on every branch, dedup, no over-fetch, no leak.
    status: **PARTIAL** (source: both)
    actual: root dedup and FORBIDDEN propagation correct. BUT nested child-collection query has zero per-row authorization predicate (library.repository.ts:463-474); safe only because the sole public entry runs the service guard (library.service.ts:44-50). Any future caller skipping the guard silently lists foreign children. Defense-in-depth gap.
21. Breadcrumb change does not leak inaccessible ancestors.
    status: **PASS** (source: thermo-nuclear-review)
22. SQL injection / parameterization.
    status: **PASS** (source: thermo-nuclear-review) — all user input bound via drizzle parameters; no injection surface.
23. Type safety at auth boundary.
    status: **PARTIAL** (source: both) — no `any`. Three `as unknown as typeof` double-casts at unionAll boundaries (pre-existing pattern, runtime-safe); `let inheritedRole: ResourceRole | null | undefined` then `toResourceRole` relies on flow-narrowing.
24. Test quality — asserts risky behaviors, not happy paths.
    status: **PASS** (source: thermo-nuclear-code-quality-review) — all five risk areas + native FORBIDDEN + dedup covered.
25. Code structure — duplication, dead code, decomposition.
    status: **PARTIAL** (source: thermo-nuclear-code-quality-review) — library.repository.ts grows to 492 lines (acceptable) with reasonable split; two near-identical recursive CTEs could be one parameterized fragment (library.repository.ts:252-277 vs 281-305); unreachable `new Error(...)` in `listSharedCollectionRows` (line 456) would surface as INTERNAL_SERVER_ERROR instead of BAD_REQUEST; fixture builders duplicated across test files; formatting glitch at library.router.test.ts:133.
26. Runnable verification of PR-claimed evidence (328 tests, typecheck/lint/build exit 0, EXPLAIN ANALYZE).
    status: **BLOCKED** — READ_ONLY review could not run tests/build against the PR branch (working tree is main). PR evidence is testimony, not proof. Notably the "depth-bounded" claim is contradicted by code (check 17).

### review-orchestrator (reachability follow-up, post-review)

27. Collection-role assignment is reachable by any user or API path.
    status: **PARTIAL**
    expected: A production write path (UI or tRPC/service) that creates `user_roles` rows scoped to `collectionId`, so the new recursive reader is reachable.
    actual: No production code writes collection-scoped roles. The only production `user_roles` writer is `document-members.repository.ts` (document-only scope, `upsertDocumentMemberRole` values `{ documentId, roleId, userId }`). No collection router/service/UI mutation exists (features/ grep for collection-scoped role writes: 0 matches; routers: collections, documents, library only). All collection-role rows in tests are created via direct `db.insert(userRoles)` fixtures. `findNearestCollectionRole` therefore reads rows the app cannot create — the resolver and the Shared collection-tree behavior are dormant until a consumer (MDP-30 / delegated-user MCP authorization) lands. PR is explicitly framed as that prerequisite, so this is consistent with stated scope, but the reviewer should have flagged the feature as unreachable/unexercisable by end users.

## Notes

- Post-review finding added after user challenge: no sharing UI exists for collections; the review passed because the PR's acceptance criteria covered resolver semantics only and never claimed a collection-sharing write path. Reachability was not part of the criteria and was not flagged by either reviewer — a review gap.
- No PR-discussion comments or reviews exist to incorporate (gh api returned empty).
- Aggregate status computed: mixed PASS/PARTIAL with one BLOCKED, zero FAIL -> PARTIAL.
- Reviewer conflict on overall status resolved toward thermos (stronger file-level evidence on check 17).
- The inherited-delete expansion (inherited admin on ancestor can soft-delete a foreign-owned subtree) is the branch's stated intent and is reported as context, not a defect; blast radius is large.

## Recommended follow-ups (informational; not blocking)

1. Add a cycle/depth guard to the recursive CTE in `findNearestCollectionRole` (or switch to `union`), reconciling with the PR's "depth-bounded" claim.
2. Decide and document the intended revocation-vs-direct-grant contract (REVOKE is currently a no-op against direct grants).
3. Add a per-row authorization predicate to the nested Shared child-collection query, or constrain `listSharedCollectionRows` so it can only be reached through the guarded service entry.
4. Add one test asserting the pure-revocation removal branch in a Shared listing.
5. Replace the unreachable `new Error(...)` guard and deduplicate the two recursive CTE fragments.

## Reviewer contract compliance

Both reviewers returned the `REVIEWER_RESULT` contract, cited file/line evidence, and respected READ_ONLY scope. No results were rejected.
