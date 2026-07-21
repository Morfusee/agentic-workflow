# Stand-up Script

Yesterday, I finished and closed the fix for EnrollMate's guardian relationship rules, so the Guardian relationship is now restricted to Other whenever both parents are marked Unknown or Deceased, covering all Unknown and Deceased combinations, with the mocker and automated test coverage updated to follow the same rule. I also scoped out three new Smoke Testing tasks: one to evaluate polling versus Server-Sent Events for refreshing the Smoke Testing page while runs are active, one to make Smoke test result writes idempotent so duplicate or retried reporter events can't create duplicate results or corrupt persisted run state, and one to persist Smoke test runs incrementally from the Hono service so a run and its observed results become available before the full suite finishes.

No major blockers right now.

---

# Selected Tasks

- 86d3r7fhy: Fix guardian relationship rules for unavailable parents
  - Status: complete
  - Activity date: 2026-07-21
  - URL: https://app.clickup.com/t/86d3r7fhy
  - Reference: `# All Scraped Tasks` -> `## 86d3r7fhy: Fix guardian relationship rules for unavailable parents`
  - Stand-up relevance: Closed as complete yesterday by Mark.

- 86d3rttu6: Determine live update strategy for Smoke Testing
  - Status: to do
  - Activity date: 2026-07-21
  - URL: https://app.clickup.com/t/86d3rttu6
  - Reference: `# All Scraped Tasks` -> `## 86d3rttu6: Determine live update strategy for Smoke Testing`
  - Stand-up relevance: Created by Mark yesterday during Smoke Testing planning.

- 86d3rttu7: Make Smoke test result writes idempotent
  - Status: to do
  - Activity date: 2026-07-21
  - URL: https://app.clickup.com/t/86d3rttu7
  - Reference: `# All Scraped Tasks` -> `## 86d3rttu7: Make Smoke test result writes idempotent`
  - Stand-up relevance: Created by Mark yesterday during Smoke Testing planning.

- 86d3rttua: Persist Smoke test runs incrementally from Hono
  - Status: to do
  - Activity date: 2026-07-21
  - URL: https://app.clickup.com/t/86d3rttua
  - Reference: `# All Scraped Tasks` -> `## 86d3rttua: Persist Smoke test runs incrementally from Hono`
  - Stand-up relevance: Created by Mark yesterday during Smoke Testing planning.

---

# Unselected Tasks

No unselected tasks remain.

---

# Manual Tasks

Entries here are not tracked in ClickUp. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tasks

## 86d3r7fhy: Fix guardian relationship rules for unavailable parents

Status: complete
Activity date: 2026-07-21
URL: https://app.clickup.com/t/86d3r7fhy
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
status changed by me

### Description
**Description**
Fix EnrollMate guardian handling so the Guardian relationship must be Other when both the Father and Mother are marked Unknown or Deceased.
**Scope**
*   Enforce Other as the only valid Guardian relationship when both parents are unavailable.
*   Cover Unknown/Unknown, Unknown/Deceased, Deceased/Unknown, and Deceased/Deceased combinations.
*   Prevent incompatible Guardian relationships from being accepted in these cases.
*   Update the EnrollMate mocker to generate Guardian details that follow the same rule.
*   Add or update automated coverage for the validation and mocked data.

**Deliverable**

*   Guardian relationship is strictly Other whenever both parents are Unknown or Deceased.
*   Other Guardian relationships remain available when at least one parent is not Unknown or Deceased.
*   Mocker-generated records consistently follow the same relationship rule.
*   Automated tests cover all affected parent-status combinations.

### Comments
No comments found.

### Activity Timeline
- 2026-07-20 11:39:14 +08:00 created: Task created by Mark Rolis Valenzuela
- 2026-07-21 16:37:49 +08:00 closed: Task moved to complete

### In-Range Day Mapping
- 2026-07-21: status changed to complete at 2026-07-21 16:37:49 +08:00

### Activity Notes
Bug fix for EnrollMate guardian relationship validation (tagged bug, high priority). Task was created on 2026-07-20 and closed as complete on 2026-07-21.

---

## 86d3rttu6: Determine live update strategy for Smoke Testing

Status: to do
Activity date: 2026-07-21
URL: https://app.clickup.com/t/86d3rttu6
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
Created by me; assigned to me

