# Smoke Testing Client Query Live Updates Implementation Plan

> **For agentic workers:** Execute this follow-up on the existing `feat/86d3rttu6` worktree. Preserve all existing uncommitted work. Do not stage or commit.

**Goal:** Remove the Smoke Testing page refresh from SSE handling by moving cards and run history behind a client TanStack Query that SSE invalidates directly.

**Architecture:** Keep authentication and the `MainShell` in the server page. Add one authenticated `/api/smoke-runs` read route that returns the existing Smoke app cards and filtered paginated run history. A client page-content component derives the existing URL filters with `useSearchParams`, fetches that route through a Smoke-specific query, and renders the existing cards/table. The SSE hook invalidates the page query key and the existing run-details keys; it must not call `router.refresh()`.

**Boundaries:** Preserve PostgreSQL as the source of truth, the existing Smoke services, URL filter behavior, details route/query, PgDog/SSE transport, and all E2E code. Do not add polling or a fallback timer. Leave all implementation and plan documents uncommitted and unstaged.

---

## File Map

- Create `mihc/nextjs/app/api/smoke-runs/route.ts`: authenticated page-data read route with existing `app`, `page`, `limit`, and `tab` query parameters.
- Create `mihc/nextjs/feature/smoke/query/smoke-testing.query.ts`: URL-keyed TanStack Query, API response typing, and Date revival for existing Smoke component types.
- Create `mihc/nextjs/feature/smoke/components/smoke-testing-content.tsx`: client loading/error/query coordinator that renders existing cards and table.
- Create `mihc/nextjs/__tests__/unit/app/api/smoke-runs/route.test.ts`: route authentication, parameter forwarding, and response tests.
- Create `mihc/nextjs/__tests__/unit/feature/smoke/smoke-testing.query.test.ts`: serialized date revival and query URL construction tests.
- Modify `mihc/nextjs/app/smoke-testing/page.tsx`: remove server data fetching/Suspenser and render the client content plus existing details sheet.
- Modify `mihc/nextjs/feature/smoke/hooks/use-smoke-run-events.ts`: remove `next/navigation` and `router.refresh`; invalidate the page query key on `ready` and `smoke-change`.
- Modify `mihc/nextjs/__tests__/unit/feature/smoke/use-smoke-run-events.test.tsx`: assert page-query invalidation and remove refresh assertions/mocks.

## Task 1: Add the client page-data API and query

- [ ] Add route tests for unauthenticated rejection and authenticated parameter forwarding.
- [ ] Implement `GET /api/smoke-runs` with `getCurrentUser`, existing `getSmokeTestApps`, and existing `getPaginatedSmokeTestRuns`. Parse positive `page`, clamp `limit` to 1–100 using the page’s existing bounds, accept only `SmokeTestRunStatus` values for `tab`, and return `ok({ appName, apps, smokeRuns })`.
- [ ] Add a query module keyed by `['smoke-runs', 'page', searchParams]`. Fetch `/api/smoke-runs?${searchParams}`, throw on non-OK/error payloads, and revive app/run `createdAt`, `updatedAt`, `checkedAt`, and `completedAt` values to `Date` objects before returning `SmokeTestApp[]` and `Paginated<SmokeTestRun>`.
- [ ] Add query tests for the URL and Date conversion contracts.

## Task 2: Render page data without a refresh

- [ ] Add a client `SmokeTestingContent` component that reads `useSearchParams().toString()`, calls the Smoke page query with `keepPreviousData`, renders `SmokeTestingCardsSkeleton` while initially loading, renders a concise error state on failure, and passes query data to the existing `SmokeTestingAppsCard` and `SmokeTestingTable`.
- [ ] Remove `getData`, `Suspenser`, server Smoke data imports, and the old data promise from `page.tsx`. Keep `requireAuthenticated`, `AppShell`, `MainShell`, `SmokeTestingLiveUpdates`, and `SmokeRunDetailsSheet` mounted.
- [ ] Keep the existing table/card components and URL state as the source of filter, app, pagination, and selection behavior.

## Task 3: Make SSE invalidate client data only

- [ ] On `ready`, invalidate `SmokeTestingQueryKey` and the base `SmokeRunDetailsQueryKey`.
- [ ] On `smoke-change`, ignore empty payloads, invalidate `SmokeTestingQueryKey`, and invalidate only `[...SmokeRunDetailsQueryKey, runId]`.
- [ ] Remove every `router.refresh` call and `next/navigation` mock/import from the hook and tests. Keep native EventSource reconnect and unmount cleanup unchanged.

## Task 4: Verify and preserve scope

- [ ] Run focused route/query/hook/Smoke tests, then the full Next.js test, TypeScript, and lint commands.
- [ ] Run `rg` to confirm no `router.refresh`, `window.location.reload`, Smoke polling identifiers, or fallback timers remain.
- [ ] Run `git diff --check`, `git status --short`, and confirm no E2E, migration, package, or previously approved-file changes were removed.
- [ ] Leave all changes unstaged and uncommitted for review.
