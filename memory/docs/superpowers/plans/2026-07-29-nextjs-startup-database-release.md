# Next.js Startup Database Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Next.js production image apply Drizzle migrations and the idempotent production bootstrap before starting the server, while restoring the original single-image CI/CD workflow and preserving development migration/seeding.

**Architecture:** The normal Next.js runner image contains a small production-release runtime alongside the standalone server. Its startup command runs the existing `release-database.ts` command and starts `server.js` only after success. Compose provides production configuration and database ordering; Docker restart behavior handles transient startup failure. There is no separate release image, release service, registry state machine, or custom database retry/lock layer.

**Tech Stack:** Next.js 16, Node.js 24, pnpm, TypeScript/tsx, Drizzle ORM, Better Auth, PostgreSQL, Docker multi-stage builds, Docker Compose, GitHub Actions, Vitest.

---

## File map

**Restore to the pre-feature version:**

- `.github/workflows/build-nextjs.yml` — original single-image build/push workflow.
- `commands/docker.just` — original Compose commands.
- `docker/services/pgdog-postgres/files/pgdog.toml` — remove release-lock parser configuration.

**Modify for the simplified design:**

- `nextjs/Dockerfile` — package the release runtime in the normal image and run it before `server.js`.
- `nextjs/package.json` / `nextjs/pnpm-lock.yaml` — make `tsx` a production runtime dependency.
- `nextjs/scripts/release-database.ts` — retain validation/migrate/bootstrap but remove custom readiness retries and advisory locking.
- `nextjs/lib/drizzle/db.ts` — remove the dedicated release client that existed only for advisory locking.
- `nextjs/__tests__/unit/scripts/release-database.test.ts` — test the simplified migrate/bootstrap/close order and failure behavior.
- `docker/compose.build.yml` — remove the separate `db-release` service and let the normal image perform startup release.
- `docker/compose.deploy.yml` — remove `db-release`, restore the normal `latest` image, and pass the production environment to Next.js.
- `docker/.env.deploy.example` — remove the paired-image tag and retain required production database/bootstrap variables.

**Keep as the production seed implementation:**

- `nextjs/lib/drizzle/seed/production-config.ts`
- `nextjs/lib/drizzle/seed/seed-apps.ts`
- `nextjs/lib/drizzle/seed/seed-production.ts`
- `nextjs/lib/better-auth/create-auth.ts`
- their focused unit and integration tests.

**Align documentation:**

- `README.md`
- `docker/README.md`
- `docs/containerized-infrastructure.md`
- `docs/docker-commands.md`

---

### Task 1: Restore the original single-image GitHub workflow

**Files:**

- Modify: `.github/workflows/build-nextjs.yml`

- [ ] **Step 1: Inspect the original workflow**

Run:

```powershell
git show main:.github/workflows/build-nextjs.yml
```

Expected: the output contains one `docker/build-push-action` step, the original
branch/latest/semver/SHA tags, and no database-release image.

- [ ] **Step 2: Restore the workflow content**

Set `.github/workflows/build-nextjs.yml` to:

```yaml
name: Build Next.js Docker image

on:
  push:
    branches:
      - main
    tags:
      - "v*.*.*"
    paths:
      - "nextjs/**"
      - ".github/**"

permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: mihc-nextjs

jobs:
  build:
    name: Build and push image
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Normalize image name
        id: image
        run: echo "name=${GITHUB_REPOSITORY_OWNER,,}/${IMAGE_NAME}" >> "$GITHUB_OUTPUT"

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ steps.image.outputs.name }}
          tags: |
            type=ref,event=branch
            type=raw,value=latest,enable={{is_default_branch}}
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-

      - name: Build and push Next.js image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./nextjs/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            NEXT_PUBLIC_APP_URL=${{ vars.NEXT_PUBLIC_APP_URL }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

- [ ] **Step 3: Verify byte-for-byte restoration**

Run:

```powershell
$original = git show main:.github/workflows/build-nextjs.yml
$current = Get-Content -Raw .github/workflows/build-nextjs.yml
if (($original -join "`n").TrimEnd() -ne $current.TrimEnd()) {
  throw "build-nextjs.yml does not match main"
}
```

Expected: exit code 0.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/build-nextjs.yml
git commit -m "revert(ci): restore single Next.js image workflow"
```

---

### Task 2: Simplify the production database release command

**Files:**

- Modify: `nextjs/scripts/release-database.ts`
- Modify: `nextjs/lib/drizzle/db.ts`
- Modify: `nextjs/__tests__/unit/scripts/release-database.test.ts`
- Modify: `docker/services/pgdog-postgres/files/pgdog.toml`

- [ ] **Step 1: Replace lock/retry tests with the required behavior**

