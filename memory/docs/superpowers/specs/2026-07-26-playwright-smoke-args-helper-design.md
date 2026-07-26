# Playwright Smoke Arguments Helper Design

## Problem

`playwright/server/runner/run-smoke.test.ts` imports `buildSmokeArgs`, but
`run-smoke.ts` keeps the same argument list inline and does not export that
helper. TypeScript compilation therefore fails with TS2305 during the
Playwright Docker image build.

## Design

Add an exported `buildSmokeArgs(target: SmokeTarget): string[]` function to
`run-smoke.ts`. It returns the existing Playwright CLI arguments without
changing their order or values. `runSmoke` passes this helper's result to
`spawn`, making the focused test exercise the production argument path.

No other files, runtime behavior, dependencies, or error handling change.

## Verification

Run the focused `run-smoke` test and the Playwright package typecheck. Both
must pass.
