---
name: job-application
description: Two-phase job application workflow: scour first, then apply after approval.
disable-model-invocation: true
---

# Job Application

User-invoked only. Invoke with the portal and locale beside the skill, for example `/job-application jobstreet ph`.

This skill has two phases. Phase 1 scours and stops. Phase 2 applies only after the user approves specific listings.

## Phase Selection

- If the user asks to find, search, scour, list, or review jobs, run Phase 1.
- If the user says to apply to `all` or specific list numbers from a prior Phase 1 result, run Phase 2.
- If the portal or locale is missing, ask for it before opening the browser.
- If Phase 2 is requested without an approved Phase 1 list in the current conversation, ask for the list or rerun Phase 1.

## Browser Rule

Use Chrome DevTools against the existing browser/profile. Do not open a new Chrome profile, isolated browser context, or separate automation profile.

## Phase 1: Scour

Goal: produce a fresh, numbered shortlist and stop before applying.

1. Load [`PROFILE.md`](PROFILE.md) before evaluating fit.
Completion criterion: the resume facts, target roles, and skill keywords are available in context.

2. Open the requested portal and locale from the invocation, such as Jobstreet Philippines for `/job-application jobstreet ph`.
Completion criterion: the active browser page is on the requested portal and locale.

3. Search for AI Engineer, Automation Engineer, AI Automation, Full Stack Developer, and FullStack Developer roles.
Completion criterion: each role family has been searched or explicitly reported as unavailable on that portal.

4. Filter to full-time, remote jobs posted at most 7 days ago, sorted by latest where the portal supports it.
Completion criterion: every retained listing is full-time, remote, and no older than 7 days, or its uncertainty is flagged.

5. Open promising listings and evaluate fit against `PROFILE.md`.
Completion criterion: every retained listing has been checked for title, company, location/remote status, employment type, freshness, core requirements, and resume fit.

6. Return a numbered shortlist and stop.
Completion criterion: the response includes portal/locale, search date, each listing's title, company, link, posted age/date, remote/full-time evidence, fit rationale, and any uncertainty. Do not apply.

## Phase 2: Apply

Goal: submit only approved applications without inventing data.

1. Resolve approved targets from the user's list numbers or `all`.
Completion criterion: every target maps to a Phase 1 listing and no unapproved listing is included.

2. Before applying on a portal, load its memory file if it exists: `$HOME/Documents/Programming/agentic-workflow/memory/miscs/job-application/<portal>.md`.
Completion criterion: known portal-specific exact answers are available, or the absence of memory is noted.

3. Open each approved listing in the existing Chrome profile and start the application flow.
Completion criterion: the application form for the approved listing is visible, or the blocker is reported.

4. Preserve existing autofill.
Completion criterion: no pre-filled field has been changed unless the user explicitly instructs it.

5. Use the portal's existing uploaded resume when the portal asks for a resume. Select the saved resume/CV already present in the account; do not ask for a disk path unless the portal has no saved resume or forces a fresh file upload. Do not include a cover letter.
Completion criterion: the saved portal resume is selected if required, and cover-letter fields are left empty or skipped unless required.

6. For every empty required field, use only an exact answer from the portal memory file. If there is no exact memory answer, stop and ask the user.
Completion criterion: every field is either already autofilled, filled from memory with a 1:1 exact answer, or left untouched because the workflow is paused for the user.

7. When the workflow pauses for a missing field, let the user fill it personally or provide the exact answer. Before continuing, save only the verified exact answer to the portal memory file, creating the parent directory if needed.
Completion criterion: the memory file records the portal, field label, exact answer, source date, and any job-specific caveat. If the exact answer cannot be read or confirmed, ask the user before saving.

8. Continue through the application until the final submit step.
Completion criterion: either the application is submitted, or the process is paused with the exact field, page, or portal blocker the user must handle.

9. Report outcomes.
Completion criterion: every approved listing is marked submitted, paused, blocked, or skipped with a concrete reason.

## Field Discipline

- Never invent personal details, credentials, work authorization, salary expectations, dates, links, phone numbers, addresses, or answers to screening questions.
- Never infer a field answer from the resume unless the field is directly asking for a fact already present and the exact answer is unambiguous.
- Do not touch autofilled fields. They are intentionally present.
- Do not submit if any required field was guessed, inferred loosely, or filled without memory/user confirmation.

## Portal Memory Format

When saving a new answer, append this structure to `$HOME/Documents/Programming/agentic-workflow/memory/miscs/job-application/<portal>.md`:

```markdown
## <YYYY-MM-DD> <Portal Name>

- Field: <exact field label>
- Answer: <exact user-provided answer>
- Scope: <global for portal | only for company/job if user says so>
- Caveat: <any limitation, or none>
```
