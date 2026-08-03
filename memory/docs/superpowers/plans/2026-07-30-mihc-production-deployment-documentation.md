# MIHC Production Deployment Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $subagent-driven-development (recommended) or $executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one authoritative operator guide that explains how to deploy the repository-backed MIHC production stack with Docker Compose, Coolify, or Dokploy.

**Architecture:** Create `docker/DEPLOYMENT.md` beside `compose.deploy.yml` and make it the sole live production runbook. Keep the existing Compose topology unchanged: GitHub Actions publishes the Next.js and Playwright/Hono images, the single Next.js image performs database release before serving traffic, and the deploy Compose file includes the repository-owned infrastructure services and configuration files.

**Tech Stack:** Markdown, Docker Compose, GitHub Actions, GHCR, Next.js, Playwright/Hono, PostgreSQL, PgDog, Inngest, Redis, pgAdmin, Coolify, Dokploy

---

## File Map

- Create `docker/DEPLOYMENT.md`: authoritative production deployment model, configuration inventory, runbooks, platform guidance, operations, and troubleshooting.
- Modify `README.md`: add a prominent production-deployment link without duplicating the runbook.
- Modify `docker/README.md`: retain the Docker-area overview and replace its long startup-release procedure with a concise summary and link.
- Modify `docs/README.md`: add production deployment to the source-of-truth map.
- Modify `docs/containerized-infrastructure.md`: retain infrastructure details and replace its production/Coolify runbook with a pointer to `docker/DEPLOYMENT.md`.

Do not modify `docker/compose.deploy.yml`, service Compose files, environment examples, GitHub Actions workflows, application code, tests, or historical brainstorm/plan documents.

## Final-review amendment (authoritative)

The approved design/spec governs this amendment. The following corrections
supersede any conflicting instruction later in this plan:

1. Keep the live guide in this order: Coolify first, plain Docker second,
   Dokploy third. Coolify and Dokploy are both blocked for the current clean
   checkout until a private Compose/deployment adaptation materializes
   `docker/.env.deploy`, all three service-local `.env` files, and
   `docker/services/pgdog-postgres/files/users.toml` before Compose parsing and
   preserves them across redeploys. UI variables do not satisfy those literal
   paths. Dokploy Advanced -> Mounts persists content under its sibling
   `../files` area, but this repository's nested Compose path still needs an
   explicit private mapping; do not claim an untested mechanism.
2. Inventory every variable in `docker/.env.deploy.example` and all three
   service `.env.example` files. For each, record its file/boundary, consumer,
   secret classification, production form/default/required status, and
   cross-file alignment. Grouped summaries are insufficient.
3. Inventory six host-published mappings: fixed `3000:3000`, `6432:6432`,
   `8288:8288`, and `5050:80`, plus short-syntax `5432` and `6379`, which
   receive random host ports. Require resolved-port inspection and a private
   port override, loopback binding, or verified platform isolation.
4. On a clean checkout, copy `users.toml.example` to ignored `users.toml`,
   replace its secrets, and warn never to commit it before Compose validation.
5. A newly created, non-empty, parseable application PostgreSQL archive is an
   abort-on-failure prerequisite before any image update/recreate that could
   run migrations. Backup and verification precede `pull` and `up`.
6. Rollback uses a temporary Compose override that pins both application images
   to known-good semantic or `sha-*` tags, then pulls and force-recreates with
   both Compose files. Warn that image rollback does not reverse migrations
   and an older image may be incompatible with a forward schema.
7. The destructive reset procedure uses bounded status/log polling, shows the
   first recreate with `DATABASE_RESET=true`, immediately restores `false`,
   and shows the second recreate. Never use unbounded `logs --follow`.
8. State that release failure prevents `server.js` startup and repeat releases
   reconcile idempotently without resetting an existing password, duplicating
   bootstrap records, loading development fixtures, or deleting operational
   data.
9. The final/redeploy checklist verifies exactly one maintainer, four apps
   without duplication, no development fixtures, Next.js-to-PgDog,
   Inngest-to-Hono, SSE, all six host exposures including random ports, and
   survival of every named volume.
10. Main-branch pushes are gated by workflow path filters; GitHub does not
    evaluate those path filters for `v*.*.*` tag pushes.
