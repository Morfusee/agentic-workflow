# Drizzle DB Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move DB initialization, writes, reads, and env documentation to Drizzle with `DATABASE_URL` as the canonical PostgreSQL connection string.

**Architecture:** Add a Drizzle schema and shared DB client module, run migrations from a script, and update the existing reporter/export code to query through Drizzle. Keep existing CLI script names stable so the current run flow continues to work.

**Tech Stack:** Node.js, TypeScript, Playwright, PostgreSQL, `pg`, Drizzle ORM, Drizzle Kit.

---

## File Structure

- Create `db/schema.ts`: Drizzle table definitions and indexes for `test_runs` and `test_results`.
- Create `db/client.ts`: shared `.env` loading, `DATABASE_URL` resolution, `pg` pool creation, Drizzle instance creation, and cleanup.
- Create `drizzle.config.ts`: Drizzle Kit config using the schema and `DATABASE_URL`.
- Create `drizzle/0000_initial.sql`: initial migration matching the current schema.
- Create `drizzle/meta/_journal.json`: Drizzle migration metadata.
- Modify `scripts/db-init.cjs`: run Drizzle migrations instead of raw SQL.
- Delete `scripts/sql/001_init.sql`: schema source moves to Drizzle migration files.
- Modify `reporters/db-reporter.ts`: replace raw `pg` client queries with Drizzle inserts/updates.
- Modify `scripts/allure-from-db.cjs`: replace raw SQL reads with Drizzle query builders.
- Modify `package.json`: add Drizzle dependencies and migration/generation scripts.
- Modify `docker-compose.yml`: keep Docker-specific env vars and remove app reliance on `.env` for container app settings.
- Modify `README.md`: document `DATABASE_URL`, migration flow, hosted PostgreSQL usage, and local Docker defaults.
- Modify `.gitignore`: ignore `.env` while allowing `.env.example`.
- Create `.env.example`: safe local defaults and DB reporter toggles.

## Tasks

### Task 1: Add Drizzle Dependencies And Scripts

**Files:**
- Modify: `package.json`

- [ ] Add `drizzle-orm` to runtime dependencies and `drizzle-kit` to dev dependencies.
- [ ] Add scripts: `db:generate`, `db:migrate`, and keep `db:init` as the stable migration runner.
- [ ] Run `pnpm install`.

### Task 2: Add Schema And Shared Client

**Files:**
- Create: `db/schema.ts`
- Create: `db/client.ts`
- Create: `drizzle.config.ts`

- [ ] Define both tables and existing indexes in Drizzle.
- [ ] Add a shared DB client factory that resolves `DATABASE_URL` and can close the `pg` pool.
- [ ] Configure Drizzle Kit to load `.env` and use the shared schema.

### Task 3: Replace Raw SQL Init With Drizzle Migrations

**Files:**
- Create: `drizzle/0000_initial.sql`
- Create: `drizzle/meta/_journal.json`
- Modify: `scripts/db-init.cjs`
- Delete: `scripts/sql/001_init.sql`

- [ ] Add an initial migration equivalent to the existing SQL schema.
- [ ] Update `scripts/db-init.cjs` to call `drizzle-orm/node-postgres/migrator`.
- [ ] Run `pnpm run db:init` if a local DB is available.

### Task 4: Migrate Reporter Writes To Drizzle

**Files:**
- Modify: `reporters/db-reporter.ts`

- [ ] Replace direct `pg.Client` usage with the shared Drizzle connection.
- [ ] Insert the running `test_runs` record through Drizzle.
- [ ] Insert `test_results` rows through Drizzle.
- [ ] Update the final `test_runs` row through Drizzle.
- [ ] Preserve disabled and strict reporter behavior.

### Task 5: Migrate Allure Export Reads To Drizzle

**Files:**
- Modify: `scripts/allure-from-db.cjs`

- [ ] Replace direct `pg.Client` usage with the shared Drizzle connection.
- [ ] Select run IDs through Drizzle.
- [ ] Select joined result rows through Drizzle.
- [ ] Preserve output JSON format and CLI argument behavior.

### Task 6: Clean Env Docs And Local Defaults

**Files:**
- Create: `.env.example`
- Modify: `docker-compose.yml`
- Modify: `README.md`
- Modify: `.gitignore`
- Modify: `playwright.config.ts`

- [ ] Make `DATABASE_URL` the documented app connection string.
- [ ] Keep `POSTGRES_*` for Docker only.
- [ ] Remove first-class `PW_DB_URL` usage from config and docs.
- [ ] Document hosted PostgreSQL usage with `DATABASE_URL`.

### Task 7: Verify And Review Diff

**Files:**
- Inspect all modified files.

- [ ] Run `pnpm exec tsc --noEmit` or the nearest available validation command.
- [ ] Run `pnpm run db:generate` to confirm schema/config compatibility.
- [ ] Run `git diff` and confirm only intended files changed.
- [ ] Confirm unrelated user-owned work remains untouched.

## Self-Review

- Spec coverage: schema, migrations, reporter writes, export reads, env cleanup, and documentation are all mapped to tasks.
- Placeholder scan: no placeholders or deferred implementation steps remain.
- Type consistency: table names, file paths, and env names match the approved design.
