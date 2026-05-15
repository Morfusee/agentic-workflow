# Stand-up Script

Yesterday, I created a ticket to address the duplicate Marketplace category slug error showing a raw Prisma constraint message. I then tested the category creation flow in STAGING, and it is now fixed with a readable user-facing validation message.

I also created a ticket for the App Installs issue in Marketplace Admin where `AppInstall.environment` null and `Insufficient permissions` GraphQL errors were blocking the page. I tested the App Installs load flow in STAGING, and it is now fixed and loads successfully without those errors.

For the Location Details modal issue, the starting point was a direction to remove Business Description due to overlap into the Banking/Other Linked Accounts panel. The fix was deployed for verification, and I tested in STAGING: Business Description is no longer rendered, the remaining fields still render correctly, and the right-side panel is no longer overlapped, so this is fixed.

For the Checkout Payment Complete issue, the starting point was item prices showing `$0`. After implementation and staging deployment notes, I tested a completed Pay Link checkout in STAGING, and this is now fixed with correct item-level prices and totals consistent with receipt items.

For the discounted Pay Link cost breakdown issue, the starting point in this flow was prior inconsistency, including earlier failed validation and follow-up requests for deeper reproduction. After engineering verification notes and a latest staging deployment check, I tested a freshly created discounted Pay Link transaction in STAGING: Subtotal, Discount, and Total Charge values are now correct, while the older cited transaction may still reflect stale pre-fix data, and the issue is fixed for fresh post-fix transactions.

No major blockers right now.

---
# Selected Tickets

## NGN-624: Marketplace: Replace duplicate category slug Prisma error with user-friendly toast

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-624/marketplace-replace-duplicate-category-slug-prisma-error-with-user

### Stand-up relevance
I created this ticket and drove same-day test validation to closure.

### High-level overview
This ticket fixed a rough UX case in Marketplace Categories where duplicate slugs surfaced raw backend errors. The work made validation feedback readable for admins.

### Activity flow
1. I created the ticket to capture the duplicate-slug error behavior.
2. I tested the fix in STAGING against the category creation flow.
3. I posted the PASSED test result with scope and notes.

### Description
Creating a Marketplace category with an existing slug shows a raw Prisma unique constraint error instead of a readable validation message.

### Comments
2026-05-14T05:20:32.390Z — Tested in STAGING by Mark. Result: PASSED.

## NGN-628: Marketplace: Fix App Installs GraphQL errors for environment and permissions

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-628/marketplace-fix-app-installs-graphql-errors-for-environment-and

### Stand-up relevance
I created this ticket and verified the final behavior directly in staging.

### High-level overview
This ticket addressed a broken App Installs experience in Marketplace Admin caused by GraphQL errors. The result is that admins can now load App Installs without the prior environment/permission failures.

### Activity flow
1. I created the ticket with the observed GraphQL errors and failing page behavior.
2. I tested the fix in STAGING for the App Installs load flow.
3. I posted the PASSED validation result and closeout note.

### Description
Accessing App Installs in the Marketplace Admin Portal failed with frontend and GraphQL errors from `adminListAppInstalls`.

### Comments
2026-05-14T08:39:05.379Z — Tested in STAGING by Mark. Result: PASSED.

## NGN-625: Location: Remove Business Description from Location Details modal

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-625/location-remove-business-description-from-location-details-modal

### Stand-up relevance
I had multiple same-day actions on this ticket, including requirement direction and final test validation.

### High-level overview
This ticket cleaned up Location Details modal presentation by removing a field that caused layout overlap. It reduced UI clutter and resolved panel collision in the modal.

### Activity flow
1. I added a direction comment to remove the Business Description field from the modal.
2. The fix was deployed and verification instructions were posted.
3. I tested in STAGING and posted a PASSED result confirming the overlap was resolved.

### Description
The Business Description field in `LocationDetailsModal` could overflow into the Banking / Other Linked Accounts panel.

### Comments
2026-05-14T05:56:51.744Z — I requested removal of Business Description.
2026-05-14T09:56:40.228Z — I tested in STAGING. Result: PASSED.

## NGN-562: Fix Transaction Details cost breakdown calculation for discounted Pay Links

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-562/fix-transaction-details-cost-breakdown-calculation-for-discounted-pay

### Stand-up relevance
I re-tested this ticket in-range and documented the final pass state after earlier inconsistency reports.

### High-level overview
This ticket focused on getting discounted Pay Link transaction breakdown values accurate in Transaction Details. The important part of the flow was validating behavior on fresh transactions after prior mixed results.

### Activity flow
1. Earlier testing history showed inconsistent outcomes and prompted deeper retest requests.
2. Follow-up verification notes were posted by engineering with updated deployment context.
3. I re-tested in STAGING on a fresh discounted transaction and posted a PASSED result.

