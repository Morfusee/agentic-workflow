# Stand-up Script

Yesterday, I filed two product-side payment link discount tickets. I documented that the Create Payment Link flow still shows expired and not-yet-active discounts in the Apply Discounts section, even though the server rejects those invalid discounts later on submit. I also filed a bug showing that discounts with a Max Claims limit can still be reused on additional Pay Link transactions after the configured limit has already been reached.

No major blockers right now.

---

# Selected Tickets

- NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-675/product-pre-filter-expiredinvalid-discounts-from-create-payment-link
  - Reference: `2026-05-22-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection`
  - Stand-up relevance: Created improvement ticket requesting upfront filtering for expired and future discounts in the pay link discount selection UI.

- NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-676/product-enforce-discount-max-claims-limit-on-pay-link-transactions
  - Reference: `2026-05-22-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions`
  - Stand-up relevance: Created bug report documenting that discount Max Claims limits are not enforced on Pay Link transactions.

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

- NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting that pending Partner invitations are not visible after a user is disabled and reactivated before acceptance.

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

# Ticket Dump

Generated: 2026-05-26T19:19:23+08:00
Requested range: 2026-05-26
Dump file date: 2026-05-26

---

# Grouped Summary

2026-05-26

## Done
- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links

## Pending Review
- NGN-723: Product: Fix Created field applying timezone offset in payment link details
- NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)
- NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance
- NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-688: Product: Fix expiration date applying timezone offset when creating payment links

Status: Done
Activity date: 2026-05-26
URL: https://linear.app/ngnair/issue/NGN-688/product-fix-expiration-date-applying-timezone-offset-when-creating
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Commented on by me

### Description
### The Problem

