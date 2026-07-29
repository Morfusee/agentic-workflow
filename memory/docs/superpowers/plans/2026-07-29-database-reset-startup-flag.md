# Database Reset Startup Flag Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `DATABASE_RESET=true` destructively rebuild and production-bootstrap the application database whenever the Next.js container starts.

**Architecture:** Keep the destructive operation in the existing reset script and select it from the Next.js Docker `CMD`; otherwise run the existing idempotent database release. Compose continues passing env files normally, while the redundant build-only reset service and command are removed.

**Tech Stack:** Docker Compose, POSIX shell, TypeScript, Drizzle ORM, Vitest, Just

---

## File map

- Modify `nextjs/scripts/reset-production-database.ts`: replace the phrase confirmation with the strict boolean flag.
- Modify `nextjs/__tests__/unit/scripts/reset-production-database.test.ts`: prove exact-`true`, false, missing, and production-environment behavior.
- Modify `nextjs/Dockerfile`: choose reset or release on every container startup.
- Modify `docker/compose.build.yml`: remove the obsolete one-shot reset profile service.
- Modify `commands/docker.just`: remove the obsolete `build-reset` recipe.
- Modify `docker/.env.build` and `docker/.env.deploy`: configure the local ignored environments.
- Modify `docker/.env.build.example` and `docker/.env.deploy.example`: document the default setting.
- Modify `README.md`, `docker/README.md`, `docs/docker-commands.md`, and `docs/containerized-infrastructure.md`: replace the old explicit reset workflow with startup-flag behavior and its restart warning.

### Task 1: Replace the reset confirmation with a boolean guard

**Files:**
- Modify: `nextjs/__tests__/unit/scripts/reset-production-database.test.ts`
- Modify: `nextjs/scripts/reset-production-database.ts`

- [ ] **Step 1: Rewrite the unit-test environment around `DATABASE_RESET`**

Use this shared environment:

```ts
const environment = {
  NODE_ENV: "production",
  DATABASE_URL: "postgresql://user:password@database:5432/mihc",
  DATABASE_RESET: "true",
};
```

Replace the confirmation test with false, missing, and non-exact cases:

```ts
it.each(["false", undefined, "TRUE", "1"])(
  "refuses to reset when DATABASE_RESET is %s",
  async (enabled) => {
    const candidate = {
      ...environment,
      DATABASE_RESET: enabled,
    };

    await expect(resetProductionDatabase(candidate)).rejects.toThrow(
      "Set DATABASE_RESET=true.",
    );

    expect(resetDatabaseSchema).not.toHaveBeenCalled();
    expect(releaseDatabase).not.toHaveBeenCalled();
  },
);
```

Keep the existing non-production and successful reset-order tests, changing
their input to the new shared environment.

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```powershell
cd nextjs
pnpm exec vitest run __tests__/unit/scripts/reset-production-database.test.ts
```

Expected: FAIL because the script still reads
`DATABASE_RESET_CONFIRMATION`.

- [ ] **Step 3: Implement the exact-true guard**

Replace the old constant and condition with:

```ts
const RESET_ENABLED = "true";

if (environment.DATABASE_RESET !== RESET_ENABLED) {
  throw new Error(
    "Refusing to reset the database. Set DATABASE_RESET=true.",
  );
}
```

Retain the `NODE_ENV=production` check, schema reset, and call to
`releaseDatabase`.

- [ ] **Step 4: Run the focused test and TypeScript check**

Run:

```powershell
cd nextjs
pnpm exec vitest run __tests__/unit/scripts/reset-production-database.test.ts
pnpm exec tsc --noEmit
```

Expected: all reset-script tests PASS and TypeScript exits zero.

- [ ] **Step 5: Commit the guard change**

```powershell
git add nextjs/scripts/reset-production-database.ts nextjs/__tests__/unit/scripts/reset-production-database.test.ts
git commit -m "fix(database): use boolean startup reset guard"
```

### Task 2: Select reset behavior during container startup

**Files:**
- Modify: `nextjs/Dockerfile`
- Modify: `docker/compose.build.yml`
- Modify: `commands/docker.just`

- [ ] **Step 1: Replace the Docker startup command**

Use a single startup branch:

```dockerfile
CMD ["sh", "-c", "cd /app/nextjs && if [ \"$DATABASE_RESET\" = \"true\" ]; then ./node_modules/.bin/tsx scripts/reset-production-database.ts; else ./node_modules/.bin/tsx scripts/release-database.ts; fi && unset PROD_MAINTAINER_PASSWORD && cd /app && exec node server.js"]
```

This deliberately executes the destructive path again after any Docker
restart while the flag remains `true`.

- [ ] **Step 2: Remove the obsolete `db-reset` service**

Delete the complete `db-reset` service block from
`docker/compose.build.yml`. Keep `nextjs`, `playwright`, and all included
infrastructure unchanged.

- [ ] **Step 3: Remove the obsolete Just recipe**

Delete only this recipe from `commands/docker.just`:

```just
# Hard-reset the build database, then restart the production-like app services
build-reset:
    @docker compose --env-file "{{ justfile_directory() }}/docker/.env.build" -f "{{ justfile_directory() }}/docker/compose.build.yml" -p docker stop nextjs playwright
    @docker compose --env-file "{{ justfile_directory() }}/docker/.env.build" -f "{{ justfile_directory() }}/docker/compose.build.yml" -p docker --profile reset run --rm -e DATABASE_RESET_CONFIRMATION=reset-local-build db-reset
    @docker compose --env-file "{{ justfile_directory() }}/docker/.env.build" -f "{{ justfile_directory() }}/docker/compose.build.yml" -p docker up -d nextjs playwright
```