11. In `docs/README.md`, use resolving Markdown links
    `../docker/compose.deploy.yml` and `../docker/DEPLOYMENT.md`, not code-form
    paths.

### Task 1: Create the deployment guide foundation and configuration contract

**Files:**
- Create: `docker/DEPLOYMENT.md`
- Reference: `.github/workflows/build-nextjs.yml`
- Reference: `.github/workflows/build-playwright.yml`
- Reference: `docker/compose.deploy.yml`
- Reference: `docker/.env.deploy.example`
- Reference: `docker/services/pgdog-postgres/.env.example`
- Reference: `docker/services/inngest/.env.example`
- Reference: `docker/services/pgadmin/.env.example`
- Reference: `docker/services/pgdog-postgres/files/pgdog.toml`
- Reference: `docker/services/pgdog-postgres/files/users.toml`

- [ ] **Step 1: Create the guide with its authority, audience, and supported paths**

Start `docker/DEPLOYMENT.md` with this structure and wording:

```markdown
# Production Deployment

This is the authoritative operator guide for deploying the MIHC production
stack. The primary deployment path connects the complete Git repository and
uses `docker/compose.deploy.yml`; copying that file alone is insufficient
because it includes service Compose files and mounts repository-backed PgDog
configuration.

Supported paths:

1. Coolify repository-backed Docker Compose deployment (expected production PaaS).
2. Plain Docker Compose on a VPS behind a dedicated reverse proxy.
3. Dokploy repository-backed Docker Compose deployment (blocked pending the
   documented persistent-file adaptation).

Provisioning every service separately is an advanced alternative. It must
preserve a shared Docker network and the service-name hostnames documented
below.
```

Add a short “What this guide does not change” note stating that the accepted
architecture uses one published Next.js image, performs database release in
the Next.js startup entrypoint, does not publish a one-shot release image, and
does not gate Playwright/Hono startup on Next.js release completion.

- [ ] **Step 2: Document the image delivery flow**

Add `## Delivery model` with the exact flow:

```text
push to main or version tag
  -> GitHub Actions builds application images
  -> GHCR stores branch, latest, semantic-version, and sha-* tags
  -> compose.deploy.yml pulls the configured image tags
  -> Next.js migrates and bootstraps before starting server.js
```

State these repository facts:

- For `main` branch pushes, `build-nextjs.yml` is path-filtered to `nextjs/**`
  or `.github/**`, while `build-playwright.yml` is path-filtered to
  `playwright/**`, `packages/enrollmate-contract/**`, or `.github/**`.
- Both workflows also run on `v*.*.*` tag pushes; GitHub does not evaluate
  `paths` filters for tag pushes. Do not describe the Playwright workflow's
  legacy feature-branch trigger as a production release path.
- `latest` is emitted only for the default branch.
- `compose.deploy.yml` currently references
  `ghcr.io/markvalenzuela-mmdc/mihc-nextjs:latest` and
  `ghcr.io/markvalenzuela-mmdc/mihc-playwright:latest`.
- Redeployment must pull/recreate containers to consume a newly published
  image.

Explain that `NEXT_PUBLIC_APP_URL` is passed as a Next.js build argument by
GitHub Actions. A public-domain change therefore requires updating the GitHub
Actions repository variable, rebuilding the Next.js image, and setting the
same runtime origin; changing only the runtime container variable may leave
browser assets with the previous URL.

- [ ] **Step 3: Document the full-repository Compose topology**

Add `## Repository and stack topology` with a service table:

| Service | Purpose | Internal dependency/hostname | Public by default? |
|---|---|---|---|
| `nextjs` | Web application and startup database release | `app-pgdog:6432`, `inngest:8288` | Application domain only |
| `playwright` | Hono/Inngest consumer | `app-pgdog:6432`, `inngest:8288` | No |
| `app-pgdog` | Application database proxy and pub/sub path | `app-postgres:5432` | No |
| `app-postgres` | Application PostgreSQL | Docker volume | No |
| `inngest` | Event orchestration | `inngest-postgres`, `inngest-redis`, `playwright:3939` | Only if the chosen operating model requires it |
| `inngest-postgres` | Inngest PostgreSQL | Docker volume | No |
| `inngest-redis` | Inngest queue/cache | Docker volume | No |
| `pgadmin` | Operator database UI | both PostgreSQL services | No |

