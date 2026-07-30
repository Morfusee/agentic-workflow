# MIHC Service-Owned Deploy Compose Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the production Next.js and Playwright service definitions and environment contracts into service-owned folders while keeping `compose.deploy.yml` as an include-only GHCR deployment entrypoint.

**Architecture:** Add one deployment Compose model and one environment example per application service under `docker/services/`. Merge those models with the existing infrastructure models through Compose `include`, then remove the obsolete root deployment environment boundary from commands and active operator documentation.

**Tech Stack:** Docker Compose include specification, YAML, dotenv files, Just, Markdown

---

## File Structure

- Create `docker/services/nextjs/compose.yml`: production Next.js service model.
- Create `docker/services/nextjs/.env.example`: Next.js deployment environment contract.
- Create `docker/services/playwright/compose.yml`: production Playwright/Hono service model.
- Create `docker/services/playwright/.env.example`: Playwright deployment environment contract.
- Modify `docker/compose.deploy.yml`: include the five service-owned Compose models.
- Delete `docker/.env.deploy.example`: remove the obsolete shared application contract.
- Modify `docker/services/inngest/.env.example`: document the Inngest-owned SDK callback.
- Modify `commands/docker.just`: run deploy Compose without the root env file.
- Modify `docker/README.md`, `docker/DEPLOYMENT.md`, `docs/containerized-infrastructure.md`, and `docs/docker-commands.md`: document the service-local deployment boundary.

### Task 1: Add service-owned application Compose models

**Files:**
- Create: `docker/services/nextjs/compose.yml`
- Create: `docker/services/nextjs/.env.example`
- Create: `docker/services/playwright/compose.yml`
- Create: `docker/services/playwright/.env.example`
- Modify: `docker/services/inngest/.env.example`

- [ ] **Step 1: Add the Next.js Compose model**

Create `docker/services/nextjs/compose.yml` with the existing GHCR image,
restart policy, port, dependencies, and an explicit environment list:

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
    ports:
      - "3000:3000"
    depends_on:
      app-pgdog:
        condition: service_started
      inngest:
        condition: service_healthy
```

- [ ] **Step 2: Add the Next.js environment example**

Create `docker/services/nextjs/.env.example`:

```dotenv
DATABASE_URL=postgresql://mihc:replace-with-a-secret@app-pgdog:6432/mihc?sslmode=disable
DATABASE_RESET=false
NEXT_PUBLIC_APP_URL=https://sanity.example.com
BETTER_AUTH_SECRET=replace-with-a-random-secret-at-least-32-characters
BETTER_AUTH_URL=https://sanity.example.com
INNGEST_EVENT_KEY=replace-with-an-event-key
INNGEST_BASE_URL=http://inngest:8288
INNGEST_SIGNING_KEY=replace-with-a-signing-key

PROD_MAINTAINER_NAME=Production Maintainer
PROD_MAINTAINER_EMAIL=maintainer@example.com
# Used only by the startup bootstrap and removed before the Next.js server starts.
PROD_MAINTAINER_PASSWORD=replace-with-a-secret
```

- [ ] **Step 3: Add the Playwright Compose model**

Create `docker/services/playwright/compose.yml`:

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
    depends_on:
      app-postgres:
        condition: service_healthy
      app-pgdog:
        condition: service_started
      inngest-redis:
        condition: service_healthy
      inngest:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3939/health').then((response)=>process.exit(response.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
```

- [ ] **Step 4: Add the Playwright environment example**

Create `docker/services/playwright/.env.example`:

```dotenv
DATABASE_URL=postgresql://mihc:replace-with-a-secret@app-pgdog:6432/mihc?sslmode=disable
INNGEST_EVENT_KEY=replace-with-an-event-key
INNGEST_BASE_URL=http://inngest:8288
INNGEST_SIGNING_KEY=replace-with-a-signing-key
```

- [ ] **Step 5: Complete the Inngest environment example**

Add the callback immediately after `INNGEST_REDIS_URI` in
`docker/services/inngest/.env.example`:

```dotenv
INNGEST_SDK_URL=http://playwright:3939/api/inngest
```

### Task 2: Convert the deploy entrypoint to includes

**Files:**
- Modify: `docker/compose.deploy.yml`
- Delete: `docker/.env.deploy.example`

- [ ] **Step 1: Replace inline application services with includes**

Make `docker/compose.deploy.yml` contain only:

