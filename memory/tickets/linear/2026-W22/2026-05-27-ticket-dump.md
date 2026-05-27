# Stand-up Script

Yesterday, I QA tested the partner invitation disable/reactivate flow on staging — verified the complete invite → disable → reactivate → accept lifecycle works and that pending invitations survive the disable/reactivate cycle. Users can now re-accept their invitations after reactivation instead of hitting an Access Denied page. All acceptance criteria passed, and I moved that ticket to Done. I also filed a Marketplace bug where deleting a category that's in use shows a raw Prisma foreign key constraint error toast instead of a user-friendly message. I pinpointed the exact file and line causing it and laid out four implementation options for the assignee. Separately, I reported that Support Admin is inaccessible, returning a 403 Forbidden Nginx error.

No major blockers right now.

---

# Selected Tickets

- NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance
  - Status: Done
  - Activity date: 2026-05-27
  - URL: https://linear.app/ngnair/issue/NGN-728/partner-keep-pending-invitation-visible-after-disablereactivate-before
  - Reference: `# All Scraped Tickets` -> `## NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance`
  - Stand-up relevance: QA tested and moved to Done; verified full invite → disable → reactivate → accept lifecycle passes on staging.

- NGN-731: Marketplace: Show user-friendly toast when Category delete fails (Category in use)
  - Status: Pending Review
  - Activity date: 2026-05-27
  - URL: https://linear.app/ngnair/issue/NGN-731/marketplace-show-user-friendly-toast-when-category-delete-fails
  - Reference: `# All Scraped Tickets` -> `## NGN-731: Marketplace: Show user-friendly toast when Category delete fails (Category in use)`
  - Stand-up relevance: Created bug ticket and provided detailed code analysis with implementation options.

- MANUAL-002: Reported that Support Admin isn't accessible, and that I'm only met with a 403 Forbidden Nginx Error when trying to access it.
  - Status: Done
  - Activity date: 2026-05-27
  - Reference: `# Manual Tasks` -> `## MANUAL-002: Reported that Support Admin isn't accessible, and that I'm only met with a 403 Forbidden Nginx Error when trying to access it.`
  - Stand-up relevance: Reported accessibility issue with Support Admin returning 403 Forbidden.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Done
  - Role: tester-only
  - Activity notes: Tested the Payment Link expiration date handling on staging and commented that all acceptance criteria passed.

- NGN-723: Product: Fix Created field applying timezone offset in payment link details
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting a timezone offset issue in the Payment Link Details Created field.

- NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created improvement ticket documenting missing optional first and last name fields in the Partner FE invite user modal.

- NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting that the Partner dropdown in the Add Revenue Split modal is clipped by the modal container.

- NGN-689: Product: Prevent payment links from being created with past expiration dates
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting payment links creatable with past expiration dates without validation.

- MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: In Progress
  - Role: dev-owner
  - Activity notes: Started creating a simple draft of feasibility for migrating tables in the location-fe to use data-table blocks from a recent project.

- NGN-719: Finance: Pay Link for Payment Plan charges full amount instead of monthly installment amount
  - Source dump: 2026-05-25
  - Status as of 2026-05-25: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting Pay Link for Payment Plans charging the full plan amount instead of per-installment amount.

- NGN-720: Finance: Surcharge line item missing from Transaction Details modal after Pay Link payment
  - Source dump: 2026-05-25
  - Status as of 2026-05-25: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting surcharge line item missing from Transaction Details modal despite appearing on Payment Complete page.

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## MANUAL-002: Reported that Support Admin isn't accessible, and that I'm only met with a 403 Forbidden Nginx Error when trying to access it.

Status: Done
Activity date: 2026-05-27
My role: dev-owner

### Description
No description provided.

### Activity Notes
Reported that Support Admin is not accessible, returning a 403 Forbidden Nginx Error on access attempt.

---

# Ticket Dump

Generated: 2026-05-27
Requested range: 2026-05-27
Dump file date: 2026-05-27

---