- [ ] **Step 4: Validate both Compose files and the Just inventory**

Run:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml config --quiet
docker compose --env-file docker/.env.deploy -f docker/compose.deploy.yml config --quiet
just --list --list-submodules --unsorted
```

Expected: both Compose configurations validate; `docker build-reset` is no
longer listed; `docker build` and `docker deploy` remain listed.

- [ ] **Step 5: Commit container startup wiring**

```powershell
git add nextjs/Dockerfile docker/compose.build.yml commands/docker.just
git commit -m "feat(docker): reset database from startup flag"
```

### Task 3: Configure and document the startup flag

**Files:**
- Modify: `docker/.env.build`
- Modify: `docker/.env.deploy`
- Modify: `docker/.env.build.example`
- Modify: `docker/.env.deploy.example`
- Modify: `README.md`
- Modify: `docker/README.md`
- Modify: `docs/docker-commands.md`
- Modify: `docs/containerized-infrastructure.md`

- [ ] **Step 1: Add the flag to environment files**

Add this beside `DATABASE_URL` in all four environment files:

```dotenv
DATABASE_RESET=false
```

The ignored `.env.build` and `.env.deploy` files affect the current machine.
The tracked example files establish the repository default.

- [ ] **Step 2: Update the command and environment documentation**

Remove `just docker build-reset` from the root command table and all live
documentation. Document this exact operational contract:

```text
DATABASE_RESET=false preserves application data while applying pending
migrations and production bootstrap data. DATABASE_RESET=true drops the
application public and drizzle schemas on every Next.js container startup,
then reapplies all migrations and production bootstrap data. Set it back to
false after the intended reset; automatic restarts repeat the deletion while
it remains true.
```

State that the reset affects only the application PostgreSQL schemas and does
not erase Inngest PostgreSQL, Redis, or pgAdmin volumes.

- [ ] **Step 3: Scan for stale reset terminology**

Run:

```powershell
rg -n "build-reset|DATABASE_RESET_CONFIRMATION|reset-local-build|reset profile" README.md docker docs commands nextjs
```

Expected: no live references remain. Historical brainstorm and plan documents
may retain their original wording.

- [ ] **Step 4: Validate whitespace and commit tracked configuration/docs**

Run:

```powershell
git diff --check
```

Expected: exit zero.

Commit tracked files only:

```powershell
git add docker/.env.build.example docker/.env.deploy.example README.md docker/README.md docs/docker-commands.md docs/containerized-infrastructure.md
git commit -m "docs(docker): document startup database reset"
```

Do not stage ignored `.env.build` or `.env.deploy`.

### Task 4: Verify the image and destructive startup behavior

**Files:**
- Verification only

- [ ] **Step 1: Run focused and full static verification**

Run:

```powershell
cd nextjs
pnpm exec vitest run __tests__/unit/scripts/reset-production-database.test.ts __tests__/unit/scripts/release-database.test.ts
pnpm exec tsc --noEmit
pnpm lint
```

Expected: tests and typecheck PASS; lint has no errors.

- [ ] **Step 2: Validate and build the production-like images**

Run from the repository root:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker config --quiet
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker build nextjs playwright
```

Expected: Compose validates and both images build.

- [ ] **Step 3: Create a disposable marker and verify the preserving path**

After the current database is migrated, insert a marker into the production
reference table:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker exec -T app-postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "INSERT INTO e2e_steps (id, label, sort_order) VALUES (''startup-reset-marker'', ''Startup reset marker'', 999) ON CONFLICT (id) DO NOTHING;"'
```

Set `DATABASE_RESET=false` in `docker/.env.build`, recreate Next.js, inspect
startup logs, and query the marker:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker up -d --force-recreate nextjs
docker logs --tail 100 docker-nextjs-1
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker exec -T app-postgres sh -c 'psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM e2e_steps WHERE id = ''startup-reset-marker'';"'
```

Expected: logs start with `Applying Drizzle migrations...`; no
`Dropping public schema...` line appears; the marker query returns `1`.

- [ ] **Step 4: Verify the destructive path**

Set `DATABASE_RESET=true` in `docker/.env.build`, recreate Next.js, and inspect
startup logs:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker up -d --force-recreate nextjs
docker logs --tail 150 docker-nextjs-1
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker exec -T app-postgres sh -c 'psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM e2e_steps WHERE id = ''startup-reset-marker'';"'
```

Expected: logs include `Dropping public schema...`, `Dropping Drizzle migration
history...`, the production maintainer, four Smoke Testing apps, eight E2E
workflow steps, and `Database release completed.` The marker query returns `0`.

- [ ] **Step 5: Restore the safe local value and recreate Next.js**

Set `DATABASE_RESET=false` in `docker/.env.build`, then run:

```powershell
docker compose --env-file docker/.env.build -f docker/compose.build.yml -p docker up -d --force-recreate nextjs
```

Expected: Next.js becomes healthy without performing another destructive
reset.

- [ ] **Step 6: Perform final repository checks**

Run:

```powershell
git status --short
git diff
git diff --check
```

Expected: only intentional changes remain, including the ignored local env
updates on disk but not in Git.
