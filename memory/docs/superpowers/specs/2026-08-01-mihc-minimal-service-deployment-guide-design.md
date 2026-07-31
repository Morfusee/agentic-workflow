# MIHC Minimal Service Deployment Guide Design

**Date:** 2026-08-01

## Goal

Replace the broad production operations runbook with a concise guide for
deploying each MIHC service group independently through Coolify or Dokploy.

## Scope

Keep the existing four service-owned production Compose files and their runtime
configuration unchanged. Simplify current documentation so it covers only:

- the service-local `.env` files;
- the shared `mihc-network`;
- PgDog `pgdog.toml` and `users.toml` configuration;
- individual Coolify and Dokploy resources;
- the service-owned `compose.deploy.yml` files; and
- the required service startup sequence.

Remove backup, update, rollback, reset, recovery, volume-migration, and general
troubleshooting procedures from the deployment guide. Local-development
documentation, including local-only pgAdmin guidance, remains available.

## Documentation Structure

`docker/DEPLOYMENT.md` is the only authoritative production guide. It contains:

1. A short topology and network explanation.
2. One section for PgDog/application PostgreSQL.
3. One section for Inngest/PostgreSQL/Redis.
4. One section for Next.js.
5. One section for Playwright/Hono.
6. The required order for deploying or starting those resources.

The root README, Docker README, documentation index, containerized
infrastructure guide, and Docker command guide link to the authoritative guide
instead of duplicating production instructions.

## Service Contracts

The PgDog/PostgreSQL production file creates the literal named bridge network
`mihc-network`. Every other production file declares that network external.
The guide instructs operators to deploy PgDog/PostgreSQL first so the network
exists.

The PgDog section explains how these values stay aligned:

```text
APP_POSTGRES_USER     == users.toml [[users]].name
APP_POSTGRES_PASSWORD == users.toml [[users]].password
APP_POSTGRES_DB       == pgdog.toml [[databases]].name
DATABASE_URL user/password/database match those values
DATABASE_URL host     == app-pgdog
pgdog.toml backend    == app-postgres:5432
```

The guide references tracked `.env.example`, `pgdog.toml`, and
`users.toml.example` files without copying real credentials into documentation.
The credential disclosed in chat remains excluded from tracked files and must
be rotated before deployment.

## Deployment Sequence

Deploy and confirm each resource in this order:

1. PgDog and application PostgreSQL.
2. Inngest, Inngest PostgreSQL, and Redis.
3. Next.js.
4. Playwright/Hono.

Coolify and Dokploy each use four individual repository-backed Compose
resources pointing at the corresponding `compose.deploy.yml`. Only Next.js is
routed publicly. pgAdmin is not a production resource.

## Validation

Validation must prove that all four production Compose files render with their
matching example environment files; PgDog/PostgreSQL owns `mihc-network`; all
consumer services attach to the external network; the guide uses exact tracked
paths and the required deployment sequence; duplicate production instructions
are removed from other current documentation; no production pgAdmin or
disclosed credential is introduced; and `git diff --check` passes.
