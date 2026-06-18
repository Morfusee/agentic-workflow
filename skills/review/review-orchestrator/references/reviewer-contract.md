# Reviewer Contract

Use this contract for every reviewer invoked by `$review-orchestrator`.

## Required Input Context

Provide each reviewer only the context it needs:

- Requirements or acceptance criteria.
- Provider ID/URL when available.
- Changed files, diff, or committed comparison range.
- Relevant source files and tests.
- Verification commands and results.
- Explicit review scope and exclusions.

Reviewers must not modify files.

## Required Output

Each reviewer must return this structure:

```text
REVIEWER_RESULT
reviewer: {skill-name}
overall_status: {PASS|FAIL|PARTIAL|BLOCKED}
checks:
- description: {specific check performed}
  status: {PASS|FAIL|PARTIAL|BLOCKED}
  expected: {expected behavior or standard, optional only when obvious from description}
  actual: {file-backed observation or blocker, optional only for PASS checks with enough detail in description}
notes:
- {optional observation}
confidence: {high|medium|low}
END_REVIEWER_RESULT
```

## Status Semantics

- `PASS`: Evidence shows the requirement or standard is satisfied.
- `FAIL`: Evidence shows the requirement or standard is not satisfied.
- `PARTIAL`: Some evidence satisfies the check, but coverage is incomplete or ambiguous.
- `BLOCKED`: The reviewer cannot determine the result because required context, access, or runnable verification is missing.

## Evidence Rules

- Tie `actual` values to files, tests, commands, or provider facts whenever possible.
- Do not mark a check `PASS` only because tests passed; inspect the implementation path.
- Use `BLOCKED`, not guesses, when the relevant implementation cannot be found.
- Keep findings concise enough for `$ticket-review-comment-drafter` to render cleanly.
