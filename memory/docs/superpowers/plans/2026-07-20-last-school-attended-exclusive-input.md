# Last School Attended Exclusive Input Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep Last School Attended visible but disabled and empty whenever "school not found" is checked, while ensuring the mock button populates only the applicable school field.

**Architecture:** Reuse the profile form's existing centralized rendering and cleanup utilities. Add one disabled-state helper that covers both parent fields and the Last School Attended select, then use it in the renderer and mock generator; trigger existing cleanup when `schoolNotFound` changes.

**Tech Stack:** TypeScript, React 19, TanStack Form, Vitest, Testing Library

---

### Task 1: Centralize rendered and disabled field behavior

**Files:**
- Modify: `nextjs/feature/e2e/utils/e2e-profile-form.util.ts`
- Modify: `nextjs/feature/e2e/components/profile-form/enrollmate-field-renderer.tsx`
- Modify: `nextjs/feature/e2e/utils/e2e-profile-form-mock.util.ts`
- Test: `nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts`
- Test: `nextjs/__tests__/unit/feature/e2e/profile-form/enrollmate-field-renderer.test.tsx`

- [ ] **Step 1: Write failing utility and renderer tests**

Import `isEnrollmateFieldDisabled` in the definition test and extend the existing visibility test with:

```ts
expect(
  isEnrollmateFieldRendered(lastSchoolAttended, { schoolNotFound: true }),
).toBe(true);
expect(
  isEnrollmateFieldDisabled(lastSchoolAttended, { schoolNotFound: true }),
).toBe(true);
expect(
  isEnrollmateFieldDisabled(lastSchoolAttended, { schoolNotFound: false }),
).toBe(false);
```

Add this renderer test:

