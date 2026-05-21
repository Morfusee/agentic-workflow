# Ticket Dump

# Stand-up Script

Yesterday, we wrapped up the HTTPS local dev setup for the location frontend and location admin apps this week. Both were still running over plain HTTP in local development, which meant any time the dev server needed to talk to HTTPS backend services or authenticate across origins, developers had to resort to Chrome flags or other workarounds just to get past browser security restrictions.

The fix follows the same pattern marketplace-frontend already uses — `mkcert` to generate trusted local certificates paired with `next dev --experimental-https`. The key constraint was that the CSP configuration in our downstream services had to account for the resulting HTTPS origins on non-default ports, which is where the bulk of the compatibility work happened. Everything is now in place and developers can run both apps locally over HTTPS without special browser flags.

No major blockers right now.

---

Generated: 2026-05-21T14:00:00.000Z
Requested range: 2026-05-21 (today)
Dump file date: 2026-05-21

---

# Grouped Summary

2026-05-21

## Done
- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

---

# Selected Tickets

- NGN-650: Location: Implement HTTPS local dev for location-frontend using mkcert
  - Status: Done
  - Activity date: 2026-05-19
  - URL: https://linear.app/ngnair/issue/NGN-650/location-implement-https-local-dev-for-location-frontend-using-mkcert
  - Reference: `2026-05-19-ticket-dump.md` -> `## NGN-650: Location: Implement HTTPS local dev for location-frontend using mkcert`
  - Stand-up relevance: Carry-over ticket; created ticket for mkcert-based HTTPS local dev for location-frontend

- NGN-651: Location: Implement HTTPS local dev for location-admin using mkcert
  - Status: Done
  - Activity date: 2026-05-19
  - URL: https://linear.app/ngnair/issue/NGN-651/location-implement-https-local-dev-for-location-admin-using-mkcert
  - Reference: `2026-05-19-ticket-dump.md` -> `## NGN-651: Location: Implement HTTPS local dev for location-admin using mkcert`
  - Stand-up relevance: Carry-over ticket; created ticket for mkcert-based HTTPS local dev for location-admin

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: Done
  - Role: tester-only
  - Activity notes: Tested CSP frame-ancestors fix on develop and staging; confirmed port-wildcard pattern present; reported QA PASS.

- MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: In Progress
  - Role: dev-owner
  - Activity notes: Started creating a simple draft of feasibility for migrating tables in the location-fe to use data-table blocks from a recent project.

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks

Status: In Progress
Activity date: 2026-05-21
My role: dev-owner

### Description
Started creating a simple draft of feasibility for migrating tables in the location-fe to use data-table blocks from a recent project.

### Activity Notes
Started creating a simple draft of feasibility for migrating tables in the location-fe to use data-table blocks from a recent project.

---

# All Scraped Tickets

## NGN-645: Finance: Allow Location FE local dev origin in CSP frame-ancestors directive

Status: Done
Activity date: 2026-05-21
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

#### josh.tating@ngnair.com - 2026-05-20T11:43:39.125Z
Implemented on `issue/NGN-645`.

Confirmed Mark's QA finding: the deployed `frame-ancestors` value `https://*.dev1.ngnair.com` does not match non-default ports per the CSP spec, so even after NGN-650 ships HTTPS at port `:3011` the host-app embedding still fails. Fix is to use a port-wildcard pattern (`:*`).

### Change

- `src/proxy.ts`
  - `ALLOWED_IFRAME_ORIGINS` fallback updated to use the HTTPS port-wildcard pattern (`https://*.dev1.ngnair.com:*`).
  - Removed the duplicate `ELAVON_HPF` constant — `HPF_HOST` (sourced from `EPG_HPF_HOST` env var) is now used directly in `frame-ancestors` and `frame-src`.
  - Promoted the hardcoded Worldpay cert host to a `WORLDPAY_HOST` env var (fallback to the current cert URL), matching the existing `EPG_HPF_HOST` pattern so the value can switch per environment.
- `.env`
  - Updated `ALLOWED_IFRAME_ORIGINS=https://*.dev1.ngnair.com` → `ALLOWED_IFRAME_ORIGINS=https://*.dev1.ngnair.com:*`.

### Deploy-side change required

The CapRover env var `ALLOWED_IFRAME_ORIGINS` for the finance-frontend app needs the same update on staging: change from `https://*.dev1.ngnair.com` to `https://*.dev1.ngnair.com:*`. Without that, the deployed CSP keeps the no-port wildcard and continues to block the Location FE local-dev origin at `:3011`.

### Verification

- Built finance-frontend cleanly (no TS / build errors).
- Started the dev server locally and inspected the response `Content-Security-Policy` header. Confirmed the emitted `frame-ancestors` directive is now:

  ```
  frame-ancestors 'self' https://*.dev1.ngnair.com:* https://uat.hpp.converge.eu.elavonaws.com
  ```

  i.e. the port wildcard `:*` is present.
