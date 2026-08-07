# PR #12 review-comment triage

overall_status: FAIL

## Review scope

- Provider: GitHub PR #12, `feat/mcp-03-endpoint-reads` -> `main`
- URL: https://github.com/Morfusee/markdown2share/pull/12
- Diff: 43 files, 3,399 additions, 58 deletions
- Provider feedback: four review submissions; the first two are duplicates; no issue comments, inline comments, or review threads
- Reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`
- Working tree: read-only; existing untracked `docs/plans/2026-08-05-pr9-review-hardening-plan.md` preserved

## Checks

### 1. Unexpected MCP error masking and logging

- status: FAIL
- expected: Unknown errors are logged server-side and exposed on the MCP wire only as a generic internal error.
- actual: The adapter uses `appRouter.createCaller`, bypassing the HTTP formatter; the original cause is rethrown and the MCP SDK serializes `error.message`. `mcpProcedure` has no masking/logging boundary. Valid and HIGH; merge blocker.

### 2. Deleted-ancestor consistency

- status: FAIL
- expected: `list_documents` and `get_draft` use one documented active-tree contract.
- actual: Listing excludes documents below a deleted ancestor, while point access plus `findActiveDraftRecord` checks only the document row. Valid and MEDIUM; not a cross-user leak, but a contradictory public API.

### 3. Route-level insufficient-scope response

- status: FAIL
- expected: A token lacking `documents:read` receives the planned RFC 6750 HTTP 403 before MCP dispatch.
- actual: The route calls `authenticateMcpRequest(request)` without required scopes, so the production 403 branch is unreachable. Per-tool middleware remains safe but returns generic JSON-RPC `FORBIDDEN`. Valid and MEDIUM.

### 4. Search wildcard semantics

- status: PARTIAL
- expected: Search is a literal trimmed substring unless wildcard syntax is documented.
- actual: `%` and `_` remain ILIKE operators. Parameterization and authorization remain intact. Valid LOW correctness hardening, consistent with older repository search behavior.

### 5. Deleted-ancestor test coverage

- status: PARTIAL
- expected: Owner, administrator, and direct-share point/list behavior is pinned after choosing semantics.
- actual: Admin listing omission is already tested; owner/admin point access and `get_draft` below a deleted ancestor are not. The original comment is overstated; the remaining gap is real and largely subsumed by check 2.

### 6. Accessible-list query performance

- status: PARTIAL
- expected: Query/index changes are evidence-driven.
- actual: `date_trunc` prevents direct use of raw timestamp indexes and correlated recursive predicates may scale poorly, but no `EXPLAIN ANALYZE` or production cardinality evidence demonstrates a current defect. Valid LOW follow-up, not a merge blocker.

### 7. MCP/library ownership and pass-through workflows

- status: FAIL
- expected: Library does not import MCP transport contracts and workflows add meaningful ownership/coordination.
- actual: `accessible-library.service.ts` imports MCP schemas/cursor utilities while two MCP list workflows only forward calls. Valid MEDIUM maintainability issue in PR scope.

### 8. Cursor length and duplicate parsing

- status: PARTIAL
- expected: Encoded cursors have a conservative size bound and a single clear decode boundary.
- actual: Cursor has `.min(1)` with no maximum and is decoded in schema refinement and again in the service. Valid LOW hardening; the size cap matters more than the negligible duplicate parse.

### 9. Detached dev-server lifecycle

- status: PARTIAL
- expected: Stop verifies process identity, awaits termination, and does not report success prematurely.
- actual: A stale reused PID can identify an unrelated process tree; Windows `taskkill` is not awaited. Readiness polling is an enhancement because output says "starting". The unawaited verification-server close is real but outside the PR diff. PID identity is MEDIUM; the rest LOW.

### 10. PR evidence accuracy and reproducibility

- status: PARTIAL
- expected: Counts match committed suites and Task 7 commands/output are available in the PR body.
- actual: Route evidence is stale (14 static `it()` blocks, versus 13 claimed; runtime cases may be higher). The cursor/schema claim of 33 is correct; the review's 32 correction is false. External `task-7-evidence.txt` is not available in the repository or PR. Valid LOW documentation cleanup.

### 11. Consent trust UI

- status: PARTIAL
- expected: Consent and missing-client states use the established centered/branded public shell.
- actual: Both render without a shell. Valid MEDIUM UX/trust debt, but consent files are unchanged in `main...HEAD`, so this is a separate follow-up unless PR scope is intentionally expanded. A remote client logo requires a separate trusted-image/product contract.

## Notes

- No cross-user authorization bypass was found in PR #12.
- SQL remains parameterized, live permission checks remain enforced, and public outputs are deliberately selected.
- Recommended in-PR order: raw-error boundary; active-tree semantics; route-level 403; ownership cleanup plus cursor bound; literal search; PID safety; evidence correction.
- Recommended separate work: consent redesign and benchmark-driven query/index optimization.
- The Thermos reviewer could not spawn its two nested reviewers because all four collaboration slots were occupied; it applied both underlying rubrics directly and disclosed the constraint.
- A focused test command started by the primary reviewer exceeded the 60-second command budget without producing usable output. The requirements reviewer independently reported 39/39 focused cursor/procedure tests passing; this does not cover the confirmed wire-error leak.
