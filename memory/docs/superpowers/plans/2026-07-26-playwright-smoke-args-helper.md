# Playwright Smoke Arguments Helper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the Playwright package build by defining the argument helper its focused test already imports.

**Architecture:** Keep argument construction beside `runSmoke` in `run-smoke.ts`. Export one pure helper and make the production `spawn` call consume it so the existing test covers the runtime path without changing behavior.

**Tech Stack:** TypeScript, Node.js test runner, pnpm

---

### Task 1: Extract and use the smoke argument helper

**Files:**
- Modify: `playwright/server/runner/run-smoke.ts:41-76`
- Test: `playwright/server/runner/run-smoke.test.ts`

- [ ] **Step 1: Run the focused test to verify the existing failure**

Run from `playwright/`:

```sh
pnpm exec node --import tsx --test server/runner/run-smoke.test.ts
```

Expected: FAIL because `./run-smoke` does not export `buildSmokeArgs`.

- [ ] **Step 2: Add the minimal helper**

Add above `runSmoke` in `playwright/server/runner/run-smoke.ts`:

```ts
export function buildSmokeArgs(target: SmokeTarget): string[] {
  return [
    "test",
    target.testPath,
    `--project=${target.project}`,
    "--workers=1",
    "--reporter=./server/reporter/incremental-smoke-reporter.ts,json",
  ];
}
```

- [ ] **Step 3: Reuse the helper in production**

Replace the inline second argument passed to `spawn` with:

```ts
buildSmokeArgs(target),
```

Keep `PLAYWRIGHT_BIN` and the existing spawn options unchanged.

- [ ] **Step 4: Run the focused test**

Run from `playwright/`:

```sh
pnpm exec node --import tsx --test server/runner/run-smoke.test.ts
```

Expected: PASS with one passing test.

- [ ] **Step 5: Run the package typecheck**

Run from `playwright/`:

```sh
pnpm typecheck
```

Expected: PASS with exit code 0 and no TypeScript errors.

- [ ] **Step 6: Review the final diff**

Run from the repository root:

```sh
git diff --check
git diff -- playwright/server/runner/run-smoke.ts
```

Expected: only the helper extraction and its use in `spawn`; the existing test remains unchanged.
