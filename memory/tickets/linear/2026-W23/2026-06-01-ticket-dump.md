# Stand-up Script

Yesterday, I filed a bug report documenting that the surcharge line item is missing from the Transaction Details modal after a Pay Link payment — it appears correctly on the Payment Complete page but is absent from the transaction detail view.

No major blockers right now.

---

# Ticket Dump

Generated: 2026-06-01T10:42:00Z
Requested range: 2026-06-01
Dump file date: 2026-06-01

---

# Grouped Summary

2026-06-01

## Done
- NGN-807: Support: Escalation ticket status not updating on parent case's Linked Escalations section

## In Review
- NGN-753: Location: Fix partner onboarding review views (L30/L20) and early draft visibility

## Pending Review
- NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors

---

# Selected Tickets

- NGN-720: Finance: Surcharge line item missing from Transaction Details modal after Pay Link payment
  - Status: Pending Review
  - Activity date: 2026-05-25
  - URL: https://linear.app/ngnair/issue/NGN-720
  - Reference: `memory/tickets/linear/2026-W22/2026-05-25-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-720`
  - Stand-up relevance: Created bug report documenting surcharge line item missing from Transaction Details modal despite appearing on Payment Complete page.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Pending Review
  - Role: contributor
  - Activity notes: Filed bug documenting empty processor dropdown for Ruby/Plat BIN ISOs during L20 underwriting. Discovered during NGN-752 QA.

- NGN-807: Support: Escalation ticket status not updating on parent case's Linked Escalations section
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: contributor
  - Activity notes: Filed bug about stale escalation status in Linked Escalations. Duane fixed and closed — refetches parent query on close/reopen to update cached children. Moved to Done.

- NGN-753: Location: Fix partner onboarding review views (L30/L20) and early draft visibility
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: In Review
  - Role: tester-only
  - Activity notes: Ran QA on staging against the L30/L20 review modal rebuild. All 6 UI checks PASS — tabs, esign staging, pricing, REVIEW-to-ESIGN transition, L20 visibility gate, L20 processor selection. One FAIL: selecting both Primary and Secondary processors on Approve violates the unique constraint on merchantAccount.internal_mid. Result: PARTIAL.

- NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: tester-only
  - Activity notes: Closed QA on staging — marked PARTIAL pass. Gold BIN ISO verified; Ruby and Plat blocked by processor dropdown issue (NGN-803). Moved to Done per Josh.

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

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-753: Location: Fix partner onboarding review views (L30/L20) and early draft visibility

Status: In Review
Activity date: 2026-06-01
URL: https://linear.app/ngnair/issue/NGN-753/location-fix-partner-onboarding-review-views-l30l20-and-early-draft
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Commented on by me (QA Result: PARTIAL)

### Description
### The Problem

Multiple defects in the partner-facing onboarding review flow. These review views are rendered by location-frontend (route `/partner/iframe`) and embedded in the partner portal via an iframe, so the fixes land in the Location services. Symptoms: the L30 (ISO) review view does not match the intended design (layout and esign-button semantics); pricing is missing from the L30 review; and the L20 (BIN ISO) sees locations during the review stage when it should not.

Defect 1 — L30 review view is wrong (layout + esign-button semantics)
Defect 2 — Pricing not showing in L30 review (STILL UNRESOLVED)
Defect 3 — L20 sees locations during the review stage

### Acceptance Criteria

- [x] L30 review view no longer renders an "Application" tab
- [x] L30 review view shows four sections per BIN ISO tab: composite score, metric scores, risk factors, pricing intelligence
- [x] Each L30 BIN ISO tab has a "Send esign" button that adds that BIN ISO's contract template; button disables and shows checkmark after click
- [x] Separate single button performs final REVIEW-to-ESIGN transition; no separate "boarding"-stage button
- [x] Pricing intelligence renders during REVIEW stage, per BIN ISO tab
- [x] L20 does not see location until sent for boarding and esign is complete
- [x] L20 review view shows per-L10 tabs, composite/metric/analysis factors, Primary+Secondary processor radios
- [ ] Processor approval with Primary + Secondary selection creates valid MerchantAccounts without violating unique constraints (FAIL)

### Comments
#### mark.valenzuela@ngnair.com - 2026-06-01T10:36:12.609Z
### QA Result: `PARTIAL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope

Verified partner onboarding review views: L30 ISO review (per-BIN-ISO tabs, esign staging, pricing intelligence, REVIEW-to-ESIGN transition), L20 BIN ISO review (per-L10 tabs, processor selection, visibility gating), and the processor approval flow including MID provisioning.

### Test Results

