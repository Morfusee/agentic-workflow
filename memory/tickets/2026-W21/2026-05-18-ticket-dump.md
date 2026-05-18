# Stand-up Script

Yesterday, I logged two bug reports. First, I reported that Finance pages are blocked from rendering inside the Location FE host app iframe during local development — the CSP `frame-ancestors` directive doesn't allow the `http` local dev origin. Then I reported that the Marketplace Admin frontend is missing role-based access control, allowing standard users to access pages that should be restricted to Platform Administrators only.

No major blockers right now.

---

# Selected Tickets

- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
  - Status: Pending Review
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-645/finance-allow-location-fe-local-dev-origin-in-csp-frame-ancestors
  - Reference: `# All Scraped Tickets` -> `## NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive`
  - Stand-up relevance: Reported CSP frame-ancestors bug blocking Finance iframe rendering in Location FE local dev

- NGN-648: Marketplace: Restrict Marketplace admin FE access to Platform Administrators only
  - Status: Pending Review
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-648/marketplace-restrict-marketplace-admin-fe-access-to-platform
  - Reference: `# All Scraped Tickets` -> `## NGN-648: Marketplace: Restrict Marketplace admin FE access to Platform Administrators only`
  - Stand-up relevance: Reported missing RBAC on Marketplace Admin FE allowing standard users unauthorized access

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-604: Customer: Fix updateCustomer bad request for newly created customers
  - Source dump: 2026-05-18
  - Status as of 2026-05-18: Done
  - Role: dev-owner
  - Activity notes: Implemented fix, QA'd on STAGING, moved to Done
- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets
  - Source dump: 2026-05-18
  - Status as of 2026-05-18: In Review
  - Role: dev-owner
  - Activity notes: Moved to In Review, working on table cutoff fix and pagination
- NGN-647: Support: Restrict Support Admin FE access to Platform Administrators only
  - Source dump: 2026-05-18
  - Status as of 2026-05-18: Pending Review
  - Role: tester-only
  - Activity notes: Reported missing RBAC on Support Admin FE
- NGN-649: Partner: Restrict Partner admin FE access to Platform Administrators only
  - Source dump: 2026-05-18
  - Status as of 2026-05-18: Pending Review
  - Role: tester-only
  - Activity notes: Reported missing RBAC on Partner FE host app

---

# Ticket Dump

Generated: 2026-05-18T20:37:45+08:00
Requested range: 2026-05-18
Dump file date: 2026-05-18

---

# Grouped Summary

2026-05-18

## Done
- NGN-604: Customer: Fix updateCustomer bad request for newly created customers

## In Review
- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets

## Pending Review
- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
- NGN-647: Support: Restrict Support Admin FE access to Platform Administrators only
- NGN-648: Marketplace: Restrict Marketplace admin FE access to Platform Administrators only
- NGN-649: Partner: Restrict Partner admin FE access to Platform Administrators only

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-604: Customer: Fix updateCustomer bad request for newly created customers

Status: Done
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-604/customer-fix-updatecustomer-bad-request-for-newly-created-customers
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: dev-owner

### Why this ticket was included
commented by me, moved to Done by me

### Description
### The Problem

Newly added customers cannot be edited after creation. Saving changes does nothing in the UI and the `updateCustomer` request returns a Bad Request Exception. Seeded customers can still be edited successfully.

### Steps to Reproduce

 1. Log in to Location FE.
 2. Go to **Customers > Customers**.
 3. Click **Add Customer**.
 4. Fill out the customer information and click **Add Customer**.
 5. Confirm the new customer appears in the customer list.
 6. Open the new customer's detail page.
 7. Click **Edit**.
 8. Change any customer value and click **Save**.
 9. Observe that the UI does not update or show a successful save state.
10. Open the console and observe the update failure.

### Technical Context

Console error:

```
Failed to update customer: ApolloError: Bad Request Exception
```

