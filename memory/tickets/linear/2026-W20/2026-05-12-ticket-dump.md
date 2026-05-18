# Stand-up Script

Yesterday, I created a ticket to fix item prices showing as $0 on the Checkout Payment Complete page so we could restore accurate receipt values after successful Pay Link payments. I also created a ticket to keep Multi-Use Pay Links active after successful transactions and ensure usage counts increment correctly instead of marking links completed too early. I created another ticket to stop full page reloads during Partner Users search so the table updates without dropping input focus.

No major blockers right now.

---

# Selected Tickets

- NGN-589: Fix item price display on the Checkout Payment Complete page
  - Status: Done
  - Activity date: 2026-05-12
  - URL: https://linear.app/ngnair/issue/NGN-589/fix-item-price-display-on-the-checkout-payment-complete-page
  - Reference: # All Scraped Tickets -> ## NGN-589: Fix item price display on the Checkout Payment Complete page
  - Stand-up relevance: Created to track and drive correction of incorrect $0 item pricing on payment success view.
- NGN-590: Keep Multi-Use Pay Links active and increment usage count correctly
  - Status: Done
  - Activity date: 2026-05-12
  - URL: https://linear.app/ngnair/issue/NGN-590/keep-multi-use-pay-links-active-and-increment-usage-count-correctly
  - Reference: # All Scraped Tickets -> ## NGN-590: Keep Multi-Use Pay Links active and increment usage count correctly
  - Stand-up relevance: Created to fix incorrect pay-link lifecycle and usage tracking behavior.
- NGN-600: Prevent full page reload during Partner Users search
  - Status: Pending Review
  - Activity date: 2026-05-12
  - URL: https://linear.app/ngnair/issue/NGN-600/prevent-full-page-reload-during-partner-users-search
  - Reference: # All Scraped Tickets -> ## NGN-600: Prevent full page reload during Partner Users search
  - Stand-up relevance: Created to improve search UX and prevent disruptive iframe reload behavior.

---

# Ticket Dump

Generated: 2026-05-16T00:41:29+08:00
Requested range: 2026-05-12
Dump file date: 2026-05-12

---

# Grouped Summary

[2026-05-12]

## [Done]
- [NGN-589]: Fix item price display on the Checkout Payment Complete page
- [NGN-590]: Keep Multi-Use Pay Links active and increment usage count correctly

## [Pending Review]
- [NGN-600]: Prevent full page reload during Partner Users search

---

# All Scraped Tickets

## NGN-589: Fix item price display on the Checkout Payment Complete page

Status: Done
Activity date: 2026-05-12
URL: https://linear.app/ngnair/issue/NGN-589/fix-item-price-display-on-the-checkout-payment-complete-page
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

After completing a Pay Link checkout, the Payment Complete page displays each item price as **** instead of the item’s actual cost/value.

### Steps to Reproduce

1. Log in as Sofia Navarro to the Location FE Host app.
2. Use either flow:
   1. Create a Pay Link.
   2. Use an existing Pay Link.
3. Open the Pay Link.
4. Complete the checkout using the test card:
   * Card Number: 4000000000000002
   * Expiration: 12/30
   * CVV: 123
5. Proceed with the transaction and wait for the payment to succeed.
6. On the Payment Complete page, observe the displayed item prices.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T11:44:04.813Z
## Environment

STAGING

## Tested By

Mark

## Test Scope

Validation of item-level price display on the Payment Complete page after completing a Pay Link checkout.

## Result

PASSED

## Note

The issue has been fixed and verified in STAGING. Completed Pay Link checkouts now show the correct item-level prices on the Payment Complete page instead of defaulting to , and the displayed total remains consistent with the receipt items.

#### josh.tating@ngnair.com - 2026-05-14T11:35:05.139Z
Ready for verification — fix deployed to staging, including fallback to unitPrice × quantity when item.total is missing in success-state rendering.

#### josh.tating@ngnair.com - 2026-05-14T11:10:15.985Z
Fix implemented and linked to combined branch with checkout success-state item price fallback.

### Activity Timeline
- 2026-05-12T06:35:48.945Z created
- 2026-05-14T11:44:04.813Z tested

### In-Range Day Mapping
- 2026-05-12: 2026-05-12T06:35:48.945Z created

### Activity Notes
Created this ticket on 2026-05-12 to track correction of checkout success-page item-price rendering.

## NGN-590: Keep Multi-Use Pay Links active and increment usage count correctly

Status: Done
Activity date: 2026-05-12
URL: https://linear.app/ngnair/issue/NGN-590/keep-multi-use-pay-links-active-and-increment-usage-count-correctly
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

Completing a transaction for a Multi-Use Pay Link updates the Pay Link status to COMPLETED, which prevents the link from being used again even when the usage limit has not been reached or no usage limit is set.

### Comments
No comments found.

### Activity Timeline
- 2026-05-12T07:18:00.630Z created

### In-Range Day Mapping
- 2026-05-12: 2026-05-12T07:18:00.630Z created

### Activity Notes
Created this ticket on 2026-05-12 to address pay-link status and usage-count behavior after successful payments.

## NGN-600: Prevent full page reload during Partner Users search

Status: Pending Review
Activity date: 2026-05-12
URL: https://linear.app/ngnair/issue/NGN-600/prevent-full-page-reload-during-partner-users-search
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

Searching Partner Users under **Manage > Users** reloads the whole iframe/page instead of only updating the users table, causing the search input to lose focus while typing.

### Comments
No comments found.

### Activity Timeline
- 2026-05-12T08:20:10.850Z created

### In-Range Day Mapping
- 2026-05-12: 2026-05-12T08:20:10.850Z created

### Activity Notes
Created this ticket on 2026-05-12 to isolate search loading to table scope and preserve typing focus.