| Check | Expected | Actual | Result |
| -- | -- | -- | -- |
| L30 review view renders four sections per BIN ISO tab | Four sections per tab, tabs toggle only | -- | PASS |
| Per-tab Send esign button stages contract template; disables + checkmark after click | Disable + checkmark per tab, other tabs still addable | -- | PASS |
| Separate single button performs final REVIEW-to-ESIGN transition | Single transition button, no boarding-stage framing | -- | PASS |
| Pricing intelligence renders during REVIEW, per BIN ISO tab | Pricing visible during REVIEW per BIN tab | -- | PASS |
| L20 does not see location until boarding + esign complete | L20 sees no pre-underwriting locations | -- | PASS |
| L20 review view: per-L10 tabs, Primary+Secondary processor radios, Approve gated on Primary | Per-L10 tabs, Primary/Secondary radios, Approve gated on Primary | -- | PASS |
| Processor approval with Primary + Secondary creates valid MerchantAccounts | One MerchantAccount per role variant, each with valid internal_mid | Selecting Primary and Secondary creates two MerchantAccounts sharing the same internal_mid, violating the unique constraint | FAIL |

Root cause: when two processors are chosen, the approval service creates one MerchantAccount via upsert and then attempts to insert a second via `create` using the same `internal_mid` value, hitting the unique constraint.

#### josh.tating@ngnair.com - 2026-06-01T09:51:51.067Z
Ready for QA — final defects on the L30/L20 review modal are resolved. Docker tags: location-backend `f0ccf08`, location-frontend `91ac93f`.

#### josh.tating@ngnair.com - 2026-05-31T15:51:12.004Z
Deployed to staging. Defects 1 & 3 shipped (Defects 0 & 2 deferred). Docker tags: location-backend `b768fc5`, location-frontend `1653e7c`.

#### josh.tating@ngnair.com - 2026-05-29T16:01:57.638Z
Defects 1 and 3 implemented on branch `feature/ngn-753`.

#### josh.tating@ngnair.com - 2026-05-29T14:46:08.410Z
Filed partner-side data dependency for Defect 2 as sub-issue NGN-754.

### Activity Timeline
- 2026-05-29T12:03:36Z created (josh.tating)
- 2026-05-29T14:46:08Z commented (josh.tating — filed NGN-754)
- 2026-05-29T16:01:57Z commented (josh.tating — implementation notes)
- 2026-05-31T15:49:49Z moved to In Progress
- 2026-05-31T15:51:12Z commented (josh.tating — deployed to staging)
- 2026-06-01T09:51:51Z commented (josh.tating — ready for QA, final defects resolved)
- 2026-06-01T10:36:12Z commented (mark.valenzuela — QA Result: PARTIAL)

### In-Range Day Mapping
- 2026-06-01: commented (mark.valenzuela — QA Result: PARTIAL at 10:36:12Z)

### Activity Notes
Ran QA on staging against the L30/L20 review modal rebuild. All 6 UI and flow checks passed: L30 review layout, per-tab esign staging with disable+checkmark, REVIEW-to-ESIGN transition, pricing intelligence during REVIEW, L20 visibility gate, and L20 processor selection UI. The one failure is a backend unique constraint violation when selecting both Primary and Secondary processors for approval — the `create` path inserts a second MerchantAccount with the same `internal_mid`. Result: PARTIAL. Ticket stays In Review pending the constraint fix.

---

## NGN-807: Support: Escalation ticket status not updating on parent case's Linked Escalations section

Status: Done
Activity date: 2026-06-01
URL: https://linear.app/ngnair/issue/NGN-807/support-escalation-ticket-status-not-updating-on-parent-cases-linked
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me; status changed to Done

### Description
### The Problem

When a user escalates a support case to a BIN ISO or Bank, closes the resulting escalation ticket via Close Case, then navigates back to the parent case via the Linked Escalations section, the recently closed escalation ticket still displays "OPEN" instead of reflecting its closed status.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE Host App
2. Navigate to Support
3. Create a new ticket with Category General Location
4. Escalate the ticket by clicking the **Escalate** button on the right-hand side of the modal
5. Select either BIN ISO or Bank (you are redirected to the escalation ticket)
6. Close the escalation ticket by clicking **Close Case**
7. In the Linked Escalations section, click the Parent Case ticket to navigate back
8. Observe the recently closed escalation ticket still shows "OPEN" in the Linked Escalations section

### Technical Requirements

* The Linked Escalations section must reflect the current status of all linked escalation tickets
* Closing an escalation ticket should propagate/cascade the status update to any parent case that references it
* The Linked Escalations UI component needs either real-time reactivity or a refresh-on-navigate mechanism

### Expected vs Actual

* **Expected:** After closing an escalation ticket and returning to the parent case, the Linked Escalations section shows the escalation ticket as "Closed"
* **Actual:** The Linked Escalations section continues to display "OPEN" for the recently closed ticket

### Acceptance Criteria

- [ ] Closing an escalation ticket updates its status in the parent case's Linked Escalations list
- [ ] Navigating from an escalation ticket back to its parent case shows accurate ticket statuses without requiring a manual page refresh
- [ ] Status is consistent whether user navigates back immediately or reloads the page

