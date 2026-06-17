# Ticket Dump

Generated: 2026-06-18 01:31:14 +08:00
Requested range: 2026-06-17
Dump file date: 2026-06-17

---

# Grouped Summary

2026-06-17

## ClickUp Tasks
- No qualifying tasks found in ClickUp for the requested date from the available task, search, closed-date, and time-entry queries.

## Manual Tasks
- [MANUAL-001]: Fix up Playwright POC test/reporting control plane
- [MANUAL-002]: Deploy Playwright POC on personal Dokploy instance

---

# Manual Tasks

Entries here are not tracked in ClickUp. They were added from user-provided context because no matching ClickUp tasks were found for the requested date.

## [MANUAL-001]: Fix up Playwright POC test/reporting control plane

Status: Done
Activity date: 2026-06-17
My role: dev-owner

### Description
Fixed up the Playwright POC so scheduled website tests can run continuously and keep an Allure dashboard available after each run.

### Activity Notes
The repo pattern uses a long-running `control-plane` worker instead of host cron or GitHub Actions as the runtime scheduler. The worker applies Drizzle migrations once, repeatedly runs `pnpm run test:website:db`, allows test failures without stopping the cycle, then runs `pnpm run allure:db` so failed and successful runs are still exported into the generated Allure dashboard. The website Playwright config uses a DB-only reporter for scheduled runs, storing run/result data in PostgreSQL through `reporters/db-reporter.ts`; `scripts/allure-from-db.ts` converts DB-backed runs into Allure result files, and `scripts/allure.cjs` generates `allure-report-db`.

### Repo Evidence
- `scripts/control-plane.ts`: scheduled worker loop, migration startup, test execution, and Allure generation.
- `playwright.website.config.ts`: website-only scheduled Playwright config using `./reporters/db-reporter.ts`.
- `reporters/db-reporter.ts`: PostgreSQL-backed Playwright reporter for run and result persistence.
- `scripts/allure-from-db.ts`: exports stored DB runs into Allure-compatible result JSON.
- `package.json`: `test:website:db`, `allure:db`, and `control-plane` scripts.
- `README.md`: documents the local run flow and control-plane behavior.

## [MANUAL-002]: Deploy Playwright POC on personal Dokploy instance

Status: Done
Activity date: 2026-06-17
My role: dev-owner

### Description
Deployed and hosted the Playwright POC on a personal server using a personal Dokploy instance.

### Activity Notes
The deployment shape uses `docker-compose.deploy.yml` with two services: `control-plane`, a worker-only service that runs `pnpm run control-plane`, and `report-ui`, an `nginx:alpine` service that serves the generated Allure dashboard from the shared `allure-report-db` volume. The deploy setup expects an external hosted PostgreSQL database through `DATABASE_URL`, persists report artifacts in Docker volumes, and exposes only the static report UI service for platform routing.

### Repo Evidence
- `docker-compose.deploy.yml`: defines the deploy-time `control-plane` worker and `report-ui` Allure dashboard service.
- `Dockerfile`: builds the Node/Playwright runtime with Java available for Allure generation.
- `README.md`: documents the Dokploy/Coolify deployment shape and recommends a single `control-plane` replica for the POC.

---

# All Scraped Tasks

No qualifying ClickUp tasks were found for 2026-06-17. Provider queries checked ClickUp assignee resolution for `me`, task keyword searches for Playwright/Allure/Dokploy/POC, closed-date filters, due-date filters, and time entries for the requested day.
