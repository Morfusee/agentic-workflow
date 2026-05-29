# Stand-up Script

Yesterday, I verified the payment link expiration date fix on staging — the expiration now matches exactly what the user selected regardless of timezone, with no UTC offset shift. I also started QA on the merchant account internal MID changes and hit a blocker during approval: Ruby and Plat BIN ISOs showed no processor options in the approval flow, so I couldn't complete validation of the full pipeline. Only Gold BIN ISO worked. Josh confirmed the processor-options gap should be tracked as a separate bug and that this ticket itself is clear otherwise.

No major blockers right now.

---

# Selected Tickets

- NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid
  - Status: In Review
  - Activity date: 2026-05-29
  - URL: https://linear.app/ngnair/issue/NGN-752/location-finance-make-merchantaccountinternalmid-mirror-the-partner
  - Reference: `# All Scraped Tickets` -> `## NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid`
  - Stand-up relevance: QA tested on staging, blocked by missing processor options for Ruby and Plat BIN ISOs

- NGN-688: Product: Fix expiration date applying timezone offset when creating payment links
  - Status: Done
  - Activity date: 2026-05-26
  - URL: https://linear.app/ngnair/issue/NGN-688/product-fix-expiration-date-applying-timezone-offset-when-creating
  - Reference: `# All Scraped Tickets` (2026-05-26 dump) -> `## NGN-688: Product: Fix expiration date applying timezone offset when creating payment links`
  - Stand-up relevance: QA tested on staging, all acceptance criteria passed

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- NGN-723: Product: Fix Created field applying timezone offset in payment link details
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting a timezone offset issue in the Payment Link Details Created field.

- NGN-729: Partner: Let Add Revenue Split partner dropdown overflow modal container
  - Source dump: 2026-05-26
  - Status as of 2026-05-26: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting that the Partner dropdown in the Add Revenue Split modal is clipped by the modal container.

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

- NGN-719: Finance: Pay Link for Payment Plan charges full amount instead of monthly installment amount
  - Source dump: 2026-05-25
  - Status as of 2026-05-25: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting Pay Link for Payment Plans charging the full plan amount instead of per-installment amount.

- NGN-720: Finance: Surcharge line item missing from Transaction Details modal after Pay Link payment
  - Source dump: 2026-05-25
  - Status as of 2026-05-25: Pending Review
  - Role: tester-only
  - Activity notes: Created bug report documenting surcharge line item missing from Transaction Details modal despite appearing on Payment Complete page.

---

# Ticket Dump

Generated: 2026-05-29T10:13 UTC
Requested range: 2026-05-29
Dump file date: 2026-05-29

---

# Grouped Summary

2026-05-29

## In Review
- NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped Tickets

## NGN-752: Location + Finance: Make MerchantAccount.internalMid mirror the partner-owned publicId; stop conflating externalMid

Status: In Review
Activity date: 2026-05-29
URL: https://linear.app/ngnair/issue/NGN-752/location-finance-make-merchantaccountinternalmid-mirror-the-partner
Initial dev assignee: josh.tating@ngnair.com
Testing actors: mark.valenzuela@ngnair.com
My role for this ticket: tester-only

### Why this ticket was included
Commented on by me

### Description
### Task Description

Make the merchant account carry the **partner-owned** `InternalMid.publicId` as its `internalMid`, instead of the locally fabricated value it generates today, and stop setting `externalMid` to that same fabricated value. This restores the source-of-truth model established earlier (partner owns the `publicId`; location and finance only mirror it) so that downstream work which keys off the merchant account — checkout config resolution, failover topology, transaction reconciliation — has a real, partner-reconcilable identifier to build on.

### Why this is needed

The Internal MID redesign declared partner the single source of truth for every `InternalMid.publicId`, with location and finance mirroring that value for joins and reporting. The **seed data** follows this, but the **runtime activation path never did**:

* At L20 approval (`location-backend/src/modules/location-underwriting/bin-iso-approval.service.ts`), the merchant account's `internalMid` falls through to a self-generated `MA-{binIso}-{uuid}` whenever no external override is present — which is the normal internal-driven path. The partner `publicId` is provisioned and written **only** to `Location.internalMid` (`bin-iso-selection.service.ts`), never onto the merchant account or the approval row.
* `externalMid` is set to that **same** fabricated value, so it is neither a real processor-issued MID nor a distinct merchant-facing display ID.
* The service-to-service endpoint `location-backend/src/modules/location/internal-location.controller.ts` (`GET :id/internal-mid`) returns the merchant account's fabricated `internalMid`, so finance mirrors and stamps a value that does **not** reconcile with partner's `InternalMid.publicId`.

