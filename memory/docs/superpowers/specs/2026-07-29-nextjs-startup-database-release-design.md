# Next.js Startup Database Release Design

Date: 2026-07-29

## Goal

Keep production deployment simple: the existing Next.js image applies Drizzle
migrations and runs the idempotent production bootstrap before starting the
Next.js server. Development migration and fixture seeding remain unchanged.

## Deployment flow

The normal production container runs one startup sequence:

1. Apply committed Drizzle migrations to `DATABASE_URL`.
2. Bootstrap the configured production maintainer and the four Smoke Testing
   apps.
3. Start `node server.js`.

If migration or bootstrap fails, the server does not start. Docker Compose's
existing restart policy retries the whole container. Downtime during a failed
release is acceptable.

## Docker and Compose

- Use only the existing Next.js production image.
- Remove the separate database-release Docker target and image.
- Remove the `db-release` service and its startup gate from
  `docker/compose.deploy.yml`.
- Package the migration files, production seed source, and required execution
  dependencies in the normal Next.js image.
- Make the image entrypoint run the release command before the standalone
  Next.js server.
- Pass the required production maintainer variables to the `nextjs` service.
- Keep the production database dependency in Compose; no additional
  deployment orchestration is introduced.

## CI/CD

Restore `.github/workflows/build-nextjs.yml` to its original single-image
workflow. It builds and publishes only the normal Next.js image with the
existing branch, `latest`, semantic-version, and SHA tags.

The workflow does not inspect registry state, coordinate image pairs, or
publish a separate migration image.

## Database behavior

- Keep the production bootstrap separate from the full development seed.
- Production creates or validates the configured maintainer and upserts only
  the canonical Smoke Testing apps.
- Existing maintainer passwords are not reset.
- Repeated container starts are safe: committed migrations and production
  bootstrap operations remain idempotent.
- Development commands retain their current behavior:
  - `just db migrate` applies development migrations.
  - `just db seed` loads the complete development fixtures.
  - `just db reset` remains a development-only destructive command.

## Error handling

- Missing production configuration fails before server startup.
- Migration or bootstrap errors are logged without exposing passwords.
- The container exits non-zero on failure.
- Compose restarts the container according to its existing restart policy.
- No registry publication state machine or separate release-service recovery
  procedure is required.

## Verification

- Unit tests cover production configuration and idempotent seed behavior.
- Integration tests cover initial bootstrap and repeat bootstrap without
  duplicate or destructive changes.
- A production-image test confirms startup order:
  migrations, production bootstrap, then Next.js.
- The original GitHub workflow is byte-for-byte restored.
- Compose renders without a `db-release` service or separate image variables.