### Comments
#### Duane Enriquez - 2026-06-01T10:38:36.217Z
**Previous behavior:** `CloseCaseModal` only refetched the currently-mounted `GetSingleTicket` query (the child). Because Apollo's normalized cache distinguishes between `Ticket` and `LinkedTicket` typenames, the parent's cached `children` array was never updated, leaving the closed child displaying as "OPEN".

**Behavior now:** `CloseCaseModal` now accepts an optional `parentId` prop. When set, both close and reopen mutations explicitly refetch the parent's `GetSingleTicket` query using `{query, variables}` syntax, which bypasses Apollo's "is this query mounted?" check and forces a cache rewrite of the parent's `children` data. Navigating back to the parent now shows the closed child with correct status.

### Activity Timeline
- 2026-06-01T09:53:19.574Z created (mark.valenzuela)
- 2026-06-01T10:38:36.217Z commented (Duane Enriquez — fix details)
- 2026-06-01T10:38:37.995Z moved to Done

### In-Range Day Mapping
- 2026-06-01: created (mark.valenzuela at 09:53:19Z); commented (Duane at 10:38:36Z); moved to Done (10:38:37Z)

### Activity Notes
Filed bug documenting that closing an escalation ticket does not update its status in the parent case's Linked Escalations section. Duane fixed the issue: `CloseCaseModal` now accepts an optional `parentId` prop and explicitly refetches the parent's query on close/reopen, forcing an Apollo cache rewrite so the parent's `children` array reflects the correct status. Moved to Done.

---

## NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors

Status: Pending Review
Activity date: 2026-06-01
URL: https://linear.app/ngnair/issue/NGN-803/location-l20-underwriting-processor-dropdown-empty-for-ruby-and-plat
Initial dev assignee: josh.tating@ngnair.com
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

In the L20 underwriting modal, the processor dropdown is empty for Ruby and Plat BIN ISOs, blocking the approval step. Gold BIN ISO works correctly and populates the dropdown. Under **Manage > Processors**, both Ruby and Plat have processors configured — they just do not surface in the underwriting modal.

Discovered during QA of NGN-752. The NGN-752 changes are confirmed working where testable (Gold BIN ISO). Ruby and Plat BIN ISOs could not be validated because processor selection is a prerequisite for the approval flow.

### Steps to Reproduce

1. Onboard a new location and select two BIN ISOs (e.g., Gold and Ruby, or Gold and Plat).
2. Log in to Partner FE as Mark Goldman (Gold BIN ISO owner).
3. Go to **Locations**, open the newly created location, and navigate to the **Underwriting** modal.
4. Observe that the processor dropdown is populated with selectable processors. Approve if desired.
5. Log out and log in as the Ruby (or Plat) BIN ISO owner.
6. Go to **Locations**, open the same location, and navigate to the **Underwriting** modal.
7. Observe that the processor dropdown is empty — no processors are selectable despite being visible under Manage > Processors for that BIN ISO.

### Expected vs Actual

* **Expected:** Every BIN ISO's underwriting modal shows the processors configured under Manage > Processors for that BIN ISO's acquiring bank(s), enabling one-click approval.
* **Actual:** Mark Goldman (Gold) sees the processor dropdown populated correctly. The Ruby and Plat BIN ISO owners see an empty dropdown, despite having processors configured under Manage > Processors.

### Technical Requirements

* Identify why the underwriting modal's processor resolution returns empty for Ruby and Plat BIN ISOs when processors are configured.
* Check whether the processor query or resolver correctly maps the acquiring bank ID for each BIN ISO — the gap may be in how the view determines which acquiring bank's processors to fetch, or in the backend returning empty results for specific BIN ISO / acquiring bank pairs.
* Confirm the fix works for all BIN ISOs (Gold, Ruby, Plat) — no regression on Gold.

### Acceptance Criteria

- [ ] Ruby BIN ISO owner sees the same selectable processors in the underwriting modal that are visible under Manage > Processors.
- [ ] Plat BIN ISO owner sees the same selectable processors in the underwriting modal that are visible under Manage > Processors.
- [ ] Mark Goldman (Gold BIN ISO) continues to see processors and approve correctly (no regression).
- [ ] Selecting a processor and confirming approval succeeds for Ruby and Plat end-to-end on staging.

### Comments
No comments found.

### Activity Timeline
- 2026-06-01T05:14:54.437Z created (mark.valenzuela)

### In-Range Day Mapping
- 2026-06-01: created (mark.valenzuela at 05:14:54Z)

### Activity Notes
Filed bug report documenting that L20 underwriting modal shows an empty processor dropdown for Ruby and Plat BIN ISOs despite processors being configured under Manage > Processors. Discovered during QA of NGN-752. Ticket assigned to Josh.