# Grouped Summary

2026-05-27

## Done
- NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance

## Pending Review
- NGN-731: Marketplace: Show user-friendly toast when Category delete fails (Category in use)

---

# All Scraped Tickets

## NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance

Status: Done
Activity date: 2026-05-27
URL: https://linear.app/ngnair/issue/NGN-728/partner-keep-pending-invitation-visible-after-disablereactivate-before
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: dev-owner

### Why this ticket was included
Created by me, assigned to me, moved to Done by me, QA tested by me

### Description
### The Problem

In Partner Admin, inviting a newly created user and then "deleting" them (disables user) allows an admin to later reactivate them, but the reactivated user can no longer see/accept the Partner invitation in Partner FE and instead hits an Access Denied page.

### Steps to Reproduce

1. Create a new/fresh user in Auth FE.
2. Log in as Mark Goldman in Partner Admin.
3. Go to Partners > Ruby BIN ISO > Partner Users.
4. Invite the newly created user (do not accept the invitation as the invited user).
5. Click the Trash icon for that user and confirm (user becomes disabled).
6. Edit the now-disabled user and reactivate them by toggling Disabled off; click Save.
7. Log in to Partner FE host app as that user.
8. Observe Partner FE shows an Access Denied page instead of the pending invitation screen.

### Technical Requirements

* Preserve pending invitation state across `invite -> disable -> reactivate` when the user has not accepted yet.
* Ensure Partner FE resolves the user into "pending invite" state (invitation screen) after reactivation, rather than denying access.
* Ensure backend authorization does not permanently deny access for users who have an unaccepted invitation after reactivation.

### Expected vs Actual

* **Expected:** If the user has not accepted the invitation yet, then after reactivation they still see the invitation screen and can accept it.
* **Actual:** After reactivation, Partner FE shows Access Denied and the invitation is no longer visible.

### Acceptance Criteria

- [ ] An unaccepted invitation remains pending/valid after the invited user is disabled and later reactivated.
- [ ] After reactivation, Partner FE shows the invitation screen (not Access Denied) for that user.
- [ ] The user can accept the invitation successfully after reactivation and gains expected access.

### Comments
#### Duane Enriquez - 2026-05-27T02:37:53.484Z
**Behavior now:** Reactivating an unaccepted invite (`userId = null`) restores `status = INVITED`. The `myPendingPartnerInvites` query finds it again, partner-frontend shows the invitation screen, and the user can accept. Reactivating a previously-accepted user (`userId` set) still sets `status = ACTIVE` — no regression.

**Why it's significant:** Unblocks the common onboarding workflow where invitations are sent, disabled for review/correction, and then reactivated. Users can now re-accept their invitations without requiring manual data cleanup. Blast radius minimal (single service method, conditional branch).

#### mark.valenzuela@ngnair.com - 2026-05-27T05:53:29.881Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Tested the partner invitation flow against the disable/reactivate cycle: verified that a pending invitation is preserved for an invited user who has not yet accepted, and that the Partner FE correctly displays the invitation screen (not Access Denied) after the user is disabled and then reactivated.

### Test Results
Verified the full invite → disable → reactivate → accept lifecycle. After an unaccepted invitation was sent and the invited user was disabled and reactivated, the pending invitation remained valid. Partner FE correctly rendered the invitation screen on login, not an Access Denied page. The user was able to accept the invitation after reactivation and gained the expected partner access. All acceptance criteria were met.

### Activity Timeline
- 2026-05-26T10:12:36.828Z created
- 2026-05-27T02:37:53.484Z commented by Duane Enriquez
- 2026-05-27T02:37:55.139Z started
- 2026-05-27T05:53:29.881Z commented by mark.valenzuela@ngnair.com (QA PASS)
- 2026-05-27T05:53:43.426Z moved to Done

### In-Range Day Mapping
- 2026-05-27: commented (QA PASS) at 05:53:29 UTC, moved to Done at 05:53:43 UTC