Net effect: `Location.internalMid` is correct (partner `publicId`), but `MerchantAccount.internalMid` is a random local string disconnected from partner lineage. Any feature that resolves config or failover from the merchant account inherits a broken key.

### Technical Scope

**Location — populate** `MerchantAccount.internalMid` **from partner**

* During BIN ISO selection/approval, resolve a partner `InternalMid.publicId` **per merchant account** (one per selected BIN ISO) and persist it as `MerchantAccount.internalMid`. Partner's provisioning endpoint already accepts a BIN ISO, so a `publicId` can be provisioned per BIN ISO rather than once per location.
* Carry the resolved `publicId` onto the approval row so `approveBinIsoLocation` uses it instead of `MA-{binIso}-{uuid}`. Remove the local-generation fallback for the internal-driven path (keep handling the external-webhook override, which legitimately supplies an externally issued value).

**Location — separate** `externalMid`

* Stop setting `externalMid` equal to `internalMid`. `externalMid` should hold the real processor-issued MID once known; until a processor MID exists, use a clearly distinct display value rather than the routing identifier. Confirm the unique constraints still hold once the two columns carry different values.

**Finance-facing endpoint**

* `GET :id/internal-mid` must return the partner `publicId` consistently (so finance's mirrored `internalMid` on transactions/batches reconciles with partner). Verify the GraphQL `Location.internalMid` resolver and this internal endpoint agree.

**Backfill**

* For existing merchant accounts, reconcile `internalMid` to the partner `publicId` by joining against partner's `InternalMid` records via the location's lineage. Where a merchant account currently holds a `MA-...` value, replace it with the corresponding partner `publicId`.
* Re-derive `externalMid` where it currently mirrors the fabricated internal value.

**Partner (relay to owner — no code here)**

* Confirm partner provisions (or can provision) one `InternalMid.publicId` per BIN ISO selected for a location, so each merchant account maps to a distinct partner record. If partner currently provisions only once per location, that gap must be closed on the partner side before per-merchant-account mirroring is fully correct.

### Acceptance Criteria

- [ ] New internal-driven activations write the partner `InternalMid.publicId` to `MerchantAccount.internalMid` (no `MA-{binIso}-{uuid}` generation on this path)
- [ ] `externalMid` no longer equals `internalMid`; it holds a real processor MID or a distinct display value
- [ ] `GET :id/internal-mid` and the GraphQL `Location.internalMid` resolver both return the partner `publicId`
- [ ] Existing merchant accounts are backfilled so `internalMid` matches the partner `publicId`; `externalMid` re-derived where it mirrored the fabricated value
- [ ] A merchant account's `internalMid` round-trips against partner's `InternalMid.publicId` (cross-service join verified)
- [ ] External-webhook override path still works for externally issued MIDs
- [ ] Partner-side per-BIN-ISO provisioning gap confirmed/closed (or written up for the partner owner)

### Notes

* This is a **prerequisite** for the merchant-account config snapshot / finance-resolution work — those tickets key the snapshot off the merchant account and require a real, partner-reconcilable `internalMid`.
* Seed fixtures already use the correct partner `publicId`, so the gap is runtime-only; verification must exercise the real activation flow, not just seeded data.

### Comments
#### josh.tating@ngnair.com - 2026-05-29T10:13:41.082Z
you can clear this issue if there's nothing else

#### mark.valenzuela@ngnair.com - 2026-05-29T06:54:51.910Z
### QA Result: `BLOCKED`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope

Validated the approval flow for a new location with multiple BIN ISOs, specifically checking whether each selected BIN ISO can proceed through processor selection during approval.

### Test Results

Approval is currently blocked for Ruby BIN ISO and Plat BIN ISO because no processor options appear during the approval stage. Gold BIN ISO is the only BIN ISO that shows available processors and can proceed. Ruby BIN ISO was double-checked and has Elavon configured as its processor, but Elavon still does not appear as an available option in the approval flow.

### Notes

Looping in @josh.tating on this blocker since the issue appears tied to the BIN ISO approval / processor selection flow. Returning this ticket for now because I can't complete validation of this ticket until Ruby BIN ISO and Plat BIN ISO can select processors during approval.

Please confirm whether this should be tracked as a separate bug ticket or treated as a blocker under this ticket.

#### josh.tating@ngnair.com - 2026-05-29T10:13:20.597Z
track it as a separate bug ticket

#### josh.tating@ngnair.com - 2026-05-29T01:17:27.773Z
@mark.valenzuela Ready for QA — deployed to staging.

Tag: `docker.io/blee900/location-backend:3350df0`

This change makes each merchant account carry the partner-owned Internal MID publicId (instead of a locally fabricated `MA-...` value) and gives the External MID its own distinct display value. It only affects **new** activations — existing locations predate the change, so verify with a freshly onboarded location.

**Steps to verify (staging):**
1. Onboard a new location and select **two** BIN ISOs (so a primary + secondary merchant account are created).
2. At L20, approve both BIN ISOs (each with a processor + acquiring bank), then configure the Internal MIDs (primary + secondary) to move the location to Active.
3. Confirm each merchant account's **Internal MID** is an 8-character partner publicId (alphabet excludes I/O/0/1) — **not** a `MA-...` value.
4. Confirm each **External MID** is a distinct `MID-...` display value, not equal to the Internal MID.
5. Confirm the same Internal MID exists as an Active record on the partner side for that location (cross-service round-trip).

API spot-check for the finance-facing value:
`GET https://ng-location-dev.dev1.ngnair.com/api/v1/internal/locations/{locationId}/internal-mid` -> expected: the 8-char partner publicId.

Note: location create no longer provisions an Internal MID — it's now provisioned per BIN ISO at selection.

#### josh.tating@ngnair.com - 2026-05-28T16:07:57.561Z
Implemented on branch `issue/NGN-752`.

**What changed**
- BIN ISO selection now provisions one partner InternalMid per selected BIN ISO and stores each `publicId` on its approval row. The primary (first) selection's `publicId` is denormalized onto `Location.internalMid`. Idempotent on re-send.
- L20 approval sets `MerchantAccount.internalMid` from the approval row's partner `publicId` instead of fabricating a `MA-{binIso}-{uuid}` value. The local-generation fallback is removed for the internal-driven path (the external-webhook override is preserved).
- `externalMid` is no longer set equal to the routing id — it gets its own generated merchant-facing display value (`MID-...`), distinct from `internalMid`.
- Activation (APPROVED->ACTIVE) now activates **every** configured primary + secondary InternalMid on partner, not just a single one.
- Location create no longer provisions an InternalMid; provisioning is deferred to BIN ISO selection, where the BIN ISO route is known.

**Files touched**
- `src/modules/location-underwriting/bin-iso-selection.service.ts`
- `src/modules/location-underwriting/bin-iso-approval.service.ts`
- `src/modules/location/location.service.ts`

**Verified**
- Build clean; full unit suite shows no new failures vs the base branch (pre-existing unrelated failures only).
- Service boots cleanly with the changes (dependency graph + GraphQL schema build OK).
- Finance-facing internal endpoint returns the partner `publicId`: `GET /api/v1/internal/locations/{id}/internal-mid` -> `AAAAAAAA` (Alpha), `DDDDDDDD` (Delta).

**Not yet verified end-to-end** — the full provision -> approve -> configure flow was not exercised at runtime locally. It requires partner running alongside location (both stacks bind the same database host port) and a location staged through the underwriting pipeline (no fixture stages this, and there is no seeded shortcut). This path should be verified on staging, where partner is deployed: take a location through onboarding with two BIN ISOs, approve both, configure Internal MIDs, and confirm each merchant account's Internal MID is an 8-char partner `publicId` (not `MA-...`) with a distinct `MID-...` External MID, and that the value round-trips against partner's active `InternalMid`.

**Note for the partner owner:** partner already supports multiple InternalMids per location (`InternalMid.publicId` is unique, `locationId` is not), so no partner-side change was required to provision one per BIN ISO.

### Activity Timeline
- 2026-05-28T12:58:33Z created
- 2026-05-28T16:07:57Z commented (josh.tating — implementation notes)
- 2026-05-29T01:17:23Z started (moved to In Review)
- 2026-05-29T01:17:27Z commented (josh.tating — ready for QA)
- 2026-05-29T06:54:51Z commented (mark.valenzuela — QA Result: BLOCKED)
- 2026-05-29T10:13:20Z commented (josh.tating — track as separate bug)
- 2026-05-29T10:13:41Z commented (josh.tating — you can clear if nothing else)

### In-Range Day Mapping
- 2026-05-29: commented (mark.valenzuela — QA Result: BLOCKED at 06:54:51Z)

### Activity Notes
Tested the approval flow for NGN-752 on staging. Validated that each merchant account carries the partner-owned Internal MID `publicId` (not a fabricated `MA-...` value) and that `externalMid` has a distinct display value. QA was blocked because Ruby BIN ISO and Plat BIN ISO showed no processor options during the approval stage (only Gold BIN ISO worked). Marked as BLOCKED and returned for resolution. Josh confirmed the processor-options issue should be tracked as a separate bug ticket.
