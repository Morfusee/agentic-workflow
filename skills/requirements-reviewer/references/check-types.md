# Requirement Check Types

Use these categories while normalizing requirements into checks.

## Functional Behavior

- User-visible behavior matches the requirement.
- API, CLI, workflow, or background-job behavior matches the requirement.
- Existing behavior remains intact when the requirement implies preservation.

## Data And State

- Data is read, written, validated, migrated, or persisted as required.
- State transitions match the accepted flow.
- Empty, missing, duplicate, or invalid data is handled when specified.

## Edge Cases And Errors

- Required error states are handled.
- Boundary cases from the ticket or prompt are covered.
- Permission, loading, retry, and unavailable-state behavior is present when specified.

## Tests And Verification

- Tests exist for required behavior when the repository convention expects tests.
- Manual or automated verification output supports the implementation claim.
- Missing tests can be `PARTIAL` or `FAIL` depending on whether tests were an explicit requirement.

## Status Guidance

- Use `PASS` only with direct implementation evidence.
- Use `FAIL` when required behavior is absent or contradicted by implementation.
- Use `PARTIAL` when some but not all of a compound requirement is covered.
- Use `BLOCKED` when context, access, or runnable evidence is missing.
