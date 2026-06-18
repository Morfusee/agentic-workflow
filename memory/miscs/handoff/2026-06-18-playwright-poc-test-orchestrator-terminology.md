# Handoff: Playwright POC Test Orchestrator Terminology

Date: 2026-06-18
Repo: `$HOME\Documents\Programming\playwright-poc`
User focus: Rename or clarify anything currently called `control-plane` if it may confuse future developers.

## Current Context

The user asked for an architecture analysis of the test-running setup. They described it as a "pseudo control plane" that runs tests on an interval and wanted terminology guidance.

After inspecting the repo, the current architecture is best described as a **singleton scheduled test orchestration worker** or **long-running scheduled test runner**, not a full distributed control plane.

## Evidence From Repo

- `scripts/control-plane.ts`
  - Loads `.env` optionally.
  - Resolves `CONTROL_PLANE_INTERVAL_MS` with default `15 * 60 * 1000` and minimum `60000`.
  - Runs `pnpm run db:migrate` once at startup.
  - Repeatedly runs `pnpm run test:website:db`, allows test failure, then runs `pnpm run allure:db`.
  - Sleeps after each completed cycle, so the cadence is fixed-delay, not fixed-rate.
  - Handles `SIGINT` and `SIGTERM` by killing active child process or clearing sleep timer.

- `playwright.website.config.ts`
  - Runs website specs only: `testMatch: ['**/website/*.website.spec.ts']`.
  - Uses `workers: 1`.
  - Uses DB reporter only plus line reporter.
  - Uses `TARGET_BASE_URL` as Playwright `baseURL`.

- `reporters/db-reporter.ts`
  - Persists a `test_runs` row on begin.
  - Persists individual `test_results` rows on test end.
  - Finalizes the `test_runs` row on end with aggregate counters and status.

- `scripts/allure-from-db.ts`
  - Reads DB-backed run/results rows.
  - Emits Allure-compatible result JSON into `allure-results-db`.
  - `pnpm run allure:db` then generates static Allure HTML into `allure-report-db`.

- `docker-compose.deploy.yml`
  - Defines `control-plane` service as worker-only, no exposed ports.
  - Defines `report-ui` as `nginx:alpine` serving `allure-report-db`.
  - Uses named volumes for report artifacts.

- `README.md`
  - Currently says "control plane" owns website test cadence.
  - Explicitly says run exactly one `control-plane` replica for this POC.
  - Notes multiple replicas would require a Postgres advisory lock, intentionally deferred.

## Terminology Conclusion

Current best name:

> Singleton scheduled test orchestration worker

Good shorter names:

- `test-orchestrator`
- `scheduled-test-runner`
- `test-scheduler`
- `website-monitor`, if the product framing is uptime/regression monitoring

Terms to avoid unless architecture grows:

- `control-plane`
- `control plane worker`
- `pseudo control plane`

Reason: the process controls cadence and subprocess execution, but does not coordinate a distributed fleet, reconcile desired state, lease work, or expose a scheduling API.

## Architecture Summary

Current flow:

```text
scheduled worker
  -> apply DB migrations once
  -> run Playwright website test cycle
  -> DB reporter writes run/results to PostgreSQL
  -> export DB rows into Allure result files
  -> generate static Allure report
  -> sleep CONTROL_PLANE_INTERVAL_MS
  -> repeat
```

Runtime topology:

```text
test orchestration worker container
  -> Playwright subprocess
  -> PostgreSQL result store
  -> shared Allure report volume

report-ui container
  -> nginx
  -> serves generated Allure HTML
```

## Important Nuance

The scheduler is **fixed-delay**, not fixed-rate:

```ts
await runCycle();
await sleep(intervalMs);
```

This means the delay starts after a cycle finishes. If tests take 3 minutes and the interval is 15 minutes, the next run starts about 18 minutes after the previous cycle started.

## Likely Follow-Up Work

If the user asks to proceed with renaming, first run the required git preservation workflow:

1. `git status`
2. `git diff`
3. Identify user-owned changes.
4. Preserve all unrelated/current work.

Potential rename scope:

- Rename `scripts/control-plane.ts` to something like `scripts/test-orchestrator.ts`.
- Rename package script `control-plane` to `test-orchestrator` or `test:scheduler`.
- Update `docker-compose.deploy.yml` service name and command.
- Update README section title and wording.
- Rename env vars only if user explicitly wants it, because `CONTROL_PLANE_INTERVAL_MS` may be a deployed/configured external interface. If renamed, consider a deliberate migration path or ask the user first.
- Search for all `control-plane`, `Control Plane`, `CONTROL_PLANE`, and `pseudo control plane` references before editing.

Potential env var replacement:

- Current: `CONTROL_PLANE_INTERVAL_MS`
- Better: `TEST_RUN_INTERVAL_MS`, `TEST_ORCHESTRATOR_INTERVAL_MS`, or `SCHEDULED_TEST_INTERVAL_MS`

Recommendation: ask before changing env var names because this can break deployed platform configuration.

## Suggested Skills

- `refactor`: if the user wants a surgical rename without changing behavior.
- `writing-plans`: if the user wants a staged rename plan before implementation.
- `requirements-reviewer`: after rename changes, validate that all user-facing terminology was updated consistently.

## Verification Ideas

After any rename implementation:

- Run a text search for old terms: `control-plane`, `Control Plane`, `CONTROL_PLANE`.
- Run TypeScript/package validation if available.
- Run the renamed script command with a short/safe configuration only if practical.
- Ensure deploy docs and compose service command still point to the renamed script.
