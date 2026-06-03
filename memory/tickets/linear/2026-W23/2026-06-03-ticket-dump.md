# Stand-up Script

Yesterday, I filed a Partner Admin bug where the Partner dropdown in the Add Revenue Split modal was clipped inside the modal container, making long partner lists hard to use. I filed a Partner Admin bug where the Partner dropdown in the Add Revenue Split modal was clipped inside the modal container, making long partner lists hard to use. I also started work on the new Network Partners page for the website app. That work covers adding a partners route, matching the existing hero and body page structure, building a large borderless logo grid for banking, sponsor bank, technology, and platform partners, adding Become a Partner calls to action at the top and bottom, and sourcing logo assets into the public directory.

No major blockers right now.

---

# Selected Tickets

- NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container
  - Status: Pending Review
  - Activity date: 2026-05-26
  - URL: https://linear.app/ngnair/issue/NGN-729/partner-let-add-revenue-split-partner-dropdown-overflow-modal
  - Reference: `memory/tickets/linear/2026-W22/2026-05-26-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container`
  - Stand-up relevance: Created bug report documenting that the Partner dropdown in the Add Revenue Split modal is clipped by the modal container.

- NGN-812: Add Network Partners to Website app
  - Status: In Progress
  - Activity date: 2026-06-02
  - URL: https://linear.app/ngnair/issue/NGN-812/add-network-partners-to-website-app
  - Reference: `memory/tickets/linear/2026-W23/2026-06-02-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-812: Add Network Partners to Website app`
  - Stand-up relevance: Started work on adding the Network Partners page, including the partners route, page layout, logo sourcing, and partner logo grid.

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-810: Marketplace: Fix radio button highlight not following the selected filter item
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: Done
  - Role: contributor
  - Activity notes: Filed bug with root cause analysis (shared radio group name attribute). Duane fixed same day.

- NGN-811: Partner: Debounce search bar input to reduce GraphQL calls per keystroke
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: Done
  - Role: contributor
  - Activity notes: Filed improvement request for debouncing Partner Admin search. Duane implemented and moved to Done same day.

- NGN-813: Partner: Fix contract template download failing with "Could not reach storage" error
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: Done
  - Role: contributor
  - Activity notes: Filed bug about BIN ISO contract template download failing. Duane fixed storage URL resolution same day.

- NGN-814: Partner: Allow Platform Admin to save placements on BIN ISO contract templates
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: Done
  - Role: contributor
  - Activity notes: Filed bug about Platform Admin authorization check blocking placement saves. Duane fixed same day.

- NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: Done
  - Role: dev-owner
  - Activity notes: QA tested Josh's fix on staging across Gold/Ruby/Plat. All acceptance criteria PASS. Moved to Done.

- NGN-753: Location: Fix partner onboarding review views (L30/L20) and early draft visibility
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: In Review
  - Role: tester-only
  - Activity notes: Ran QA on staging - 6 UI checks PASS, 1 FAIL on Primary+Secondary processor constraint. Result: PARTIAL.

- NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: tester-only
  - Activity notes: Closed QA on staging - PARTIAL pass. Gold verified; Ruby/Plat blocked by NGN-803. Moved to Done.

- NGN-807: Support: Escalation ticket status not updating on parent case's Linked Escalations section
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: contributor
  - Activity notes: Filed bug about stale escalation status in Linked Escalations. Duane fixed - refetches parent query on close/reopen.

- MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: In Progress
  - Role: dev-owner
  - Activity notes: Started creating a simple draft of feasibility for migrating tables in location-fe to use data-table blocks.

---

# Ticket Dump

Generated: 2026-06-03T18:14:18+08:00
Requested range: 2026-06-03
Dump file date: 2026-06-03

---

# Grouped Summary

2026-06-03

- No qualifying tickets.

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

No qualifying tickets.
