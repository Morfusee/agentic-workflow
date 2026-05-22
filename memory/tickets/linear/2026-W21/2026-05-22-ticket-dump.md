# Stand-up Script

Yesterday, I tested two items. I verified the CSP frame-ancestors fix on the Finance FE staging and develop environments, confirming the port-wildcard pattern is now present and the Location FE local-dev iframe embedding is no longer blocked — reported a QA PASS. I also filed a bug report for the Partner Admin status update flow where non-BIN-ISO partners were getting a confusing error message that exposed internal field names. Duane picked that up and resolved it with a fix that conditionally includes the `isExternal` field only for BIN-ISO partners.

No major blockers right now.

---

# Selected Tickets

- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
  - Status: Done
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-645/finance-allow-location-fe-local-dev-origin-in-csp-frame-ancestors
  - Reference: 2026-05-21 dump — `# All Scraped Tickets` -> `## NGN-645`
  - Stand-up relevance: Tested CSP fix on develop and staging, confirmed port-wildcard pattern, reported QA PASS.

- NGN-671: Partner: Return user-friendly error when updating status on non-BIN-ISO partners
  - Status: Done
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-671/partner-return-user-friendly-error-when-updating-status-on-non-bin-iso
  - Reference: `# All Scraped Tickets` -> `## NGN-671: Partner: Return user-friendly error when updating status on non-BIN-ISO partners`
  - Stand-up relevance: Filed bug report for confusing error message; resolved by Duane with conditional isExternal field handling.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting raw Elavon API error surfacing to users during refund flow.

- NGN-674: Product: Category detail modal shows 0 total products regardless of actual count
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting stale product count in category detail modal.

- NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created improvement ticket for pre-filtering expired/future discounts from pay link discount selection UI.

- NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting discount Max Claims limit not enforced on Pay Link transactions.

- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting timezone offset issue with payment link expiration dates.

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

---

# Ticket Dump

Generated: 2026-05-22
Requested range: 2026-05-21 to 2026-05-22
Dump file date: 2026-05-22

---

# Grouped Summary

2026-05-21

## Done
- NGN-671: Partner: Return user-friendly error when updating status on non-BIN-ISO partners

## Pending Review
- NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction
- NGN-674: Product: Category detail modal shows 0 total products regardless of actual count
- NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection
- NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions

2026-05-22

## Pending Review
- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links
- NGN-689: Product: Prevent payment links from being created with past expiration dates

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-671: Partner: Return user-friendly error when updating status on non-BIN-ISO partners

Status: Done
Activity date: 2026-05-21
URL: https://linear.app/ngnair/issue/NGN-671/partner-return-user-friendly-error-when-updating-status-on-non-bin-iso
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Updating status on a non-BIN-ISO partner shows a toast error that is vague and not actionable for a non-technical admin user: `Update failed: isExternal can only be set on BIN_ISO partners`

### Steps to Reproduce

1. Log in to Partner Admin as Mark Goldman
2. Navigate to Partners
3. Edit a non-BIN-ISO partner
4. Change Status to any value other than the default
5. Observe the toast component after clicking the Save Changes button.

### Technical Requirements

* The error message surfaced in the UI toast should describe the problem in terms the user can understand, not expose internal field names (`isExternal`) or partner classifications (`BIN_ISO`)
* Identify whether the status update itself is the invalid operation, or whether a hidden field (`isExternal`) is being incorrectly sent for this partner type — fix whichever side is causing the confusing error

### Expected vs Actual

* **Expected:** Toast shows a clear, user-friendly message (e.g. "Status update failed for this partner type")
* **Actual:** Toast shows `Update failed: isExternal can only be set on BIN_ISO partners`

### Acceptance Criteria

- [ ] Admin users see an understandable error message when status update fails on a non-BIN-ISO partner
- [ ] Internal implementation details (`isExternal`, `BIN_ISO`) are not exposed in the UI

### Comments
#### Duane Enriquez - 2026-05-22T00:58:35.548Z
**Previous behavior:** `partnerToSnapshot()` in the edit form unconditionally copied `partner.isExternal` into the update payload for all partner levels. The backend rejected `isExternal` on non-BIN-ISO partners with the error `Update failed: isExternal can only be set on BIN_ISO partners`, which was surfaced verbatim in the toast. This made every save operation fail on ISV/ISO/acquirer partners, including simple status changes, with a confusing leaky-error message.

**Behavior now:** `partnerToSnapshot()` now conditionally includes `isExternal` only when `partner.level === PartnerLevel.BinIso`; for all other levels the field is omitted from the payload. Saves on non-BIN-ISO partners now succeed with the expected `Partner updated successfully` toast. BIN ISO partners remain unaffected — the BIN ISO Type select still reads, writes, and persists `isExternal` normally.

**Why it's significant:** Unblocks edit operations for the majority of partners in the system (all non-BIN-ISO levels). Eliminates the confusing backend error message that users encountered, restoring basic form functionality.

