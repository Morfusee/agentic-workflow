# Database Reset Startup Flag Design

## Goal

Replace the current reset confirmation phrase with a simple
`DATABASE_RESET=true|false` setting. The production Next.js image must inspect
this setting every time its container starts.

## Startup behavior

- `DATABASE_RESET=true` destructively drops the application `public` and
  `drizzle` schemas, reapplies every committed Drizzle migration, runs the
  production bootstrap, and then starts Next.js.
- `DATABASE_RESET=false` applies pending Drizzle migrations, runs the
  idempotent production bootstrap, and then starts Next.js without deleting
  existing data.
- A missing value behaves like `false`.
- Only the exact lowercase value `true` enables the destructive reset.
- If migration, reset, or bootstrap fails, Next.js does not start.

This behavior applies on every container startup, including automatic Docker
restarts. Leaving `DATABASE_RESET=true` intentionally causes each restart to
delete application data again.

## Configuration

Add `DATABASE_RESET=false` to:

- `docker/.env.build`
- `docker/.env.deploy`
- `docker/.env.build.example`
- `docker/.env.deploy.example`

The existing Compose `env_file` configuration passes the setting to the
Next.js container. No duplicate conditional command belongs in the Compose
files.

## Implementation

The Next.js Docker image startup command selects one of the existing scripts:

- `true`: run `scripts/reset-production-database.ts`, which resets the schemas
  and then performs the normal database release.
- otherwise: run `scripts/release-database.ts`.

After either path completes, the startup command removes the maintainer
password from the server process environment and starts the standalone Next.js
server.

Rename the reset script guard from `DATABASE_RESET_CONFIRMATION` to
`DATABASE_RESET` and require its value to be exactly `true`. Remove the
now-redundant `db-reset` profile service from `docker/compose.build.yml`.

## Seed boundary

Both startup paths use the existing production bootstrap. A fresh database
receives only:

- the configured production maintainer;
- the Smoke Testing application catalog; and
- the E2E workflow step definitions.

Development profiles, runs, and other fixture data are not loaded.

## Verification

- Unit tests cover `true`, `false`, missing, and non-production reset-script
  behavior.
- Compose configuration validates for both build and deploy files.
- Docker image build succeeds.
- Starting with `DATABASE_RESET=false` preserves an existing marker record.
- Starting with `DATABASE_RESET=true` removes the marker and produces the
  migrated, production-bootstrapped database.
- Startup logs clearly identify whether the destructive reset path ran.

