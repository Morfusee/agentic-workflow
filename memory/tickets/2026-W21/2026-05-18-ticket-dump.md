# Ticket Dump

Generated: 2026-05-18T15:59:00+08:00
Requested range: 2026-05-18
Dump file date: 2026-05-18

---

# Grouped Summary

2026-05-18

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
