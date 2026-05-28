# Stand-up Script

Yesterday, I created a support ticket to block duplicate escalations to the same entity type (BIN ISO or Bank). Duane implemented the backend enforcement, and I QA tested the fix on staging and moved it to Done after verification passed. I also created an improvement ticket to add optional first/last name fields to the Partner FE invite user modal for parity with Partner Admin. After discussing with Duane, we determined that the email-only invite flow is sufficient, so I canceled the ticket.

No major blockers right now.

---

# Selected Tickets

- NGN-744: Support: Block duplicate escalation to the same entity type (BIN ISO or Bank)
  - Status: Done
  - Activity date: 2026-05-28
  - URL: https://linear.app/ngnair/issue/NGN-744/support-block-duplicate-escalation-to-the-same-entity-type-bin-iso-or
  - Reference: `# All Scraped Tickets` -> `## NGN-744: Support: Block duplicate escalation to the same entity type (BIN ISO or Bank)`
  - Stand-up relevance: Created ticket, Duane implemented backend enforcement, I QA tested and moved to Done.

- NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)
  - Status: Canceled
  - Activity date: 2026-05-28
  - URL: https://linear.app/ngnair/issue/NGN-727/partner-add-optional-firstlast-name-fields-to-partner-fe-invite-user
  - Reference: `# All Scraped Tickets` -> `## NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)`
  - Stand-up relevance: Created improvement ticket, determined email-only flow sufficient, canceled ticket.

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

---

# Ticket Dump

Generated: 2026-05-28T22:16:05.2209642+08:00
Requested range: today (2026-05-28)
Dump file date: 2026-05-28

---

# Grouped Summary

2026-05-28

## Done
- NGN-744: Support: Block duplicate escalation to the same entity type (BIN ISO or Bank)

## Canceled
- NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)

---

# All Scraped Tickets

## NGN-744: Support: Block duplicate escalation to the same entity type (BIN ISO or Bank)

Status: Done
Activity date: 2026-05-28
URL: https://linear.app/ngnair/issue/NGN-744/support-block-duplicate-escalation-to-the-same-entity-type-bin-iso-or
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: Mark
My role for this ticket: tester-only

### Why this ticket was included
Created by me, assigned to me, moved to Done by me, QA tested by me

### Description
### The Problem

After a support ticket is escalated to a BIN ISO or Bank, the same ticket remains eligible for escalation to that same entity type again, allowing duplicate escalations to the same entity type.

### Steps to Reproduce

1. Log in as Sofia Navarro.
2. Go to Support.
3. Create a new ticket with Category General Location.
4. The newly created ticket will open up/pop up. Click the **Escalate** button on the right-hand side of the modal.
5. Choose either BIN ISO or Bank (note which one you selected).
6. Observe that an Internal Escalation ticket is created based on the original ticket case.
7. Go back to the same ticket case and re-escalate it to the **same** entity type chosen in step 5.
8. Observe that the same ticket case can be escalated again to the same entity type.

### Technical Requirements

* Track the escalation entity type (BIN ISO or Bank) associated with each ticket's escalation.
* Allow escalation to an entity type only if no prior escalation to that same entity type exists for the ticket.
* Hide or disable the **Escalate** button option for an entity type when that type has already been used.
* The backend escalation mutation must reject attempts to escalate to an entity type that already has an active escalation on the ticket.
* Escalating to the other entity type (e.g., Bank after a BIN ISO escalation) should remain allowed.

### Expected vs Actual

* **Expected:** A ticket can be escalated to BIN ISO once and to Bank once (one per entity type). Escalating to the same entity type a second time is blocked.
* **Actual:** The same ticket can be escalated multiple times to the same entity type.

### Acceptance Criteria

- [ ] Escalation to BIN ISO is blocked if the ticket already has an active BIN ISO escalation.
- [ ] Escalation to Bank is blocked if the ticket already has an active Bank escalation.
- [ ] Escalating to a different entity type than the prior escalation remains allowed.
- [ ] The UI reflects which entity types are no longer available for a given ticket.

