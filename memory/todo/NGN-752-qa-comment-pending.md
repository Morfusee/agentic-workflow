# Pending: NGN-752 QA Comment

**Status:** PENDING (execute Monday)
**Created:** 2026-05-30
**Target:** https://linear.app/ngnair/issue/NGN-752

## Action

Publish a `PARTIAL` QA comment on NGN-752 updating the existing `BLOCKED` comment. Afterward, optionally move status (Josh said "clear this issue if there's nothing else").

## Context

- Mark tested NGN-752 and found a blocker: Ruby/Plat BIN ISOs show no processor options during approval
- Josh replied: "track it as a separate bug ticket" and "you can clear this issue if there's nothing else"
- The NGN-752 changes themselves work (verified with Gold BIN ISO)

## Draft Comment

```
### QA Result: `PARTIAL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope

Validated the merchant account Internal MID mirroring changes for a newly onboarded location with multiple BIN ISOs — confirming the partner-owned `publicId` replaces the locally fabricated `MA-...` value, `externalMid` carries a distinct display value, and the finance endpoint returns the correct identifier.

### Test Results

Verified successfully against the Gold BIN ISO: the merchant account's Internal MID carries the partner `publicId` (8-char, no `MA-...`), External MID is a distinct `MID-...` display value, the finance endpoint `GET /api/v1/internal/locations/{id}/internal-mid` returns the partner publicId, and the value round-trips against partner's active InternalMid record. Ruby BIN ISO and Plat BIN ISO could not be fully validated because no processor options appear during the approval stage — this is a pre-existing processor-selection issue under a separate bug ticket.

### Notes

- The NGN-752 changes themselves are confirmed working where testable (Gold BIN ISO).
- Ruby and Plat BIN ISO processor selection is blocked by a separate bug tracked externally — per Josh, this does not gate NGN-752.
```

## Execution Steps

1. Publish comment via `linear_save_comment` on NGN-752
2. Ask Mark whether to also move NGN-752 status (based on Josh's "clear this issue")
