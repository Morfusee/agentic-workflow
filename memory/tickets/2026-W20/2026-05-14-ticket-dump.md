# Stand-up Script

Yesterday, I created and triaged several user-facing issues across Marketplace and Customer flows: I reported that new service providers were not appearing immediately after creation, I documented the clipboard-permissions failure when copying contact emails from Customer Contacts, and I logged the Customers table cutoff/navigation problem for large result sets. I also opened and verified Marketplace fixes, confirming that duplicate category slug handling now shows a user-friendly message and that App Installs now loads without the previous GraphQL environment and permissions errors.

I also tested the discounted Pay Link transaction breakdown in staging and confirmed the Transaction Details modal now shows consistent Subtotal, Discount, and Total Charge values on freshly created discounted transactions, while noting that older reference rows could still appear stale.

No major blockers right now.

---

# Selected Tickets

- NGN-562: Fix Transaction Details cost breakdown calculation for discounted Pay Links
  - Status: Done
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-562/fix-transaction-details-cost-breakdown-calculation-for-discounted-pay
  - Reference: `# All Scraped Tickets` -> `## NGN-562: Fix Transaction Details cost breakdown calculation for discounted Pay Links`
  - Stand-up relevance: In-range testing and verification update with explicit staging result.
- NGN-624: Marketplace: Replace duplicate category slug Prisma error with user-friendly toast
  - Status: Done
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-624/marketplace-replace-duplicate-category-slug-prisma-error-with-user
  - Reference: `# All Scraped Tickets` -> `## NGN-624: Marketplace: Replace duplicate category slug Prisma error with user-friendly toast`
  - Stand-up relevance: Created ticket and posted passing verification.
- NGN-628: Marketplace: Fix App Installs GraphQL errors for environment and permissions
  - Status: Done
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-628/marketplace-fix-app-installs-graphql-errors-for-environment-and
  - Reference: `# All Scraped Tickets` -> `## NGN-628: Marketplace: Fix App Installs GraphQL errors for environment and permissions`
  - Stand-up relevance: Created ticket and posted passing verification.
- NGN-630: Marketplace: Refetch service providers list after provider creation
  - Status: Pending Review
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-630/marketplace-refetch-service-providers-list-after-provider-creation
  - Reference: `# All Scraped Tickets` -> `## NGN-630: Marketplace: Refetch service providers list after provider creation`
  - Stand-up relevance: New issue creation capturing reproducible stale-list behavior.
- NGN-631: Customer: Allow clipboard copy from Customer Contacts email field
  - Status: Pending Review
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-631/customer-allow-clipboard-copy-from-customer-contacts-email-field
  - Reference: `# All Scraped Tickets` -> `## NGN-631: Customer: Allow clipboard copy from Customer Contacts email field`
  - Stand-up relevance: New issue creation for permissions-policy break in copy flow.
- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets
  - Status: Pending Review
  - Activity date: 2026-05-14
  - URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
  - Reference: `# All Scraped Tickets` -> `## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets`
  - Stand-up relevance: New issue creation for table truncation and missing navigation controls.

---
# All Scraped Tickets

## NGN-562: Fix Transaction Details cost breakdown calculation for discounted Pay Links

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-562/fix-transaction-details-cost-breakdown-calculation-for-discounted-pay
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela
My role for this ticket: tester-only

### Why this ticket was included
commented on by me

### Description
### The Problem

The Transaction Details cost breakdown shows incorrect values for discounted Pay Link transactions. The Subtotal does not reflect the full item cost before discount, and the Discount line item does not show the correct deducted amount.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T11:55:11.525Z
## Environment

STAGING

## Tested By

Mark

## Test Scope

Validation of Transaction Details cost breakdown values for freshly-created discounted Pay Link transactions.

## Result

PASSED

## Note

The issue has been verified working in STAGING using a freshly-created discounted Pay Link transaction. The Transaction Details modal now shows the correct Subtotal, Discount, and Total Charge values, while the previously cited transaction `T-26-2c8b-9774` may still show stale values because it was created before the upstream fix was available.

#### josh.tating@ngnair.com - 2026-05-14T11:35:20.698Z
Ready for verification on staging with docker tag `docker.io/blee900/finance-backend:8feafec`; details include resolver behavior and validation steps.

### Activity Timeline
- 2026-05-14T11:55:11.525Z commented

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T11:55:11.525Z commented

### Activity Notes
Tested and documented a passing staging verification in comment form.

## NGN-624: Marketplace: Replace duplicate category slug Prisma error with user-friendly toast

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-624/marketplace-replace-duplicate-category-slug-prisma-error-with-user
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela
My role for this ticket: tester-only

### Why this ticket was included
Created by me; commented on by me

### Description
### The Problem

Creating a Marketplace category with an existing slug shows a raw Prisma unique constraint error instead of a readable validation message.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T05:20:32.390Z
Verified in STAGING that duplicate slug now shows a readable validation message instead of raw Prisma error. Result: PASSED.

### Activity Timeline
- 2026-05-14T04:18:43.923Z created
- 2026-05-14T05:20:32.390Z commented

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T04:18:43.923Z created; 2026-05-14T05:20:32.390Z commented

### Activity Notes
Created the ticket and added explicit staging test verification.

## NGN-628: Marketplace: Fix App Installs GraphQL errors for environment and permissions

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-628/marketplace-fix-app-installs-graphql-errors-for-environment-and
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela
My role for this ticket: tester-only

### Why this ticket was included
Created by me; commented on by me

### Description
### The Problem

Accessing App Installs in the Marketplace Admin Portal fails with GraphQL errors including null non-nullable environment and insufficient permissions.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T08:39:05.379Z
Verified in STAGING that App Installs now loads for Mark Goldman without the prior GraphQL errors. Result: PASSED.

### Activity Timeline
- 2026-05-14T05:58:18.523Z created
- 2026-05-14T08:39:05.379Z commented

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T05:58:18.523Z created; 2026-05-14T08:39:05.379Z commented

### Activity Notes
Created the ticket and recorded successful staging verification.

## NGN-630: Marketplace: Refetch service providers list after provider creation

Status: Pending Review
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-630/marketplace-refetch-service-providers-list-after-provider-creation
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

After creating a Service Provider in the Marketplace Admin Portal, the newly created provider does not appear in the Services list until the page is manually refreshed.

### Comments
No comments found.

### Activity Timeline
- 2026-05-14T09:55:51.593Z created

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T09:55:51.593Z created

### Activity Notes
Created the issue with reproducible problem statement and expected behavior.

## NGN-631: Customer: Allow clipboard copy from Customer Contacts email field

Status: Pending Review
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-631/customer-allow-clipboard-copy-from-customer-contacts-email-field
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: None identified
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Copying a contact email from the Customer Details modal fails because the Clipboard API is blocked by the current permissions policy.

### Comments
No comments found.

### Activity Timeline
- 2026-05-14T10:55:47.864Z created

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T10:55:47.864Z created

### Activity Notes
Created the issue with explicit reproduction and acceptance criteria.

## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets

Status: Pending Review
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: None identified
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

The Customers table cuts off the last visible entry when there are too many records, and there are no sufficient navigation controls to access the rest.

### Comments
No comments found.

### Activity Timeline
- 2026-05-14T11:07:26.261Z created

### In-Range Day Mapping
- 2026-05-14: 2026-05-14T11:07:26.261Z created

### Activity Notes
Created the issue describing UI truncation and missing navigation behavior.

