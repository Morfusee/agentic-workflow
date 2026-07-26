# EnrollMate Consent Submission Design

## Problem

The EnrollMate UAT wizard does not submit directly when its `SUBMIT` button is
clicked. That click opens a mandatory “Consent to Data Use & Enrollment” dialog,
and the application is sent only after `AGREE & PROCEED` is clicked.

The current Playwright driver clicks `SUBMIT` but does not accept the dialog.
Its confirmation check can then match the wizard’s existing “Confirmation” step
label, producing a false successful result without a final submission.

## Scope

Modify the shared EnrollMate Playwright submission driver and its Node unit test:

- `$HOME/Documents/Programming/mihc/playwright/lib/enrollmate/apply-now-driver.ts`
- `$HOME/Documents/Programming/mihc/playwright/server/__tests__/unit/apply-now-driver.test.ts`

No Next.js, Inngest, database schema, Salesforce integration, or form-data
generation changes are required.

## Design

`submitForm` will perform an explicit two-stage submission:

1. Click the exact `SUBMIT` button on the confirmation step.
2. Require the consent dialog’s exact `AGREE & PROCEED` button to become visible.
3. Click `AGREE & PROCEED`.
4. Wait for the resulting page activity to settle.

The consent action is mandatory. If the dialog or button does not appear, the
existing `run` wrapper will return a failed `StepOutcome`, and the `submit`
Playwright check will fail with the underlying locator error.

`confirmSubmission` will no longer accept the generic word “confirmation.”
It will wait only for post-submit success language such as “thank you,”
“submitted,” “received,” or “success.” This prevents the pre-submit wizard step
label from satisfying the check.

## Testing

Extend the existing Node unit test file with a focused regression test using a
small `Page` test double. The test will call `submitForm` and assert that:

- `SUBMIT` is clicked first;
- `AGREE & PROCEED` is clicked second;
- the function returns `{ ok: true }`.

Add a second assertion for the mandatory behavior: when the consent button
cannot be clicked, `submitForm` returns `{ ok: false, message: ... }`.

Run:

```sh
cd $HOME/Documents/Programming/mihc/playwright
pnpm test:unit
pnpm typecheck
```

## Non-goals

- Persisting the outbound UAT/Salesforce network request or response.
- Verifying the resulting Salesforce record.
- Changing submitted names or other profile values.
- Supporting a consent-free UAT variant.
