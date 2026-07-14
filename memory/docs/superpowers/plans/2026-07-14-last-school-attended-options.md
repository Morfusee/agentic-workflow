# Last School Attended Options Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with review checkpoints.

**Goal:** Add a small, verified 10-school option set and make the checkbox/manual fallback validate like the UAT form.

**Architecture:** Keep the shared EnrollMate contract as the source of truth. Convert the primary school field from an empty external source to a reusable option set, and express the UAT replacement UI with the existing `visibleWhen`/`requiredWhenVisible` metadata. The existing renderer, validator, fixture builder, and cleanup utility will consume the normalized contract without new behavior-specific code.

**Tech Stack:** JSON contract source, Zod normalization/validation, React form adapters, Vitest, Node test runner, pnpm.

---

### Task 1: Update the shared school contract

**Files:**

- Modify: `packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json`

- [ ] **Step 1: Add the reusable option set**

Add `lastSchoolAttendedOptions` under `reusableOptionSets` with exactly these `{label,value}` pairs:

```json
[
  { "label": "Mapua University-Makati", "value": "Mapua University-Makati" },
  { "label": "Mapua University-Manila", "value": "Mapua University-Manila" },
  { "label": "Rizal National High School", "value": "Rizal National High School" },
  { "label": "Manila Science High School", "value": "Manila Science High School" },
  { "label": "Philippine Science High School", "value": "Philippine Science High School" },
  { "label": "Ateneo de Manila University, Inc.", "value": "Ateneo de Manila University, Inc." },
  { "label": "De La Salle-Araneta University", "value": "De La Salle-Araneta University" },
  { "label": "University of Santo Tomas", "value": "University of Santo Tomas" },
  { "label": "Adamson University", "value": "Adamson University" },
  { "label": "Polytechnic University of the Philippines", "value": "Polytechnic University of the Philippines" }
]
```

- [ ] **Step 2: Make the primary field use the set and match UAT visibility**

Change `lastSchoolAttended` to `required: false`, replace its external source with `{ "kind": "reusable", "optionSet": "lastSchoolAttendedOptions" }`, and add:

```json
"visibleWhen": {
  "field": "schoolNotFound",
  "equalsAny": [false]
},
"requiredWhenVisible": true
```

Keep `schoolNotFound` and `lastschOther`; the latter remains visible and required when `schoolNotFound` is true.

- [ ] **Step 3: Parse the contract and run the focused contract tests**

Run:

```sh
pnpm --dir nextjs exec vitest run __tests__/unit/lib/enrollmate-contract.test.ts __tests__/unit/lib/enrollmate-fixture.test.ts
```

Expected: existing tests may fail until Task 2 updates their assumptions; no JSON parse or schema error should remain after the test updates.

### Task 2: Update contract, fixture, and seed assertions

**Files:**

- Modify: `nextjs/__tests__/unit/lib/enrollmate-contract.test.ts`
- Modify: `nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts`
- Modify: `nextjs/__tests__/unit/lib/enrollmate-fixture.test.ts`
- Modify: `playwright/server/__tests__/unit/enrollmate-contract.test.ts`
- Modify: `nextjs/lib/drizzle/seed/profile/profile-form-value-policy.ts`

- [ ] **Step 1: Assert the normalized option set and primary field metadata**

In the Next.js contract test, assert that `lastSchoolAttendedOptions` has length 10, contains `Mapua University-Makati`, and that `lastSchoolAttended` normalizes to the reusable option source with `conditionalOn` set to `schoolNotFound = false` and `requiredWhenConditionMet: true`.

- [ ] **Step 2: Cover both validation branches**

Keep the existing hidden-value rejection and missing-manual-value rejection. Add assertions that:

```ts
validator.safeParse({ ...validData, schoolNotFound: false, lastSchoolAttended: undefined }).success === false
validator.safeParse({ ...validData, schoolNotFound: true, lastschOther: "Example Academy" }).success === true
```

The first failure must point to `lastSchoolAttended`; the second must not require the hidden field.

- [ ] **Step 3: Update client cleanup expectations**

Assert that `lastSchoolAttended` is visible with `schoolNotFound: false` and removed when `schoolNotFound: true`; assert that `lastschOther` is visible only with `schoolNotFound: true` and removed when false.

- [ ] **Step 4: Update fixture resolvers and seed policy**

Where a resolver handles captured choice fields, return the first normalized option when `field.options.length > 0` so the new reusable school field receives a valid value. Remove the unused `lastschOther` duplicate from `createProfileFormValueResolver` while retaining `lastSchoolAttended: "Mapua University-Makati"` or another verified option.

- [ ] **Step 5: Run focused Next.js and Playwright tests**

Run:

```sh
pnpm --dir nextjs exec vitest run __tests__/unit/lib/enrollmate-contract.test.ts __tests__/unit/lib/enrollmate-fixture.test.ts __tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts
pnpm --dir playwright test:unit -- --test-name-pattern="EnrollMate|enrollmate"
```

Expected: all selected tests pass.

### Task 3: Verify the final diff and project checks

**Files:** No additional files.

- [ ] **Step 1: Inspect the diff**

Run `git diff --check` and `git diff --` in `$HOME/Documents/Programming/mihc`. Confirm only the contract, focused tests, and seed resolver changed; preserve all pre-existing user-owned modifications.

- [ ] **Step 2: Run typecheck and lint**

Run:

```sh
pnpm --dir nextjs exec tsc --noEmit
pnpm --dir nextjs lint
```

Expected: both commands pass, or any unrelated pre-existing failure is reported explicitly.
