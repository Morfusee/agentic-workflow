# Playwright Node 25 Loader Compatibility Design

## Goal

Make the manual and automated EnrollMate Playwright E2E entrypoints work on
Windows with Node 25 while preserving the shared EnrollMate contract as the
single source of truth.

## Cause

Both entrypoints preload `tsx` around Playwright 1.61.1. Playwright installs its
own TypeScript loader, and composing the two loaders on Node 25 causes the load
hook to return an invalid `undefined` source value. Removing `tsx` alone exposes
a second issue: the local `@mihc/enrollmate-contract` dependency exports
TypeScript source from inside `node_modules`, where Playwright does not transform
it automatically.

## Design

Use Playwright's native TypeScript transformation for the test suite and map the
shared package imports directly to the canonical source directory through
`playwright/tsconfig.json`.

The path mappings will cover the package root and its exported subpaths. This
keeps imports package-shaped while ensuring Playwright sees the source outside
`node_modules` and compiles it. The package script will invoke Playwright's CLI
without `--import tsx`, and the automated child-process runner will stop adding
`NODE_OPTIONS=--import tsx`.

No contract definitions will be copied or built into Playwright. The existing
`tsx` preload remains in place for Node-only server unit tests, which do not run
through Playwright's loader.

## Alternatives Considered

- Build `@mihc/enrollmate-contract` to JavaScript before E2E runs. This adds a
  build lifecycle and generated-output concerns for a source-only local package.
- Pin or downgrade Node. This avoids the immediate loader interaction but leaves
  the command dependent on a particular local runtime and does not resolve the
  underlying double-loader design.
- Keep both loaders and add a custom loader wrapper. This is more fragile and
  complex than letting Playwright handle the TypeScript it already supports.

## Scope

- Modify `playwright/tsconfig.json` to resolve the shared contract source.
- Modify `playwright/package.json` to remove the E2E `tsx` preload.
- Modify `playwright/server/runner/run-e2e.ts` to remove the automated preload.
- Preserve the existing changes in `playwright/pnpm-lock.yaml`,
  `playwright/server/runner/map-e2e-results.ts`, and
  `playwright/server/runner/map-e2e-results.test.ts`.

## Verification

1. List EnrollMate tests without starting a browser to prove configuration,
   shared-package resolution, and test collection work.
2. Run Playwright type-checking and relevant server unit tests.
3. Run `just test-playwright-e2e` to verify the advertised entrypoint reaches
   and executes the live UAT suite without the loader error.
4. Review the final diff to confirm the pre-existing mapper and lockfile work is
   still present and no unrelated files changed.

