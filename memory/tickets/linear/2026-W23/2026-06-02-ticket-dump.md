# Stand-up Script

Previously, I filed a bug report documenting that Pay Links created for Payment Plans charge the full plan amount instead of the per-installment amount — the Order Summary shows the total rather than the monthly installment, and the transaction goes through for the full amount. I also reported an issue with the Created field in Payment Link details showing a timezone-shifted timestamp, where the displayed date and time is offset by the viewer's UTC offset rather than showing the consistent creation time.

No major blockers right now.

---

# Selected Tickets

- NGN-719: Finance: Pay Link for Payment Plan charges full amount instead of monthly installment amount
  - Status: In Review
  - Activity date: 2026-05-25
  - URL: https://linear.app/ngnair/issue/NGN-719
  - Reference: `memory/tickets/linear/2026-W22/2026-05-25-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-719`
  - Stand-up relevance: Created bug report documenting Pay Link for Payment Plans charging full plan amount instead of per-installment amount.

- NGN-723: Product: Fix Created field applying timezone offset in payment link details
  - Status: Pending Review
  - Activity date: 2026-05-26
  - URL: https://linear.app/ngnair/issue/NGN-723
  - Reference: `memory/tickets/linear/2026-W22/2026-05-26-ticket-dump.md` -> `# All Scraped Tickets` -> `## NGN-723`
  - Stand-up relevance: Created bug report documenting timezone offset applied to Created timestamp in Payment Link Details modal.

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

- NGN-812: Add Network Partners to Website app
  - Source dump: 2026-06-02
  - Status as of 2026-06-02: In Progress
  - Role: dev-owner
  - Activity notes: Started work on new partners page. Implementing /partners route, logo sourcing, and page layout.

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
  - Activity notes: Ran QA on staging — 6 UI checks PASS, 1 FAIL on Primary+Secondary processor constraint. Result: PARTIAL.

- NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: tester-only
  - Activity notes: Closed QA on staging — PARTIAL pass. Gold verified; Ruby/Plat blocked by NGN-803. Moved to Done.

- NGN-807: Support: Escalation ticket status not updating on parent case's Linked Escalations section
  - Source dump: 2026-06-01
  - Status as of 2026-06-01: Done
  - Role: contributor
  - Activity notes: Filed bug about stale escalation status in Linked Escalations. Duane fixed — refetches parent query on close/reopen.

- NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting Partner dropdown clipped by modal container in Add Revenue Split.

- MANUAL-001: Feasibility draft for migrating tables in location-fe to use data-table blocks
  - Source dump: 2026-05-21
  - Status as of 2026-05-21: In Progress
  - Role: dev-owner
  - Activity notes: Started creating a simple draft of feasibility for migrating tables in location-fe to use data-table blocks.

---

# Ticket Dump

Generated: 2026-06-02T08:56:50Z
Requested range: 2026-06-02
Dump file date: 2026-06-02

---

# Grouped Summary

2026-06-02

## Done
- NGN-810: Marketplace: Fix radio button highlight not following the selected filter item
- NGN-811: Partner: Debounce search bar input to reduce GraphQL calls per keystroke
- NGN-814: Partner: Allow Platform Admin to save placements on BIN ISO contract templates
- NGN-813: Partner: Fix contract template download failing with "Could not reach storage" error
- NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors

## In Progress
- NGN-812: Add Network Partners to Website app

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-810: Marketplace: Fix radio button highlight not following the selected filter item

Status: Done
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-810/marketplace-fix-radio-button-highlight-not-following-the-selected
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me; commented on by me

### Description
### The Problem

The radio button in Marketplace FE's "Show only" filter lists does not highlight the currently selected item. Toggling between filter items correctly swaps the displayed content, but the radio button indicator drifts out of sync and eventually points to the wrong option.

### Steps to Reproduce

1. Log in to Marketplace FE as Sofia Navarro.
2. Go to Marketplace.
3. Toggle some items on the top "Show only" radio button list.
4. Toggle some items on the bottom "Show only" radio button list.
5. Observe that the radio button highlight drifts and no longer reflects the currently selected filter item.

### Technical Requirements

* Identify where the radio button group's selected state is managed and why it desyncs from the active filter.
* Ensure the selected radio button stays in sync when toggling between items in both "Show only" lists.
* Verify the fix works across all "Show only" filter groups on the page.

### Expected vs Actual

* **Expected:** The radio button highlight always matches the currently active filter item in each "Show only" group.
* **Actual:** The radio button highlight drifts out of sync from the active filter, showing the wrong item as selected even though filtering works correctly.

