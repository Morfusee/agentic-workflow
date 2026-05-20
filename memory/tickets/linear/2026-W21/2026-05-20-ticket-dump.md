# Stand-up Script

Yesterday, I reported a bug in Location Details where banking info is hardcoded — the same Banking Info values appear across different locations instead of reflecting per-location GraphQL data. Right now you can open two different locations and the Banking Info section shows identical, mocked data for both. 

I also wrapped up QA on two customer fixes earlier this week. The updateCustomer fix resolved a BAD_REQUEST error that blocked editing newly created customers — seeded customers could be edited, but fresh ones would silently fail. I tested the full create-then-edit flow on staging, confirmed the backend no longer returns BAD_REQUEST for valid edit data, verified seeded customer edits remained unaffected, and checked that the UI shows the correct success state after saving. All acceptance criteria passed. The Customers table cutoff fix addressed an issue where the last visible entry in the Customers table was getting cut off and there were no navigation controls for locations with large result sets. I tested it as a location super admin at Alpha City Branch — the table now renders all ten seeded rows fully visible, the Rows per Page selector with options for 5, 10, 25, and 50 is functional, pagination works correctly across pages, and the location selector behavior is preserved.

No major blockers right now.

---

# Selected Tickets

- NGN-661: Location: Replace hardcoded banking info with location GraphQL data
  - Status: Pending Review
  - Activity date: 2026-05-20
  - URL: https://linear.app/ngnair/issue/NGN-661/location-replace-hardcoded-banking-info-with-location-graphql-data
  - Reference: `# All Scraped Tickets` -> `## NGN-661: Location: Replace hardcoded banking info with location GraphQL data`
  - Stand-up relevance: Reported bug documenting hardcoded banking info in Location Details with reproduction steps and acceptance criteria

- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets
  - Status: Done
  - Activity date: 2026-05-19
  - URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
  - Reference: `2026-05-19-ticket-dump.md` -> `## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets`
  - Stand-up relevance: QA tested the Customers table fix in staging; PASS result

- NGN-604: Customer: Fix updateCustomer bad request for newly created customers
  - Status: Done
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-604/customer-fix-updatecustomer-bad-request-for-newly-created-customers
  - Reference: `2026-05-18-ticket-dump.md` -> `## NGN-604: Customer: Fix updateCustomer bad request for newly created customers`
  - Stand-up relevance: QA tested the updateCustomer fix on STAGING; PASS result

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
  - Source dump: 2026-05-20
  - Status as of 2026-05-20: Pending Review
  - Role: tester-only
  - Activity notes: Tested CSP fix on staging and reported QA FAIL — CSP wildcard does not match non-default HTTPS port 3011. Resolution blocked on NGN-650.

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

Generated: 2026-05-20T11:20:00 UTC
Requested range: 2026-05-20
Dump file date: 2026-05-20

---

# Grouped Summary

2026-05-20

## Pending Review
- NGN-661: Location: Replace hardcoded banking info with location GraphQL data
- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-661: Location: Replace hardcoded banking info with location GraphQL data

Status: Pending Review
Activity date: 2026-05-20
URL: https://linear.app/ngnair/issue/NGN-661/location-replace-hardcoded-banking-info-with-location-graphql-data
Initial dev assignee: josh.tating@ngnair.com
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

Banking info in the Location Details view is hardcoded/mocked and shows the same values across different locations.

### Steps to Reproduce

1. Log in to Partner FE host app as Sofia Navarro.
2. Navigate to Locations > Locations.
3. Open a location entry from the Locations table.
4. Open a different location entry.
5. Observe that the Banking Info section across both entries are showing the same data.

### Technical Requirements

* Remove hardcoded/mocked banking data from the Location Details view.
* Fetch banking info from the correct location-level GraphQL query/fields.
* Bind the Banking Info UI to the selected location payload and render per-location values.
* Preserve proper empty-state handling when banking data is null/missing.

### Expected vs Actual

* **Expected:** Banking Info reflects real, location-specific data returned by GraphQL for the selected location.
* **Actual:** Banking Info appears identical across different locations, indicating static/hardcoded values.

### Acceptance Criteria

- [ ] Hardcoded/mocked banking values are removed from Location Details.
- [ ] Banking info is sourced from the confirmed GraphQL operation/fields.
- [ ] Different locations display different banking info when underlying data differs.
- [ ] Null/missing banking fields render a valid empty/fallback state (not placeholder hardcoded values).
- [ ] Verified with at least two distinct location records in Locations table.

### Comments
No comments found.

### Activity Timeline
- 2026-05-20T10:56:44 UTC: created by mark.valenzuela@ngnair.com

### In-Range Day Mapping
- 2026-05-20: created by mark.valenzuela (2026-05-20T10:56:44)

### Activity Notes
Created bug report documenting hardcoded banking info in Location Details — same values appear across different locations. Detailed reproduction steps, technical requirements, and acceptance criteria provided.

---

## NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

Status: Pending Review
Activity date: 2026-05-20
URL: https://linear.app/ngnair/issue/NGN-645/finance-allow-location-fe-local-dev-origin-in-csp-frame-ancestors
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Commented on by me

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
#### mark.valenzuela@ngnair.com - 2026-05-20T06:59:09 UTC
### QA Result: `FAIL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Finance-frontend embedding of the local-dev iframe-child origin over HTTPS, and CSP `frame-ancestors` directive handling for non-default ports.

### Test Results
Finance FE cannot be embedded inside `https://ng-location-fe-local-dev.dev1.ngnair.com:3011` because the current `frame-ancestors` CSP allows `https://*.dev1.ngnair.com` but does not explicitly allow the non-default HTTPS port `3011`. The embedding fails until the local-dev host origin with port `3011` is added, or the required dev ports are allowed in the Finance FE CSP configuration.

### Notes
Update Finance FE CSP to include the local-dev `:3011` origin or the approved dev port set. Ensure the change is scoped to dev only — production CSP must remain unchanged.

#### josh.tating@ngnair.com - 2026-05-19T10:04:15 UTC
Resolution path: the iframe-child origin (location-frontend local dev) is being switched to HTTPS via mkcert as part of NGN-650. Once that lands, the deployed finance-frontend CSP wildcard `https://*.dev1.ngnair.com` will match the new `https://ng-location-fe-local-dev.dev1.ngnair.com:3011` origin automatically — no change to the finance-frontend CSP needed. The decision is to keep CSP locked to HTTPS rather than loosening it to allow `http://` dev origins.

Action: leave finance-frontend CSP untouched. Verify and close after NGN-650 ships.

### Activity Timeline
- 2026-05-18T05:37:26 UTC: created by mark.valenzuela@ngnair.com
- 2026-05-19T10:04:15 UTC: commented by josh.tating@ngnair.com (resolution path via NGN-650)
- 2026-05-20T06:59:09 UTC: commented by mark.valenzuela@ngnair.com (QA FAIL result)

### In-Range Day Mapping
- 2026-05-20: commented QA FAIL result by mark.valenzuela (2026-05-20T06:59:09)

### Activity Notes
Tested CSP fix on staging and reported QA FAIL — CSP `frame-ancestors` wildcard `https://*.dev1.ngnair.com` does not match non-default HTTPS port 3011 used by location-fe local dev. Resolution blocked on NGN-650 (HTTPS via mkcert for location-frontend local dev).
