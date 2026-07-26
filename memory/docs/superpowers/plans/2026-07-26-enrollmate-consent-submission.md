# EnrollMate Consent Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the EnrollMate UAT Playwright flow accept the mandatory consent dialog before treating an application as submitted.

**Architecture:** Keep the behavior in the existing shared submission driver. `submitForm` will click the confirmation-step `SUBMIT` button, require and click `AGREE & PROCEED`, then wait for page activity; `confirmSubmission` will accept only post-submit success language. The existing Node unit-test file will verify click order, required-consent failure, and the tightened confirmation selector.

**Tech Stack:** TypeScript, Playwright locators, Node.js test runner, strict assertions.

---

## File map

- Modify: `$HOME/Documents/Programming/mihc/playwright/lib/enrollmate/apply-now-driver.ts` — perform the mandatory two-click submission and remove the false-positive confirmation term.
- Modify: `$HOME/Documents/Programming/mihc/playwright/server/__tests__/unit/apply-now-driver.test.ts` — cover click order, missing consent, and confirmation matching.

### Task 1: Add submission regression coverage

**Files:**
- Test: `$HOME/Documents/Programming/mihc/playwright/server/__tests__/unit/apply-now-driver.test.ts`

- [x] **Step 1: Import the submission functions**

Replace the driver import with:

```ts
import {
  confirmSubmission,
  fillStep,
  submitForm,
} from "../../../lib/enrollmate/apply-now-driver";
```

- [x] **Step 2: Add a failing test for mandatory consent click order**

Append:

```ts
test("accepts mandatory consent after clicking submit", async () => {
  const clicks: string[] = [];
  const page = {
    getByRole(role: string, options: { name: RegExp }) {
      assert.equal(role, "button");
      const label = options.name.test("AGREE & PROCEED")
        ? "AGREE & PROCEED"
        : "SUBMIT";

      return {
        first() {
          return this;
        },
        waitFor: async () => undefined,
        click: async () => {
          clicks.push(label);
        },
      };
    },
    waitForLoadState: async () => undefined,
  } as unknown as Page;

  const outcome = await submitForm(page);

  assert.deepEqual(outcome, { ok: true });
  assert.deepEqual(clicks, ["SUBMIT", "AGREE & PROCEED"]);
});
```

- [x] **Step 3: Add a failing test for missing required consent**

Append:

```ts
test("fails submission when mandatory consent is unavailable", async () => {
  const page = {
    getByRole(_role: string, options: { name: RegExp }) {
      const isConsent = options.name.test("AGREE & PROCEED");

      return {
        first() {
          return this;
        },
        click: async () => undefined,
        waitFor: async () => {
          if (isConsent) throw new Error("consent unavailable");
        },
      };
    },
    waitForLoadState: async () => undefined,
  } as unknown as Page;

  const outcome = await submitForm(page);

  assert.equal(outcome.ok, false);
  assert.match(outcome.message ?? "", /consent unavailable/);
});
```

- [x] **Step 4: Add a failing test that rejects the wizard label as confirmation**

Append:

```ts
test("does not treat the wizard Confirmation label as submitted", async () => {
  let successPattern: RegExp | undefined;
  const page = {
    getByText(pattern: RegExp) {
      successPattern = pattern;
      return {
        first() {
          return this;
        },
        waitFor: async () => undefined,
      };
    },
  } as unknown as Page;

  const outcome = await confirmSubmission(page);

  assert.deepEqual(outcome, { ok: true });
  assert.equal(successPattern?.test("Confirmation"), false);
  assert.equal(successPattern?.test("Thank you"), true);
});
```

- [x] **Step 5: Run the focused unit test and verify it fails**

Run:

```sh
cd $HOME/Documents/Programming/mihc/playwright
node --import tsx --test server/__tests__/unit/apply-now-driver.test.ts
```

Expected: the consent tests fail because only `SUBMIT` is clicked, and the confirmation test fails because the current pattern matches “Confirmation.”

### Task 2: Implement the mandatory consent flow

**Files:**
- Modify: `$HOME/Documents/Programming/mihc/playwright/lib/enrollmate/apply-now-driver.ts`
- Test: `$HOME/Documents/Programming/mihc/playwright/server/__tests__/unit/apply-now-driver.test.ts`

- [x] **Step 1: Replace `submitForm` with the explicit two-click flow**

Use:

```ts
/** Submit the completed application and accept the required consent dialog. */
export async function submitForm(page: Page): Promise<StepOutcome> {
  return run(async () => {
    await page
      .getByRole("button", { name: /^submit$/i })
      .first()
      .click();

    const consentButton = page
      .getByRole("button", { name: /^agree\s*&\s*proceed$/i })
      .first();
    await consentButton.waitFor({ state: "visible", timeout: 30_000 });
    await consentButton.click();

    await page.waitForLoadState("networkidle").catch(() => {});
  });
}
```

- [x] **Step 2: Remove the false-positive confirmation term**

Change the success locator to:

```ts
await page
  .getByText(/thank you|submitted|received|success/i)
  .first()
  .waitFor({ state: "visible", timeout: 30_000 });
```

- [x] **Step 3: Run the focused unit test**

Run:

```sh
cd $HOME/Documents/Programming/mihc/playwright
node --import tsx --test server/__tests__/unit/apply-now-driver.test.ts
```

Expected: all tests in `apply-now-driver.test.ts` pass.

- [x] **Step 4: Run all Playwright server unit tests**

Run:

```sh
cd $HOME/Documents/Programming/mihc/playwright
pnpm test:unit
```

Expected: all server unit tests pass.

- [x] **Step 5: Run TypeScript validation**

Run:

```sh
cd $HOME/Documents/Programming/mihc/playwright
pnpm typecheck
```

Expected: TypeScript exits successfully with no diagnostics.

- [x] **Step 6: Inspect the final repository diff**

Run:

```sh
cd $HOME/Documents/Programming/mihc
git status --short
git diff -- playwright/lib/enrollmate/apply-now-driver.ts playwright/server/__tests__/unit/apply-now-driver.test.ts
```

Expected: only the two intended Playwright files contain changes from this fix; the pre-existing user changes remain intact.