### Acceptance Criteria

- [ ] Toggling any radio item in the top "Show only" list highlights only that item.
- [ ] Toggling any radio item in the bottom "Show only" list highlights only that item.
- [ ] Toggling between items in both lists never causes the radio highlight to drift from the active selection.
- [ ] Filtering behavior (which items are shown/hidden) remains correct for all radio selections.

### Comments
#### mark.valenzuela@ngnair.com - 2026-06-02T02:36:12.008Z
## Root Cause

Both "Show only" filter groups in `CatalogContent.tsx` render with the same `name` attribute (`"showOnlyFilter"`, the component's default). In HTML, all radio inputs sharing a `name` belong to the same native radio group, so the browser treats them as mutually exclusive across both filter lists. Clicking a radio in one group causes the other group's visual highlight to desync.

## Suggested Fix

Pass distinct `name` values to each `<ShowOnlyFilterButtons>` instance in `CatalogContent.tsx`:

- **Top group** (type filter): `name="typeFilter"`
- **Bottom group** (install filter): `name="installFilter"`

This makes them independent radio groups at the browser level. No changes needed to the React state logic — each group already tracks its own `value`/`onChange` correctly.

## File to Change

- `src/features/catalog/CatalogContent.tsx` — add `name` prop to both `<ShowOnlyFilterButtons>` usages (~2 lines)

### Activity Timeline
- 2026-06-02T02:36:05.404Z created (mark.valenzuela)
- 2026-06-02T02:36:12.008Z commented (mark.valenzuela — root cause analysis)
- 2026-06-02T04:03:03.712Z moved to Done (Duane Enriquez)

### In-Range Day Mapping
- 2026-06-02: created (mark.valenzuela at 02:36:05Z); commented (mark.valenzuela at 02:36:12Z)

### Activity Notes
Filed bug documenting that Marketplace FE radio button highlight drifts from selected filter item. Provided root cause analysis: both "Show only" filter groups share the same `name` attribute, making them a single native radio group. Suggested fix: pass distinct `name` values per group. Duane fixed and moved to Done same day.

---

## NGN-811: Partner: Debounce search bar input to reduce GraphQL calls per keystroke

Status: Done
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-811/partner-debounce-search-bar-input-to-reduce-graphql-calls-per
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

The Partners page search bar in Partner Admin fires a GraphQL request on every keystroke, generating unnecessary network calls. Search inputs should be debounced to batch rapid keystrokes into a single request after the user stops typing.

### Steps to Reproduce

1. Log in to Partner Admin as Mark Goldman.
2. Go to Partners.
3. Open DevTools and switch to the Network tab.
4. Type a search term into the search bar.
5. Observe that every keystroke triggers a discrete GraphQL call.

### Technical Requirements

* Add a debounce (e.g., 300ms) to the Partners page search input so a GraphQL call fires only after the user pauses typing, not on every keystroke.
* Ensure the debounce is cancelable — a new keystroke within the window resets the timer.
* Confirm existing search behavior (results, loading state, empty state) remains correct after debounce.

### Expected vs Actual

* **Expected:** Typing in the search bar triggers at most one GraphQL call after the user stops typing.
* **Actual:** Every keystroke triggers a separate GraphQL call.

### Acceptance Criteria

- [ ] Rapidly typing 5+ characters in the Partners search bar triggers 1 GraphQL call, not 5+.
- [ ] Search results update correctly with the debounced query.
- [ ] Clearing the search field resets results as before.
- [ ] No regression on other search bars in Partner Admin.

### Comments
No comments found.

### Activity Timeline
- 2026-06-02T02:57:40.586Z created (mark.valenzuela)
- 2026-06-02T04:03:43.865Z moved to Done (Duane Enriquez)

### In-Range Day Mapping
- 2026-06-02: created (mark.valenzuela at 02:57:40Z)

### Activity Notes
Filed improvement request documenting that Partner Admin's search bar fires a GraphQL request on every keystroke. Duane implemented debounce and moved to Done same day.

---

## NGN-812: Add Network Partners to Website app

Status: In Progress
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-812/add-network-partners-to-website-app
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: None identified
My role for this ticket: dev-owner

### Why this ticket was included
Assigned to me; started by me

### Description
### The Problem

The website has no page showcasing NGnair's network partners. A new page is needed that lists all banking, technology, and platform partners in a consistent, branded layout.

### Technical Requirements

* Add a new route/page for `/partners` (or appropriate slug).
* Page layout: hero/top section followed by a main body section, matching existing site conventions.
* Partner logos displayed in a borderless grid, **4–5 partners per row**.
* **Logos should be large** — they serve as a signal of who NGnair works with, not just decorative badges.
* **"Become a Partner" CTA** must appear at both the top and bottom of the partner list.
* Store logo assets in the `/public` directory.
* Prefer **webp** format, then **svg**. Source logos from:
  * [brandfetch.com](<https://brandfetch.com/>)
  * [logo.dev](<https://www.logo.dev/search>)
  * [commons.wikimedia.org](<https://commons.wikimedia.org/wiki/Main_Page>)
  * [svgrepo.com](<https://www.svgrepo.com/>)
* Note any partners whose logos could not be found.

### Partner List

**Banking Partners**
Elavon, Worldpay, TSYS, Fiserv, BMO Harris Bank, Central Bank of St. Louis, Citizens Bank, Commercial Bank of California (CBC), Fifth Third Bank, First National Bank of Omaha (FNBO), First National Bank of Pennsylvania (FNB PA), KeyBank, Synovus Bank, Truist Bank, UMB Bank, Wells Fargo Bank

**Sponsor Banks**
Celtic Bank, Chesapeake Bank, Column (formerly Northern California National Bank), Cross River Bank, Evolve Bank & Trust, Hatch Bank, Lead Bank, Lineage Bank, MVB Bank, Pathward (formerly MetaBank), Piermont Bank, Republic Bank & Trust Company, Sutton Bank, The Bancorp Bank, WebBank, East West Bank

**Technology & Platform Partners**
HubSpot, HighLevel, Salesforce, Pipedrive, QuickBooks, Sage, Entrust, Onfido, Apple, Google, Citcon

### Acceptance Criteria

- [ ] New partners page is live at the correct URL.
- [ ] Page matches existing site design (hero + body sections).
- [ ] Partner logos render in a borderless grid at 4–5 per row, sized large and prominently.
- [ ] "Become a Partner" CTA appears at both top and bottom of the partner list.
- [ ] Logo assets stored under `/public`.
- [ ] Missing logos are documented for follow-up.
- [ ] Page is responsive and renders correctly on mobile.

### Comments
No comments found.

### Activity Timeline
- 2026-06-02T03:15:03.097Z created (blee@ngnair.com)
- 2026-06-02T03:33:50.530Z moved to In Progress (mark.valenzuela)

### In-Range Day Mapping
- 2026-06-02: moved to In Progress (mark.valenzuela at 03:33:50Z)

### Activity Notes
Started work on adding a Network Partners page to the website app. Moved to In Progress. Currently implementing the /partners route, partner logo sourcing, and page layout.

---

## NGN-813: Partner: Fix contract template download failing with "Could not reach storage" error

Status: Done
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-813/partner-fix-contract-template-download-failing-with-could-not-reach
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

L20 BIN ISO users (Gordon Blake, Rafael Costa, Priya Kapoor) cannot download contract templates they have uploaded under Manage > Templates. Clicking **Download** on a template entry triggers a toast error: "Could not reach storage to download the PDF."

### Steps to Reproduce

1. Log in to Partner FE as a BIN ISO user (Gordon Blake, Rafael Costa, or Priya Kapoor).
2. Go to **Manage > Templates**.
3. If no templates exist, upload at least one.
4. Click **Download** on any contract template in the table.
5. Observe the toast error: "Could not reach storage to download the PDF."

### Technical Requirements

* Identify why the storage URL for contract template downloads is unreachable from the client (e.g., expired or missing signed URL, incorrect Backblaze bucket path, CSP restriction, or missing proxy route).
* Fix the download path so clicking **Download** returns the stored file to the browser.
* Verify the fix for all BIN ISO roles that have access to templates.

### Expected vs Actual

* **Expected:** Clicking **Download** on a contract template retrieves and downloads the file.
* **Actual:** The download fails with "Could not reach storage to download the PDF."

### Acceptance Criteria

- [ ] Any BIN ISO user with uploaded contract templates can download them without error, and the downloaded file matches the originally uploaded template.

### Comments
No comments found.

### Activity Timeline
- 2026-06-02T03:17:25.860Z created (mark.valenzuela)
- 2026-06-02T03:45:34.719Z moved to Done (Duane Enriquez)

### In-Range Day Mapping
- 2026-06-02: created (mark.valenzuela at 03:17:25Z)

### Activity Notes
Filed bug documenting that BIN ISO users cannot download contract templates — download triggers "Could not reach storage to download the PDF" toast. Duane fixed the storage URL resolution and moved to Done same day.

---

## NGN-814: Partner: Allow Platform Admin to save placements on BIN ISO contract templates

Status: Done
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-814/partner-allow-platform-admin-to-save-placements-on-bin-iso-contract
Initial dev assignee: Duane Enriquez
Testing actors: None identified
My role for this ticket: contributor

### Why this ticket was included
Created by me

### Description
### The Problem

Platform Admins (e.g., Mark Goldman) cannot save placements on BIN ISO contract templates. The save fails with a toast error "Partner is not a BIN ISO". Platform Admins are intended to perform this action on behalf of BIN ISOs, but the authorization check is blocking them. BIN ISO users themselves can save placements without issue — the failure is specific to the Platform Admin role.

### Steps to Reproduce

1. Log in as **Mark Goldman** (Platform Admin) to Partner Admin.
2. Navigate to **BIN ISO Templates**.
3. Select a BIN ISO with uploaded signable documents (e.g., Gold BIN ISO). Upload one if needed.
4. In the table, click the **Placements** action.
5. Add a placement element to any page (Signature, Date, or Text).
6. Click the **Save Placements** button at the top right.
7. Observe the toast error: "Partner is not a BIN ISO".

### Technical Requirements

* The save placements authorization check must permit Platform Admins acting on behalf of a BIN ISO to save placements.
* BIN ISO users already save placements successfully — the fix must not regress their flow.

### Expected vs Actual

* **Expected:** Platform Admin can save placements on a BIN ISO contract template without error.
* **Actual:** Platform Admin receives "Partner is not a BIN ISO" toast and the save is rejected.

### Acceptance Criteria

- [ ] Platform Admin can save placements on any BIN ISO contract template.
- [ ] Placements persist correctly after save (fields appear on reload).
- [ ] BIN ISO user placement saves continue to work without regression.

### Comments
No comments found.

### Activity Timeline
- 2026-06-02T03:27:31.607Z created (mark.valenzuela)
- 2026-06-02T03:50:30.027Z moved to Done (Duane Enriquez)

### In-Range Day Mapping
- 2026-06-02: created (mark.valenzuela at 03:27:31Z)

### Activity Notes
Filed bug documenting that Platform Admins cannot save placements on BIN ISO contract templates — authorization check incorrectly rejects them as "not a BIN ISO". Duane fixed the authorization guard and moved to Done same day.

---

## NGN-803: Location: L20 underwriting processor dropdown empty for Ruby and Plat BIN ISOs despite configured processors

Status: Done
Activity date: 2026-06-02
URL: https://linear.app/ngnair/issue/NGN-803/location-l20-underwriting-processor-dropdown-empty-for-ruby-and-plat
Initial dev assignee: mark.valenzuela@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: dev-owner

### Why this ticket was included
Created by me; QA tested by me; moved to Done by me

### Description
### The Problem

In the L20 underwriting modal, the processor dropdown is empty for Ruby and Plat BIN ISOs, blocking the approval step. Gold BIN ISO works correctly and populates the dropdown. Under **Manage > Processors**, both Ruby and Plat have processors configured — they just do not surface in the underwriting modal.

Discovered during QA of NGN-752. The NGN-752 changes are confirmed working where testable (Gold BIN ISO). Ruby and Plat BIN ISOs could not be validated because processor selection is a prerequisite for the approval flow.

### Steps to Reproduce

1. Onboard a new location and select two BIN ISOs (e.g., Gold and Ruby, or Gold and Plat).
2. Log in to Partner FE as Mark Goldman (Gold BIN ISO owner).
3. Go to **Locations**, open the newly created location, and navigate to the **Underwriting** modal.
4. Observe that the processor dropdown is populated with selectable processors. Approve if desired.
5. Log out and log in as the Ruby (or Plat) BIN ISO owner.
6. Go to **Locations**, open the same location, and navigate to the **Underwriting** modal.
7. Observe that the processor dropdown is empty — no processors are selectable despite being visible under Manage > Processors for that BIN ISO.

### Expected vs Actual

* **Expected:** Every BIN ISO's underwriting modal shows the processors configured under Manage > Processors for that BIN ISO's acquiring bank(s), enabling one-click approval.
* **Actual:** Mark Goldman (Gold) sees the processor dropdown populated correctly. The Ruby and Plat BIN ISO owners see an empty dropdown, despite having processors configured under Manage > Processors.

### Technical Requirements

* Identify why the underwriting modal's processor resolution returns empty for Ruby and Plat BIN ISOs when processors are configured.
* Check whether the processor query or resolver correctly maps the acquiring bank ID for each BIN ISO — the gap may be in how the view determines which acquiring bank's processors to fetch, or in the backend returning empty results for specific BIN ISO / acquiring bank pairs.
* Confirm the fix works for all BIN ISOs (Gold, Ruby, Plat) — no regression on Gold.

### Acceptance Criteria

- [ ] Ruby BIN ISO owner sees the same selectable processors in the underwriting modal that are visible under Manage > Processors.
- [ ] Plat BIN ISO owner sees the same selectable processors in the underwriting modal that are visible under Manage > Processors.
- [ ] Mark Goldman (Gold BIN ISO) continues to see processors and approve correctly (no regression).
- [ ] Selecting a processor and confirming approval succeeds for Ruby and Plat end-to-end on staging.

### Comments
#### mark.valenzuela@ngnair.com - 2026-06-02T01:45:00.376Z
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
Verified the underwriting processor dropdown behavior across all BIN ISOs (Gold, Ruby, Plat) on staging, including processor visibility matching the Manage > Processors configuration and end-to-end approval flow.

### Test Results
All acceptance criteria verified successfully. Ruby and Plat BIN ISO owners see the same selectable processors in the underwriting modal as configured under Manage > Processors. Gold BIN ISO continues to see processors and approve correctly with no regression. Selecting a processor and confirming approval succeeds end-to-end on staging for Ruby, Plat, and Gold.

#### josh.tating@ngnair.com - 2026-06-01T11:53:06.630Z
@mark.valenzuela Ready for verification — the L20 processor dropdown is now sourced from the BIN ISO's own configured processors instead of `Processor.supportedAcquirerIds`.

**Docker tag**
- location-frontend: `docker.io/blee900/location-frontend:9f9aed9`

**Root cause**
The L20 underwriting modal filtered the processors list by `Processor.supportedAcquirerIds.includes(acquirer.publicUid)`. `supportedAcquirerIds` is seeded only with `PTR-840-000001` (Diamond Acquirer) and isn't updated when a BIN ISO configures a processor under Manage > Processors (that page writes `PartnerConfig` rows, not the global Processor's `supportedAcquirerIds`). Gold's acquirer happens to be Diamond, so it worked; Ruby/Plat acquirers aren't in `supportedAcquirerIds`, so the dropdown was empty.

**Fix**
The L20 view now queries `financePartnerConfigs(partnerId=binIsoPublicUid)` — the BIN ISO partner's own active configs — and uses that as the primary source for the dropdown. Falls back to the legacy `supportedAcquirerIds` filter if the partner has no configs yet (so Gold and any other partner already covered by the seeded acquirer keeps working). Duplicate processors across primary/secondary configs are deduped by name.

**Verify on staging**
1. As **Mark Goldman** (Gold), open a location at UNDERWRITING. Confirm the processor dropdown still populates and Approve still works end-to-end.
2. As the **Ruby** BIN ISO owner, open the same/another location. The dropdown should now list whatever processors are visible under Manage > Processors for Ruby. Pick Primary, click Approve, expect a success toast and the approval to persist on refresh.
3. Repeat for **Plat** BIN ISO owner.
4. Also try Primary + Secondary processor selection (NGN-753) — the dropdowns should populate from the partner's configured processors.

### Activity Timeline
- 2026-06-01T05:14:54.437Z created (mark.valenzuela)
- 2026-06-01T11:52:56.069Z moved to In Review (mark.valenzuela)
- 2026-06-01T11:53:06.630Z commented (josh.tating — ready for verification)
- 2026-06-02T01:45:00.376Z commented (mark.valenzuela — QA Result: PASS)
- 2026-06-02T01:45:13.413Z moved to Done (mark.valenzuela)

### In-Range Day Mapping
- 2026-06-01: created (mark.valenzuela at 05:14:54Z); moved to In Review (mark.valenzuela at 11:52:56Z)
- 2026-06-02: commented QA Result PASS (mark.valenzuela at 01:45:00Z); moved to Done (mark.valenzuela at 01:45:13Z)

### Activity Notes
Created bug report on 6/1 after discovering empty processor dropdown for Ruby/Plat BIN ISOs during NGN-752 QA. Josh implemented a fix sourcing from partner-level configs instead of global Processor.supportedAcquirerIds. On 6/2, ran full QA on staging across Gold, Ruby, and Plat BIN ISOs — all acceptance criteria PASS. Moved to Done after verification.
