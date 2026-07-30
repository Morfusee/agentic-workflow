# MIHC Service-Owned Deploy Compose Design

**Date:** 2026-07-30

## Goal

Decouple the production deployment definitions for Next.js and Playwright in
the MIHC repository. Each application service will own its Compose definition
and deployment environment contract under `docker/services/`, matching the
existing Inngest, pgAdmin, and PgDog/PostgreSQL layout.

## Scope

This change affects the production deployment entrypoint and its operator
documentation. It does not change `docker/compose.build.yml`,
`docker/.env.build.example`, application source code, Dockerfiles, image
publishing, or runtime behavior.

## Architecture

Create these service-owned deployment files:

- `docker/services/nextjs/compose.yml`
- `docker/services/nextjs/.env.example`
- `docker/services/playwright/compose.yml`
- `docker/services/playwright/.env.example`

The real `docker/services/nextjs/.env` and
`docker/services/playwright/.env` files remain ignored, as with the existing
service directories. Operators create them from their corresponding examples.

`docker/compose.deploy.yml` becomes an include-only entrypoint. It includes the
existing three infrastructure Compose files plus the new Next.js and Playwright
Compose files. Each include supplies its service-local `.env` for Compose
interpolation, following the established infrastructure pattern.

## Service Definitions

The Next.js service-owned Compose file preserves:

- `ghcr.io/markvalenzuela-mmdc/mihc-nextjs:latest`
- the existing restart policy and `3000:3000` port mapping
- dependencies on PgDog and healthy Inngest
- all runtime variables currently required for database release, database
  reset control, authentication, public URL configuration, Inngest access, and
  production maintainer bootstrap

The Playwright service-owned Compose file preserves:

- `ghcr.io/markvalenzuela-mmdc/mihc-playwright:latest`
- `INNGEST_DEV=0` and `PORT=3939`
- port exposure, dependencies, and the existing healthcheck
- its database and Inngest runtime variables

Values required by both containers, such as the application database URL and
Inngest credentials, appear in both service-local examples. This duplication is
intentional: each service can be configured and deployed from its own contract
without depending on a shared application env file.

## Root Environment Removal

Production deployment stops depending on `docker/.env.deploy`. The tracked
`docker/.env.deploy.example` is removed after its variables are assigned to the
two service-local examples. Existing ignored `docker/.env.deploy` files are
user-owned and are not automatically deleted.

Deployment commands no longer pass `--env-file docker/.env.deploy`. The
service-local include declarations supply the environment used to interpolate
each included Compose model.

Inngest continues to own `INNGEST_SDK_URL` in
`docker/services/inngest/.env`; its example and deployment documentation must
describe that ownership explicitly.

## Documentation and Commands

Update the live deployment command wrapper and current Docker documentation so
that operators:

1. Copy each service-local `.env.example` to `.env`.
2. Configure secrets in the service that consumes them.
3. Run the deploy entrypoint without a root deployment env file.
4. Change `DATABASE_RESET` only in the Next.js service env during the guarded
   reset procedure.

Historical brainstorm and plan documents remain unchanged.

## Validation

Validation must prove:

- `docker compose -f docker/compose.deploy.yml config --quiet` succeeds with
  service-local env files present.
- The merged model contains exactly the expected Next.js, Playwright, PgDog,
  PostgreSQL, Inngest, Redis, and pgAdmin services.
- The Next.js and Playwright image values resolve to their existing GHCR
  `latest` images.
- Dependencies, ports, Playwright healthcheck, and fixed environment overrides
  are unchanged in the merged model.
- Active commands and operator documentation contain no dependency on
  `docker/.env.deploy`.
- `docker/compose.build.yml` remains unchanged.
- `git diff --check` passes and the final diff contains no unrelated changes.

## Migration

This is a configuration-path migration. Before the first deployment after the
change, operators create the two new ignored `.env` files from their examples
and transfer the corresponding values from the previous root file. Shared
credentials must match across service files and the relevant infrastructure
env files. The old ignored root file can be retained temporarily for rollback,
but the updated deployment entrypoint does not read it.