### Description
Transaction Details cost breakdown values for discounted Pay Link transactions were inconsistent for Subtotal, Discount, and Total Charge.

### Comments
2026-05-14T11:55:11.525Z — I tested in STAGING by Mark. Result: PASSED.

## NGN-589: Fix item price display on the Checkout Payment Complete page

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-589/fix-item-price-display-on-the-checkout-payment-complete-page

### Stand-up relevance
I validated the fix after deployment and closed the testing loop with a clear same-day result.

### High-level overview
This ticket fixed an end-user receipt issue where Payment Complete displayed item prices as zero. The final validation confirmed correct item-level values and consistent totals.

### Activity flow
1. The implementation and deploy notes were posted with fallback logic details.
2. I ran staging verification on completed Pay Link checkout.
3. I posted a PASSED result confirming item price and total display behavior.

### Description
Payment Complete page displayed item prices as $0 instead of each item's actual value.

### Comments
2026-05-14T11:44:04.813Z — I tested in STAGING by Mark. Result: PASSED.

---
# All Scraped Tickets

## NGN-624: Marketplace: Replace duplicate category slug Prisma error with user-friendly toast

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-624/marketplace-replace-duplicate-category-slug-prisma-error-with-user

### Why this ticket was included
created_by_me_in_range / commented_by_me

### Description
### The Problem

Creating a Marketplace category with an existing slug shows a raw Prisma unique constraint error instead of a readable validation message.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T05:20:32.390Z
## Environment

STAGING

## Tested By

Mark

## Test Scope

Validation of duplicate Marketplace category slug handling and user-facing error messaging in the Marketplace Admin Portal.

## Note

The issue has been fixed and verified in STAGING. Creating a Marketplace category with an existing slug now shows a readable validation message instead of exposing the raw Prisma unique constraint error.

## Result

PASSED

## 

### Activity Timeline
- 2026-05-14T04:18:43.923Z created
- 2026-05-14T05:20:32.390Z commented
- 2026-05-14T05:20:32.390Z tested

### Activity Notes
I created this ticket on 2026-05-14, then I tested it in STAGING and posted test results on the same day.

## NGN-628: Marketplace: Fix App Installs GraphQL errors for environment and permissions

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-628/marketplace-fix-app-installs-graphql-errors-for-environment-and

### Why this ticket was included
created_by_me_in_range / commented_by_me

### Description
### The Problem

Accessing **App Installs** in the Marketplace Admin Portal fails with frontend and GraphQL errors from `adminListAppInstalls`.

The page shows:

```
Failed to load app installs: Cannot return null for non-nullable field AppInstall.environment.
```

GraphQL also returns:

```
Cannot return null for non-nullable field AppInstall.environment.
```

```
Insufficient permissions
```

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T08:39:05.379Z
## Environment

STAGING

## Tested By

Mark

## Test Scope

Validation of Marketplace Admin Portal App Installs loading behavior, `adminListAppInstalls`

## Note

The issue has been fixed and verified in STAGING. App Installs now loads successfully for Mark Goldman without the `AppInstall.environment` null error or the `Insufficient permissions` GraphQL error.

## Result

PASSED

### Activity Timeline
- 2026-05-14T05:58:18.523Z created
- 2026-05-14T08:39:05.379Z commented
- 2026-05-14T08:39:05.379Z tested

### Activity Notes
I created this ticket on 2026-05-14, then I tested it in STAGING and posted test results on the same day.

## NGN-625: Location: Remove Business Description from Location Details modal

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-625/location-remove-business-description-from-location-details-modal

### Why this ticket was included
commented_by_me / tested_by_me

### Description
### The Problem

The **Business Description** field in `LocationDetailsModal` can display long unbroken text that overflows into the right-side **Banking / Other Linked Accounts** panel.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-14T05:56:51.744Z
As requested by sir Brandon, we should now remove the Business Description on the Location Details Modal

#### josh.tating@ngnair.com - 2026-05-14T09:46:04.395Z
@josh.tating Ready for verification — fix deployed to staging.

**Docker tag:** `docker.io/blee900/location-frontend:5a7b39f`

**Summary:**
The Business Description row has been removed from `LocationDetailsModal`. The right-side Banking / Other Linked Accounts panel can no longer be overlapped by long unbroken Business Description values, since the field is no longer rendered.

**Verify on staging:**
1. Sign in to https://ng-location-fe-dev.dev1.ngnair.com/locations
2. Open any location's Location Details modal.
3. Confirm Business Description is no longer rendered.
4. Confirm the remaining fields (Business Name (DBA), Legal Name, Entity Type, Email, Phone, Website, Country, Address, MCC) still render unchanged.
5. Confirm the right-side Banking / Other Linked Accounts panel is no longer overlapped.

No backend or data-model changes; `businessDescription` remains in the GraphQL fragment since it is still consumed by the onboarding `TransactionProcessingForm`.

