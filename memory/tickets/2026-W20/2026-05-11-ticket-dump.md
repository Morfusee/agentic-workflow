# Stand-up Script

Yesterday, I tested the Reporting table search behavior in staging across Transactions, Batches, Deposits, and Disputes, and verified the debounce fix is working as expected with a PASS result.

No major blockers right now.

---

# Selected Tickets

- NGN-561: Debounce Reporting search requests across all tables
  - Status: Done
  - Activity date: 2026-05-11
  - URL: https://linear.app/ngnair/issue/NGN-561/debounce-reporting-search-requests-across-all-tables
  - Reference: `# All Scraped Tickets` -> `## [NGN-561]: Debounce Reporting search requests across all tables`
  - Stand-up relevance: Captures explicit testing and verification completed by me on 2026-05-11.

---

# All Scraped Tickets

## [NGN-561]: Debounce Reporting search requests across all tables

Status: Done
Activity date: 2026-05-11
URL: https://linear.app/ngnair/issue/NGN-561/debounce-reporting-search-requests-across-all-tables
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
commented on by me

### Description
### The Problem

Table search inputs for Transactions, Batches, Deposits, and Disputes trigger a GraphQL request on every keystroke instead of waiting for the user to finish typing.

### Steps to Reproduce

1. Log in as Elena Santos to the Location FE Host app.
2. Go to Reporting.
3. Open DevTools and monitor the Network tab.
4. Use the table search input on the Transaction table.
5. Repeat the same search behavior on the Batches, Deposits, and Disputes tables.

### Expected vs Actual

* **Expected:** Search requests should be debounced to avoid firing on every keystroke.
* **Actual:** GraphQL requests are sent on every keystroke.

### Acceptance Criteria

* All Reporting table searches are debounced consistently.
* Typing continuously does not send one request per keypress.
* Results still update correctly after debounce delay.

### Comments
#### mark.valenzuela@ngnair.com - 2026-05-11T08:03:15.260Z
### Environment:

STAGING

### Tested By:

Mark

### Test Scope:

Validation of debounced search behavior for Reporting > Transactions, Batches, Deposits, and Disputes tables.

### Note:

The issue has been fixed and verified working in STAGING. The affected Reporting table searches now wait for the debounce delay before sending GraphQL requests, and table results still update correctly after the user stops typing.

### Result:

PASSED

#### josh.tating@ngnair.com - 2026-05-09T12:21:01.209Z
## Deployed to Staging

Added a `useDebounce` hook (300ms delay) and applied it to the search inputs on all four Reporting tables: Transactions, Batches, Deposits, and Disputes. The debounced search value is used in GraphQL query variables instead of the raw input state.

**Docker tag:** `docker.io/blee900/finance-frontend:938ed32`

### Verification
1. Open Reporting -> Transactions
2. Open DevTools -> Network tab, filter by `graphql`
3. Type a search term quickly (e.g., "test")
4. Verify only 1 GraphQL request fires ~300ms after you stop typing
5. Repeat on Batches, Deposits, and Disputes pages

### Activity Timeline
- 2026-05-11T08:03:15.260Z tested
- 2026-05-11T08:03:15.260Z commented

### In-Range Day Mapping
- 2026-05-11: 2026-05-11T08:03:15.260Z tested; 2026-05-11T08:03:15.260Z commented

### Activity Notes
Tested and confirmed the debounce behavior in staging with a PASS result and explicit verification details for all targeted Reporting tables.