- Confirmed the rest of the CSP (`frame-src`, `connect-src`, `script-src`) still includes the Elavon UAT host (now via `HPF_HOST`) and the Worldpay cert host (now via `WORLDPAY_HOST`).
- Local screenshot captured of the finance-frontend home rendering under the new CSP.

End-to-end verification of the iframe scenario depends on NGN-650 (HTTPS for Location FE local dev) — once that ships and the CapRover env var is updated, Mark's QA scenario should pass.

Branch: `issue/NGN-645` (finance-frontend repo).

#### josh.tating@ngnair.com - 2026-05-20T11:51:51.746Z
@mark.valenzuela Ready for verification — deployed to staging.

### Docker tag
`docker.io/blee900/finance-frontend:04a50ab`

### CapRover env var update applied
- `ALLOWED_IFRAME_ORIGINS`: `https://*.dev1.ngnair.com` → `https://*.dev1.ngnair.com:*`

The trailing `:*` is the actual fix — CSP hostname wildcards do not match non-default ports per the CSP spec, so the previous value silently blocked the Location FE local-dev origin at `:3011` even after the HTTPS migration (NGN-650) lands.

### Verified on staging

Curl against `https://ng-finance-fe-dev.dev1.ngnair.com/` returns:

```
content-security-policy: ...; frame-ancestors 'self' https://*.dev1.ngnair.com:* https://uat.hpp.converge.eu.elavonaws.com; ...
```

i.e. the port wildcard `:*` is now present on the deployed CSP.

### How to verify

1. Fetch the CSP header from staging and confirm `frame-ancestors` includes `https://*.dev1.ngnair.com:*` (with the trailing `:*`):

   ```
   curl -sI https://ng-finance-fe-dev.dev1.ngnair.com/ | grep -i 'content-security-policy'
   ```

2. End-to-end iframe scenario: once NGN-650 ships HTTPS for the Location FE local dev origin (`https://ng-location-fe-local-dev.dev1.ngnair.com:3011`), run that host app locally, sign in, and navigate to a Finance-embedded page (Reporting / Manage > Payments / Manage > Integrations). The Finance iframe should render with no `frame-ancestors` violations in the browser console.

### Notes

- Also promoted the hardcoded Worldpay cert host to a `WORLDPAY_HOST` env var (fallback to the existing cert URL), matching the existing `EPG_HPF_HOST` pattern so the value can switch per environment.
- Removed a duplicate Elavon UAT constant — `HPF_HOST` (`EPG_HPF_HOST` env var) is now used directly in `frame-ancestors` and `frame-src`.

#### mark.valenzuela@ngnair.com - 2026-05-21T00:56:54.515Z
### QA Result: `PASS`

**Environment:** DEVELOP & STAGING
**Tested By:** Mark

### Test Scope
Finance-frontend CSP handling for the Location FE local-dev iframe origin over HTTPS, including non-default port support.

### Test Results
`develop` includes the CSP wildcard allowlist required for iframe embedding:

- `.env` sets `ALLOWED_FRAME_SRC=https://*.dev1.ngnair.com:*`
- `src/proxy.ts` uses `ALLOWED_FRAME_SRC` to build `frame-src`

Josh also noted the same CSP value was deployed to staging, so the staged finance frontend should now allow the local-dev iframe origin on port `3011`.

### Notes
The functional fix described in the ticket is present in `develop`, and the CSP now supports the local-dev iframe scenario without broadening production exposure.

### Activity Timeline
- 2026-05-18T05:37:26.666Z - created by mark.valenzuela@ngnair.com
- 2026-05-19T10:04:15.790Z - josh.tating commented (resolution path, decision to defer to NGN-650)
- 2026-05-20T06:59:09.503Z - mark.valenzuela commented (QA FAIL on staging)
- 2026-05-20T11:43:39.125Z - josh.tating commented (implementation with port-wildcard fix)
- 2026-05-20T11:51:42.518Z - started by josh.tating@ngnair.com
- 2026-05-20T11:51:51.746Z - josh.tating commented (ready for verification, deployed to staging)
- 2026-05-21T00:56:54.515Z - mark.valenzuela commented (QA PASS on develop and staging)
- 2026-05-21T00:57:14.185Z - completed (moved to Done)

### In-Range Day Mapping
- 2026-05-21: commented at 2026-05-21T00:56:54.515Z (QA PASS)

### Activity Notes
Tested the CSP frame-ancestors fix on both develop and staging. Confirmed the port-wildcard pattern (`https://*.dev1.ngnair.com:*`) is present in both environments and the local-dev iframe scenario is no longer blocked. Reported QA PASS.