The unit test must assert this exact successful order:

```ts
expect(events).toEqual([
  "migrate",
  "seed",
  "pool:end",
]);
```

Add separate cases that assert:

```ts
await expect(
  releaseDatabase({ environment: { NODE_ENV: "development" } }),
).rejects.toThrow("Database release requires NODE_ENV=production.");

await expect(
  releaseDatabase({ environment: { NODE_ENV: "production" } }),
).rejects.toThrow("DATABASE_URL is required for database release.");
```

For a migration failure, assert that seeding is not called and `pool.end()` is
called once. For a seed failure, assert that `pool.end()` is called once.

- [ ] **Step 2: Run the unit test and confirm it fails**

Run:

```bash
cd nextjs
pnpm test -- __tests__/unit/scripts/release-database.test.ts
```

Expected: FAIL because the current implementation performs readiness probes
and advisory locking.

- [ ] **Step 3: Implement the minimal release sequence**

Use `createDatabaseClient(databaseUrl)` and reduce `releaseDatabase()` to:

```ts
export async function releaseDatabase({
  environment = process.env,
  createClient = createDatabaseClient,
  migrateDatabase = async (db) => {
    await migrate(db, {
      migrationsFolder: path.resolve(process.cwd(), "drizzle"),
    });
  },
  seedDatabase = seedProductionDatabase,
}: ReleaseDatabaseDependencies = {}) {
  if (environment.NODE_ENV !== "production") {
    throw new Error("Database release requires NODE_ENV=production.");
  }

  const databaseUrl = environment.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL is required for database release.");
  }

  const seedConfig = getProductionSeedConfig(environment);
  const { pool, db } = createClient(databaseUrl);

  try {
    console.log("Applying Drizzle migrations...");
    await migrateDatabase(db);

    console.log("Running production bootstrap...");
    const messages = await seedDatabase(db, seedConfig);
    for (const message of messages) console.log(message);

    console.log("Database release completed.");
  } finally {
    await pool.end();
  }
}
```

Retain the existing top-level error sanitization so database URLs, Better Auth
secrets, and maintainer passwords are not printed.

Delete `createDedicatedDatabaseClient()` from `nextjs/lib/drizzle/db.ts`.

Remove this line from PgDog configuration:

```toml
query_parser = "on"
```

- [ ] **Step 4: Run focused tests**

```bash
cd nextjs
pnpm test -- \
  __tests__/unit/scripts/release-database.test.ts \
  __tests__/unit/lib/drizzle/seed/production-config.test.ts \
  __tests__/unit/lib/drizzle/seed/seed-apps.test.ts \
  __tests__/unit/lib/drizzle/seed/seed-production.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add \
  nextjs/scripts/release-database.ts \
  nextjs/lib/drizzle/db.ts \
  nextjs/__tests__/unit/scripts/release-database.test.ts \
  docker/services/pgdog-postgres/files/pgdog.toml
git commit -m "refactor(database): simplify production release"
```

---

### Task 3: Run database release from the normal Next.js image

**Files:**

- Modify: `nextjs/Dockerfile`
- Modify: `nextjs/package.json`
- Modify: `nextjs/pnpm-lock.yaml`

- [ ] **Step 1: Make `tsx` a production runtime dependency**

Move:

```json
"tsx": "^4.22.4"
```

from `devDependencies` to `dependencies`, then run:

```bash
cd nextjs
pnpm install --lockfile-only
```

Expected: the lockfile records `tsx` as a production dependency without
changing its version.

- [ ] **Step 2: Add a production-only dependency stage**

After the existing `deps` stage, add:

```dockerfile
FROM base AS runtime-deps

COPY packages/enrollmate-contract ./packages/enrollmate-contract
COPY nextjs/package.json nextjs/pnpm-lock.yaml nextjs/pnpm-workspace.yaml ./nextjs/
WORKDIR /app/nextjs
RUN pnpm install --prod --frozen-lockfile --ignore-scripts
```

Delete the entire separate `database-release` stage.

- [ ] **Step 3: Package the release runtime in the normal runner**

Keep the standalone server layout and add:

```dockerfile
COPY --from=runtime-deps --chown=nextjs:nodejs /app/nextjs/node_modules ./nextjs/node_modules
COPY --chown=nextjs:nodejs packages ./packages
COPY --chown=nextjs:nodejs nextjs/package.json nextjs/tsconfig.json ./nextjs/
COPY --chown=nextjs:nodejs nextjs/drizzle ./nextjs/drizzle
COPY --chown=nextjs:nodejs nextjs/lib ./nextjs/lib
COPY --chown=nextjs:nodejs nextjs/scripts ./nextjs/scripts
```

Replace the runner command with:

