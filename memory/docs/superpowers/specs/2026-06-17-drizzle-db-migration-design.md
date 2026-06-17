# Drizzle DB Migration Design

## Goal

Migrate the Playwright monitoring database layer from raw SQL initialization and raw `pg` queries to Drizzle-managed schema, migrations, and query access. The result should support local Docker PostgreSQL and hosted PostgreSQL through one canonical application connection string.

## Scope

- Add Drizzle schema definitions for the existing `test_runs` and `test_results` tables.
- Add Drizzle migration configuration and scripts.
- Replace the current DB initialization script with a Drizzle migration runner.
- Update the Playwright DB reporter to write through Drizzle.
- Update the Allure DB export script to read through Drizzle.
- Clean up environment variable usage and documentation for local and hosted PostgreSQL.

## Non-Goals

- Change the database shape or reporting behavior beyond what Drizzle requires.
- Add a new hosted database provider integration.
- Rewrite Playwright tests or Allure generation behavior.
- Add compatibility abstractions for multiple database engines.

## Environment Contract

`DATABASE_URL` is the canonical application database URL for local and hosted PostgreSQL.

Local Docker variables remain limited to the PostgreSQL container:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

Reporter/runtime toggles remain:

- `PW_DB_ENABLED`
- `PW_DB_REPORTER_STRICT`
- `PW_RUN_ENV`

`PW_DB_URL` should be removed from first-class docs and code paths unless a short compatibility alias is necessary during implementation. Prefer failing clearly when DB persistence is enabled and `DATABASE_URL` is missing.

## Architecture

Add a small Drizzle DB module:

- `db/schema.ts`: exports `testRuns` and `testResults` table definitions and indexes matching the existing SQL schema.
- `db/client.ts`: loads `.env`, resolves `DATABASE_URL`, creates a `pg` pool, and exposes a Drizzle database instance plus cleanup helpers.
- `drizzle.config.ts`: points Drizzle Kit at the schema and migration output directory.

Migration/init flow:

- Generated migrations become the source of truth for schema initialization.
- `scripts/db-init.cjs` becomes a migration runner or is replaced by a script that runs Drizzle migrations.
- `pnpm run db:init` remains as a stable command, but it runs migrations.

Runtime query flow:

- `reporters/db-reporter.ts` inserts and updates `test_runs` and inserts `test_results` through Drizzle.
- `scripts/allure-from-db.cjs` selects run IDs and joined results through Drizzle query builders.
- Existing output formats and script names remain unchanged.

## Data Model

The Drizzle schema must preserve the current SQL tables:

- `test_runs`: run metadata, counters, status, timestamps, CI metadata, and base URL.
- `test_results`: individual test result records, result metadata, attachments, timing, and foreign key to `test_runs` with cascade delete.

Indexes must preserve current lookup patterns:

- `test_runs(started_at DESC)`
- `test_runs(status, started_at DESC)`
- `test_results(run_id)`
- `test_results(status, project)`
- `test_results(file, title)`

## Error Handling

- If DB reporting is disabled, tests run without DB connections.
- If DB reporting is enabled and `DATABASE_URL` is missing, reporter records a clear error and follows existing strict/non-strict behavior.
- Migration failures should exit non-zero with the underlying error message.
- Export failures should keep the current fail-fast behavior.

## Testing And Verification

- Generate or check Drizzle migrations from the schema.
- Run the migration script against local Docker PostgreSQL when available.
- Run TypeScript checking or the nearest available validation command.
- Run existing monitoring/report scripts if the local DB is available.
- Verify the final diff only changes Drizzle migration, DB access, env docs, and package scripts.

## Open Decisions Resolved

- Drizzle should be used for both schema management and DB access.
- `DATABASE_URL` is the canonical app connection string.
- Existing command names should remain stable where possible.
