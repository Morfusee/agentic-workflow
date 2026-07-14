# Last School Attended Options Design

**Date:** 2026-07-14

## Goal

Make the profile form match the UAT Last School Attended behavior without importing the full school catalog.

## Scope

- Add one shared reusable option set containing 10 verified school names from the UAT autocomplete API.
- Use that option set for the unchecked `lastSchoolAttended` field.
- Keep the UAT checkbox/manual fallback flow: checking `schoolNotFound` hides the option field and shows the required `lastschOther` text field.
- Keep existing field names and persisted value shape so the change does not require a database migration.

## Data flow

When `schoolNotFound` is false, the form renders a select-like control backed by the shared 10-item option set and requires `lastSchoolAttended`. When it is true, the option field is hidden, `lastschOther` is shown, and the manual value is required. The shared validator and client cleanup utility will derive this behavior from the existing `visibleWhen` and `requiredWhenVisible` contract metadata.

## Verified option values

The values are school names returned by the UAT `app-schools` search endpoint:

1. Mapua University-Makati
2. Mapua University-Manila
3. Rizal National High School
4. Manila Science High School
5. Philippine Science High School
6. Ateneo de Manila University, Inc.
7. De La Salle-Araneta University
8. University of Santo Tomas
9. Adamson University
10. Polytechnic University of the Philippines

## Files in scope

- `packages/enrollmate-contract/src/definitions/enrollmate-form-fields.json`: add the reusable option set and update the three school fields' source/conditional metadata.
- `nextjs/__tests__/unit/lib/enrollmate-contract.test.ts`: assert the 10-item set and the conditional field contract.
- `nextjs/__tests__/unit/feature/e2e/profile-form/profile-form-definition.test.ts`: update visibility/default cleanup expectations for the UAT-style replacement behavior.
- `nextjs/__tests__/unit/lib/enrollmate-fixture.test.ts`: update fixture overrides to use the new conditional contract.
- `playwright/server/__tests__/unit/enrollmate-contract.test.ts`: update server-side contract fixtures and required-field checks.
- `nextjs/lib/drizzle/seed/profile/profile-form-value-policy.ts`: remove the redundant fallback value from seeded data while retaining a valid primary school value.

## Verification

- Contract parsing exposes exactly 10 school options.
- The primary field is required and visible when `schoolNotFound` is false.
- The primary field is omitted and the manual field is required when `schoolNotFound` is true.
- Focused Next.js and Playwright contract tests pass, followed by TypeScript/lint checks as practical.