```dockerfile
CMD ["sh", "-c", "cd /app/nextjs && ./node_modules/.bin/tsx scripts/release-database.ts && cd /app && exec node server.js"]
```

This deliberately favors a clear runtime layout over image-size optimization.

- [ ] **Step 4: Build the normal image**

Run:

```bash
docker build -f nextjs/Dockerfile -t mihc-nextjs:start-release-verification .
```

Expected: PASS. There is no `database-release` target.

- [ ] **Step 5: Verify the packaged files**

Run:

```bash
docker run --rm --entrypoint sh mihc-nextjs:start-release-verification -c \
  "test -f /app/nextjs/drizzle/meta/_journal.json &&
   test -f /app/nextjs/scripts/release-database.ts &&
   test -x /app/nextjs/node_modules/.bin/tsx &&
   test -f /app/server.js"
```

Expected: exit code 0.

- [ ] **Step 6: Commit**

```bash
git add nextjs/Dockerfile nextjs/package.json nextjs/pnpm-lock.yaml
git commit -m "feat(deploy): release database before Next.js startup"
```

---

### Task 4: Remove the separate release service from Compose

**Files:**

- Modify: `docker/compose.build.yml`
- Modify: `docker/compose.deploy.yml`
- Modify: `docker/.env.deploy.example`
- Modify: `commands/docker.just`

- [ ] **Step 1: Remove `db-release` from both Compose files**

Delete the complete `db-release` service and every:

```yaml
db-release:
  condition: service_completed_successfully
```

dependency.

- [ ] **Step 2: Restore the normal deploy image and service environment**

The deploy `nextjs` service must use:

```yaml
nextjs:
  image: ghcr.io/markvalenzuela-mmdc/mihc-nextjs:latest
  restart: unless-stopped
  env_file: .env.deploy
  ports:
    - "3000:3000"
  depends_on:
    app-postgres:
      condition: service_healthy
    app-pgdog:
      condition: service_started
    inngest:
      condition: service_healthy
```

Use `env_file: .env.deploy` for Playwright as well. Restore the three included
service-level `env_file` declarations from `main`.

The build stack keeps `env_file: .env.build`; its normal Next.js image now
performs the same release sequence against the disposable build database.

- [ ] **Step 3: Remove paired-image configuration**

Delete from `docker/.env.deploy.example`:

```dotenv
MIHC_IMAGE_TAG=sha-replace-with-the-full-40-character-git-commit
```

Retain:

```dotenv
DATABASE_URL=postgresql://mihc:change-me@app-pgdog:6432/mihc?sslmode=disable
NEXT_PUBLIC_APP_URL=https://sanity.example.com
BETTER_AUTH_SECRET=generate-a-long-random-secret
BETTER_AUTH_URL=https://sanity.example.com
INNGEST_BASE_URL=http://inngest:8288
PROD_MAINTAINER_NAME=Production Maintainer
PROD_MAINTAINER_EMAIL=maintainer@example.com
PROD_MAINTAINER_PASSWORD=replace-with-a-secret
```

- [ ] **Step 4: Restore the original Docker command recipes**

Restore `commands/docker.just` to the `main` version. The deploy recipe should
again be:

```just
deploy action="up":
    @docker compose -f "{{ justfile_directory() }}/docker/compose.deploy.yml" {{action}} {{if action == "up" { "-d" } else { "" }}}
```

- [ ] **Step 5: Validate Compose**

Create only ignored disposable environment files from the examples, then run:

```bash
docker compose -f docker/compose.build.yml config --quiet
docker compose -f docker/compose.deploy.yml config --quiet
docker compose -f docker/compose.deploy.yml config --services
```

Expected:

- both configs pass;
- deploy services do not include `db-release`;
- deploy uses only `ghcr.io/markvalenzuela-mmdc/mihc-nextjs:latest`;
- no `MIHC_IMAGE_TAG` interpolation remains.

Remove only the disposable files created for this validation.

- [ ] **Step 6: Commit**

```bash
git add \
  docker/compose.build.yml \
  docker/compose.deploy.yml \
  docker/.env.deploy.example \
  commands/docker.just
git commit -m "refactor(deploy): use Next.js startup release"
```

---

### Task 5: Replace the obsolete release-service documentation

**Files:**

- Modify: `README.md`
- Modify: `docker/README.md`
- Modify: `docs/containerized-infrastructure.md`
- Modify: `docs/docker-commands.md`

- [ ] **Step 1: Remove obsolete concepts**

Delete documentation for:

- a `db-release` Compose service;
- a database-release image;
- `MIHC_IMAGE_TAG`;
- paired immutable image publication;
- partial image-pair recovery;
- `service_completed_successfully` startup gating;
- release-service-only retry commands.

