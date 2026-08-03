# MIHC Minimal Service Deployment Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broad MIHC production runbook with one concise guide for configuring and deploying four individual Coolify or Dokploy Compose resources in the correct order.

**Architecture:** Keep the existing production Compose and Just files unchanged. Make `docker/DEPLOYMENT.md` the only detailed production guide; reduce all other current documentation to short links while preserving local-development guidance.

**Tech Stack:** Markdown, Docker Compose v2, Coolify, Dokploy, PostgreSQL, PgDog, Inngest, Redis

---

## File Map

- Rewrite `docker/DEPLOYMENT.md`: minimal individual-service deployment guide.
- Modify `README.md`: production section links to the guide.
- Modify `docker/README.md`: short production file index and guide link.
- Modify `docs/README.md`: production source-of-truth row points to the guide and service files.
- Modify `docs/containerized-infrastructure.md`: retain local infrastructure and pgAdmin; replace production detail with a link.
- Modify `docs/docker-commands.md`: retain local/build commands; replace production detail with a link.
- Verify without modifying `docker/services/*/compose.deploy.yml`, `commands/docker.just`, `.env.example` files, and PgDog TOML examples.

### Task 1: Rewrite the authoritative deployment guide

**Files:**
- Rewrite: `docker/DEPLOYMENT.md`
- Reference: `docker/services/pgdog-postgres/compose.deploy.yml`
- Reference: `docker/services/inngest/compose.deploy.yml`
- Reference: `docker/services/nextjs/compose.deploy.yml`
- Reference: `docker/services/playwright/compose.deploy.yml`
- Reference: service-local `.env.example` files
- Reference: `docker/services/pgdog-postgres/files/pgdog.toml`
- Reference: `docker/services/pgdog-postgres/files/users.toml.example`

- [ ] **Step 1: Record the branch baseline**

Run:

```powershell
git status --short --branch
git diff
```

Expected: the feature branch is clean; preserve all existing Compose and command commits.

- [ ] **Step 2: Replace the broad runbook with the minimal outline**

Rewrite `docker/DEPLOYMENT.md` with only these top-level sections:

```markdown
# Individual Service Deployment

## Deployment model
## Shared network
## 1. PgDog and application PostgreSQL
## 2. Inngest, PostgreSQL, and Redis
## 3. Next.js
## 4. Playwright/Hono
## Deployment order
```

The introduction must state that Coolify and Dokploy use four separate
repository-backed Compose resources. pgAdmin is local-only and not deployed.
Do not add backup, update, rollback, reset, recovery, volume-migration,
troubleshooting, shell startup, or shutdown procedures.

- [ ] **Step 3: Document the shared network**

State exactly:

- `docker/services/pgdog-postgres/compose.deploy.yml` creates the named bridge
  network `mihc-network`.
- The Inngest, Next.js, and Playwright production files declare
  `mihc-network` external.
- Deploy PgDog/PostgreSQL first; consumer resources cannot attach before the
  network exists.
- Coolify and Dokploy resources must use the same literal Docker network name.

- [ ] **Step 4: Document PgDog/PostgreSQL configuration**

List these exact files:

```text
docker/services/pgdog-postgres/compose.deploy.yml
docker/services/pgdog-postgres/.env.example -> .env
docker/services/pgdog-postgres/files/pgdog.toml
docker/services/pgdog-postgres/files/users.toml.example -> users.toml
```

List the `.env` variables `PGDOG_RUST_LOG`, `APP_POSTGRES_USER`,
`APP_POSTGRES_PASSWORD`, and `APP_POSTGRES_DB`. Explain that the ignored real
`users.toml` must be supplied through a persistent platform file/config mount.
Include this alignment block:

```text
APP_POSTGRES_USER     == users.toml [[users]].name
APP_POSTGRES_PASSWORD == users.toml [[users]].password
APP_POSTGRES_DB       == pgdog.toml [[databases]].name
DATABASE_URL user/password/database match those values
DATABASE_URL host     == app-pgdog
pgdog.toml backend    == app-postgres:5432
```

State that any credential disclosed in chat must be rotated and never copied
into tracked files.

- [ ] **Step 5: Document Inngest configuration**

Reference `docker/services/inngest/compose.deploy.yml` and
`docker/services/inngest/.env.example -> .env`. List the required connection
values and their internal forms:

```text
INNGEST_POSTGRES_URI -> postgresql://...@inngest-postgres:5432/...
INNGEST_REDIS_URI    -> redis://inngest-redis:6379
INNGEST_SDK_URL      -> http://playwright:3939/api/inngest
```

Also identify `INNGEST_EVENT_KEY`, `INNGEST_SIGNING_KEY`,
`INNGEST_POSTGRES_DB`, `INNGEST_POSTGRES_USER`, and
`INNGEST_POSTGRES_PASSWORD`. Point operators to the tracked example for the
optional tuning/logging variables instead of reproducing another table.

- [ ] **Step 6: Document application configuration**

For Next.js, reference its production Compose and `.env.example -> .env`, then
list:

```text
DATABASE_URL -> postgresql://...@app-pgdog:6432/...
DATABASE_RESET -> false
NEXT_PUBLIC_APP_URL
BETTER_AUTH_SECRET
BETTER_AUTH_URL
INNGEST_EVENT_KEY
INNGEST_BASE_URL -> http://inngest:8288
INNGEST_SIGNING_KEY
PROD_MAINTAINER_NAME
PROD_MAINTAINER_EMAIL
PROD_MAINTAINER_PASSWORD
```