### Activity Timeline
- 2026-05-21T16:10:29.871Z created
- 2026-05-22T00:58:38.052Z moved to Done

### In-Range Day Mapping
- 2026-05-21: created ticket (2026-05-21T16:10:29.871Z)

### Activity Notes
Created bug report documenting unclear error message when updating status on non-BIN-ISO partners. Ticket was resolved by Duane on 2026-05-22 with a fix to conditionally include `isExternal` only for BIN-ISO partners.

---

## NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction

Status: Pending Review
Activity date: 2026-05-21
URL: https://linear.app/ngnair/issue/NGN-673/finance-raw-elavon-error-shown-when-refunding-fresh-pay-link
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Refunding a fresh successful pay link transaction shows this raw error toast:

```
Elavon POST /transactions failed: {"status":400,"failures":[{"code":"badRequest","description":"The request is invalid; correct all issues before resending","field":null},{"code":"invalidRefundParentCaptureFlag","description":"Parent transaction is not eligible for settlement","field":null}]}
```

### Steps to Reproduce

1. Log in to Location FE host app as Sofia Navarro
2. Create a pay link
3. Complete the pay link transaction using these test card credentials:
   * Card Number: `5121212121212124`
   * CVV: `123`
   * Expiry Date: `12/30`
4. Go to Reporting > Transactions
5. Select the latest successful transaction and click Refund on the Transaction Details modal
6. Observe the error toast shown to the user

### Technical Requirements

* The `refundTransaction` GraphQL mutation propagates the raw Elavon error response to the UI without modification
* The Elavon API returned `invalidRefundParentCaptureFlag` for this transaction

### Expected vs Actual

* **Expected:** A user-friendly error message is displayed when a refund cannot be processed
* **Actual:** The raw Elavon API error response is shown as a toast

### Acceptance Criteria

- [ ] Raw Elavon error responses are not surfaced directly to the user in refund flows
- [ ] The `refundTransaction` mutation returns a structured error that the UI can display as a user-friendly message

### Comments
No comments found.

### Activity Timeline
- 2026-05-21T16:43:14.490Z created

### In-Range Day Mapping
- 2026-05-21: created ticket (2026-05-21T16:43:14.490Z)

### Activity Notes
Created bug report documenting raw Elavon API error surfacing directly to users during refund flow.

---

## NGN-674: Product: Category detail modal shows 0 total products regardless of actual count

Status: Pending Review
Activity date: 2026-05-21
URL: https://linear.app/ngnair/issue/NGN-674/product-category-detail-modal-shows-0-total-products-regardless-of
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Adding a product to a category does not update the category's modal details. The category list card shows the correct product count, but clicking into the category modal always displays 0 total products.

### Steps to Reproduce

1. Log in as Sofia Navarro to the Location FE Host app
2. Go to Catalog > Categories
3. Create a category
4. Go to Products, create a product, and assign it to the previously created category
5. Go back to Categories
6. Observe that the category card shows the correct number of products
7. Click the category card to open the detail modal
8. Observe that "Total Products" shows 0 instead of the actual count

### Technical Requirements

* Ensure the category detail modal queries or receives the updated product count after product assignment
* Verify the modal is not using a stale/initialized-at-zero data source
* Confirm the list view and modal view reference the same count field

### Expected vs Actual

* **Expected:** Category detail modal reflects the same product count shown on the category card
* **Actual:** Category detail modal always displays 0 total products

### Acceptance Criteria

- [ ] Category detail modal shows the correct product count that matches the card count
- [ ] Product count in the modal updates when products are added or removed from the category
- [ ] Count is consistent between the list view and modal view at all times

### Comments
No comments found.

### Activity Timeline
- 2026-05-21T17:04:00.416Z created

### In-Range Day Mapping
- 2026-05-21: created ticket (2026-05-21T17:04:00.416Z)

### Activity Notes
Created bug report documenting stale product count in category detail modal.

---

## NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection

Status: Pending Review
Activity date: 2026-05-21
URL: https://linear.app/ngnair/issue/NGN-675/product-pre-filter-expiredinvalid-discounts-from-create-payment-link
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

The "Apply Discounts" section in the Create Payment Link modal lists all discounts regardless of their Valid From/To dates. Server-side validation correctly rejects expired or not-yet-active discounts on submit, but the UI should not present them as selectable options in the first place.

### Steps to Reproduce

1. Log in as Sofia Navarro to the Location FE Host app
2. Go to Catalog > Discounts
3. Create a discount with status Active, set Valid From to a past date and Valid To before today (expired)
4. Create another discount with status Scheduled, set Valid From to a future date (not yet active)
5. Go to Customers > Pay Links, click Create Payment Link
6. Expand the "Apply Discounts" section
7. Observe that both discounts appear in the list regardless of their Valid From/To dates
8. Select one and submit — observe server-side rejection rather than upfront filtering

### Technical Requirements