State that `compose.deploy.yml` uses relative `include` paths, and the included
PgDog Compose file bind-mounts `files/pgdog.toml` and `files/users.toml`.
Therefore, a PaaS must check out the full repository and preserve those paths,
or the operator must deliberately translate them into provider-managed file
mounts/configs.

- [ ] **Step 4: Add the build-time and application-runtime variable table**

Add `## Configuration inventory` with one row for every variable in
`docker/.env.deploy.example` and all three service `.env.example` files. Each
row must include the exact file/boundary, consumer, secret classification,
production form/default/required status, and cross-file alignment. At minimum,
the application portion contains:

| Variable | Boundary | Secret? | Production value/relationship |
|---|---|---:|---|
| `NEXT_PUBLIC_APP_URL` | GitHub Actions build and application runtime | No | Exact public HTTPS origin; rebuild image when changed |
| `DATABASE_URL` | Application runtime | Yes | `postgresql://<APP_POSTGRES_USER>:<APP_POSTGRES_PASSWORD>@app-pgdog:6432/<APP_POSTGRES_DB>?sslmode=disable` |
| `DATABASE_RESET` | Next.js startup | No | `false`; use `true` only for a deliberate backed-up reset |
| `BETTER_AUTH_SECRET` | Application runtime | Yes | At least 32 random characters |
| `BETTER_AUTH_URL` | Application runtime | No | Same public HTTPS origin as `NEXT_PUBLIC_APP_URL` |
| `INNGEST_EVENT_KEY` | Application and Inngest runtime | Yes | Same value on producers and Inngest |
| `INNGEST_SIGNING_KEY` | Application and Inngest runtime | Yes | Same value on consumer and Inngest |
| `INNGEST_BASE_URL` | Application runtime | No | `http://inngest:8288` |
| `INNGEST_SDK_URL` | Inngest registration | No | `http://playwright:3939/api/inngest` |
| `PROD_MAINTAINER_NAME` | Next.js startup bootstrap | No | Intended production maintainer display name |
| `PROD_MAINTAINER_EMAIL` | Next.js startup bootstrap | No | Stable maintainer email |
| `PROD_MAINTAINER_PASSWORD` | Next.js startup bootstrap | Yes | Initial password; entrypoint unsets it before `server.js` |

Clarify that the root `--env-file docker/.env.deploy` supplies Compose
interpolation, while the `nextjs` and `playwright` services also load
`docker/.env.deploy` through `env_file`. Internal service URLs use Docker DNS,
not the public domain and not `localhost`.

- [ ] **Step 5: Add service-local environment and PgDog file tables**

Continue the row-by-row inventory for `PGDOG_RUST_LOG`, all application
PostgreSQL credentials, both Inngest keys and service URIs, poll/worker/retry/
tick/log/JSON/verbose settings, all Inngest PostgreSQL credentials, and both
pgAdmin credentials. Do not replace these rows with a file-level grouped
summary.

Then add a PgDog consistency checklist:

```text
APP_POSTGRES_USER     == users.toml [[users]].name
APP_POSTGRES_PASSWORD == users.toml [[users]].password
APP_POSTGRES_DB       == pgdog.toml [[databases]].name
DATABASE_URL user/password/database match the same three values
DATABASE_URL host     == app-pgdog
pgdog.toml backend    == app-postgres:5432
```

Warn that the committed `users.toml` values and every `.env.example` value are
examples, not production secrets. Preserve `pub_sub_channel_size = 4096`
because Smoke Testing live updates use PostgreSQL `LISTEN`/`NOTIFY`.

- [ ] **Step 6: Document persistent volumes and public exposure**

List these named volumes exactly:

- `app-postgres-data`
- `inngest-data`
- `inngest-postgres-data`
- `inngest-redis-data`
- `pgadmin-data`

State that `down -v` destroys named-volume data and must not appear in the
normal deployment/upgrade procedure.

Add `## Network and reverse proxy` explaining:

- route the public application domain to the `nextjs` container’s port `3000`;
- terminate HTTPS at the platform or dedicated proxy;
- keep Playwright/Hono, PostgreSQL, PgDog, Redis, and pgAdmin private;
- `ports` publishes a host port, while `expose` is container-network-only;
- current Compose publishes fixed mappings `3000:3000`, `6432:6432`,
  `8288:8288`, and `5050:80`, plus short-syntax container ports `5432` and
  `6379` on random host ports;