#### mark.valenzuela@ngnair.com - 2026-05-14T09:56:40.228Z
## Environment

STAGING

## Tested By

Mark

## Test Scope

Validation that Business Description is removed from `LocationDetailsModal` and no longer overlaps the Banking / Other Linked Accounts panel.

## Note

The issue has been fixed and verified in STAGING. Business Description is no longer rendered in the Location Details modal, the remaining location detail fields still display correctly, and the right-side Banking / Other Linked Accounts panel is no longer overlapped.

## Result

PASSED

### Activity Timeline
- 2026-05-14T05:56:51.744Z commented
- 2026-05-14T09:56:40.228Z commented
- 2026-05-14T09:56:40.228Z tested

### Activity Notes
I posted two separate same-day actions on this ticket: an implementation-direction comment and a later STAGING test result.

## NGN-562: Fix Transaction Details cost breakdown calculation for discounted Pay Links

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-562/fix-transaction-details-cost-breakdown-calculation-for-discounted-pay

### Why this ticket was included
commented_by_me / tested_by_me

### Description
### The Problem

The Transaction Details cost breakdown shows incorrect values for discounted Pay Link transactions. The Subtotal does not reflect the full item cost before discount, and the Discount line item does not show the correct deducted amount.

### Comments
#### josh.tating@ngnair.com - 2026-05-09T12:20:56.103Z
## Deployed to Staging

**Backend:** Added `subtotalAmount`, `discountAmount`, and `taxAmount` fields to the Transaction GraphQL type, resolved from the associated CheckoutSession model.

**Frontend:** Updated the Transaction Details cost breakdown to use real values from the backend instead of hardcoded `$0.00` for discount and using the total as subtotal.

**Docker tags:**
- `docker.io/blee900/finance-backend:8102141`
- `docker.io/blee900/finance-frontend:938ed32`

### Verification
1. Open Reporting -> Transactions
2. Find transaction `T-26-2c8b-9774` (or any discounted Pay Link transaction)
3. Open the transaction details
4. Verify Subtotal shows the pre-discount amount, Discount shows the actual deduction, and Total = Subtotal - Discount + Tax

#### mark.valenzuela@ngnair.com - 2026-05-11T08:31:45.000Z
### Environment:

STAGING

### Tested By:

Mark

### Test Scope:

Validation of Transaction Details cost breakdown values for discounted Pay Link transactions.

### Note:

The issue is still reproducible in STAGING. The Discount line item now shows the actual discount value, but Total Charge does not consistently reflect the deducted amount; some discounted transactions calculate correctly, while others still show an undeducted total despite having the correct discount line item.

### Result:

FAILED

### Additional Context:

Transaction with correct Total Charge and one with incorrect Total Charge were attached.

#### josh.tating@ngnair.com - 2026-05-14T09:53:13.929Z
I am unable to reproduce the problem, can you test more intensively and give better steps to reproduce @mark.valenzuela

#### josh.tating@ngnair.com - 2026-05-14T11:06:55.677Z
## Status: already fixed on develop / staging

Verified `TransactionRepository` relations and resolver fields are already returning populated values from checkout session.

#### josh.tating@ngnair.com - 2026-05-14T11:35:20.698Z
@mark.valenzuela Ready for verification — verified on staging in the latest deployment.

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

### Activity Timeline
- 2026-05-14T11:55:11.525Z commented
- 2026-05-14T11:55:11.525Z tested

### Activity Notes
I tested this ticket in STAGING and posted detailed results in-range.

## NGN-589: Fix item price display on the Checkout Payment Complete page

Status: Done
Activity date: 2026-05-14
URL: https://linear.app/ngnair/issue/NGN-589/fix-item-price-display-on-the-checkout-payment-complete-page

### Why this ticket was included
commented_by_me / tested_by_me

### Description
### The Problem

After completing a Pay Link checkout, the Payment Complete page displays each item price as **$0** instead of the item's actual cost/value.

### Comments
#### josh.tating@ngnair.com - 2026-05-14T11:10:15.985Z
Fix implemented on branch `issue/NGN-587` (combined with NGN-587, shipped together), including fallback item total logic in checkout success render.

#### josh.tating@ngnair.com - 2026-05-14T11:35:05.139Z
@mark.valenzuela Ready for verification — fix deployed to staging with Docker tag `docker.io/blee900/finance-frontend:9050ef7`.

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

The issue has been fixed and verified in STAGING. Completed Pay Link checkouts now show the correct item-level prices on the Payment Complete page instead of defaulting to $0, and the displayed total remains consistent with the receipt items.

### Activity Timeline
- 2026-05-14T11:44:04.813Z commented
- 2026-05-14T11:44:04.813Z tested

### Activity Notes
I tested this ticket in STAGING and posted test results in-range.