For Playwright, reference its production Compose and `.env.example -> .env`,
then list `DATABASE_URL`, `INNGEST_EVENT_KEY`, `INNGEST_BASE_URL`, and
`INNGEST_SIGNING_KEY`. State that shared database/Inngest values must match the
infrastructure resources.

- [ ] **Step 7: Document platform setup and sequence without shell commands**

For both Coolify and Dokploy, state that the operator creates four individual
repository-backed Docker Compose resources, selects each exact
`compose.deploy.yml`, configures the matching environment and required PgDog
files, and deploys them in this order:

```text
1. pgdog-postgres — app-postgres and app-pgdog; creates mihc-network
2. inngest — inngest-postgres, inngest-redis, and inngest
3. nextjs — route this resource publicly to container port 3000
4. playwright — keep internal; Inngest reaches port 3939
```

Do not include `docker compose up`, `just docker deploy`, backup, rollback, or
shutdown commands.

- [ ] **Step 8: Audit and commit the minimal guide**

Run:

```powershell
rg -n "^## |compose.deploy.yml|\.env|mihc-network|pgdog.toml|users.toml|Coolify|Dokploy" docker/DEPLOYMENT.md
rg -n "backup|rollback|recovery|pg_dump|DATABASE_RESET=true|docker compose .* up|just docker deploy|troubleshooting" docker/DEPLOYMENT.md
git diff --check
```

Expected: the first command finds every required topic; the second returns no
matches; whitespace check passes.

Commit:

```powershell
git add docker/DEPLOYMENT.md
git commit -m "docs(deploy): simplify individual service guide"
```

### Task 2: Remove duplicate production instructions

**Files:**
- Modify: `README.md`
- Modify: `docker/README.md`
- Modify: `docs/README.md`
- Modify: `docs/containerized-infrastructure.md`
- Modify: `docs/docker-commands.md`

- [ ] **Step 1: Reduce the root production section**

Keep one short paragraph linking `docker/DEPLOYMENT.md` and stating that it
covers individual Coolify/Dokploy services, environment values, network/PgDog
configuration, and deployment order. Remove references to backups, recovery,
rollback, and reset safety from the production link text.

- [ ] **Step 2: Reduce Docker-area production documentation**

Keep the four production Compose paths in `docker/README.md` as a short file
index and link to `DEPLOYMENT.md`. Do not repeat environment variables,
platform steps, or deployment commands.

Keep the production source-of-truth row in `docs/README.md`, pointing to
`docker/DEPLOYMENT.md` and the four service-owned production files.

- [ ] **Step 3: Remove duplicate production procedures from supporting guides**

In `docs/containerized-infrastructure.md`, preserve local infrastructure,
database access, local pgAdmin, Smoke Testing, and local troubleshooting.
Replace detailed production topology/instructions with a short link to
`docker/DEPLOYMENT.md`.

In `docs/docker-commands.md`, preserve local/build command documentation and
environment boundaries. Replace the detailed production deployment section
with a short link to `docker/DEPLOYMENT.md`. Do not duplicate the individual
service sequence or Compose paths there.

- [ ] **Step 4: Verify the Compose contract stayed unchanged**

Run:

```powershell
git diff --exit-code b2e09e1 -- docker/services/pgdog-postgres/compose.deploy.yml docker/services/inngest/compose.deploy.yml docker/services/nextjs/compose.deploy.yml docker/services/playwright/compose.deploy.yml commands/docker.just
```

Expected: no output and exit code 0.

Render all four models using the matching examples:

```powershell
docker compose --env-file docker/services/pgdog-postgres/.env.example -f docker/services/pgdog-postgres/compose.deploy.yml config --quiet
docker compose --env-file docker/services/inngest/.env.example -f docker/services/inngest/compose.deploy.yml config --quiet
docker compose --env-file docker/services/nextjs/.env.example -f docker/services/nextjs/compose.deploy.yml config --quiet
docker compose --env-file docker/services/playwright/.env.example -f docker/services/playwright/compose.deploy.yml config --quiet
```

Expected: all commands exit 0.

- [ ] **Step 5: Verify one authoritative production guide**

Run:

```powershell
rg -n "backup|rollback|recovery|pg_dump|DATABASE_RESET=true" README.md docker/README.md docker/DEPLOYMENT.md docs/README.md docs/containerized-infrastructure.md docs/docker-commands.md
rg -n "docker compose .* up|just docker deploy" docker/DEPLOYMENT.md docs/containerized-infrastructure.md docs/docker-commands.md
git diff --check
git status --short --branch
```

Expected: production operational terms and startup commands have been removed
from current deployment documentation; local-development reset references may
remain in explicitly local sections; whitespace check passes; only intentional
documentation changes are present.

- [ ] **Step 6: Commit supporting documentation**

```powershell
git add README.md docker/README.md docs/README.md docs/containerized-infrastructure.md docs/docker-commands.md
git diff --cached --check
git commit -m "docs(deploy): route to minimal service guide"
```

### Task 3: Final review

**Files:**
- Verify all files modified in Tasks 1-2.

- [ ] **Step 1: Review final scope and preservation**

Run:

```powershell
git status --short --branch
git diff b2e09e1..HEAD --stat
git diff b2e09e1..HEAD
git diff --check b2e09e1..HEAD
```

Expected: only the six current documentation files changed after `b2e09e1`;
the minimal guide contains the exact requested scope; Compose, environment
examples, PgDog TOML files, command recipes, application code, and historical
documents remain unchanged.