The Expiration Date selected when creating a Payment Link is stored with a timezone offset applied, causing the displayed expiration to differ from what the user selected.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Customers > Pay Links
3. Create a Payment Link with an Expiration Date set. Note the exact Expiration Date you chose.
4. Click the newly created Pay Link
5. Observe that the Expires field shows a date/time different from what was selected (shifted by the user's UTC offset).

### Technical Requirements

* Ensure expiration date is stored and displayed in a timezone-agnostic manner (e.g., UTC) so it matches the user's intent regardless of their local offset.
* Check if the bug is in the FE (sending a timezone-adjusted date) or BE (converting the date on receipt/storage).

### Expected vs Actual

* **Expected:** Expiration date matches exactly what the user selected.
* **Actual:** Expiration date is shifted by the user's UTC offset.

### Acceptance Criteria

- [ ] Expiration date shown after creation matches the date and time selected during creation, regardless of the user's timezone.
- [ ] Timezone handling is consistent across all timezones.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-26T07:00:07.390Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Validated the Payment Link creation flow expiration date handling, ensuring the stored and displayed expiration matches the date/time selected by the user across timezones.

### Test Results
All acceptance criteria pass. After creating a Payment Link with a specific expiration date/time, the Expires value shown post-creation matches exactly what was selected during creation, and the behavior remains consistent when the user is in different timezones (no UTC-offset shift).

### Activity Timeline
- 2026-05-26T07:00:07.390Z commented

### In-Range Day Mapping
- 2026-05-26: commented with QA PASS result (2026-05-26T07:00:07.390Z)

### Activity Notes
Tested the Payment Link expiration date handling on staging and commented that all acceptance criteria passed.

---

## NGN-723: Product: Fix Created field applying timezone offset in payment link details

Status: Pending Review
Activity date: 2026-05-26
URL: https://linear.app/ngnair/issue/NGN-723/product-fix-created-field-applying-timezone-offset-in-payment-link
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

The **Created** value shown in the Payment Link Details modal (after clicking a newly created Pay Link) is displayed with a timezone offset applied, causing the shown Created date/time to differ from what the user expects (shifted by the user's UTC offset).

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Customers > Pay Links
3. Create a Payment Link
4. Click the newly created Pay Link to open the Payment Link Details modal
5. Observe the **Created** field shows a date/time shifted by the user's UTC offset

### Technical Requirements

* Ensure the Created timestamp is stored and displayed consistently (timezone-agnostic/normalized, e.g. UTC) and rendered correctly for the user without introducing an offset shift.
* Verify whether the issue is FE rendering/formatting or BE serialization/storage.

### Expected vs Actual

* **Expected:** Created matches the correct creation timestamp (no offset shift).
* **Actual:** Created is shifted by the user's UTC offset.

### Acceptance Criteria

- [ ] Created shown in the Payment Link Details modal matches the correct creation timestamp and does not shift based on the viewer's timezone.
- [ ] Timezone handling is consistent across all timezones.

### Comments
No comments found.

### Activity Timeline
- 2026-05-26T07:05:30.432Z created

### In-Range Day Mapping
- 2026-05-26: created ticket (2026-05-26T07:05:30.432Z)

### Activity Notes
Created bug report documenting a timezone offset issue in the Payment Link Details Created field.

---

## NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)

Status: Pending Review
Activity date: 2026-05-26
URL: https://linear.app/ngnair/issue/NGN-727/partner-add-optional-firstlast-name-fields-to-partner-fe-invite-user
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Partner FE host app (Manage > Users) invite modal does not include optional First Name / Last Name fields, so the invited user's displayed Name falls back to email. Partner Admin's invite modal includes optional First Name / Last Name fields, so invited users can have a proper name.

### Steps to Reproduce

1. Log in as Rafael Costa in Partner FE host app.
2. Go to Manage > Users.
3. Click to invite a user.
4. Observe the "Invite New User" modal has no First Name or Last Name fields.
5. Log in as Mark Goldman in Partner Admin.
6. Go to Partners > Ruby BIN ISO > Partner Users.
7. Click to invite a user.
8. Observe the "Invite Partner Users" modal includes optional First Name and Last Name fields.
9. Invite a user from Partner FE and observe the newly invited user's displayed Name falls back to the email address.

### Technical Requirements

* Add optional `First Name` and `Last Name` inputs to the Partner FE "Invite New User" modal (UI parity with Partner Admin).
* When provided, send first/last name values in the Partner FE invite request so the invited user record has a proper display name.
* When omitted, keep current behavior (fallback to email) unchanged.

### Expected vs Actual

* **Expected:** Partner FE invite flow allows optionally providing first/last name; when provided, the user displays a proper name; when omitted, fallback to email remains.
* **Actual:** Partner FE invite flow cannot capture first/last name, so user name always falls back to email.

### Acceptance Criteria

- [ ] Partner FE "Invite New User" modal includes optional First Name and Last Name fields.
- [ ] Submitting an invite from Partner FE with first/last name provided results in the invited user showing a name (not email fallback).
- [ ] Submitting an invite from Partner FE with first/last name omitted preserves current email-fallback behavior.
- [ ] Partner FE and Partner Admin invite modals are aligned on name-field availability.

### Comments
No comments found.

### Activity Timeline
- 2026-05-26T09:48:06.580Z created

### In-Range Day Mapping
- 2026-05-26: created ticket (2026-05-26T09:48:06.580Z)

### Activity Notes
Created improvement ticket documenting missing optional first and last name fields in the Partner FE invite user modal.

---

## NGN-728: Partner: Keep pending invitation visible after disable/reactivate before acceptance

Status: Pending Review
Activity date: 2026-05-26
URL: https://linear.app/ngnair/issue/NGN-728/partner-keep-pending-invitation-visible-after-disablereactivate-before
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

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
No comments found.

### Activity Timeline
- 2026-05-26T10:12:36.828Z created

### In-Range Day Mapping
- 2026-05-26: created ticket (2026-05-26T10:12:36.828Z)

### Activity Notes
Created bug report documenting that pending Partner invitations are not visible after a user is disabled and reactivated before acceptance.

---

## NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container

Status: Pending Review
Activity date: 2026-05-26
URL: https://linear.app/ngnair/issue/NGN-729/partner-let-add-revenue-split-partner-dropdown-overflow-modal
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

The Partner dropdown in the Add Revenue Split modal under Partner Org Recipient Type is clipped inside the modal container, so the full list is not visible when the menu opens.

### Steps to Reproduce

1. Log in as Mark Goldman in Partner Admin.
2. Go to Partners > Ruby BIN ISO (or any partner in the table) > Revenue Splits.
3. Add a split for any Internal MID by clicking Add Split.
4. Select `Partner (Org)` for Recipient Type.
5. Click the Partner dropdown field.
6. Observe that the dropdown is clipped inside the modal container, making it hard to navigate the list of partners.

### Technical Requirements

* Allow the Partner dropdown menu to render outside the modal bounds.
* Prevent modal overflow or scroll containers from clipping the dropdown menu.
* Keep the dropdown usable for long partner lists.

### Expected vs Actual

* **Expected:** The Partner dropdown opens fully and is not clipped by the modal container.
* **Actual:** The dropdown is restrained inside the modal and the list is cut off.

### Acceptance Criteria

- [ ] The Partner dropdown in Add Revenue Split renders fully visible when opened.
- [ ] The dropdown is not clipped by modal overflow or scroll constraints.
- [ ] The dropdown remains usable across typical viewport sizes and long option lists.

### Comments
No comments found.

### Activity Timeline
- 2026-05-26T10:27:18.326Z created

### In-Range Day Mapping
- 2026-05-26: created ticket (2026-05-26T10:27:18.326Z)

### Activity Notes
Created bug report documenting that the Partner dropdown in the Add Revenue Split modal is clipped by the modal container.
