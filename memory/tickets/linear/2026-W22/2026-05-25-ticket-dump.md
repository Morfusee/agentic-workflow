# Stand-up Script

Yesterday, I filed two bug reports. I documented a raw Elavon API error that surfaces to users when refunding fresh pay link transactions — the full API response is shown as a toast instead of a user-friendly message. I also reported an issue in the catalog where the category detail modal consistently displays 0 total products regardless of how many products are actually assigned to the category.

Today, I plan to just do QA and find bugs.

No major blockers right now.

---

# Selected Tickets

- NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-673/finance-raw-elavon-error-shown-when-refunding-fresh-pay-link
  - Reference: `# All Scraped Tickets` -> `## NGN-673: Finance: Raw Elavon error shown when refunding fresh pay link transaction`
  - Stand-up relevance: Filed bug report documenting raw Elavon API error surfacing to users during refund flow.

- NGN-674: Product: Category detail modal shows 0 total products regardless of actual count
  - Status: Pending Review
  - Activity date: 2026-05-21
  - URL: https://linear.app/ngnair/issue/NGN-674/product-category-detail-modal-shows-0-total-products-regardless-of
  - Reference: `# All Scraped Tickets` -> `## NGN-674: Product: Category detail modal shows 0 total products regardless of actual count`
  - Stand-up relevance: Filed bug report documenting stale product count in category detail modal.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-675: Product: Pre-filter expired/invalid discounts from Create Payment Link discount selection
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created improvement ticket for pre-filtering expired/future discounts from pay link discount selection UI.

- NGN-676: Product: Enforce Discount Max Claims limit on Pay Link transactions
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting discount Max Claims limit not enforced on Pay Link transactions.

- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting timezone offset issue with payment link expiration dates.

- NGN-689: Product: Prevent payment links from being created with past expiration dates
  - Source dump: 2026-05-22
  - Status as of 2026-05-22: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting payment links creatable with past expiration dates without validation.

- MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: In Progress
  - Role: dev-owner
  - Activity notes: Started creating a simple draft of feasibility for migrating tables in the location-fe to use data-table blocks from a recent project.

---

# Manual Tasks

*No manual tasks recorded.*

---

# All Scraped Tickets

*No tickets with qualifying user activity for 2026-05-25.*