```yaml
include:
  - path: services/pgdog-postgres/compose.yml
    env_file: services/pgdog-postgres/.env
  - path: services/inngest/compose.yml
    env_file: services/inngest/.env
  - path: services/pgadmin/compose.yml
    env_file: services/pgadmin/.env
  - path: services/nextjs/compose.yml
    env_file: services/nextjs/.env
  - path: services/playwright/compose.yml
    env_file: services/playwright/.env
```

- [ ] **Step 2: Delete the obsolete shared example**

Delete `docker/.env.deploy.example`; do not delete any ignored
`docker/.env.deploy` file in the user's workspace.

### Task 3: Update the executable deployment command

**Files:**
- Modify: `commands/docker.just`

- [ ] **Step 1: Remove the root env argument**

Change the deploy recipe command to:

```just
deploy action="up":
    @docker compose -f "{{ justfile_directory() }}/docker/compose.deploy.yml" {{action}} {{if action == "up" { "-d" } else { "" }}}
```

- [ ] **Step 2: Verify the recipe renders**

Run:

```powershell
just --list docker
just --dry-run docker deploy up
```

Expected: the deploy command contains `docker/compose.deploy.yml` and no
`.env.deploy`.

### Task 4: Update active deployment documentation

**Files:**
- Modify: `docker/README.md`
- Modify: `docker/DEPLOYMENT.md`
- Modify: `docs/containerized-infrastructure.md`
- Modify: `docs/docker-commands.md`

- [ ] **Step 1: Update service-layout summaries**

List `docker/services/nextjs/` and `docker/services/playwright/` as
service-owned production definitions. State that `.env.build` remains shared
only by the build stack, while every deploy include reads its own ignored
service-local `.env`.

- [ ] **Step 2: Update the production configuration inventory**

Split the application table by file ownership:

```text
docker/services/nextjs/.env
  DATABASE_URL, DATABASE_RESET, NEXT_PUBLIC_APP_URL, BETTER_AUTH_SECRET,
  BETTER_AUTH_URL, INNGEST_EVENT_KEY, INNGEST_BASE_URL,
  INNGEST_SIGNING_KEY, PROD_MAINTAINER_NAME, PROD_MAINTAINER_EMAIL,
  PROD_MAINTAINER_PASSWORD

docker/services/playwright/.env
  DATABASE_URL, INNGEST_EVENT_KEY, INNGEST_BASE_URL, INNGEST_SIGNING_KEY

docker/services/inngest/.env
  INNGEST_SDK_URL and the existing Inngest-owned variables
```

Explain that duplicate database and Inngest values must remain aligned.

- [ ] **Step 3: Update setup, reset, backup, and deployment commands**

Replace setup of `docker/.env.deploy` with:

```bash
cp docker/services/nextjs/.env.example docker/services/nextjs/.env
cp docker/services/playwright/.env.example docker/services/playwright/.env
```

Remove `--env-file docker/.env.deploy` from deploy Compose commands. Update the
guarded reset procedure to read and edit
`docker/services/nextjs/.env`. Update persistent-file and platform mappings to
list both application service env files instead of the root deployment file.

- [ ] **Step 4: Verify active references are gone**

Run:

```powershell
rg -n "\.env\.deploy" README.md docker docs commands justfile `
  -g "*.md" -g "*.just" -g "*.yml" -g "*.yaml" `
  -g "!docs/brainstorm/**" -g "!docs/plans/**"
```

Expected: no active references. Historical documents under `docs/brainstorm`
and `docs/plans` are excluded from modification and may retain historical
command text.

### Task 5: Validate the merged deployment model

**Files:**
- Verify all files changed above.

- [ ] **Step 1: Prepare ignored validation env files without exposing secrets**

If the new ignored `.env` files do not exist, copy their examples for local
configuration validation. These ignored files are validation artifacts and
must not be staged.

- [ ] **Step 2: Validate Compose**

Run:

```powershell
docker compose -f docker/compose.deploy.yml config --quiet
docker compose -f docker/compose.deploy.yml config --services
docker compose -f docker/compose.deploy.yml config --images
```

Expected: config validation succeeds; the service list contains `nextjs`,
`playwright`, `app-pgdog`, `app-postgres`, `inngest`, `inngest-postgres`,
`inngest-redis`, and `pgadmin`; application images are the two expected GHCR
`latest` images.

- [ ] **Step 3: Confirm build deployment remains unchanged**

Run:

```powershell
git diff --exit-code -- docker/compose.build.yml docker/.env.build.example
```

Expected: exit code 0.

- [ ] **Step 4: Review the final diff**

Run:

```powershell
git diff --check
git status --short
git diff -- docker commands docs
```

Expected: no whitespace errors, no unrelated files, and no staged or tracked
real `.env` files.
