---
name: requirements-reviewer
description: Reviews implemented code against requirements and acceptance criteria, producing pass/fail checks with evidence. Use when implementation work must be validated against a ticket, prompt, PRD, spec, or acceptance criteria after code changes exist.
---

# Requirements Reviewer

Review implementation coverage against the stated requirements.

## Workflow

1. Collect source requirements from the ticket, prompt, PRD, spec, or provided acceptance criteria.
2. Normalize requirements into atomic checks. Split compound acceptance criteria into independently reviewable behaviors.
3. Inspect implementation evidence: changed files, related source paths, tests, route/UI behavior, and verification output.
4. Compare each atomic requirement to the implementation.
5. Classify each check as `PASS`, `FAIL`, `PARTIAL`, or `BLOCKED` using `references/check-types.md`.
6. Return only the reviewer contract result expected by `$review-orchestrator`.

## Rules

- Do not modify files.
- Do not publish comments or update tickets.
- Do not mark a requirement `PASS` solely because tests passed.
- Use file paths, function names, tests, commands, or provider facts as evidence.
- Mark unclear or uninspectable requirements as `BLOCKED` instead of guessing.
- Preserve the original requirement wording in the check description when practical.
- If no explicit requirements are available, derive checks from the implementation prompt and mark confidence low.

## Output Contract

Use this exact shape:

```text
REVIEWER_RESULT
reviewer: requirements-reviewer
overall_status: {PASS|FAIL|PARTIAL|BLOCKED}
checks:
- description: {requirement or acceptance criterion checked}
  status: {PASS|FAIL|PARTIAL|BLOCKED}
  expected: {required behavior}
  actual: {implementation evidence, missing behavior, or blocker}
notes:
- {optional concise observation}
confidence: {high|medium|low}
END_REVIEWER_RESULT
```

## Supporting References

- `references/check-types.md` defines classification rules and common requirement categories.