* Add a date-range filter to the discount query used by the Create Payment Link modal's discount selection
* Exclude discounts whose Valid To is before the current date
* Exclude discounts whose Valid From is after the current date
* Discounts with no Valid From/To set should remain visible (no restriction)
* The existing server-side validation should remain unchanged

### Expected vs Actual

* **Expected:** Only discounts whose Valid From/To window includes the current date appear in the selection dropdown
* **Actual:** All discounts appear; invalid ones are rejected server-side on submit instead of being filtered from the list

### Acceptance Criteria

- [ ] Expired discounts (Valid To before today) are excluded from the Create Payment Link discount list
- [ ] Future discounts (Valid From after today) are excluded from the Create Payment Link discount list
- [ ] Discounts without Valid From/To set remain visible
- [ ] Discounts within their valid window continue to appear normally
- [ ] Existing server-side validation is preserved

### Comments
No comments found.

### Activity Timeline
- 2026-05-21T18:36:20.639Z created

### In-Range Day Mapping
- 2026-05-21: created ticket (2026-05-21T18:36:20.639Z)

### Activity Notes
Created improvement ticket requesting pre-filtering of expired/future discounts from the pay link discount selection UI.

---

## NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions

Status: Pending Review
Activity date: 2026-05-21
URL: https://linear.app/ngnair/issue/NGN-676/product-enforce-discount-max-claims-limit-on-pay-link-transactions
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Discounts with a configured Max Claims value can still be used after the limit is reached in Pay Links.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Catalog > Discounts
3. Create a discount, set Max Claims to 1
4. Go to Customers > Pay Links
5. Create a Pay Link using the discount from step 3
6. Complete the transaction using test card:
   * Card Number: 5121212121212124
   * CVV: 123
   * Expiry Date: 12/30
7. Go back to Customers > Pay Links, create a new pay link with the same discount
8. Complete the transaction. Observe that the discount is applied again despite Max Claims being set to 1

### Technical Requirements

* Verify Max Claims is persisted correctly when the discount is created or updated
* Enforce Max Claims during Pay Link discount application
* Prevent discounts that have reached their Max Claims limit from being applied to additional Pay Links

### Expected vs Actual

* **Expected:** After a discount reaches its Max Claims limit, it should no longer be usable or applicable to new Pay Links
* **Actual:** The discount can still be applied to additional Pay Link transactions after Max Claims is set to 1

### Acceptance Criteria

- [ ] Max Claims is saved correctly on discount creation or update
- [ ] A discount at its Max Claims limit cannot be applied to new Pay Links
- [ ] Fully-claimed discounts are excluded from Pay Link discount selection

### Comments
No comments found.

### Activity Timeline
- 2026-05-21T19:11:28.327Z created

### In-Range Day Mapping
- 2026-05-21: created ticket (2026-05-21T19:11:28.327Z)

### Activity Notes
Created bug report documenting that discount Max Claims limit is not enforced on Pay Link transactions.

---

## NGN-688: Product: Fix expiration date applying timezone offset when creating payment links

Status: Pending Review
Activity date: 2026-05-22
URL: https://linear.app/ngnair/issue/NGN-688/product-fix-expiration-date-applying-timezone-offset-when-creating
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

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
No comments found.

### Activity Timeline
- 2026-05-22T06:42:02.164Z created

### In-Range Day Mapping
- 2026-05-22: created ticket (2026-05-22T06:42:02.164Z)

### Activity Notes
Created bug report documenting timezone offset issue with payment link expiration dates.

---

## NGN-689: Product: Prevent payment links from being created with past expiration dates

Status: Pending Review
Activity date: 2026-05-22
URL: https://linear.app/ngnair/issue/NGN-689/product-prevent-payment-links-from-being-created-with-past-expiration
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Users can set an Expiration Date that goes back before the current date, and the payment link creation flow allows it with no validation. The link becomes expired when opened, but creation should be blocked upfront.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Customers > Pay Links
3. Create a Payment Link with an Expiration Date set 10 days in the past.
4. Observe that the creation flow completes without error.
5. Observe that the newly created Pay Link does not show an "Expired" status despite having a past expiration date.

### Technical Requirements

* Add client-side validation to prevent selecting past dates in the expiration date picker.
* Add server-side validation to reject creation/update of payment links with past expiration dates.
* Ensure the payment link status correctly reflects "Expired" when the expiration date has passed.

### Expected vs Actual

* **Expected:** Past expiration dates are rejected during creation; expired links display "Expired" status.
* **Actual:** Creation succeeds with past dates, and the link does not show an Expired status.

### Acceptance Criteria

- [ ] Date picker does not allow selecting a date/time earlier than the current moment.
- [ ] API rejects payment link creation with a past expiration date.
- [ ] Payment links with passed expiration dates display an "Expired" status.

### Comments
No comments found.

### Activity Timeline
- 2026-05-22T06:42:14.489Z created

### In-Range Day Mapping
- 2026-05-22: created ticket (2026-05-22T06:42:14.489Z)

### Activity Notes
Created bug report documenting that payment links can be created with past expiration dates without validation.