### Description
**Description**
Evaluate polling and Server-Sent Events (SSE) for refreshing the Smoke Testing page while Playwright smoke runs are active, then select the simplest reliable approach for the current deployment architecture.
**Scope**
*   Compare polling and SSE for update latency, operational complexity, database load, reconnect behavior, and multi-instance deployment.
*   Confirm how clients will learn that persisted Smoke Testing data has changed and refetch the database-backed state.
*   Treat PostgreSQL as the source of truth rather than sending complete test results through notifications.
*   Base the comparison on observed smoke-test results as they are persisted; do not require expected-test records.
*   Limit the analysis to the Smoke Testing page and Smoke Testing tables; exclude E2E Testing.

**Deliverable**

*   Document the selected polling or SSE approach and the reason for the decision.
*   Define the client refresh flow, active-run behavior, failure recovery, and acceptable update latency.
*   Identify any infrastructure or deployment constraints required by the selected approach.
*   Provide implementation-ready requirements for the Smoke Testing frontend without changing E2E Testing.

### Comments
No comments found.

### Activity Timeline
- 2026-07-21 17:19:31 +08:00 created: Task created by Mark Rolis Valenzuela

### In-Range Day Mapping
- 2026-07-21: created at 2026-07-21 17:19:31 +08:00

### Activity Notes
New feature task (tagged feature) scoped during planning: decide between polling and SSE for live Smoke Testing page updates.

---

## 86d3rttu7: Make Smoke test result writes idempotent

Status: to do
Activity date: 2026-07-21
URL: https://app.clickup.com/t/86d3rttu7
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
Created by me; assigned to me

### Description
**Description**
Prevent duplicate or retried Hono/Playwright reporter events from creating duplicate Smoke Testing results or corrupting persisted run state.
**Scope**
*   Define stable identifiers for a Smoke test result and its retry attempt within a run.
*   Add the required Smoke Testing database uniqueness constraint.
*   Persist reporter events with idempotent insert or upsert behavior.
*   Preserve separate Playwright retry attempts without merging them into one result.
*   Define how repeated start, completion, and terminal run events are handled.
*   Add concurrency and duplicate-delivery coverage for Smoke Testing writes.
*   Limit all changes to Smoke Testing tables and execution paths; exclude E2E Testing.

**Deliverable**

*   Replaying the same reporter event does not create duplicate Smoke test results.
*   Concurrent delivery preserves a consistent result and run state.
*   Separate retry attempts remain independently queryable.
*   Database constraints enforce the idempotency rules.
*   Automated tests verify duplicate, retry, and concurrent event handling without changing E2E Testing.

### Comments
No comments found.

### Activity Timeline
- 2026-07-21 17:19:31 +08:00 created: Task created by Mark Rolis Valenzuela

### In-Range Day Mapping
- 2026-07-21: created at 2026-07-21 17:19:31 +08:00

### Activity Notes
New feature task (tagged feature) scoped during planning: idempotent Smoke Testing result writes with DB uniqueness constraints.

---

## 86d3rttua: Persist Smoke test runs incrementally from Hono

Status: to do
Activity date: 2026-07-21
URL: https://app.clickup.com/t/86d3rttua
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
Created by me; assigned to me

### Description
**Description**
Decouple Smoke Testing database writes in the Hono/Playwright service so a run and its observed test results become available before the full suite finishes. Add temporary frontend polling to validate that persisted progress can be displayed during an active run.
**Scope**
*   Create and commit the Smoke test run record before Playwright execution begins.
*   Persist observed test start, completion, status, timing, and failure details through short independent database transactions as reporter events arrive.
*   Avoid holding one database transaction open for the duration of the Playwright run.
*   Preserve partial results when execution fails, crashes, or stops before suite completion.
*   Add temporary polling to the Smoke Testing page while a run is active so the frontend can fetch newly persisted state.
*   Render only tests reported by Playwright; do not introduce expected-test records.
*   Limit all schema, query, Hono, reporter, and frontend changes to Smoke Testing; exclude E2E Testing.

**Deliverable**

*   A Smoke test run is visible from the frontend shortly after execution starts.
*   Observed test results appear before the full suite completes.
*   Completed results remain persisted when later tests or the overall run fail.
*   Temporary polling stops when the run reaches a terminal state.
*   Reloading the Smoke Testing page reconstructs the current run from PostgreSQL.
*   Automated tests cover incremental persistence, partial failure, and active-run polling without changing E2E Testing.

### Comments
No comments found.

### Activity Timeline
- 2026-07-21 17:19:31 +08:00 created: Task created by Mark Rolis Valenzuela

### In-Range Day Mapping
- 2026-07-21: created at 2026-07-21 17:19:31 +08:00

### Activity Notes
New feature task (tagged feature) scoped during planning: incremental persistence of Smoke test runs from the Hono/Playwright service with temporary frontend polling.
