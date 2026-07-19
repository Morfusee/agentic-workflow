# MIHC PR #12 review

overall_status: FAIL

## Review scope

- Provider: `markvalenzuela-mmdc/mihc#12`
- Exact head: `26374d5cdf83fae57d08732e431b68f7946d395f`
- Scope: PR diff and immediate tests/callers affected by the diff
- Reviewers: `requirements-reviewer`, `thermos`, `react-quality-review`
- Mode: read-only; no GitHub comments or code changes published

## Checks

- description: Keep aggregate verification free of live submission side effects.
  status: FAIL
  expected: The opt-in live E2E suite must not run as part of the ordinary aggregate test command.
  actual: `justfile:123` adds the suite to `test-all`, while `playwright/tests/e2e/enrollmate/apply-now.spec.ts:106` submits a real UAT application.

- description: Validate lifecycle step IDs before creating the running-row lock.
  status: FAIL
  expected: Only canonical, existing step IDs reach mapping and persistence, and failures release/finalize the lock.
  actual: The producer and consumer accept arbitrary non-empty strings. An unknown ID reaches the foreign-key insert in `persist-e2e-run.ts`; the completion transaction rolls back its status update and leaves the profile locked as `running`.

- description: Bucket confirmation results into the enrollment-confirmation lifecycle step.
  status: FAIL
  expected: `submission-confirmed` maps to `enrollment_confirmation`.
  actual: `map-e2e-results.ts` checks substring `submit` before `submission-confirmed`, so the first-match dispatcher always classifies confirmation as `verification`.

- description: Keep the documented E2E command platform-neutral.
  status: FAIL
  expected: `pnpm run test:e2e` works on supported Windows and POSIX developer environments.
  actual: `playwright/package.json:9` uses POSIX-only inline environment assignment and fails before Playwright starts under Windows `cmd.exe`.

- description: Preserve the server action's typed error contract and unit-test isolation.
  status: FAIL
  expected: Database failures return `err(...)`, and unit tests mock the new preflight query.
  actual: `request-e2e-test.action.ts:37-41` performs the query before its only `try/catch`; the unchanged action tests mock neither `getDb` nor the query and can hit a real database requirement.

- description: Enforce profile eligibility at the server execution boundary.
  status: FAIL
  expected: Only an active form matching the current EnrollMate definition may trigger a live submission.
  actual: The UI has an active-form gate, but the server action and consumer accept any existing profile/form, so a direct authenticated action call bypasses it.

- description: Provide verification evidence for the new automated E2E pipeline.
  status: PARTIAL
  expected: A live E2E or consumer integration run demonstrates the advertised end-to-end workflow and persistence.
  actual: The PR reports lint, typecheck, migrations, and smoke tests only; the exact head has no attached GitHub Actions checks and no live E2E/pipeline evidence.

## Notes

- The exact PR head is mergeable but has no submitted reviews, review threads, workflow runs, or commit status checks.
- The local remote-tracking PR branch was stale, so review evidence came from the GitHub connector at the exact head.
- No repository files were changed.
