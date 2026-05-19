# Stand-up Script

Yesterday, I reported two access control gaps in our admin frontends. The Support Admin and Partner Admin pages were missing role-based access control — any authenticated user could reach them just by navigating to the URL directly. I verified this with standard user accounts like Sofia Navarro, Ivan Petrov, and Blake Tanaka — all three could access pages that should be restricted to Platform Administrators only. These were two of three identical RBAC gaps I filed on Monday; Duane picked up all three, implementing access control following the existing Location Admin pattern. As of yesterday, both are resolved — unauthorized users now see an Access Denied page consistent with the rest of the platform.

No major blockers right now.

---

# Selected Tickets

- NGN-647: Support: Restrict Support Admin FE access to Platform Administrators only
  - Status: Done
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-647/support-restrict-support-admin-fe-access-to-platform-administrators
  - Reference: `# All Scraped Tickets` -> `## NGN-647: Support: Restrict Support Admin FE access to Platform Administrators only` (source: 2026-05-18 dump)
  - Stand-up relevance: Reported missing RBAC on Support Admin FE; completed by Duane on May 19

- NGN-649: Partner: Restrict Partner admin FE access to Platform Administrators only
  - Status: Done
  - Activity date: 2026-05-18
  - URL: https://linear.app/ngnair/issue/NGN-649/partner-restrict-partner-admin-fe-access-to-platform-administrators
  - Reference: `# All Scraped Tickets` -> `## NGN-649: Partner: Restrict Partner admin FE access to Platform Administrators only` (source: 2026-05-18 dump)
  - Stand-up relevance: Reported missing RBAC on Partner FE host app; completed by Duane on May 19

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

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

- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets
  - Source dump: 2026-05-19
  - Status as of 2026-05-19: Done
  - Role: tester-only
  - Activity notes: QA tested the Customers table fix in staging; PASS result

- NGN-604: Customer: Fix updateCustomer bad request for newly created customers
  - Source dump: 2026-05-18
  - Status as of 2026-05-18: Done
  - Role: dev-owner
  - Activity notes: Implemented fix, QA'd on STAGING, moved to Done

---

# Ticket Dump

Generated: 2026-05-20T00:54:00+08:00
Requested range: 2026-05-19
Dump file date: 2026-05-19

---

# Grouped Summary

[2026-05-19]

## Done
- NGN-650: Location: Implement HTTPS local dev for location-frontend using mkcert
- NGN-651: Location: Implement HTTPS local dev for location-admin using mkcert
- NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-650: Location: Implement HTTPS local dev for location-frontend using mkcert

Status: Done
Activity date: 2026-05-19
URL: https://linear.app/ngnair/issue/NGN-650/location-implement-https-local-dev-for-location-frontend-using-mkcert
Initial dev assignee: josh.tating@ngnair.com
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

`location-frontend` local development currently runs over plain HTTP. When the dev server needs to interact with HTTPS backend services or authenticate across origins, developers must use Chrome flags or other workarounds to bypass security restrictions. `marketplace-frontend` already solved this by using `mkcert` to generate trusted local certificates and running `next dev` with `--experimental-https`.

### Steps to Reproduce

1. Run `pnpm dev` in `location-frontend`
2. Observe the dev server starts on `http://`
3. Compare with `marketplace-frontend`, which serves `https://` locally without browser warnings

### Technical Requirements

* Add a `justfile` following the `marketplace-frontend` pattern:
  * `DOMAIN`: `ng-location-fe-local-dev.dev1.ngnair.com`
  * `PORT`: `3011`
  * `setup` command to run `mkcert -install`
  * `certs` command to generate `.pem` and `-key.pem` for the domain
  * `dev` command that depends on `certs` and passes `--experimental-https`, `--experimental-https-key`, and `--experimental-https-cert`
* Update `package.json` dev script to include `--experimental-https`
* Ensure generated certificate files are gitignored (already covered by existing `*.pem` and `certificates` entries)

### Expected vs Actual

* **Expected:** `just dev` (or `pnpm dev`) starts the server on HTTPS with a trusted local certificate
* **Actual:** Dev server starts on HTTP; no automated certificate management exists in the repo

### Acceptance Criteria

- [ ] `justfile` added to repo with mkcert-based certificate generation
- [ ] `package.json` dev script includes `--experimental-https`
- [ ] `just dev` starts the server on HTTPS using the generated certs
- [ ] No Chrome security flags are required to access the local dev site
- [ ] Generated `.pem` files remain gitignored

### Comments
#### josh.tating@ngnair.com - 2026-05-19T10:07:16.432Z
Implemented HTTPS local dev for location-frontend, mirroring marketplace-frontend.