```tsx
it("keeps the known-school field visible and disables it when the school is not found", () => {
  const definition = getField("lastSchoolAttended");

  render(
    <RendererHarness
      definition={definition}
      initialValue=""
      values={{ schoolNotFound: true }}
    />,
  );

  expect(screen.getByLabelText(definition.label)).toBeDisabled();
});
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```powershell
pnpm --dir nextjs exec vitest run __tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts __tests__/unit/feature/e2e/profile-form/enrollmate-field-renderer.test.tsx
```

Expected: FAIL because `isEnrollmateFieldDisabled` is not exported and the conditional Last School Attended field is not rendered when `schoolNotFound` is true.

- [ ] **Step 3: Implement the shared rendered/disabled rule**

In `e2e-profile-form.util.ts`, add the smallest shared helper and retain the existing parent helper API:

```ts
export function isEnrollmateFieldDisabled(
  field: EnrollmateField,
  values: Record<string, unknown>,
) {
  return (
    isEnrollmateParentFieldDisabled(field, values) ||
    (field.name === "lastSchoolAttended" && values.schoolNotFound === true)
  );
}
```

Keep the known-school field mounted by extending `isEnrollmateFieldRendered`:

```ts
return (
  isEnrollmateParentField(field) ||
  field.name === "lastSchoolAttended" ||
  isEnrollmateFieldVisible(field, values)
);
```

Replace `isEnrollmateParentFieldDisabled` with `isEnrollmateFieldDisabled` only where general field availability is needed:

```ts
const isDisabled = isEnrollmateFieldDisabled(definition, values);
```

Use the same helper in `e2e-profile-form-mock.util.ts` for required-file checks, generation eligibility, and required checkbox candidates. This prevents a rendered-but-disabled Last School Attended field from being mocked.

- [ ] **Step 4: Run focused tests and verify success**

Run the Step 2 command.

Expected: both test files PASS.

- [ ] **Step 5: Commit the shared behavior**

```powershell
git add -- nextjs/feature/e2e/utils/e2e-profile-form.util.ts nextjs/feature/e2e/components/profile-form/enrollmate-field-renderer.tsx nextjs/feature/e2e/utils/e2e-profile-form-mock.util.ts nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts nextjs/__tests__/unit/feature/e2e/profile-form/enrollmate-field-renderer.test.tsx
git commit -m "fix(e2e): disable unavailable last school field"
```

### Task 2: Clear the selection immediately and verify mock exclusivity

**Files:**
- Modify: `nextjs/feature/e2e/components/profile-form/use-e2e-profile-form-controller.tsx`
- Test: `nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-page.test.tsx`
- Test: `nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts`

- [ ] **Step 1: Write the failing form interaction test**

Add this page test beside the existing parent-field clearing test:

```tsx
it("clears and disables Last School Attended when the school is not found", async () => {
  renderPage();
  await chooseOption("Last School Attended", "Mapua University-Makati");

  const lastSchool = screen.getByRole("combobox", {
    name: "Last School Attended",
  });
  const schoolNotFound = screen.getByRole("checkbox", {
    name: "Tick this checkbox if the school is not found",
  });

  fireEvent.click(schoolNotFound);

  await waitFor(() => expect(lastSchool).toHaveValue(""));
  expect(lastSchool).toBeDisabled();
  expect(
    screen.getByRole("textbox", { name: "Last School Attended (Other)" }),
  ).toBeEnabled();

  fireEvent.click(schoolNotFound);

  await waitFor(() => expect(lastSchool).toBeEnabled());
  expect(lastSchool).toHaveValue("");
  expect(
    screen.queryByRole("textbox", { name: "Last School Attended (Other)" }),
  ).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Strengthen the existing mock branch test**

For each deterministic seed, merge generated values with current values and run `clearUnavailableE2eProfileFormValues`. Assert both sides of the invariant:

```ts
if (values.schoolNotFound === true) {
  sawCheckedBranch = true;
  expect(values).not.toHaveProperty("lastSchoolAttended");
  expect(values.lastschOther).toEqual(expect.any(String));
  expect(values.lastschOther).not.toBe("");
} else {
  sawUncheckedBranch = true;
  expect(values.lastSchoolAttended).toEqual(expect.any(String));
  expect(values.lastSchoolAttended).not.toBe("");
  expect(values).not.toHaveProperty("lastschOther");
}
```

Use full mock mode so every applicable required field is deterministically populated while the seeds exercise both checkbox branches.

- [ ] **Step 3: Run the focused tests and verify the interaction failure**

Run:

```powershell
pnpm --dir nextjs exec vitest run __tests__/unit/feature/e2e/profile-form/profile-form-page.test.tsx __tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts
```

Expected: the page test FAILS because changing `schoolNotFound` does not immediately invoke unavailable-value cleanup.

- [ ] **Step 4: Trigger the existing cleanup for the checkbox**

Extend the controller's existing dependency-field listener condition:

```ts
if (
  fieldApi.name === "enrollmate.fthrDeceased" ||
  fieldApi.name === "enrollmate.mthrDeceased" ||
  fieldApi.name === "enrollmate.schoolNotFound"
) {
```

No new clearing function is needed: `clearUnavailableE2eProfileFormValues` already removes the now-inapplicable school branch.

- [ ] **Step 5: Run all focused tests and lint**

Run:

```powershell
pnpm --dir nextjs exec vitest run __tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts __tests__/unit/feature/e2e/profile-form/enrollmate-field-renderer.test.tsx __tests__/unit/feature/e2e/profile-form/profile-form-page.test.tsx
pnpm --dir nextjs exec eslint feature/e2e/utils/e2e-profile-form.util.ts feature/e2e/utils/e2e-profile-form-mock.util.ts feature/e2e/components/profile-form/enrollmate-field-renderer.tsx feature/e2e/components/profile-form/use-e2e-profile-form-controller.tsx __tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts __tests__/unit/feature/e2e/profile-form/enrollmate-field-renderer.test.tsx __tests__/unit/feature/e2e/profile-form/profile-form-page.test.tsx
```

Expected: all focused tests PASS and ESLint exits successfully.

- [ ] **Step 6: Review and commit the final change**

Run `git diff --check`, `git diff`, and `git status --short` to confirm only the seven planned Next.js files changed and the prior option/seed work remains present.

```powershell
git add -- nextjs/feature/e2e/components/profile-form/use-e2e-profile-form-controller.tsx nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-page.test.tsx nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts
git commit -m "test(e2e): enforce exclusive last school inputs"
```