### Comments
#### Duane Enriquez - 2026-05-28T04:35:15.258Z
**Previous behavior:** `escalateTicket` always created a child escalation ticket regardless of whether the same entity type had already been escalated. `availableEscalationTargets` returned every level the caller's hierarchy supported, never accounting for existing escalations — so the Escalate modal kept offering an already-used type.

**Behavior now:** `availableEscalationTargets` (GraphQL field resolver) excludes any level whose target partner already has a non-closed child escalation on the ticket. The support-frontend Escalate button + radio options are fully driven by this field, so used types disappear from the UI automatically. `escalateTicket` mutation rejects with BadRequestException ("This ticket already has an active escalation to [BIN ISO/Bank]") when a non-closed child escalation to the resolved target partner already exists. Escalating to the *other* entity type remains allowed; once an escalation child is closed, that type frees up again.

**Why it's significant:** Prevents duplicate escalation tickets that confuse support staff and create orphaned internal records. Backend-only enforcement means no frontend coordination needed — the UI simply follows the truth from `availableEscalationTargets`. Blast radius minimal: three files changed in support-backend, no schema changes, no new models.

#### mark.valenzuela@ngnair.com - 2026-05-28T05:52:31.683Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Verified the support ticket escalation flow to ensure duplicate escalations to the same entity type (BIN ISO or Bank) are blocked while cross-entity escalation remains functional.

### Test Results
Escalation to BIN ISO was blocked after an active BIN ISO escalation already existed on the ticket, and escalation to Bank was blocked after an active Bank escalation already existed. Escalating to a different entity type than the prior escalation (BIN ISO after Bank, or Bank after BIN ISO) remained allowed. The UI correctly reflected which entity types were no longer available for a given ticket by hiding or disabling the corresponding escalation options.

### Activity Timeline
- 2026-05-28T02:04:48.486Z created
- 2026-05-28T04:35:17.417Z started
- 2026-05-28T04:35:15.258Z commented by Duane Enriquez
- 2026-05-28T05:52:31.683Z commented by mark.valenzuela@ngnair.com (QA PASS)
- 2026-05-28T05:53:24.520Z moved to Done

### In-Range Day Mapping
- 2026-05-28: created at 02:04:48 UTC, started at 04:35:17 UTC, commented at 04:35:15 UTC, commented at 05:52:31 UTC, moved to Done at 05:53:24 UTC

### Activity Notes
Created this bug ticket and assigned it to myself. Duane implemented backend enforcement to block duplicate escalations to the same entity type. QA tested on staging and moved to Done after verification passed.

---

## NGN-727: Partner: Add optional first/last name fields to Partner FE invite user modal (parity with Partner Admin)

Status: Canceled
Activity date: 2026-05-28
URL: https://linear.app/ngnair/issue/NGN-727/partner-add-optional-firstlast-name-fields-to-partner-fe-invite-user
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me, commented on by me, status changed to Canceled by me

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
#### mark.valenzuela@ngnair.com - 2026-05-28T01:59:42.238Z
### QA Result: `CANCELLED`

### Notes
Per Duane: email-only invite flow is sufficient. No need to add first/last name columns to the partner schema — the auth service remains the source of truth for user names.

### Activity Timeline
- 2026-05-26T09:48:06.580Z created
- 2026-05-28T01:59:42.238Z commented by mark.valenzuela@ngnair.com (QA CANCELLED)
- 2026-05-28T01:59:49.358Z moved to Canceled

### In-Range Day Mapping
- 2026-05-28: commented at 01:59:42 UTC, moved to Canceled at 01:59:49 UTC

### Activity Notes
Created this improvement ticket for UI parity with Partner Admin. After discussion with Duane, determined that email-only invite flow is sufficient, so ticket was canceled.