- operators must inspect all six resolved host mappings after deployment and
  must not call PostgreSQL/Redis private merely because no fixed host port is
  shown;
- production requires an override that removes private `ports` in favor of
  `expose`, loopback-only bindings, or independently verified platform
  isolation;
- the proxy must not buffer `text/event-stream` and must allow idle
  connections longer than the 20-second SSE heartbeat.

- [ ] **Step 7: Check the new guide for internal consistency**

Run:

```bash
rg -n "one-shot|Playwright/Hono|NEXT_PUBLIC_APP_URL|DATABASE_URL|users.toml|pub_sub_channel_size|3000|text/event-stream" docker/DEPLOYMENT.md
```

Expected: each accepted architecture and configuration boundary is explicitly
present; no section implies that Playwright waits for Next.js release.

- [ ] **Step 8: Commit the guide foundation**

```bash
git add docker/DEPLOYMENT.md
git commit -m "docs(deploy): define production deployment contract"
```

### Task 2: Add Coolify, plain Docker, Dokploy, and operations runbooks

**Files:**
- Modify: `docker/DEPLOYMENT.md`
- Reference: `commands/docker.just`
- Reference: `nextjs/scripts/start-container.sh`
- Reference: official Coolify Docker Compose documentation
- Reference: official Dokploy Docker Compose and Domains documentation

- [ ] **Step 1: Add prerequisites and pre-deployment checklist**

Add `## Before deployment` requiring:

- a host with Docker Engine and Compose v2, or a Compose-capable PaaS;
- DNS control and a public HTTPS domain;
- access to the complete Git repository;
- GHCR authentication when the images are private;
- unique production secrets;
- persistent storage and a tested database backup destination; and
- the GitHub Actions `NEXT_PUBLIC_APP_URL` variable set before the image build.

Include a “Never deploy examples unchanged” callout for every example password,
key, email, and PgDog credential.

- [ ] **Step 2: Add the plain Docker Compose runbook**

Document these repository-root commands in order:

```bash
cp docker/.env.deploy.example docker/.env.deploy
cp docker/services/pgdog-postgres/.env.example docker/services/pgdog-postgres/.env
cp docker/services/inngest/.env.example docker/services/inngest/.env
cp docker/services/pgadmin/.env.example docker/services/pgadmin/.env
cp docker/services/pgdog-postgres/files/users.toml.example \
  docker/services/pgdog-postgres/files/users.toml

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml config --quiet

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml pull

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml up -d

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml ps

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml logs --tail=200 nextjs
```

Before validation, tell the operator to replace secrets and update both PgDog
TOML files. Explicitly state that the copied `users.toml` and `.env` files are
ignored secret material and must never be committed. For private GHCR images,
document:

```bash
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin
```

Do not show actual credentials or recommend placing the token in a file.

- [ ] **Step 3: Add first-deploy verification**

Provide an explicit checklist:

```bash
docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml ps

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml logs --tail=200 nextjs playwright inngest app-pgdog

curl --fail --show-error --silent https://sanity.example.com/ >/dev/null
curl --fail --show-error --silent https://sanity.example.com/favicon.ico >/dev/null
```

Tell the operator to replace `https://sanity.example.com` with the production
origin and verify:

- Next.js logs end with `Database release completed.` before server startup;
- release failure prevents `server.js` startup;
- exactly one configured maintainer can sign in and keeps the same password
  after a repeated deployment;
- the four Smoke Testing apps exist exactly once without duplication;
- no profiles, run histories, or development credentials were created;
- existing operational data remains intact through a repeated deployment;
- Next.js reaches PostgreSQL through `app-pgdog:6432`;
- Inngest reports the Hono endpoint at
  `http://playwright:3939/api/inngest`; and
- SSE live updates remain connected through the proxy;
- all six host mappings, including random PostgreSQL/Redis ports, are not
  unintentionally public; and
- all five named volumes survive redeployment.

- [ ] **Step 4: Add backup-gated update, retry, rollback, and recovery procedures**

Before showing any update/recreate command that may run migrations, document a
new application-database backup and abort-on-failure verification. Create a
custom-format dump, require a non-empty file, and parse its archive listing
with `pg_restore --list` without printing secrets. Only then document the
normal image update:

