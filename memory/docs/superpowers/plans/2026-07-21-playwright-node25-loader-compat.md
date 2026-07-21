# Playwright Node 25 Loader Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run manual and automated EnrollMate Playwright E2E tests on Node 25 without composing Playwright's TypeScript loader with `tsx`.

**Architecture:** Playwright remains responsible for transforming browser-suite TypeScript. TypeScript path mappings resolve the source-only shared contract outside `node_modules`, while both Playwright entrypoints stop preloading `tsx`; Node-only unit tests retain their existing loader.

**Tech Stack:** Node.js 25, Playwright 1.61, TypeScript, pnpm, just

---

## File Structure

- Modify `playwright/tsconfig.json` — map shared contract package imports to canonical TypeScript source.
- Modify `playwright/package.json` — launch the manual E2E suite without the conflicting `tsx` preload.
- Modify `playwright/server/runner/run-e2e.ts` — launch automated E2E child processes without the same preload.
- Preserve `playwright/pnpm-lock.yaml`, `playwright/server/runner/map-e2e-results.ts`, and `playwright/server/runner/map-e2e-results.test.ts` — these contain pre-existing user work.

### Task 1: Resolve the shared contract through Playwright

**Files:**
- Modify: `playwright/tsconfig.json`

- [ ] **Step 1: Record the failing loader behavior**

Run from `playwright/`:

```powershell
pnpm run test:e2e -- --list
```

Expected before the fix: exit code `1` with `ERR_INVALID_RETURN_PROPERTY_VALUE` from the composed `tsx` and Playwright load hooks.

- [ ] **Step 2: Add direct source mappings**

Add `baseUrl` and exact mappings under `compilerOptions`:

```json
"baseUrl": ".",
"paths": {
  "@mihc/enrollmate-contract": ["../packages/enrollmate-contract/src/index.ts"],
  "@mihc/enrollmate-contract/server": ["../packages/enrollmate-contract/src/server.ts"],
  "@mihc/enrollmate-contract/testing": ["../packages/enrollmate-contract/src/testing.ts"]
}
```

Keep every existing compiler option and include/exclude rule.

### Task 2: Remove the conflicting loader from both E2E entrypoints

**Files:**
- Modify: `playwright/package.json`
- Modify: `playwright/server/runner/run-e2e.ts`

- [ ] **Step 1: Simplify the manual package script**

Set the script to invoke the installed CLI through Node without a loader:

```json
"test:e2e": "node ./node_modules/@playwright/test/cli.js test tests/e2e --project=enrollmate"
```

Do not change dependencies or the Node-only `test:unit` script.

- [ ] **Step 2: Simplify the automated child-process environment**

Remove only this property from the `env` object in `runE2e`:

```ts
NODE_OPTIONS: "--import tsx",
```

Keep all profile-data, flow-type, and JSON-report environment variables.

- [ ] **Step 3: Verify test discovery**

Run from `playwright/`:

```powershell
pnpm run test:e2e -- --list
```

Expected: exit code `0`, one or more EnrollMate tests listed, and no loader or shared-package resolution error.

### Task 3: Regression and end-to-end verification

**Files:**
- Verify only; no additional file changes expected.

- [ ] **Step 1: Run TypeScript checking**

```powershell
pnpm run typecheck
```

Expected: exit code `0`.

- [ ] **Step 2: Run server unit tests**

```powershell
pnpm run test:unit
```

Expected: exit code `0`, proving the retained Node-only `tsx` loader still works.

- [ ] **Step 3: Run the advertised E2E command from the repository root**

```powershell
just test-playwright-e2e
```

Expected: Playwright executes the EnrollMate project without `ERR_INVALID_RETURN_PROPERTY_VALUE`. A UAT assertion failure is distinct from the loader defect and should be reported with its test evidence.

- [ ] **Step 4: Review the final worktree**

```powershell
git diff -- playwright/package.json playwright/tsconfig.json playwright/server/runner/run-e2e.ts
git status --short
```

Expected: only the three intended loader-resolution files contain new changes; all pre-existing mapper and lockfile work remains present. Leave implementation changes uncommitted unless the user separately requests a commit.