Backend response:

```
{
  "errors": [
    {
      "message": "Bad Request Exception",
      "code": "BAD_REQUEST",
      "path": ["updateCustomer"]
    }
  ],
  "data": null
}
```

### Expected vs Actual

* **Expected:** Newly created customers can be edited and saved the same way seeded customers can.
* **Actual:** Editing a newly created customer fails with a `BAD_REQUEST` error on `updateCustomer`, and no change is saved.

### Acceptance Criteria

* Newly created customers can be edited successfully after creation.
* `updateCustomer` no longer returns `BAD_REQUEST` for newly created customers with valid edit data.
* Seeded customer edit behavior remains unchanged.
* The UI shows the correct success or error state after saving customer edits.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-18T09:14:59.386Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Verified the updateCustomer fix for newly created customers on STAGING, covering the create-then-edit flow, backend error handling, seeded customer regression, and UI save state feedback.

### Test Results
All acceptance criteria verified successfully. Newly created customers can be edited after creation, updateCustomer no longer returns BAD_REQUEST for valid edit data, seeded customer edits remain unchanged, and the UI shows correct success state after saving.

### Activity Timeline
- 2026-05-12T13:39:20.024Z created
- 2026-05-13T08:02:44.226Z moved to In Progress
- 2026-05-18T09:14:59.386Z commented on ticket
- 2026-05-18T09:19:42.552Z moved to Done

### In-Range Day Mapping
- 2026-05-18: commented QA PASS (2026-05-18T09:14:59.386Z), moved to Done (2026-05-18T09:19:42.552Z)

### Activity Notes
Implemented the fix for updateCustomer bad request on newly created customers. Tested the fix on STAGING across the create-then-edit flow, backend error handling, seeded customer regression, and UI save state feedback. All acceptance criteria passed. Moved ticket to Done.

---

## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets

Status: In Review
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: None identified
My role for this ticket: dev-owner

### Why this ticket was included
created by me, moved to In Review by me

### Description
### The Problem

The **Customers > Customers** table cuts off the last visible entry when there are too many records, and there are no sufficient navigation controls to access the rest of the customer list.

### Steps to Reproduce

1. Log in to the Location FE Host app as Sofia Navarro.
2. Go to **Customers > Customers**.
3. Select **Alpha City Branch** in the location selector.
4. Observe the Customers table when there are many customer records.
5. Observe that the last visible entry is cut off.
6. Observe that there are no sufficient pagination or navigation controls to access the remaining customer records.

### Technical Requirements

* Fix the Customers table layout so entries are fully visible and not cut off.
* Provide a way to access additional customer records when the list exceeds the visible table area.
* Add or restore pagination controls for the Customers table where needed.
* Preserve the existing location selector and table behavior.
* Ensure the Customers table remains usable for locations with large result sets.

### Expected vs Actual

* **Expected:** The Customers table displays entries without cutting off content and provides a way to navigate through larger result sets.
* **Actual:** The Customers table cuts off the last visible entry, and users cannot reliably access the remaining records.

### Acceptance Criteria

* Customers table entries are fully visible and not cut off.
* Users can access all Customers results when the list exceeds the visible table area.
* Pagination or sufficient navigation controls are available for large customer result sets.
* Existing location selector and Customers table behavior remain unchanged.

### Comments
No comments found.

### Activity Timeline
- 2026-05-14T11:07:26.261Z created
- 2026-05-18T08:01:11.947Z moved to In Review

### In-Range Day Mapping
- 2026-05-18: moved to In Review (2026-05-18T08:01:11.947Z)

### Activity Notes
Moved ticket to In Review. Working on fixing the Customers table cutoff and adding pagination/navigation for large result sets.

---

## NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

