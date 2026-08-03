# MIHC Independent Production Stacks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the merged production Compose entrypoint with four independently deployable service stacks that share a creator-owned `mihc-network`, omit pgAdmin from production, and deploy foundations before applications.

**Architecture:** Keep existing `compose.yml` files as the local-development definitions. Add production-only `compose.deploy.yml` files for PgDog/PostgreSQL, Inngest, Next.js, and Playwright; the PgDog/PostgreSQL stack creates the named bridge network and all later stacks consume it as external. Replace monolithic production commands and documentation with ordered per-stack operations.

**Tech Stack:** Docker Compose v2, Just, PostgreSQL 18, PgDog, Inngest, PostgreSQL 16, Redis 7, Next.js, Playwright/Hono, Markdown

---

## File Map

- Create `docker/services/pgdog-postgres/compose.deploy.yml`: production PgDog/application PostgreSQL stack and owner of `mihc-network`.
- Create `docker/services/inngest/compose.deploy.yml`: production Inngest/PostgreSQL/Redis stack on the external network.
- Create `docker/services/nextjs/compose.deploy.yml`: production Next.js stack on the external network.
- Create `docker/services/playwright/compose.deploy.yml`: production Playwright/Hono stack on the external network.
- Delete `docker/compose.deploy.yml`: remove the obsolete merged production entrypoint.
- Modify `commands/docker.just`: add ordered foundation/application deploy and reverse-order shutdown recipes.
- Modify `README.md`: update the Docker command inventory without duplicating the runbook.
- Modify `docker/README.md`: distinguish local Compose files from service-owned production files.
- Rewrite `docker/DEPLOYMENT.md`: make independent stacks, network ownership, deployment order, backup, rollback, reset, and platform deployment authoritative.
- Modify `docs/README.md`: point the production source-of-truth entry at the service-owned files.
- Modify `docs/containerized-infrastructure.md`: retain pgAdmin as local-only and update deploy/local differences.
- Modify `docs/docker-commands.md`: document the new Just recipes and direct per-stack Compose commands.

Historical files under `docs/brainstorm/` and `docs/plans/` remain unchanged.

### Task 1: Add the four production Compose models

**Files:**
- Create: `docker/services/pgdog-postgres/compose.deploy.yml`
- Create: `docker/services/inngest/compose.deploy.yml`
- Create: `docker/services/nextjs/compose.deploy.yml`
- Create: `docker/services/playwright/compose.deploy.yml`
- Delete: `docker/compose.deploy.yml`
- Reference: each service directory's existing `compose.yml` and `.env.example`

- [ ] **Step 1: Record the clean MIHC worktree baseline**

Run:

```powershell
git status --short --branch
git diff
```

Expected: record all pre-existing changes and preserve them. Do not proceed by resetting or rewriting unrelated files.

- [ ] **Step 2: Create the PgDog/PostgreSQL production model**

Create `docker/services/pgdog-postgres/compose.deploy.yml` with the supplied images, environment contract, volume paths, healthcheck, and PgDog port mapping. Attach both services to the creator-owned network:

```yaml
services:
  app-pgdog:
    image: ghcr.io/pgdogdev/pgdog:v0.1.31
    restart: unless-stopped
    ports:
      - "6432:6432"
    volumes:
      - ./files/pgdog.toml:/pgdog/pgdog.toml
      - ./files/users.toml:/pgdog/users.toml
    environment:
      - RUST_LOG=${PGDOG_RUST_LOG}
    depends_on:
      app-postgres:
        condition: service_healthy
    networks:
      - mihc-network

  app-postgres:
    image: postgres:18-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${APP_POSTGRES_USER}
      - POSTGRES_PASSWORD=${APP_POSTGRES_PASSWORD}
      - POSTGRES_DB=${APP_POSTGRES_DB}
    volumes:
      - app-postgres-data:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${APP_POSTGRES_USER} -d ${APP_POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - mihc-network

volumes:
  app-postgres-data:

networks:
  mihc-network:
    name: mihc-network
    driver: bridge
```

- [ ] **Step 3: Render the network creator model**

Run:

```powershell
docker compose --env-file docker/services/pgdog-postgres/.env.example -f docker/services/pgdog-postgres/compose.deploy.yml config --quiet
docker compose --env-file docker/services/pgdog-postgres/.env.example -f docker/services/pgdog-postgres/compose.deploy.yml config --format json
```

