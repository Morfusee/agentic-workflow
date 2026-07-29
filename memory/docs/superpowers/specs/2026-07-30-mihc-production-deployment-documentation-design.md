# MIHC Production Deployment Documentation Design

Date: 2026-07-30
Status: Approved

## Purpose

Create one operator-focused production deployment guide for the MIHC stack. The
guide must explain how the published application images, repository-backed
Compose topology, environment variables, configuration files, public domain,
reverse proxy, persistent services, and database release behavior fit
together.

The guide is documentation for deploying the existing stack. It does not
redesign the Compose topology or decouple its services.

## Documentation Location

Add the long-form guide at:

```text
docker/DEPLOYMENT.md
```

Keep `docker/README.md` as the short Docker-area index. Replace duplicated live
deployment instructions elsewhere with concise links to the deployment guide
where practical, while retaining material that belongs to general
infrastructure or command documentation.

Add discoverable links from:

- the repository `README.md`;
- `docker/README.md`;
- `docs/README.md`; and
- `docs/containerized-infrastructure.md`.

`docker/DEPLOYMENT.md` becomes the live source of truth for production
deployment. Historical brainstorm and plan documents do not override it.

## Audience and Supported Paths

The primary audience is an operator deploying MIHC from the Git repository to
a Compose-capable platform.

Document these paths in this order:

1. Coolify service-stack deployment as the expected production PaaS.
2. Plain Docker Compose on a VPS with a dedicated reverse proxy.
3. Dokploy as a deployment path that has been exercised in practice.
4. Individually provisioned services as an advanced alternative, not the
   default.

Do not claim that the complete Coolify path has been tested unless it has been.
Distinguish repository facts, official platform behavior, and
platform-dependent operator choices.

## Deployment Model

The guide must establish the following mental model before giving procedures:

1. GitHub Actions builds the Next.js and Playwright/Hono images.
2. The workflows publish those images to GitHub Container Registry.
3. `docker/compose.deploy.yml` pulls the published images rather than building
   them on the deployment host.
4. The same Compose file owns the production application and infrastructure
   stack by including the service Compose files for PgDog/PostgreSQL, Inngest
   and Redis, and pgAdmin.
5. Next.js startup applies committed Drizzle migrations and runs the
   idempotent production bootstrap before serving traffic.

Document the actual workflow triggers and tags. In particular, explain that
the `latest` tag is published from the default branch, and that a deployment
must pull or redeploy to consume a newly published image.

## Repository Requirement

The primary deployment path connects or checks out the full repository. Merely
copying `docker/compose.deploy.yml` is insufficient because it uses relative
`include` paths and repository-backed PgDog configuration files.

For Coolify and similar platforms, instruct the operator to:

- connect the Git repository;
- select the intended production branch;
- point the Compose path to `docker/compose.deploy.yml`; and
- verify that included Compose files and mounted configuration files remain
  available at their repository-relative paths.

The advanced decoupled path may provision PgDog/PostgreSQL, Inngest/Redis,
pgAdmin, Next.js, and Playwright/Hono separately. It must preserve a shared
Docker network and stable service-name hostnames such as `app-pgdog`,
`inngest`, and `playwright`, or update every dependent internal URL
consistently. The guide must not imply that provider templates are known to
exist for these services.

## Configuration Inventory

Provide a table for every required or operationally significant value,
including:

- where it is configured;
- which service consumes it;
- whether it is build-time or runtime;
- whether it is secret;
- the expected production form; and
- which other values must remain aligned with it.

Divide configuration into these boundaries:

### GitHub Actions build configuration

`NEXT_PUBLIC_APP_URL` is passed to the Next.js image build. Because public
Next.js variables may be embedded in browser assets, a domain change requires:

1. changing the GitHub repository or Actions variable;
2. rebuilding and publishing the Next.js image; and
3. setting the matching runtime public URL.

### Application runtime configuration

Document the values represented by `docker/.env.deploy.example`, including:

- `DATABASE_URL`;
- `DATABASE_RESET`;
- `NEXT_PUBLIC_APP_URL`;
- `BETTER_AUTH_SECRET`;
- `BETTER_AUTH_URL`;
- the Inngest URLs and keys; and
- production maintainer bootstrap fields.

State that `NEXT_PUBLIC_APP_URL` and `BETTER_AUTH_URL` should use the externally
reachable HTTPS origin. Internal service-to-service URLs must continue to use
Docker DNS names rather than the public domain.

### Service-local environment

Document the ignored `.env` files required by each included service and how a
PaaS must provision them without committing secrets.

### PgDog configuration

Explain the relationship among:

- `docker/services/pgdog-postgres/.env`;
- `docker/services/pgdog-postgres/files/users.toml`;
- `docker/services/pgdog-postgres/files/pgdog.toml`; and
- the username, password, database, and host in `DATABASE_URL`.

The guide must warn operators not to deploy the example or repository
credentials as production secrets. It must explain that platform file editors,
file mounts, Compose configs, or another secret-backed file mechanism may be
needed for the TOML files.

### Persistent data

