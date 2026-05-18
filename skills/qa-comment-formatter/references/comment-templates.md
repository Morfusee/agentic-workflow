# QA Comment Templates

## Template Selection

| Overall Status | Template |
|---|---|
| All checks PASS | PASS Template |
| All checks FAIL | FAIL Template |
| All checks BLOCKED | BLOCKED Template |
| Mix of PASS/FAIL/BLOCKED | PARTIAL Template |

## PASS Template

```
### QA Result: `PASS`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
[paragraph or table — omitted when not provided]

### Test Results

| # | Check | Result |
|---|---|---|
| 1 | {description} | PASS |
| 2 | {description} | PASS |
```

- Omit Expected and Actual columns since everything passed.
- Omit Test Scope section when `test_scope` is not provided.
- Include Notes section only if `notes` is provided.
- Include Attachments section only if `screenshots` is provided.

## FAIL Template

```
### QA Result: `FAIL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
[paragraph or table — omitted when not provided]

### Test Results

| # | Check | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | {description} | {expected} | {actual} | FAIL |
| 2 | {description} | {expected} | {actual} | FAIL |
```

- Always include Expected and Actual columns when at least one check failed.
- If expected/actual is not provided for a failed check, use `—` (em dash) as placeholder.
- Omit Test Scope section when `test_scope` is not provided.
- Include Notes section only if `notes` is provided.
- Include Attachments section only if `screenshots` is provided.

## PARTIAL Template

```
### QA Result: `PARTIAL`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
[paragraph or table — omitted when not provided]

### Test Results

| # | Check | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | {description} | — | — | PASS |
| 2 | {description} | {expected} | {actual} | FAIL |
| 3 | {description} | — | — | BLOCKED |
```

- Always include Expected and Actual columns when at least one check failed or was blocked.
- For PASS checks without issues, use `—` in Expected/Actual columns.
- Use `—` in Expected/Actual columns for BLOCKED checks unless details are provided.
- Omit Test Scope section when `test_scope` is not provided.
- Include Notes section only if `notes` is provided.
- Include Attachments section only if `screenshots` is provided.

## BLOCKED Template

```
### QA Result: `BLOCKED`

**Environment:** STAGING
**Tested By:** Mark

### Test Scope
[paragraph or table — omitted when not provided]

### Test Results

| # | Check | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | {description} | — | {reason blocked} | BLOCKED |
```

- Include Expected and Actual columns.
- Use Actual column to describe what blocked the test.
- Omit Test Scope section when `test_scope` is not provided.
- Include Notes section only if `notes` is provided.
- Include Attachments section only if `screenshots` is provided.

## Test Scope Section

When `test_scope` is not explicitly provided, infer it from the issue title, description, and the test checks provided. Derive a concise 1-2 sentence summary of what was tested.

**Paragraph form** (default, when `test_scope` is a string or inferred):

```
### Test Scope
Verified the customer create and edit flow for newly created customers on the STAGING environment.
```

**Table form** (when `test_scope` is provided as an array):

```
### Test Scope

| Area | Description | Coverage |
|---|---|---|
| Customer CRUD | Create and edit flow for new customers | Full |
| Regression | Seeded customer edit behavior | Spot check |
```

Table columns: Area, Description, Coverage. Omit Coverage column when all entries lack it.

Never omit Test Scope. Always include it, inferring from context when not provided.

## Test Results Section

**Paragraph form** (default):

Write a single flowing paragraph that describes what was tested and the outcome. Do not append `— PASS` or `— FAIL` to each sentence. Weave status into the natural prose.

```
### Test Results
All acceptance criteria verified successfully. Newly created customers can be edited after creation, updateCustomer no longer returns BAD_REQUEST for valid edit data, seeded customer edits remain unchanged, and the UI shows correct success state after saving.
```

For a FAIL overall status, describe what passed and what failed in plain prose:
```
### Test Results
Customer creation and seeded customer edits pass. However, editing a newly created customer still returns BAD_REQUEST from updateCustomer, and the UI does not show a save success state.
```

For PARTIAL, describe what passed, what failed, and what was blocked in natural prose.

**Table form** (only when caller explicitly asks for a table or checks carry expected/actual detail):

```
### Test Results

| # | Check | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | {description} | {expected} | {actual} | PASS |
```

Default to paragraph form. Never render Test Results as bulleted lists.

## Notes Section

Only include when `notes` has content:

```
### Notes
- {observation or concern}
- {another observation}
```

If the caller provides `notes` as a single string, split on newlines and render as bullet points. If already a list, render as-is.

## Attachments Section

Only include when `screenshots` has entries:

```
### Attachments
- {screenshot-reference-1}
- {screenshot-reference-2}
```

Render each screenshot reference as a bullet point. The caller may provide filenames, URLs, or Linear attachment references.