```bash
docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml pull nextjs playwright

docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml up -d --force-recreate nextjs playwright
```

Require another current verified backup before retry after correcting
configuration:

```bash
docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml up -d --force-recreate nextjs
docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml logs --tail=200 nextjs
```

Provide an executable temporary Compose override that pins both Next.js and
Playwright to known-good semantic or `sha-*` tags, then uses both Compose files
for `config`, `pull`, and `up -d --force-recreate`. Require a new verified
backup first. State that image rollback does not reverse applied migrations,
that an older image can be incompatible with a forward schema, and that schema
problems require a forward Drizzle migration. For a broken or partial
maintainer account, use a supported Better Auth password/account recovery path,
then retry Next.js release.

Document safe shutdown without `-v`:

```bash
docker compose --env-file docker/.env.deploy \
  -f docker/compose.deploy.yml down
```

- [ ] **Step 5: Add the deliberate reset warning**

Document `DATABASE_RESET=true` as an exceptional, destructive operation:

1. take and verify a backup;
2. set the value to `true`;
3. force-recreate only `nextjs`;
4. use a bounded completion/status poll (never unbounded `logs --follow`);
5. immediately set the value back to `false`; and
6. force-recreate `nextjs` again.

Explain that `docker restart` and `docker compose start` retain the old
container environment and can repeat the destructive reset.

- [ ] **Step 6: Add the Coolify primary path first, prominently blocked**

Use the official Coolify Docker Compose guidance at
`https://coolify.io/docs/knowledge-base/docker/compose` and document:

1. create a repository-backed Docker Compose resource;
2. select the production branch and `docker/compose.deploy.yml`;
3. do not use Raw Compose unless the operator intentionally supplies proxy
   labels and accepts the advanced path;
4. label the current path blocked until a private deployment overlay/Compose
   adaptation materializes `docker/.env.deploy`, all three service-local
   `.env` files, and `docker/services/pgdog-postgres/files/users.toml` before
   Compose parsing and persists them across redeploys;
5. do not claim that Coolify UI variables or container storage create those
   exact checkout files;
6. assign the Next.js domain using the container port:
   `https://<production-domain>:3000`;
7. verify that Coolify routes normal public HTTPS to container port `3000`;
8. assign no public domains to PostgreSQL, PgDog, Redis, Playwright/Hono, or
   pgAdmin;
9. review persistent volumes; and
10. deploy, inspect logs, and run the shared verification checklist.

Explicitly explain that the `:3000` in Coolify’s domain setting identifies the
internal target port; users still browse normal HTTPS without `:3000`.

Do not claim that Coolify automatically creates files matching this
repository’s custom `env_file` paths. The guide must design the required
adaptation/blocker, not merely say “provision files.”

- [ ] **Step 7: Add concise Dokploy blocked-path notes**

Use:

- `https://docs.dokploy.com/docs/core/docker-compose`
- `https://docs.dokploy.com/docs/core/docker-compose/domains`

Document:

1. create a Compose application backed by the complete repository;
2. use Docker Compose rather than Docker Stack unless Swarm is intentional;
3. set the Compose path to `docker/compose.deploy.yml`;
4. explain that Dokploy Advanced -> Mounts persists files in its sibling
   `../files` area, but the current nested checkout-relative paths remain
   blocked pending a private Compose mapping to all five exact targets;
5. use the Domains tab to route the `nextjs` service to container port `3000`;
6. prefer isolated deployments or verify shared network attachment;
7. preview the generated Compose before deploying; and
8. use the shared verification checklist.

State the documented Dokploy behavior that UI variables are written to one
`.env` file but are not injected into containers unless referenced through
`env_file` or `${VARIABLE}`. Do not claim its current file workflow satisfies
this repository without the explicit persistent mapping/adaptation.

- [ ] **Step 8: Add the advanced decoupled-services alternative**

Keep this section short. Require one shared Docker network and either retain
these DNS names or update every consumer consistently:

```text
app-postgres
app-pgdog
inngest-postgres
inngest-redis
inngest
playwright
```

State that provider templates are optional and not assumed. Operators who
split services own health dependencies, secrets, persistent storage, file
mounts, and internal DNS.

- [ ] **Step 9: Add troubleshooting table**