Expected: both services render; `mihc-network` has `name: mihc-network` and is not external. Do not print a real `.env` or `users.toml`.

- [ ] **Step 4: Create the Inngest production model**

Copy the service definitions, commands, environment variables, volumes, and healthchecks from `docker/services/inngest/compose.yml`, with these production differences:

```yaml
services:
  inngest:
    expose:
      - "8288"
    networks:
      - mihc-network
  inngest-postgres:
    expose:
      - "5432"
    networks:
      - mihc-network
  inngest-redis:
    expose:
      - "6379"
    networks:
      - mihc-network

networks:
  mihc-network:
    external: true
    name: mihc-network
```

The complete file must retain `inngest/inngest:v1.12.1`, `postgres:16-alpine`, `redis:7-alpine`, all three named volumes, the Inngest startup command, and every existing healthcheck. Replace only the local `ports` entries with the shown `expose` entries and add network attachment to all three services.

- [ ] **Step 5: Create the Next.js production model**

Create `docker/services/nextjs/compose.deploy.yml` from the supplied server definition:

```yaml
services:
  nextjs:
    image: ghcr.io/markvalenzuela-mmdc/mihc-nextjs:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_RESET=${DATABASE_RESET}
      - NEXT_PUBLIC_APP_URL=${NEXT_PUBLIC_APP_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - BETTER_AUTH_URL=${BETTER_AUTH_URL}
      - INNGEST_EVENT_KEY=${INNGEST_EVENT_KEY}
      - INNGEST_BASE_URL=${INNGEST_BASE_URL}
      - INNGEST_SIGNING_KEY=${INNGEST_SIGNING_KEY}
      - PROD_MAINTAINER_NAME=${PROD_MAINTAINER_NAME}
      - PROD_MAINTAINER_EMAIL=${PROD_MAINTAINER_EMAIL}
      - PROD_MAINTAINER_PASSWORD=${PROD_MAINTAINER_PASSWORD}
    pull_policy: always
    expose:
      - "3000"
    networks:
      - mihc-network

networks:
  mihc-network:
    external: true
    name: mihc-network
```

Do not retain cross-project `depends_on`; deployment order and health verification replace it.

- [ ] **Step 6: Create the Playwright production model**

Create `docker/services/playwright/compose.deploy.yml` from the supplied server definition:

```yaml
services:
  playwright:
    image: ghcr.io/markvalenzuela-mmdc/mihc-playwright:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - INNGEST_EVENT_KEY=${INNGEST_EVENT_KEY}
      - INNGEST_BASE_URL=${INNGEST_BASE_URL}
      - INNGEST_SIGNING_KEY=${INNGEST_SIGNING_KEY}
      - INNGEST_DEV=0
      - PORT=3939
    expose:
      - "3939"
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3939/health').then((response)=>process.exit(response.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
    networks:
      - mihc-network

networks:
  mihc-network:
    external: true
    name: mihc-network
```

Do not retain cross-project `depends_on`.

- [ ] **Step 7: Remove the merged production entrypoint**

Delete `docker/compose.deploy.yml`. It cannot simultaneously model a creator-owned network and independent consumers declaring that same network external. Local `docker/compose.local.yml` remains unchanged and continues to include pgAdmin.

- [ ] **Step 8: Validate all production models and production service inventory**

Run:

```powershell
$deployModels = @(
  @('pgdog-postgres', 'app-postgres', 'app-pgdog'),
  @('inngest', 'inngest-postgres', 'inngest-redis', 'inngest'),
  @('nextjs', 'nextjs'),
  @('playwright', 'playwright')
)

foreach ($model in $deployModels) {
  $serviceDirectory = $model[0]
  $composeFile = "docker/services/$serviceDirectory/compose.deploy.yml"
  $envFile = "docker/services/$serviceDirectory/.env.example"
  docker compose --env-file $envFile -f $composeFile config --quiet
  if ($LASTEXITCODE -ne 0) { throw "Compose validation failed: $composeFile" }
  docker compose --env-file $envFile -f $composeFile config --services
  if ($LASTEXITCODE -ne 0) { throw "Service inventory failed: $composeFile" }
}
```

Expected inventories: `app-postgres app-pgdog`; `inngest-postgres inngest-redis inngest`; `nextjs`; `playwright`. No inventory contains `pgadmin`.

