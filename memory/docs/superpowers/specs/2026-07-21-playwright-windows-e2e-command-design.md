# Playwright Windows E2E Command Design

## Goal

Make the advertised `test:e2e` package script run on Windows while preserving its existing TypeScript loader and Playwright arguments.

## Design

Replace the POSIX-only inline `NODE_OPTIONS` assignment with an explicit Node invocation:

```text
node --import tsx ./node_modules/@playwright/test/cli.js test tests/e2e --project=enrollmate
```

This uses Node's cross-platform `--import` option, relies only on the existing `tsx` and `@playwright/test` dependencies, and does not modify the lockfile.

## Alternatives Considered

- Add `cross-env` and retain `NODE_OPTIONS`: portable, but adds an unnecessary dependency and lockfile changes.
- Remove the loader entirely: simpler, but risks changing why the E2E configuration currently requests `tsx`.

## Scope

Only `playwright/package.json` changes. Existing work in `playwright/pnpm-lock.yaml` remains untouched.

## Verification

Run the package script in Windows PowerShell with Playwright's `--list` argument. Success means the script reaches Playwright, loads the TypeScript setup, and lists the EnrollMate E2E tests without a shell assignment error.