Identify the named volumes for PostgreSQL, Redis, and pgAdmin, explain that
redeployment must retain them, and require a database backup before risky
database or image changes.

## Network and Public Exposure

Only the Next.js service should receive the normal public application domain.
The proxy must route that domain to container port `3000` and terminate HTTPS.

The guide must distinguish:

- `ports`, which publishes a container port on the host;
- `expose`, which documents or permits container-network access without a
  host mapping; and
- PaaS domain routing, which forwards through the provider proxy.

Because the current deploy Compose file publishes `3000:3000`, explicitly
warn that the host port remains directly reachable unless a firewall,
loopback-only binding, Compose override, or platform isolation prevents it.
Document the risk without changing the Compose file as part of this
documentation task.

Keep PostgreSQL, PgDog, Redis, the Playwright/Hono consumer, and pgAdmin private
unless an operator has a specific protected administrative need. If Inngest
requires external access for the selected operating model, document it
separately rather than presenting it as the public application.

The reverse proxy must support unbuffered `text/event-stream` responses and
idle connections longer than the application's SSE heartbeat.

## Coolify Procedure

The Coolify section must instruct the operator to:

1. create a repository-backed Docker Compose resource;
2. select `docker/compose.deploy.yml`;
3. provision runtime values and all required service-local files;
4. configure the Next.js domain with container port `3000`;
5. verify HTTPS and DNS;
6. keep internal services without public domains;
7. validate persistent storage;
8. deploy and inspect startup health and logs; and
9. verify the application, authentication, database bootstrap, and SSE path.

Explain that Compose is the source of truth for the service stack. Where
Coolify UI behavior cannot directly satisfy the repository's `env_file` or
bind-mounted file paths, give explicit options and label them as
platform-specific adaptations.

## Plain Docker Compose Procedure

Provide copyable commands to:

- create ignored environment files from examples;
- validate the resolved Compose configuration;
- authenticate to GHCR when images are private;
- pull images;
- start or recreate the stack;
- inspect service status and health;
- inspect Next.js startup logs;
- redeploy after image publication; and
- stop the stack without deleting named volumes.

Document a dedicated reverse proxy as the normal public entrypoint and caution
against an unprotected direct port mapping.

## Dokploy Notes

Describe the tested repository-backed Compose workflow:

- select Docker Compose rather than Docker Stack unless Swarm behavior is
  intentionally required;
- point to `docker/compose.deploy.yml`;
- provide environment values;
- use the Domains UI to route the Next.js service to container port `3000`;
- provision or edit PgDog TOML files through the platform-supported file
  workflow; and
- preview the final Compose configuration before deployment.

Do not let the Dokploy section become a second full runbook; refer back to the
shared configuration and verification sections.

## Database Release and Recovery

Document the startup release gate and its observable behavior:

- pending migrations and production bootstrap run before Next.js starts;
- failed migration, validation, or bootstrap prevents application startup;
- repeated deployment remains idempotent;
- production bootstrap does not load development fixtures;
- `PROD_MAINTAINER_PASSWORD` is removed before the long-running server starts;
  and
- `DATABASE_RESET` remains `false` except during a deliberate, backed-up reset.

Include validation, retry, log inspection, backup, and forward-recovery
guidance. State that rolling an image back does not reverse an applied database
migration.

## Verification and Troubleshooting

The final checklist must verify:

- both GHCR images can be pulled;
- all Compose services start or become healthy as appropriate;
- the configured HTTPS domain reaches Next.js;
- authentication uses the same public origin;
- exactly one configured production maintainer exists;
- the four required application records exist without duplication;
- no development fixtures or credentials were seeded;
- Next.js can reach PgDog;
- Inngest can reach the Playwright/Hono consumer;
- SSE responses survive the proxy;
- internal/admin services are not unintentionally public; and
- named volumes survive redeployment.

Troubleshooting must cover at least image authentication, missing included
files, unresolved `env_file` paths, PgDog credential mismatch, internal
hostname mistakes, stale build-time public URLs, reverse-proxy port mistakes,
SSE buffering/timeouts, failed startup migration/bootstrap, and accidental
port exposure.

## Scope Boundaries

This documentation task does not:

- change `compose.deploy.yml`;
- create provider-specific Compose overrides;
- split the stack into independently managed services;
- add a new image release workflow;
- verify a production Coolify deployment; or
- promise the availability of provider templates.

Any limitation discovered while documenting the existing topology should be
called out clearly and proposed as separate follow-up work.

## Acceptance Criteria

The documentation is complete when an operator can:

1. explain the GitHub Actions-to-GHCR-to-Compose delivery flow;
2. identify every build-time, runtime, service-local, and file-backed setting;
3. deploy the repository-backed stack with plain Docker Compose;
4. configure the expected Coolify path without exposing internal services;
5. adapt the same stack to Dokploy using its tested UI workflow;
6. update a production domain without leaving stale client-side configuration;
7. validate migrations and idempotent bootstrap behavior;
8. preserve and back up persistent data;
9. diagnose the documented common failures; and
10. find this guide from the repository's main documentation entrypoints.
