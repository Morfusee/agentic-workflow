# Stand-up Script

Yesterday, I tested the updateCustomer fix for newly created customers in staging and confirmed the create-edit-save flow passed, including seeded customer regression coverage and the UI success state. I also moved the Customers table cutoff work into review and kept working on the table layout and pagination/navigation needed for larger result sets.

No major blockers right now.

---

# Selected Tickets

- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets
  - Status: In Review
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
  - Reference: `2026-05-18-ticket-dump.md` -> `## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets`
  - Stand-up relevance: Moved to In Review while working on the table cutoff fix and pagination/navigation

- NGN-604: Customer: Fix updateCustomer bad request for newly created customers
  - Status: Done
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-604/customer-fix-updatecustomer-bad-request-for-newly-created-customers
  - Reference: `2026-05-18-ticket-dump.md` -> `## NGN-604: Customer: Fix updateCustomer bad request for newly created customers`
  - Stand-up relevance: Tested the fix on STAGING and confirmed the PASS result

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
  - Source dump: 2026-05-20
  - Status as of 2026-05-20: Pending Review
  - Role: tester-only
  - Activity notes: Tested on staging and commented with QA results, reporting a FAIL because the CSP frame-ancestors directive does not allow the non-default HTTPS port.

- NGN-650: Location: Implement HTTPS local dev for location-frontend using mkcert
  - Source dump: 2026-05-19
  - Status as of 2026-05-19: Done
  - Role: contributor
  - Activity notes: Created ticket for mkcert-based HTTPS local dev for location-frontend; implemented by Josh

- NGN-651: Location: Implement HTTPS local dev for location-admin using mkcert
  - Source dump: 2026-05-19
  - Status as of 2026-05-19: Done
  - Role: contributor
  - Activity notes: Created ticket for mkcert-based HTTPS local dev for location-admin; implemented by Josh

---

# Ticket Dump

Generated: 2026-05-20T17:24:48Z
Requested range: 2026-05-20
Dump file date: 2026-05-20

---

# Grouped Summary

2026-05-20

## Pending Review
- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

Status: Pending Review
Activity date: 2026-05-20
URL: https://linear.app/ngnair/issue/NGN-645/finance-allow-location-fe-local-dev-origin-in-csp-frame-ancestors
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
commented on by me

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
#### josh.tating@ngnair.com - 2026-05-19T10:04:15.790Z
Resolution path: the iframe-child origin (location-frontend local dev) is being switched to HTTPS via mkcert as part of NGN-650. Once that lands, the deployed finance-frontend CSP wildcard `https://*.dev1.ngnair.com` will match the new `https://ng-location-fe-local-dev.dev1.ngnair.com:3011` origin automatically — no change to the finance-frontend CSP needed. The decision is to keep CSP locked to HTTPS rather than loosening it to allow `http://` dev origins.

Action: leave finance-frontend CSP untouched. Verify and close after NGN-650 ships.

#### mark.valenzuela@ngnair.com - 2026-05-20T06:59:09.503Z
### QA Result: `FAIL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Finance-frontend embedding of the local-dev iframe-child origin over HTTPS, and CSP `frame-ancestors` directive handling for non-default ports.

### Test Results
Finance FE cannot be embedded inside `https://ng-location-fe-local-dev.dev1.ngnair.com:3011` because the current `frame-ancestors` CSP allows `https://*.dev1.ngnair.com` but does not explicitly allow the non-default HTTPS port `3011`. The embedding fails until the local-dev host origin with port `3011` is added, or the required dev ports are allowed in the Finance FE CSP configuration.

### Notes
Update Finance FE CSP to include the local-dev `:3011` origin or the approved dev port set. Ensure the change is scoped to dev only — production CSP must remain unchanged.

### Activity Timeline
- 2026-05-18T05:37:26.666Z created
- 2026-05-19T10:04:15.790Z commented
- 2026-05-20T06:59:09.503Z commented
- 2026-05-20T07:01:03.429Z updated

### In-Range Day Mapping
- 2026-05-20: commented at 2026-05-20T06:59:09.503Z

### Activity Notes
Tested on staging and commented with QA results, reporting a FAIL because the CSP frame-ancestors directive does not allow the non-default HTTPS port.