Status: Pending Review
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-645/finance-allow-location-fe-local-dev-origin-in-csp-frame-ancestors
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Finance pages (`ng-finance-fe-dev.dev1.ngnair.com`) are blocked from rendering inside the Location FE host app iframe during local development. The Finance app's CSP `frame-ancestors` directive restricts embedding to `'self'`, `https://*.dev1.ngnair.com`, and `https://uat.hpp.converge.eu.elavonaws.com`. The Location FE local dev origin (`http://ng-location-fe-local-dev.dev1.ngnair.com:3011`) is not in the allowed list, and the wildcard `https://*.dev1.ngnair.com` does not match `http` origins.

### Steps to Reproduce

1. Run Location FE host app locally (`http://ng-location-fe-local-dev.dev1.ngnair.com:3011`)
2. Log in (e.g., as Sofia Navarro)
3. Navigate to Finance pages: Reporting, Manage > Payments, Manage > Integrations
4. Observe iframe shows "refused to connect" — console logs:

   ```
   Framing 'https://ng-finance-fe-dev.dev1.ngnair.com/' violates Content Security Policy
   directive: "frame-ancestors 'self' https://*.dev1.ngnair.com https://uat.hpp.converge.eu.elavonaws.com"
   ```

### Technical Requirements

* Add `http://ng-location-fe-local-dev.dev1.ngnair.com:3011` to the `frame-ancestors` CSP directive in Finance FE dev environment
* Scope the change to dev environment only — production CSP must not be affected
* Consider also allowing `http://*.dev1.ngnair.com:*` to cover all local dev ports and subdomains over HTTP in dev only

### Expected vs Actual

* **Expected:** Finance pages render inside the Location FE host app iframe during local development
* **Actual:** Finance pages are blocked by CSP `frame-ancestors` — the wildcard `https://*.dev1.ngnair.com` does not match `http` origins and does not include the specific dev subdomain

### Acceptance Criteria

- [ ] Finance pages render in the Location FE host app iframe when running locally at `http://ng-location-fe-local-dev.dev1.ngnair.com:3011`
- [ ] No CSP `frame-ancestors` violations appear in the browser console
- [ ] Production CSP is unchanged and unaffected

### Comments
No comments found.

### Activity Timeline
- 2026-05-18T05:37:26.666Z created

### In-Range Day Mapping
- 2026-05-18: created

### Activity Notes
Created bug report for Finance CSP frame-ancestors blocking Location FE local dev origin.

---

## NGN-647: Support: Restrict Support Admin FE access to Platform Administrators only

Status: Pending Review
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-647/support-restrict-support-admin-fe-access-to-platform-administrators
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

The Support Admin frontend allows Standard Users (non-platform admins) to access the page directly via URL, when it should only be accessible to Platform Administrators.

### Steps to Reproduce

