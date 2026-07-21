# E2E Aborted Error Capture Design

## Goal

Ensure aborted EnrollMate E2E runs persist Playwright diagnostics when a test fails before its first `assertCheck` annotation.

## Scope

- Modify only `playwright/server/runner/map-e2e-results.ts` and its focused unit tests.
- Preserve existing handling of report-level errors.
- Collect error messages from the final Playwright attempt's `errors` array, falling back to its singular `error` field.
- Deduplicate messages shared by report-level and attempt-level error shapes.
- Attach collected messages only to the first selected step when the mapped run is `aborted`.
- Do not change successful or completed-run notes, the database schema, persistence shape, runner process, or frontend.

## Data Flow

`mapE2eResults` initializes a `Set<string>` with non-empty `report.errors` messages. While traversing each test, it inspects only the final attempt and adds its non-empty messages. After check annotations determine the overall status, the mapper joins the set with newlines into `steps[0].note` only for an aborted run.

## Retry and Error Handling

Only the final attempt is inspected so diagnostics do not include stale failures from retries. The `errors` array is authoritative when non-empty; `error` is the fallback for Playwright report variants. A set prevents duplicate persisted messages.

## Verification

Add focused mapper tests covering:

1. An aborted run with a singular final-attempt `error`.
2. An aborted run with final-attempt `errors`.
3. Deduplication across report-level and attempt-level messages.
4. A completed run that does not receive an aborted-run note.

Run the focused Node test file and the Playwright project typecheck/unit-test commands appropriate to the repository.

## Residual Limitation

When `runE2e` returns `report === null`, no Playwright report diagnostic exists for the mapper to persist. Capturing runner spawn or unreadable-report errors is outside this fix.