- [ ] **Step 9: Commit the production models**

```powershell
git add docker/services/pgdog-postgres/compose.deploy.yml docker/services/inngest/compose.deploy.yml docker/services/nextjs/compose.deploy.yml docker/services/playwright/compose.deploy.yml docker/compose.deploy.yml
git diff --cached --check
git commit -m "feat(deploy): add independent service stacks"
```

### Task 2: Add ordered deployment commands

**Files:**
- Modify: `commands/docker.just`
- Reference: `docs/justfile-conventions.md`

- [ ] **Step 1: Read and follow the Justfile conventions**

Run:

```powershell
Get-Content -Raw docs/justfile-conventions.md
```

Expected: preserve namespaced recipes, private helpers, and existing formatting conventions.

- [ ] **Step 2: Replace the merged deploy recipe with explicit lifecycle recipes**

Keep `local`, `build`, and `down` unchanged. Replace the current `deploy action="up"` recipe with:

```just
# Deploy foundational services first, then application services
deploy:
    @just docker deploy-foundations
    @just docker deploy-apps

# Deploy PostgreSQL/PgDog first so it creates mihc-network, then Inngest
deploy-foundations:
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/pgdog-postgres/.env" -f "{{ justfile_directory() }}/docker/services/pgdog-postgres/compose.deploy.yml" up -d
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/inngest/.env" -f "{{ justfile_directory() }}/docker/services/inngest/compose.deploy.yml" up -d

# Deploy application services after foundational services are healthy
deploy-apps:
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/nextjs/.env" -f "{{ justfile_directory() }}/docker/services/nextjs/compose.deploy.yml" up -d
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/playwright/.env" -f "{{ justfile_directory() }}/docker/services/playwright/compose.deploy.yml" up -d

# Stop independent deployment stacks in reverse dependency order
deploy-down:
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/playwright/.env" -f "{{ justfile_directory() }}/docker/services/playwright/compose.deploy.yml" down
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/nextjs/.env" -f "{{ justfile_directory() }}/docker/services/nextjs/compose.deploy.yml" down
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/inngest/.env" -f "{{ justfile_directory() }}/docker/services/inngest/compose.deploy.yml" down
    @docker compose --env-file "{{ justfile_directory() }}/docker/services/pgdog-postgres/.env" -f "{{ justfile_directory() }}/docker/services/pgdog-postgres/compose.deploy.yml" down
```

- [ ] **Step 3: Verify recipe discovery and ordering**

Run:

```powershell
just --list docker
just --dry-run docker deploy
just --dry-run docker deploy-down
```

Expected: the deploy dry run lists PgDog/PostgreSQL, Inngest, Next.js, then Playwright; shutdown lists Playwright, Next.js, Inngest, then PgDog/PostgreSQL.

- [ ] **Step 4: Commit the command surface**

```powershell
git add commands/docker.just
git diff --cached --check
git commit -m "build(deploy): order independent stack lifecycle"
```

### Task 3: Rewrite production deployment documentation

**Files:**
- Rewrite: `docker/DEPLOYMENT.md`
- Modify: `docker/README.md`
- Modify: `README.md`
- Modify: `docs/README.md`
- Modify: `docs/containerized-infrastructure.md`
- Modify: `docs/docker-commands.md`

- [ ] **Step 1: Rewrite the authoritative production topology and file inventory**

Replace monolithic/include language in `docker/DEPLOYMENT.md` with these production groups:

```text
Foundation 1: pgdog-postgres/compose.deploy.yml
  app-postgres -> creates/joins mihc-network
  app-pgdog    -> joins mihc-network, publishes restricted host port 6432

Foundation 2: inngest/compose.deploy.yml
  inngest-postgres -> external mihc-network
  inngest-redis    -> external mihc-network
  inngest          -> external mihc-network

Applications:
  nextjs/compose.deploy.yml     -> external mihc-network, expose 3000
  playwright/compose.deploy.yml -> external mihc-network, expose 3939
```

State explicitly that pgAdmin is local-only and is not part of production provisioning, secrets, volumes, exposure checks, PaaS setup, or verification.

- [ ] **Step 2: Update environment and credential guidance**

Retain the existing application, PgDog/PostgreSQL, and Inngest variable tables. Delete the production pgAdmin variable table. Keep the alignment checklist:

```text
APP_POSTGRES_USER     == users.toml [[users]].name
APP_POSTGRES_PASSWORD == users.toml [[users]].password
APP_POSTGRES_DB       == pgdog.toml [[databases]].name
DATABASE_URL user/password/database match the same values
DATABASE_URL host     == app-pgdog
pgdog.toml backend    == app-postgres:5432
```

Add a prominent warning that the credential pasted into chat must be considered disclosed and rotated before deployment. Never reproduce that credential in any tracked file or command.

- [ ] **Step 3: Replace plain Docker validation and startup commands**

Document environment preparation without pgAdmin:

```bash
cp docker/services/pgdog-postgres/.env.example docker/services/pgdog-postgres/.env
cp docker/services/inngest/.env.example docker/services/inngest/.env
cp docker/services/nextjs/.env.example docker/services/nextjs/.env
cp docker/services/playwright/.env.example docker/services/playwright/.env
cp docker/services/pgdog-postgres/files/users.toml.example \
  docker/services/pgdog-postgres/files/users.toml
```

Document `config --quiet` for each file with its matching `--env-file`, then the required deployment order:

```bash
just docker deploy-foundations

docker compose --env-file docker/services/pgdog-postgres/.env \
  -f docker/services/pgdog-postgres/compose.deploy.yml ps
docker compose --env-file docker/services/inngest/.env \
  -f docker/services/inngest/compose.deploy.yml ps

just docker deploy-apps
```

Require healthy foundational services before `deploy-apps`. Document `just docker deploy` as the ordered convenience command, not as a substitute for reviewing health on a first deployment.

- [ ] **Step 4: Update network, exposure, persistence, and shutdown guidance**

Document that:

- PgDog/PostgreSQL creates `mihc-network`; operators must not create it manually.
- Consumer stacks fail if the foundation has not created the external network.
- PgDog's `6432:6432` is the only fixed host publication in the supplied production models and must be firewalled or bound through platform isolation.
- Next.js, Playwright, Inngest, both PostgreSQL containers, and Redis use `expose` only; the reverse proxy/platform must join or route to `mihc-network` to reach Next.js port 3000.
- Production volumes are `app-postgres-data`, `inngest-data`, `inngest-postgres-data`, and `inngest-redis-data`; there is no `pgadmin-data` production volume.
- Normal shutdown is `just docker deploy-down`; never use `down -v`.
- Independent Compose project names prefix named volumes unless the platform overrides the project name. Operators must inspect existing volume names before migrating an already-running monolithic deployment.

- [ ] **Step 5: Convert backup, update, rollback, and reset commands to per-stack commands**

Use the PgDog/PostgreSQL production file for `exec app-postgres`, the Next.js file for Next.js pull/recreate/logs, and the Playwright file for Playwright pull/recreate/logs. Preserve the existing verified backup gate and reset safeguards. The update sequence must be:

```bash
docker compose --env-file docker/services/nextjs/.env \
  -f docker/services/nextjs/compose.deploy.yml pull nextjs
docker compose --env-file docker/services/playwright/.env \
  -f docker/services/playwright/compose.deploy.yml pull playwright
docker compose --env-file docker/services/nextjs/.env \
  -f docker/services/nextjs/compose.deploy.yml up -d --force-recreate nextjs
docker compose --env-file docker/services/playwright/.env \
  -f docker/services/playwright/compose.deploy.yml up -d --force-recreate playwright
```

Rollback overrides must be applied separately to their matching application Compose files. State that image rollback does not reverse migrations.

- [ ] **Step 6: Replace Coolify and Dokploy merged-stack instructions**

Describe four separate repository-backed Compose resources/applications using the four exact `compose.deploy.yml` paths. Require deployment in the same foundation-first order, persistent secret-backed material for each service-local `.env`, the ignored PgDog `users.toml`, and attachment to the literal external network name `mihc-network`. Route only Next.js to container port 3000. Assign no public domain to PgDog, PostgreSQL, Inngest, Redis, or Playwright. Remove every pgAdmin production mount, variable, port, domain, and verification instruction.

- [ ] **Step 7: Update the Docker-area indexes and local infrastructure guide**

In `docker/README.md`, list each service-owned production file and say `services/pgadmin/compose.yml` is local-only. In `docs/containerized-infrastructure.md`, retain local pgAdmin setup and registration sections but update `Compose files`, `Deploy vs Local Differences`, and `Production deployment` so production points to the four independent files and has no pgAdmin. In `docs/README.md`, replace the deleted `docker/compose.deploy.yml` link with the service directory pattern plus `docker/DEPLOYMENT.md`.