### Activity Notes
Moved to Done after QA testing on staging. Verified the full invite → disable → reactivate → accept lifecycle. All acceptance criteria met.

---

## NGN-731: Marketplace: Show user-friendly toast when Category delete fails (Category in use)

Status: Pending Review
Activity date: 2026-05-27
URL: https://linear.app/ngnair/issue/NGN-731/marketplace-show-user-friendly-toast-when-category-delete-fails
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me, commented on by me

### Description
### The Problem

Deleting a Category that is currently assigned to an App in Marketplace Admin triggers a raw Prisma foreign key constraint error in a toast (`App_categoryId_fkey`) instead of a user-friendly message.

### Steps to Reproduce

1. Login as Mark Goldman to Marketplace Admin.
2. Go to Categories.
3. Go to Apps, then select an app to view its details.
4. Note the selected App's Category.
5. Go back to Categories and attempt to delete that Category.
6. Observe the toast shows the raw Prisma error (`Invalid this.prisma.appCategory.delete() invocation ... Foreign key constraint violated ... App_categoryId_fkey`).

### Technical Requirements

* UI-only fix in Marketplace Admin.
* When delete fails due to the category being in use, show a friendly toast message and do not display raw error text/stack traces.
* Keep deletion blocked (no changes to backend behavior required).

### Expected vs Actual

* **Expected:** Deletion is blocked and a friendly toast indicates the Category can't be deleted because it's assigned to one or more Apps.
* **Actual:** Deletion is blocked but the UI shows a raw Prisma FK constraint error toast.

### Acceptance Criteria

- [ ] Attempting to delete a Category that is assigned to at least one App shows a friendly toast (e.g., "Cannot delete category because it's assigned to one or more apps.").
- [ ] The toast does not include raw Prisma error text, stack traces, file paths, or constraint names (e.g., `App_categoryId_fkey`).
- [ ] The Category is not deleted when it is assigned to an App.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-27T07:30:42.509Z
**Area:** `src/app/(dashboard)/categories/page.tsx` — the `handleDelete` catch block (currently lines 170–175)

**Current code:**
```ts
} catch (err) {
  console.error("Failed to delete category:", err);
  toast.error(
    err instanceof Error ? err.message : "Failed to delete category",
  );
}
```

**Problem:** `err.message` passes a raw Prisma error string (including `App_categoryId_fkey` and stack traces) directly into the toast.

**Options to consider:**

| # | Approach | Tradeoff |
|---|----------|----------|
| 1 | Replace with a hardcoded generic message (e.g. `"Failed to delete category"`) | Simplest fix. Matches the pattern used in every other page in the app. Loses the specificity of the server error message. |
| 2 | Hardcoded generic, but hint at the common cause (e.g. `"Failed to delete category. It may be assigned to one or more apps."`) | Same simplicity, slightly more helpful. Still not specific to the actual error. |
| 3 | Inspect `err.message` for FK-related keywords (`"Foreign key constraint"`, `"constraint"`, etc.) and show a specific message for that case, fall back to generic | Specific toast for the known failure mode. Fragile — depends on Prisma error text remaining stable. |
| 4 | Check `(err as ApolloError).graphQLErrors` for a structured error code or extension field from the backend | Most structured if the backend provides one (needs checking). If not, same as option 3. |

**Relevant context:** The categories page is the only place in the codebase that passes `err.message` to `toast.error`. All other pages (`apps/[id]`, `services/[id]`, `app-installs/[id]`, `review-queue`) use the pattern in option 1. `console.error` is already called in all cases, preserving the full error for debugging.

### Activity Timeline
- 2026-05-27T06:26:38.872Z created
- 2026-05-27T07:30:42.397Z commented by mark.valenzuela@ngnair.com

### In-Range Day Mapping
- 2026-05-27: created at 06:26:38 UTC, commented at 07:30:42 UTC

### Activity Notes
Created this bug ticket and provided a detailed code analysis in comments, pinpointing the exact file and line causing the raw Prisma error toast. Listed four implementation options with tradeoffs for the assignee.