**Changes**
- Added `justfile` with `setup` / `certs` / `dev` / `codegen` / `clean` recipes. `dev` runs `pnpm codegen` then `pnpm next dev` with `--experimental-https` and the mkcert-generated cert/key for `ng-location-fe-local-dev.dev1.ngnair.com` on port `3011`.
- Updated `package.json` `dev` script to add `--experimental-https` so `pnpm dev` also serves HTTPS (Next auto-generates self-signed certs into the gitignored `certificates/` dir when key/cert flags aren't passed).
- `.gitignore` already covers `*.pem` and `certificates` — no change needed.
- `dev:start` (which is `next start`, a production server) was left untouched since `--experimental-https` is a `next dev` flag only.

**Files touched**
- `justfile` (new)
- `package.json`
- `.verification.md`

**Verified locally**
- `mkcert -install` + `just certs` generates the cert/key pair for the domain.
- `just dev` starts Next on `https://ng-location-fe-local-dev.dev1.ngnair.com:3011` — `curl -k` returns HTTP 200 over TLS, no startup errors.
- `pnpm dev` (without just) also boots on HTTPS using Next's auto-generated certs in `certificates/`, returning HTTP 200.

**Branch**
- `issue/ngn-650`

**Side-effect: closes NGN-645**
The deployed finance-frontend CSP header `frame-ancestors https://*.dev1.ngnair.com` already matches any HTTPS origin under that wildcard, so once a developer runs location-frontend over HTTPS locally, embedded finance iframes (Reporting, Manage > Payments, Manage > Integrations) load without a CSP violation. No finance-frontend change required.

#### josh.tating@ngnair.com - 2026-05-19T11:18:12.903Z
Deployed to staging.

Docker tag: `docker.io/blee900/location-frontend:4db4c57`

This work only affects local development — adds a `justfile` and the `--experimental-https` flag to the dev script. Verification is a local-machine check, not a staging behavior change:

1. From the `location-frontend` repo root: `just setup` (one-time — installs the mkcert CA and generates certs).
2. Run `just dev`.
3. Open https://ng-location-fe-local-dev.dev1.ngnair.com:3011.
4. Expected: page loads with a trusted lock icon and no browser security warnings.

This also auto-resolves NGN-645 (CSP `frame-ancestors`): the deployed finance-frontend CSP wildcard `https://*.dev1.ngnair.com` now matches the HTTPS local-dev origin, so iframe embedding from the local Location FE host into Finance pages no longer hits a CSP violation.

### Activity Timeline
- 2026-05-19T08:46:58.918Z: created
- 2026-05-19T10:07:16.432Z: commented (josh.tating)
- 2026-05-19T11:18:10.994Z: moved to Done
- 2026-05-19T11:18:12.903Z: commented (josh.tating)

### In-Range Day Mapping
- 2026-05-19: created (08:46)

### Activity Notes
Created ticket requesting mkcert-based HTTPS local dev for location-frontend. Josh implemented the change, adding a `justfile`, updating `package.json`, and verifying locally. Deployed to staging. This also auto-resolved NGN-645 since the HTTPS local dev origin now matches the finance-frontend CSP wildcard.

---

## NGN-651: Location: Implement HTTPS local dev for location-admin using mkcert

Status: Done
Activity date: 2026-05-19
URL: https://linear.app/ngnair/issue/NGN-651/location-implement-https-local-dev-for-location-admin-using-mkcert
Initial dev assignee: josh.tating@ngnair.com
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

`location-admin` has no HTTPS support for local development. The `package.json` dev script starts Next.js over plain HTTP, and there is no certificate management or `justfile` setup. This forces developers to use Chrome flags when working with HTTPS backends or secure-context APIs. `marketplace-frontend` already established a working pattern using `mkcert` and `--experimental-https`.

### Steps to Reproduce

1. Run `pnpm dev` in `location-admin`
2. Observe the dev server starts on `http://`
3. Compare with `marketplace-frontend`, which serves `https://` locally without browser warnings

### Technical Requirements

* Add a `justfile` following the `marketplace-frontend` pattern:
  * `DOMAIN`: `ng-location-admin-local-dev.dev1.ngnair.com`
  * `PORT`: `3012`
  * `setup` command to run `mkcert -install`
  * `certs` command to generate `.pem` and `-key.pem` for the domain
  * `dev` command that depends on `certs` and passes `--experimental-https`, `--experimental-https-key`, and `--experimental-https-cert`
* Update `package.json` dev script to include `--experimental-https`
* Ensure generated certificate files are gitignored (already covered by existing `*.pem` entry)

### Expected vs Actual

* **Expected:** `location-admin` local dev runs over HTTPS with trusted certificates, matching the `marketplace-frontend` setup
* **Actual:** `location-admin` local dev runs over HTTP only

### Acceptance Criteria

- [ ] `justfile` added to repo with mkcert-based certificate generation
- [ ] `package.json` dev script includes `--experimental-https`
- [ ] `just dev` starts the server on HTTPS using the generated certs
- [ ] No Chrome security flags are required to access the local dev site
- [ ] Generated `.pem` files remain gitignored

### Comments
#### josh.tating@ngnair.com - 2026-05-19T10:08:06.817Z
Added mkcert-based HTTPS for local dev on location-admin, mirroring the marketplace-frontend pattern.

**Changes**
- Added `justfile` with `setup`, `certs`, `dev`, `codegen`, and `clean` recipes. `dev` regenerates GraphQL types via `pnpm codegen`, then runs `next dev` with `--experimental-https` and the mkcert-generated cert/key.
- Updated `package.json` dev script to include `--experimental-https`.
- `.gitignore`: Next.js' built-in HTTPS dev mode auto-creates a `certificates/` directory on first launch; that entry was appended. `*.pem` was already covered.

**Files touched**
- `justfile` (new)
- `package.json`
- `.gitignore`

**Branch**
- `issue/ngn-651` (off `develop`)

**Verification**
- Ran `mkcert -install` (CA already trusted) and `just certs` — generated `ng-location-admin-local-dev.dev1.ngnair.com.pem` + `-key.pem`.
- Started the dev server and confirmed it listens on HTTPS: `Ready in 1077ms` at `https://ng-location-admin-local-dev.dev1.ngnair.com:3012`.
- `curl -k -o /dev/null -w '%{http_code}' https://ng-location-admin-local-dev.dev1.ngnair.com:3012/` returned `200`.

Local-dev only; no runtime or production impact.

#### josh.tating@ngnair.com - 2026-05-19T11:18:16.850Z
Deployed to staging.

Docker tag: `docker.io/blee900/location-admin:96d1333`

Local-dev tooling only — adds a `justfile` and the `--experimental-https` flag to the dev script. Local verification:

1. From the `location-admin` repo root: `just setup` (one-time).
2. Run `just dev`.
3. Open https://ng-location-admin-local-dev.dev1.ngnair.com:3012.
4. Expected: page loads with a trusted lock icon and no browser security warnings.

### Activity Timeline
- 2026-05-19T08:46:59.137Z: created
- 2026-05-19T10:08:06.817Z: commented (josh.tating)
- 2026-05-19T11:18:15.015Z: moved to Done
- 2026-05-19T11:18:16.850Z: commented (josh.tating)

### In-Range Day Mapping
- 2026-05-19: created (08:46)

### Activity Notes
Created ticket requesting mkcert-based HTTPS local dev for location-admin. Josh implemented the change, adding a `justfile`, updating `package.json` and `.gitignore`, and verifying locally. Deployed to staging.

---

## NGN-632: Customer: Fix Customers table cutoff and add navigation for large result sets

Status: Done
Activity date: 2026-05-19
URL: https://linear.app/ngnair/issue/NGN-632/customer-fix-customers-table-cutoff-and-add-navigation-for-large
Initial dev assignee: john.demonteverde@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Commented on by me

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
#### mark.valenzuela@ngnair.com - 2026-05-19T02:49:31.339Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope

Verified the Customers table layout, pagination controls, and navigation for large result sets in the Location FE Host App using the Alpha City Branch location with seeded customer data.

### Test Results

Logged in as Elena Santos (location super admin) via the dev login, navigated to Customers > Customers, and selected Alpha City Branch in the location selector. The table renders 10 customer rows with all columns fully visible and no cutoff. The "Rows per page" selector (5, 10, 25, 50) is present and functional. Previous (disabled on page 1) and Next pagination buttons are available. Clicking Next advances to page 2 and displays a new set of customer records with all rows intact. The location selector and existing Customers table behavior are preserved.

### Activity Timeline
- 2026-05-14T11:07:26.261Z: created
- 2026-05-18T08:01:11.947Z: moved to In Progress (john.demonteverde)
- 2026-05-19T02:49:31.339Z: commented (mark.valenzuela)
- 2026-05-19T02:49:39.629Z: moved to Done (john.demonteverde)

### In-Range Day Mapping
- 2026-05-19: tested (02:49)

### Activity Notes
Tested/QA'd the Customers table fix in staging. Verified table rendering with 10 customer rows fully visible, no cutoff. Confirmed "Rows per page" selector (5, 10, 25, 50) is functional, pagination buttons work correctly, and the location selector is preserved. QA result: PASS.
