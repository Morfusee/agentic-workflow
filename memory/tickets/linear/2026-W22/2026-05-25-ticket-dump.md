# Stand-up Script

Yesterday, I filed two bug reports. I documented a raw Elavon API error that surfaces to users when refunding fresh pay link transactions — the full API response is shown as a toast instead of a user-friendly message. I also reported an issue in the catalog where the category detail modal consistently displays 0 total products regardless of how many products are actually assigned to the category.

Today, I plan to just do QA and find bugs.

No major blockers right now.

---

# Selected Tickets

- NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-673/finance-raw-elavon-error-shown-when-refunding-fresh-pay-link
  - Reference: `# All Scraped Tickets` -> `## NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction`
  - Stand-up relevance: Filed bug report documenting raw Elavon API error surfacing to users during refund flow.

- NGN-674: Product: Category detail modal shows 0 total products regardless of actual count
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-674/product-category-detail-modal-shows-0-total-products-regardless-of
  - Reference: `# All Scraped Tickets` -> `## NGN-674: Product: Category detail modal shows 0 total products regardless of actual count`
  - Stand-up relevance: Filed bug report documenting stale product count in category detail modal.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

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

*No manual tasks recorded.*

---

# Ticket Dump

Generated: 2026-05-25
Requested range: 2026-05-25
Dump file date: 2026-05-25

---

# Grouped Summary

2026-05-25

## Pending Review
- NGN-719: Finance: Pay Link for Payment Plan charges full amount instead of monthly installment amount
- NGN-720: Finance: Surcharge line item missing from Transaction Details modal after Pay Link payment

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-719: Finance: Pay Link for Payment Plan charges full amount instead of monthly installment amount

Status: Pending Review
Activity date: 2026-05-25
URL: https://linear.app/ngnair/issue/NGN-719/finance-pay-link-for-payment-plan-charges-full-amount-instead-of
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Creating a Pay Link for a Payment Plan with monthly installment frequency charges the full Payment Plan amount on the first transaction instead of the correct monthly installment.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Customers > Payment Plans
3. Create a Payment Plan for any product
4. Set Payment Frequency to Monthly and Number of Installments to 12
5. Create a Pay Link for the newly created Payment Plan
6. Initiate the Pay Link transaction by copy-pasting it into another tab
7. Observe that the Order Summary shows the full Payment Plan amount
8. Complete the Pay Link transaction using the following test card details:
   * Card number: 4000 0000 0000 0002
   * CVC: 123
   * Expiration: 12/30
   * Postal Code: 1772
9. Observe that the user paid the full amount instead of the installment amount

### Technical Requirements

* Pay Link transaction amount for Payment Plans must reflect the individual installment amount based on the configured frequency and number of installments, not the total plan amount
* The installment calculation should divide the total Payment Plan amount by the number of installments

### Expected vs Actual

* **Expected:** Pay Link charges the monthly installment amount (total / number of installments)
* **Actual:** Pay Link charges the full Payment Plan amount as a single transaction

### Acceptance Criteria

- [ ] Pay Link for a monthly Payment Plan charges the correct per-installment amount on the first transaction
- [ ] Order Summary displays the installment amount, not the full plan total
- [ ] Subsequent installments are scheduled correctly after the first payment

### Comments
No comments found.

### Activity Timeline
- 2026-05-25T09:25:31.222Z created

### In-Range Day Mapping
- 2026-05-25: created ticket (2026-05-25T09:25:31.222Z)

### Activity Notes
Created bug report documenting Pay Link for Payment Plans charging the full plan amount instead of the correct per-installment amount.

---

## NGN-720: Finance: Surcharge line item missing from Transaction Details modal after Pay Link payment

Status: Pending Review
Activity date: 2026-05-25
URL: https://linear.app/ngnair/issue/NGN-720/finance-surcharge-line-item-missing-from-transaction-details-modal
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

After completing a Pay Link transaction with surcharge enabled, the Payment Complete page correctly displays the surcharge line item, but the Transaction Details modal under Reporting > Transaction does not show the surcharge — the Extra Fees line item shows $0 and no surcharge appears anywhere in the Cost Breakdown.

### Steps to Reproduce

1. Log in as Sofia Navarro to Location FE host app
2. Go to Manage > Payments and enable the Surcharge setting
3. Go to Customers > Pay Links
4. Create or select a Pay Link with type Product, ensuring the amount ends in .00
5. Initiate the Pay Link transaction by copy-pasting it into another tab
6. Complete the transaction using the following test card details:
   * Card number: 4000 0000 0000 0002
   * CVC: 123
   * Expiration: 12/30
   * Postal Code: 1772
7. Observe that the Payment Complete page shows a Surcharge line item of $3.00
8. Go to Reporting > Transaction and click the latest Captured transaction
9. Observe that the Cost Breakdown shows only the subtotal, Extra Fees is $0, and no Surcharge line item is visible

### Technical Requirements

* The Transaction Details modal must include the surcharge as a line item in the Cost Breakdown when surcharge was applied to the transaction
* The Extra Fees line item should reflect the surcharge amount, or a dedicated Surcharge line item should be rendered

### Expected vs Actual

* **Expected:** Transaction Details modal displays the surcharge line item matching what appears on the Payment Complete page
* **Actual:** Transaction Details modal shows Extra Fees as $0 and no surcharge line item anywhere in the Cost Breakdown

### Acceptance Criteria

- [ ] Surcharge line item appears in the Transaction Details modal Cost Breakdown
- [ ] The surcharge amount in the modal matches the amount displayed on the Payment Complete page
- [ ] Extra Fees or a dedicated Surcharge line item correctly reflects the applied surcharge

### Comments
No comments found.

### Activity Timeline
- 2026-05-25T09:45:59.870Z created

### In-Range Day Mapping
- 2026-05-25: created ticket (2026-05-25T09:45:59.870Z)

### Activity Notes
Created bug report documenting surcharge line item missing from Transaction Details modal despite appearing on the Payment Complete page.
