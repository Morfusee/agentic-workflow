# EnrollMate Reusable Option Sets API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the canonical EnrollMate reusable option sets through a typed shared getter usable by both Next.js and Playwright.

**Architecture:** Add a registry-level getter that clones the validated source option sets into a read-only typed record, then re-export it from `@mihc/enrollmate-contract`. Add the local contract package dependency to Playwright so both repository projects import the same API; no HTTP route or duplicated data is introduced.

**Tech Stack:** TypeScript, Zod 4, Vitest, Node test runner, pnpm workspace-local file dependency.

---

## Existing context and preservation rules

- Preserve the existing dirty changes in `nextjs/__tests__/unit/lib/enrollmate-contract.test.ts`.
- Preserve all existing committed EnrollMate contract, E2E, seed, and migration changes.
- Next.js already declares `@mihc/enrollmate-contract` as `file:../packages/enrollmate-contract` and transpiles it.
- Playwright currently has no dependency on the shared package; its unit tests run from `playwright/server/**/*.test.ts` with Node’s test runner.

### Task 1: Add failing consumer coverage

**Files:**

- Modify: `nextjs/__tests__/unit/lib/enrollmate-contract.test.ts`
- Create: `playwright/server/__tests__/unit/enrollmate-contract.test.ts`

- [ ] **Step 1: Add the Next.js getter contract test**

Import `getEnrollmateReusableOptionSets` and assert the static definition exposes the five current set names, a known option, and detached nested values:

```ts
it("exposes all reusable option sets without sharing mutable source objects", () => {
  const first = getEnrollmateReusableOptionSets();
  const second = getEnrollmateReusableOptionSets();

  expect(Object.keys(first).sort()).toEqual([
    "countryOptions",
    "nationalityOptions",
    "philippineProvinces",
    "religionOptions",
    "suffixOptions",
  ]);
  expect(first.countryOptions[0]).toEqual({ label: "Afghanistan", value: "Afghanistan" });
  expect(first.countryOptions).not.toBe(second.countryOptions);
  expect(first.countryOptions[0]).not.toBe(second.countryOptions[0]);
});
```

- [ ] **Step 2: Add a Playwright import test**

Create a Node unit test under the server-only unit-test tree that imports the package by name and verifies the getter returns a reusable set:

```ts
import assert from "node:assert/strict";
import { test } from "node:test";
import { getEnrollmateReusableOptionSets } from "@mihc/enrollmate-contract";

test("Playwright can consume shared EnrollMate reusable options", () => {
  const optionSets = getEnrollmateReusableOptionSets();
  assert.ok(optionSets.countryOptions.length > 0);
  assert.deepEqual(optionSets.countryOptions[0], {
    label: "Afghanistan",
    value: "Afghanistan",
  });
});
```

- [ ] **Step 3: Run the new tests to confirm the API is not implemented yet**

Run:

```powershell
npx --yes pnpm@10.29.2 --dir nextjs test __tests__/unit/lib/enrollmate-contract.test.ts
pnpm --dir playwright exec node --import tsx --test server/__tests__/unit/enrollmate-contract.test.ts
```

Expected: the Next.js test fails because the getter is not exported, and the Playwright server test fails because the package is not yet declared/resolvable there.

### Task 2: Implement the shared getter

**Files:**

- Modify: `packages/enrollmate-contract/src/types.ts`
- Modify: `packages/enrollmate-contract/src/registry.ts`
- Modify: `packages/enrollmate-contract/src/index.ts`

- [ ] **Step 1: Add the public read-only option-set type**

Add this type next to the existing option type in `types.ts`:

```ts
export type EnrollmateReusableOptionSets = Readonly<
  Record<string, readonly EnrollmateOption[]>
>;
```

- [ ] **Step 2: Add the cloning registry getter**

Add this function to `registry.ts` beside `getEnrollmateFlowDefinition`:

```ts
export function getEnrollmateReusableOptionSets(): EnrollmateReusableOptionSets {
  return Object.fromEntries(
    Object.entries(source.reusableOptionSets).map(([name, options]) => [
      name,
      options.map((option) => ({ ...option })),
    ]),
  );
}
```

Import `EnrollmateReusableOptionSets` as a type. The copied record, arrays, and option objects prevent consumers from mutating the imported source object.

- [ ] **Step 3: Re-export the getter and type**

Update `index.ts` so consumers can import both symbols from the package root:

```ts
export {
  enrollmateDefinition,
  getEnrollmateFlowDefinition,
  getEnrollmateReusableOptionSets,
} from "./registry";
export type {
  EnrollmateReusableOptionSets,
} from "./types";
```

- [ ] **Step 4: Run the Next.js contract test**

Run:

```powershell
npx --yes pnpm@10.29.2 --dir nextjs test __tests__/unit/lib/enrollmate-contract.test.ts
```

Expected: the getter test passes and the existing contract tests remain green.

### Task 3: Wire Playwright to the shared package

**Files:**

- Modify: `playwright/package.json`
- Modify: `playwright/pnpm-lock.yaml`

- [ ] **Step 1: Add the local package dependency**

Add this dependency to `playwright/package.json`:

```json
"@mihc/enrollmate-contract": "file:../packages/enrollmate-contract"
```

- [ ] **Step 2: Regenerate only the Playwright lockfile metadata**

Run:

```powershell
pnpm --dir playwright install --lockfile-only
```

Expected: the Playwright importer records the local package dependency and its Zod peer resolution without changing unrelated package versions.

- [ ] **Step 3: Run Playwright unit tests and typecheck**

Run:

```powershell
pnpm --dir playwright test:unit
pnpm --dir playwright typecheck
```

Expected: all existing Node unit tests plus the new server getter test pass, and TypeScript resolves the shared package from Playwright. The command must not invoke the browser Playwright suite.

### Task 4: Complete repository verification

- [ ] **Step 1: Run full Next.js validation**

Run:

```powershell
npx --yes pnpm@10.29.2 --dir nextjs test
npx --yes pnpm@10.29.2 --dir nextjs exec tsc --noEmit --types vitest/globals
npx --yes pnpm@10.29.2 --dir nextjs lint
```

Expected: all tests and typecheck pass; lint has no errors, with any existing warnings reported separately.

- [ ] **Step 2: Audit the final diff and preserve unrelated work**

Run:

```powershell
git diff --check
git status --short --branch
git diff -- packages/enrollmate-contract/src/types.ts packages/enrollmate-contract/src/registry.ts packages/enrollmate-contract/src/index.ts nextjs/__tests__/unit/lib/enrollmate-contract.test.ts playwright/package.json playwright/pnpm-lock.yaml playwright/server/__tests__/unit/enrollmate-contract.test.ts
```

Confirm the only new repository changes are the shared getter, its tests, and Playwright dependency wiring. Leave the existing dirty contract test changes in place and do not reset or commit user-owned work.
