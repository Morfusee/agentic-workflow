# Handoff: MMDC EnrollMate Test Suite

**Branch**: `feat/enrollment-test-suite`
**Last commit**: `9bfa2e4` — fix: fill step 1 form and navigate to step 2
**Uncommitted changes**: `tests/enrollmate/bachelors-apply.spec.ts` (+185/-52, adds Step 2 test suite)

## What exists

- **Config**: `playwright.enrollmate.config.ts` — standalone config, 3 browser projects, base URL `https://uat.enrollmate.mmdc.mcl.edu.ph`
- **Test file**: `tests/enrollmate/bachelors-apply.spec.ts` — 18 tests
- **npm scripts**: `test:enrollmate`, `test:enrollmate:headed`, `test:enrollmate:chromium`, `report:enrollmate`

### Test structure (307 lines)

| Step | Tests | Type |
|------|-------|------|
| Step 1 — Student's Information | 8 tests | Independent (`test.describe`), each navigates fresh |
| Step 2 — Parent/Guardian's | 8 tests | Independent, each calls `advanceToStep2()` (fills ~20 Step 1 fields + clicks NEXT) |
| Step 3 — Additional Info | 1 placeholder | Passes with annotation |

## The problem

Each Step 2 test calls `advanceToStep2(page)` at the top, which:
1. Opens a fresh page
2. Fills 20+ Step 1 fields with cascading address selects (NCR → Manila City, with `waitForTimeout` for API responses)
3. Injects fake barangay options via `page.evaluate()` (UAT API doesn't serve them)
4. Fills the school search combobox (click → type → press Enter)
5. Clicks NEXT and validates advancement

This takes **~25 seconds per test**. With 8 Step 2 tests, that's ~200 seconds just repeating the same work.

## Desired refactor

Convert to a **continuous wizard flow** using `test.describe.serial` with a shared `Page`:

```
test.describe.serial('Step 1', () => {
  let page: Page;
  test.beforeAll(async ({ browser }) => { page = await browser.newPage(); ... });

  // 8 fast read-only tests against Step 1
  test('heading', () => { ... });
  test('nav', () => { ... });

  // One test fills Step 1 and clicks NEXT
  test('fills and advances to Step 2', () => { ... });

  test.afterAll(() => page.close());
});

test.describe.serial('Step 2', () => {
  let page: Page;
  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
    // navigate, fill Step 1, advance to Step 2 (one time)
  });

  // All content checks run against the existing Step 2 page
  test('heading and nav', () => { ... });
  test('living status dropdowns', () => { ... });
  // ...

  // Final test fills Step 2 and advances to Step 3
  test('fills step 2 and advances', () => { ... });

  test.afterAll(() => page.close());
});

// Repeat for Step 3, Step 4
```

**Key insight**: Story the page reference in `beforeAll` and close in `afterAll`. Tests within the serial describe use the shared `page` variable (not the fixture).

## Prior attempts & gotchas

1. **Commit `28c2aa7`**: First used `test.describe.serial` with shared page for the ENTIRE suite (all 4 steps). The page accumulated state and Angular got into a bad state by test 9. Solution: scope serial describes PER STEP (not across steps).

2. **Commit `77f5d25`**: Used `beforeAll` + `afterAll` but tests were still in a single giant `test.describe.serial`. Now we want smaller per-step serial describes.

3. **The school search combobox** is an `app-search-school` component — must click → type → wait → press Enter. `page.getByRole('combobox', { name: /last school/i })`.

4. **Barangay dropdowns** (`#curraddrBarangay`, `#permaddrBarangay`) — UAT API doesn't return options. Workaround: `page.evaluate(() => el.add(new Option(...)))` then Playwright's `selectOption()` (NOT `evaluate` + `dispatchEvent`, Angular doesn't see it).

5. **Step 2 parent forms**: Father/Mother info sections appear when Living status is anything other than Deceased. Setting `fthrDeceased` = `Deceased` and `mthrDeceased` = `Deceased` hides their address forms, leaving only the guardian form to fill.

6. **Guardian copy-address checkboxes** (`#copyGuardianAddressCheckbox`, `#copyPermaGuardianAddressCheckbox`) must be checked to avoid filling guardian address fields. They become visible only after guardian is selected.

## Helper functions (in test file)

- `fillStep1(page)` — fills all Step 1 fields (email, personal info, school search, addresses with barangay hack, scholarship/medical)
- `advanceToStep2(page)` — calls `fillStep1(page)` then clicks NEXT, asserts no validation dialog, asserts Step 2 button enabled

## Known blockers

- **Barangay cascade API**: UAT doesn't serve barangay options. Tests create synthetic options.
- **Step 3/4**: Placeholder tests only. No test has explored Step 3 content yet.

## Suggested skills

- `refactor` — for surgically restructuring the test file to use serial describes
- `skill-orchestrator-go` — if the refactor spans multiple files or needs parallel work
- `requirements-reviewer` — to verify refactored tests still pass after cleanup

## Verification

```bash
# Run entire suite headless
pnpm run test:enrollmate:chromium

# Run with browser visible, one-at-a-time
pnpm run test:enrollmate:chromium -- --headed --workers=1

# Open HTML report
pnpm run report:enrollmate
```

All 18 tests currently pass (57s headless, 3.6m headed). After refactor, the same assertions should pass but in less time.