Cover these symptoms and fixes:

| Symptom | Check/fix |
|---|---|
| Compose cannot find included file | Full repository and correct Compose path are required |
| `env_file` missing | Provision the exact repository-relative file |
| GHCR pull denied | Authenticate or make the package readable by the deployment |
| PgDog auth failure | Align `.env`, `users.toml`, `pgdog.toml`, and `DATABASE_URL` |
| Next.js restart loop | Inspect release logs and correct missing/invalid runtime values |
| Browser uses old origin | Rebuild Next.js after updating the GitHub Actions public URL |
| Hono does not register | Verify `INNGEST_SDK_URL=http://playwright:3939/api/inngest` |
| SSE disconnects/stalls | Disable proxy buffering and increase idle timeout |
| Domain returns gateway error | Route proxy to Next.js container port `3000` |
| Admin/database port is public | Remove domain, firewall host port, or use a private override |
| Data disappears after redeploy | Restore/reattach the expected named volume; never use `down -v` |

- [ ] **Step 10: Validate commands and commit the runbooks**

Run:

```bash
docker compose --env-file docker/.env.deploy.example \
  -f docker/compose.deploy.yml config --quiet
rg -n "Coolify|Dokploy|reverse proxy|backup|retry|rollback|recovery|down -v|Playwright/Hono" docker/DEPLOYMENT.md
git diff --check
```

Expected: Compose resolves when the service-local `.env` files exist; every
operational topic is present; `git diff --check` reports no whitespace errors.
If ignored service `.env` files are absent locally, create temporary copies
from their examples for validation and remove only those temporary copies
after confirming their exact paths.

Commit:

```bash
git add docker/DEPLOYMENT.md
git commit -m "docs(deploy): add production operator runbooks"
```

### Task 3: Make the guide discoverable and remove duplicate live runbooks

**Files:**
- Modify: `README.md:25-40`
- Modify: `docker/README.md:5-63`
- Modify: `docs/README.md:7-18`
- Modify: `docs/containerized-infrastructure.md:238-299`
- Reference: `docker/DEPLOYMENT.md`

- [ ] **Step 1: Link the guide from the root README**

After the existing containerized-infrastructure link near `README.md:25`, add:

```markdown
For production, follow [`docker/DEPLOYMENT.md`](docker/DEPLOYMENT.md). It
documents the GitHub Actions image pipeline, full-repository Compose
deployment, environment and configuration files, reverse proxy, Coolify,
Dokploy, backups, and recovery.
```

Do not copy environment tables or deploy commands into the root README.

- [ ] **Step 2: Reduce `docker/README.md` to a Docker-area index**

At `docker/README.md:17`, link both guides:

```markdown
- [Production Deployment](DEPLOYMENT.md) — authoritative operator runbook
- [Containerized Infrastructure](../docs/containerized-infrastructure.md) —
  local services, database access, and topology details
```

Replace the long `## Next.js startup database release` section with a concise
summary:

```markdown
## Production deployment

GitHub Actions publishes the Next.js and Playwright/Hono images, and
`compose.deploy.yml` deploys those images with the repository-owned
infrastructure services. The Next.js container applies migrations and
production bootstrap data before starting its server; Playwright/Hono starts
independently after its own infrastructure dependencies are healthy.

Follow [`DEPLOYMENT.md`](DEPLOYMENT.md) for configuration, deployment,
verification, reset, backup, rollback, Coolify, and Dokploy procedures.
```

Retain the local `just docker local` command guidance.

- [ ] **Step 3: Add deployment to the documentation source-of-truth map**

Add this row to `docs/README.md`:

```markdown
| Production deployment | [`../docker/compose.deploy.yml`](../docker/compose.deploy.yml) and [`../docker/DEPLOYMENT.md`](../docker/DEPLOYMENT.md) | Use the complete repository; the guide owns environment, proxy, PaaS, backup, and recovery procedures |
```

- [ ] **Step 4: Replace duplicated infrastructure runbooks with a pointer**

In `docs/containerized-infrastructure.md`, replace `## Production deployment
runbook` and `## Coolify Deployment` with:

```markdown
## Production deployment

The authoritative production runbook is
[`../docker/DEPLOYMENT.md`](../docker/DEPLOYMENT.md). It covers the
GitHub-Actions-to-GHCR delivery flow, repository provisioning, every
environment and configuration file, reverse-proxy exposure, Coolify, Dokploy,
database release, backups, retries, rollback, recovery, and first-deploy
verification.

This document remains the source for local infrastructure topology, database
access, pgAdmin registration, and service relationships.
```

Keep the existing troubleshooting rows that are useful for local
infrastructure. Remove only production rows that are now fully owned by
`docker/DEPLOYMENT.md`.

- [ ] **Step 5: Verify there is one live production runbook**

Run:

```bash
rg -n "^## (Production deployment runbook|Coolify Deployment)|docker/compose.deploy.yml up -d" README.md docker/README.md docs docker/DEPLOYMENT.md
```

Expected: the full production procedure appears only in
`docker/DEPLOYMENT.md`; index documents point to it.

- [ ] **Step 6: Check Markdown links**

Run a repository-available Markdown link checker if one exists. Independently
verify every new relative link target:

```powershell
@(
  'docker/DEPLOYMENT.md',
  'docs/containerized-infrastructure.md',
  'docker/compose.deploy.yml'
) | ForEach-Object {
  if (-not (Test-Path $_)) { throw "Missing link target: $_" }
}
```

Expected: no missing target.

- [ ] **Step 7: Commit documentation routing**

```bash
git add README.md docker/README.md docs/README.md docs/containerized-infrastructure.md
git commit -m "docs(deploy): route operators to production guide"
```

### Task 4: Final documentation and repository verification

**Files:**
- Verify: `docker/DEPLOYMENT.md`
- Verify: `README.md`
- Verify: `docker/README.md`
- Verify: `docs/README.md`
- Verify: `docs/containerized-infrastructure.md`

- [ ] **Step 1: Confirm only requested files changed**

Run:

```bash
git status --short
git diff main...HEAD --stat
git diff main...HEAD -- README.md docker/README.md docker/DEPLOYMENT.md docs/README.md docs/containerized-infrastructure.md
```

Expected: only the five planned documentation files differ from `main`.

- [ ] **Step 2: Validate the live Compose contract**

With ignored environment files provisioned from examples and no production
secrets in the output, run:

```bash
docker compose --env-file docker/.env.deploy.example \
  -f docker/compose.deploy.yml config --quiet
docker compose --env-file docker/.env.deploy.example \
  -f docker/compose.deploy.yml config --services
```

Expected services:

```text
app-postgres
app-pgdog
inngest-postgres
inngest-redis
inngest
pgadmin
nextjs
playwright
```

- [ ] **Step 3: Audit the guide against its required topics**

Run:

```bash
rg -n "GitHub Actions|GHCR|compose.deploy.yml|NEXT_PUBLIC_APP_URL|BETTER_AUTH_URL|DATABASE_URL|DATABASE_RESET|users.toml|pgdog.toml|Coolify|Dokploy|reverse proxy|text/event-stream|backup|retry|rollback|recovery|Playwright/Hono" docker/DEPLOYMENT.md
```

Expected: every topic has a substantive section or table entry.

- [ ] **Step 4: Scan for unsafe or stale guidance**

Run:

```bash
rg -n "down -v|localhost|host.docker.internal|one-shot|gate.*playwright|copy.*compose.deploy.yml" docker/DEPLOYMENT.md README.md docker/README.md docs/containerized-infrastructure.md
```

Review every match. Expected:

- `down -v` appears only in a warning;
- `localhost` appears only when distinguishing host/container behavior or
  loopback binding;
- `host.docker.internal` is rejected for the containerized consumer;
- one-shot image and Playwright gating appear only as explicitly rejected
  architecture;
- no instruction says to copy `compose.deploy.yml` without the repository.

- [ ] **Step 5: Run final formatting checks**

```bash
git diff --check
git status --short --branch
```

Expected: no whitespace errors; the branch is `feat/86d3v1vyn`; only the
intentional documentation commits are ahead of `main`.

- [ ] **Step 6: Review the final commit history**

```bash
git log --oneline main..HEAD
```

Expected commits:

```text
docs(deploy): route operators to production guide
docs(deploy): add production operator runbooks
docs(deploy): define production deployment contract
```

Do not push, open a pull request, or mark the ClickUp task complete until the
user reviews the implemented documentation and explicitly requests those
actions.