1. Navigate to [https://ng-support-admin-dev.dev1.ngnair.com/](<https://ng-support-admin-dev.dev1.ngnair.com/>)
2. Log in as a Standard User (e.g., Sofia Navarro, Ivan Petrov, or Blake Tanaka)
3. Observe that the user is redirected to and can access the Support Micro Frontend

### Technical Requirements

* Implement role-based access control on the Support Admin FE route, matching the existing pattern used by the Location Admin FE
* Restrict access to users with the "Platform Administrator" role only
* Show an "Access Denied" page for unauthorized users (consistent with Location Admin FE behavior)

### Expected vs Actual

* **Expected:** Only Platform Administrators can access the Support Admin page; all other users see an "Access Denied" page (same behavior as Location Admin FE)
* **Actual:** Any authenticated user, regardless of role, can access the page

### Acceptance Criteria

- [ ] Mark Goldman (Platform Administrator) can access the Support Admin page
- [ ] Sofia Navarro, Ivan Petrov, and Blake Tanaka (Standard Users) see an "Access Denied" page
- [ ] Behavior matches the existing Location Admin FE access control pattern

### Comments
No comments found.

### Activity Timeline
- 2026-05-18T07:09:35.260Z created

### In-Range Day Mapping
- 2026-05-18: created

### Activity Notes
Created bug report for Support Admin FE missing role-based access control for Platform Administrators.

---

## NGN-648: Marketplace: Restrict Marketplace admin FE access to Platform Administrators only

Status: Pending Review
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-648/marketplace-restrict-marketplace-admin-fe-access-to-platform
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Standard users (non-platform admins such as Sofia Navarro, Ivan Petrov, Blake Tanaka) can access the Marketplace Admin page by navigating directly to the URL. Only Platform Administrators (Mark Goldman) should be granted access.

### Steps to Reproduce

1. Navigate to `https://ng-marketplace-admin-dev.dev1.ngnair.com`
2. Log in as any user other than Mark Goldman (e.g., Sofia Navarro, Ivan Petrov, Blake Tanaka)
3. Observe that the user is not blocked and can access the Marketplace Micro Frontend

### Technical Requirements

* Implement role-based access control on the Marketplace Admin FE route, matching the existing pattern used by the Location FE admin
* Restrict access to users with the "Platform Administrator" role only
* Show an "Access Denied" page for unauthorized users (consistent with Location FE admin behavior)

### Expected vs Actual

* **Expected:** Only Platform Administrators can access the Marketplace Admin page; all other users see an "Access Denied" page (same behavior as Location FE admin)
* **Actual:** Any authenticated user, regardless of role, can access the page

### Acceptance Criteria

- [ ] Mark Goldman (Platform Administrator) can access the Marketplace Admin page
- [ ] Sofia Navarro, Ivan Petrov, and Blake Tanaka (Standard Users) see an "Access Denied" page
- [ ] Behavior matches the existing Location FE admin access control pattern

### Comments
No comments found.

### Activity Timeline
- 2026-05-18T07:09:52.095Z created

### In-Range Day Mapping
- 2026-05-18: created

### Activity Notes
Created bug report for Marketplace Admin FE missing role-based access control for Platform Administrators.

---

## NGN-649: Partner: Restrict Partner admin FE access to Platform Administrators only

Status: Pending Review
Activity date: 2026-05-18
URL: https://linear.app/ngnair/issue/NGN-649/partner-restrict-partner-admin-fe-access-to-platform-administrators
Initial dev assignee: Duane Enriquez
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Created by me

### Description
### The Problem

Standard users (non-platform admins such as Sofia Navarro, Ivan Petrov, Blake Tanaka) can access the Partner Admin page by navigating directly to the URL. Only Platform Administrators (Mark Goldman) should be granted access.

### Steps to Reproduce

1. Navigate to `https://ng-partner-admin-dev.dev1.ngnair.com`
2. Log in as any user other than Mark Goldman (e.g., Sofia Navarro, Ivan Petrov, Blake Tanaka)
3. Observe that the user is not blocked and can access the Partner FE host app

### Technical Requirements

* Implement role-based access control on the Partner FE host app route, matching the existing pattern used by the Location FE admin
* Restrict access to users with the "Platform Administrator" role only
* Show an "Access Denied" page for unauthorized users (consistent with Location FE admin behavior)

### Expected vs Actual

* **Expected:** Only Platform Administrators can access the Partner FE host app; all other users see an "Access Denied" page (same behavior as Location FE admin)
* **Actual:** Any authenticated user, regardless of role, can access the page

### Acceptance Criteria

- [ ] Mark Goldman (Platform Administrator) can access the Partner FE host app
- [ ] Sofia Navarro, Ivan Petrov, and Blake Tanaka (Standard Users) see an "Access Denied" page
- [ ] Behavior matches the existing Location FE admin access control pattern

### Comments
No comments found.

### Activity Timeline
- 2026-05-18T07:39:08.523Z created

### In-Range Day Mapping
- 2026-05-18: created

### Activity Notes
Created bug report for Partner FE host app missing role-based access control for Platform Administrators.