- [ ] **Step 2: Document the actual startup behavior**

Use this concise description consistently:

```markdown
The production Next.js container applies committed Drizzle migrations and runs
the idempotent production bootstrap before starting the Next.js server. If
migration or bootstrap fails, the server does not start and Docker retries the
container according to its restart policy.
```

State that production bootstrap creates or validates the configured maintainer,
upserts the four Smoke Testing apps, does not reset an existing password, and
does not load development fixtures.

- [ ] **Step 3: Keep development commands explicit**

Document:

```text
just db migrate  # apply migrations manually in development
just db seed     # load complete development fixtures
just db release  # manually run the same production migrate/bootstrap sequence
```

Keep the warning that `just db reset` must never be run against production.

- [ ] **Step 4: Validate documentation**

```bash
just
just db
just docker
rg -n "db-release|database-release image|MIHC_IMAGE_TAG|image pair|service_completed_successfully" \
  README.md docker/README.md docs/containerized-infrastructure.md docs/docker-commands.md
git diff --check
```

Expected: command listings pass and the search returns no obsolete deployment
language.

- [ ] **Step 5: Commit**

```bash
git add README.md docker/README.md docs/containerized-infrastructure.md docs/docker-commands.md
git commit -m "docs(deploy): describe Next.js startup migrations"
```

---

### Task 6: Verify production startup and development preservation

**Files:**

- Verify all changed files.
- Fix only failures caused by this simplified implementation.

- [ ] **Step 1: Run production seed tests**

```bash
cd nextjs
pnpm test -- \
  __tests__/unit/lib/drizzle/seed/seed-apps.test.ts \
  __tests__/unit/lib/drizzle/seed/production-config.test.ts \
  __tests__/unit/lib/drizzle/seed/seed-production.test.ts \
  __tests__/unit/scripts/release-database.test.ts \
  __tests__/integration/production-bootstrap.test.ts
```

Expected: unit tests pass. Integration tests pass when `TEST_DATABASE_URL` is
valid; otherwise record only the already-known credential blocker.

- [ ] **Step 2: Run static and application checks**

```bash
just check lint
just check typecheck
just app build
```

Expected: PASS, with only the repository's existing lint warnings.

- [ ] **Step 3: Verify startup order in an isolated Compose project**

Use a unique project name and disposable non-production credentials:

```bash
docker compose -p mihc_startup_release_verification \
  -f docker/compose.build.yml up --build --wait
docker compose -p mihc_startup_release_verification \
  -f docker/compose.build.yml logs nextjs
```

Expected Next.js logs, in order:

```text
Applying Drizzle migrations...
Running production bootstrap...
Database release completed.
```

Then verify the Next.js health endpoint responds.

- [ ] **Step 4: Verify idempotent restart**

```bash
docker compose -p mihc_startup_release_verification \
  -f docker/compose.build.yml restart nextjs
docker compose -p mihc_startup_release_verification \
  -f docker/compose.build.yml logs nextjs
```

Expected: migration/bootstrap completes again without duplicate-key errors and
the server starts.

- [ ] **Step 5: Clean up exact disposable resources**

After confirming the project name:

```bash
docker compose -p mihc_startup_release_verification \
  -f docker/compose.build.yml down --volumes --remove-orphans
docker image rm mihc-nextjs:start-release-verification
```

Do not stop, remove, or modify any pre-existing Compose project.

- [ ] **Step 6: Run the full suite for regression comparison**

```bash
just dev test
```

Expected: no new failure beyond the known invalid `TEST_DATABASE_URL`
integration setup and the two existing request-smoke-test environment/mock
failures.

- [ ] **Step 7: Verify final scope**

```bash
git status --short --branch
git diff main...HEAD --check
git diff main...HEAD --stat
git diff main...HEAD -- .github/workflows/build-nextjs.yml
rg -n "db-release|mihc-nextjs-db-release|MIHC_IMAGE_TAG" .github docker nextjs/Dockerfile
```

Expected:

- workflow diff is empty;
- no separate release target/service/image/tag remains;
- production seed files and tests remain;
- development seed/reset implementation remains unchanged;
- no actual `.env` file or secret is tracked.

- [ ] **Step 8: Commit any verification-only correction**

If verification required a scoped fix:

```bash
git add \
  nextjs/Dockerfile \
  nextjs/package.json \
  nextjs/pnpm-lock.yaml \
  nextjs/scripts/release-database.ts \
  nextjs/lib/drizzle/db.ts \
  nextjs/__tests__/unit/scripts/release-database.test.ts \
  docker/compose.build.yml \
  docker/compose.deploy.yml \
  docker/.env.deploy.example
git commit -m "fix(deploy): correct Next.js startup release"
```

If no correction was required, do not create an empty commit.