- [ ] **Step 8: Update root and detailed command references**

In `README.md`, replace `just docker deploy [up|down]` with these rows:

```markdown
| docker | `just docker deploy` | Deploy foundations, then Next.js and Playwright |
| docker | `just docker deploy-foundations` | Deploy PgDog/PostgreSQL, then Inngest |
| docker | `just docker deploy-apps` | Deploy Next.js and Playwright after foundations are healthy |
| docker | `just docker deploy-down` | Stop production stacks in reverse dependency order |
```

In `docs/docker-commands.md`, replace the merged deploy section and its service inventory with the same recipes, direct per-stack equivalents, external-network behavior, and reverse shutdown order. Keep local pgAdmin descriptions explicitly labeled local.

- [ ] **Step 9: Audit stale production references**

Run:

```powershell
rg -n "docker/compose\.deploy\.yml|services/pgadmin/\.env|pgadmin-data|mihc-shared|merged deploy|include-only deployment|deploy \[up\|down\]" README.md docker/README.md docker/DEPLOYMENT.md docs/README.md docs/containerized-infrastructure.md docs/docker-commands.md commands/docker.just
```

Expected: no matches. Local references to `services/pgadmin/compose.yml`, local port 5050, and local registration instructions may remain.

- [ ] **Step 10: Commit current documentation**

```powershell
git add README.md docker/README.md docker/DEPLOYMENT.md docs/README.md docs/containerized-infrastructure.md docs/docker-commands.md
git diff --cached --check
git commit -m "docs(deploy): document independent production stacks"
```

### Task 4: Verify the complete deployment contract

**Files:**
- Verify all files created or modified in Tasks 1-3.

- [ ] **Step 1: Validate every Compose model again**

Run the four `docker compose --env-file <service>/.env.example -f <service>/compose.deploy.yml config --quiet` commands. Expected: all exit successfully without reading or printing production secrets.

- [ ] **Step 2: Assert network ownership and attachments from rendered JSON**

For each rendered model, inspect `.networks.mihc-network`. Expected: PgDog/PostgreSQL has `name` and `driver` without `external: true`; the other three have `name: mihc-network` and `external: true`. Inspect every service's `networks` property and confirm no production service relies on the implicit default network.

- [ ] **Step 3: Verify local behavior was preserved**

Run:

```powershell
docker compose -f docker/compose.local.yml config --quiet
docker compose -f docker/compose.local.yml config --services
git diff -- docker/compose.local.yml docker/services/pgadmin/compose.yml docker/services/pgdog-postgres/compose.yml docker/services/inngest/compose.yml
```

Expected: local config includes `pgadmin`; the diff for all four existing local Compose files is empty.

- [ ] **Step 4: Scan for the disclosed credential and production pgAdmin**

Search changed tracked files for the exact disclosed password from the user request without echoing it in logs; use a locally assigned secure string or manually compare without embedding it in the plan or repository. Also run:

```powershell
rg -n "pgadmin|PGADMIN|5050" docker/services docker/DEPLOYMENT.md -g compose.deploy.yml -g DEPLOYMENT.md
```

Expected: no matches. Do not print secret-bearing ignored files.

- [ ] **Step 5: Validate commands and documentation links**

Run:

```powershell
just --list docker
just --dry-run docker deploy
just --dry-run docker deploy-down
@(
  'docker/DEPLOYMENT.md',
  'docker/services/pgdog-postgres/compose.deploy.yml',
  'docker/services/inngest/compose.deploy.yml',
  'docker/services/nextjs/compose.deploy.yml',
  'docker/services/playwright/compose.deploy.yml'
) | ForEach-Object {
  if (-not (Test-Path $_)) { throw "Missing documented file: $_" }
}
```

Expected: command order is foundation-first for deployment and application-first for shutdown; every documentation target exists.

- [ ] **Step 6: Perform the required final preservation review**

Run:

```powershell
git diff --check
git status --short --branch
git diff --stat
git diff
```

Expected: only the intentional production Compose, command, and current documentation changes are present; pre-existing user-owned work remains untouched; no historical files, local Compose definitions, real `.env`, or real `users.toml` files changed.
