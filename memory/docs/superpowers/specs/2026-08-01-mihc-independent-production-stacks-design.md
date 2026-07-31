# MIHC Independent Production Stacks Design

**Date:** 2026-08-01

## Goal

Make each production service group independently deployable while preserving a
single private Docker network. The application PostgreSQL/PgDog stack creates
that network, foundational infrastructure starts before application services,
and pgAdmin is omitted from production deployment.

## Scope

This change affects Docker production Compose definitions, deployment commands,
and current operator documentation in the MIHC repository. Local development
continues to use the existing `compose.yml` files and may continue to include
pgAdmin. Application source, Dockerfiles, image publishing, build Compose, and
runtime behavior remain unchanged.

## Architecture

Create service-owned production definitions at:

- `docker/services/pgdog-postgres/compose.deploy.yml`
- `docker/services/inngest/compose.deploy.yml`
- `docker/services/nextjs/compose.deploy.yml`
- `docker/services/playwright/compose.deploy.yml`

The corresponding service-local `.env` files remain the interpolation source.
No pgAdmin production Compose file is added, and production documentation no
longer provisions or verifies pgAdmin.

The deployment model consists of independent Compose projects rather than one
merged include model. This permits the PostgreSQL/PgDog definition to own the
network while later definitions reference the same network as external.

## Network Ownership

Use `mihc-network` as both the Compose network key and the Docker network name.

The PgDog/PostgreSQL deployment definition declares a named bridge network and
attaches both `app-postgres` and `app-pgdog`. Starting this foundational stack
creates the network. The Inngest, Next.js, and Playwright deployment definitions
declare `mihc-network` as external and attach every service they define.

Consumers fail clearly if the foundational stack has not created the network.
Documentation therefore treats starting PgDog/PostgreSQL first as mandatory.

## Service Definitions

Production definitions preserve the images, environment contracts, volumes,
healthchecks, exposure settings, and internal service hostnames from the
supplied deployed-server configuration. PgDog retains its `6432:6432` host
mapping and must be restricted at the host or platform boundary; the supplied
Next.js, Playwright, Inngest, PostgreSQL, and Redis definitions use `expose`.
No production definition publishes pgAdmin or includes its data volume.

The Inngest stack contains `inngest`, `inngest-postgres`, and `inngest-redis`.
The PgDog/PostgreSQL stack contains `app-pgdog` and `app-postgres`. Next.js and
Playwright remain separate application stacks and use their existing GHCR
images.

Tracked examples remain placeholders. The real PgDog `users.toml` stays ignored
and no credential supplied through chat is copied into version control. Because
a production-looking password was disclosed in the request, operators must
rotate it before the next deployment and align PostgreSQL, PgDog, and
`DATABASE_URL` values.

## Deployment Sequence

The production runbook deploys and verifies stacks in this order:

1. Start PgDog and application PostgreSQL, creating `mihc-network`.
2. Start Inngest, its PostgreSQL database, and Redis on that network.
3. Start Next.js and Playwright after foundational health checks succeed.

Each command identifies the service-owned production Compose file explicitly.
Shutdown and recovery guidance preserves named volumes and accounts for the
independent Compose project boundaries.

## Documentation

Update current Docker documentation and executable deployment commands to:

- describe service-owned `compose.deploy.yml` files;
- remove pgAdmin from the production topology, configuration inventory,
  persistence inventory, exposure checks, PaaS instructions, and verification;
- explain network ownership and the required deployment order;
- use per-stack commands instead of the previous all-services entrypoint; and
- retain pgAdmin only in local-development documentation where applicable.

Historical brainstorm and plan documents remain unchanged.

## Failure Handling

If `mihc-network` is absent, stop and deploy the PgDog/PostgreSQL stack rather
than creating the network manually. If a foundational healthcheck fails, do not
start Next.js or Playwright. Normal shutdown must not use `down -v`; backup,
reset, rollback, and recovery procedures continue to protect application data.

## Validation

Validation must prove:

- each service-owned production Compose file renders successfully with its
  service-local environment present;
- the PgDog/PostgreSQL model creates the named bridge network `mihc-network`;
- every other production model references `mihc-network` as external and every
  production service is attached to it;
- pgAdmin is absent from all production Compose definitions and current
  production instructions;
- the documented commands enforce foundations before applications;
- expected images, volumes, environment variables, and healthchecks remain
  present;
- local Compose behavior remains unchanged;
- no secret from the supplied server configuration is committed; and
- `git diff --check` passes with no unrelated changes.
