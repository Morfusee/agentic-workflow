# Personal Tasks Template

Use this template for Notion Personal Tasks only.

## Configuration Contract

Load `skill-configs/notion-orchestrator.json` from the canonical memory root before using this template. Resolve the `personal_tasks` domain and verify its configured values against Notion before writes.

Expected domain shape:

- `kind`: `lightweight_task`
- `template`: `personal_task_four_section`
- `database`: Personal Tasks database URL
- `data_source`: Personal Tasks data source URL
- `parent_page`: parent page URL
- `fields`: title, status, due, priority, URL, parent, and subtasks field names
- `write_fields`: Notion write aliases for reserved property names, such as `userDefined:URL`
- `defaults.status`: default task status
- `allowed_statuses` and `allowed_priorities`: Notion schema values expected by this domain

Do not hardcode database IDs in this reference file. Use the config, then fetch Notion to verify the data source schema still matches.

## Database Contract

Required fields, using configured field names:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `Name` | Title | Yes | Verb-first personal task title. |
| `Status` | Status | No | Defaults to `Not started` when creating. |
| `Due Date` | Date | No | Use `YYYY-MM-DD`; only use a date range when the user explicitly asks for a span, range, or end date. Ask if the date is ambiguous. |
| `Priority` | Select | No | `Low`, `Medium`, or `High`; leave empty unless the user indicates priority. |
| `URL` | URL | No | Optional reference link. |
| `Parent Task` | Relation | No | Link a subtask back to its parent Personal Task. |
| `Subtasks` | Relation | No | Link a parent Personal Task to its child subtasks. |

Known status values:

- `Not started`
- `Waiting`
- `In progress`
- `Done`

Use exactly the database's current status labels and configured `allowed_statuses`. Do not invent `Backlog` unless it exists in the fetched schema and config.

## Intent Mapping

Route personal task requests by wording:

- Create: `add`, `create`, `remind me`, `track`, `put this in Personal Tasks`.
- Update: `mark`, `move`, `change`, `set`, `reschedule`, `rename`.
- Review: `what is due`, `show personal tasks`, `what should I do`, `what is pending`.
- Draft: vague task idea, missing target, missing date, or multi-step personal request.

Ask one clarification when required information is missing and cannot be inferred safely.

## Draft Format

Present drafts in this format:

```markdown
**Task:** [verb-first task title]
**Status:** [Not started / Waiting / In progress / Done]
**Due Date:** [YYYY-MM-DD, YYYY-MM-DD to YYYY-MM-DD, or none]
**Priority:** [Low / Medium / High or none]
**URL:** [URL or none]
**What It Is:** [one short sentence]
**How To Do It:** [2-5 simple inferred steps, or none stated]
**Requirements:** [stated requirements, resources, links, deadlines, or none stated]
**Notes:** [caveats, blockers, related context, or none stated]
**Subtasks:** [only include when explicitly requested; child task titles, each with status/date/priority if stated]
```

Keep drafts concise. Avoid business-style issue sections unless the user asks for more detail.
Do not draft database-backed subtasks unless the user explicitly asks for subtasks, child tasks, linked tasks, or separate trackable task rows.

## Body Format

Every Personal Task page body must use these sections in this order:

```markdown
## What It Is
[Explain the task in 1-2 plain sentences.]

## How To Do It
1. [Infer the first likely step.]
2. [Infer the next likely step.]
3. [Stop once the task is clear enough to act on.]

## Requirements
- [List stated requirements, resources, dates, links, people, forms, or accounts.]
- If nothing was stated, write `None stated.`

## Notes
- [List caveats, blockers, related context, eligibility rules, or reminders.]
- If nothing was stated, write `None stated.`
```

Subtask pages must use the same four sections in the same order. Do not use checklist-only child pages when creating database-backed subtasks.

Use inference only for practical next actions. Do not invent requirements, deadlines, links, eligibility, or people.

Keep `How To Do It` short; use 2-5 steps unless the user explicitly asks for a detailed checklist.

Put URLs in the `URL` property when a primary reference link exists, and include the same link in `Requirements` only when it helps the task remain understandable from the page body.

## Title Rules

- Use imperative, action-oriented phrasing.
- Keep titles short enough to scan in a list or board.
- Prefer concrete verbs: `Pay`, `Book`, `Review`, `Prepare`, `Buy`, `Call`, `Clean`, `Schedule`, `Submit`, `Check`.
- Avoid vague titles like `Reminder`, `Personal thing`, or `Task`.

Examples:

- `Pay internet bill`
- `Book dental appointment`
- `Review monthly budget`
- `Prepare gym clothes`
- `Call bank about card replacement`

## Field Defaults

- `Status`: default to `Not started` for new tasks.
- `Priority`: leave empty unless the user indicates urgency or importance; map urgent or very important tasks to `High`.
- `Due Date`: leave empty unless the user gives a date or relative date.
- `URL`: leave empty unless the user provides a link.

Relative dates use the user's local date. If the date could mean more than one day, ask before writing.

## Date Range Rules

- Only set `date:Due Date:end` when the user explicitly says the task should span dates, gives a date range, or asks for a start and end date.
- Treat `deadline`, `due`, `by`, and similar wording as a single due date unless the user also explicitly asks for a span or range.
- If the user says a task should span a vague period such as `this weekend`, infer the start and end from local context only when the phrase clearly indicates a range.
- If the user gives only an end date and does not explicitly ask for a span or range, set only `date:Due Date:start` to that date.
- For a single due date with no span/range wording, set only `date:Due Date:start` and omit `date:Due Date:end`.

## Create Workflow

1. Load Notion Orchestrator config.
2. Resolve the `personal_tasks` domain.
3. Resolve the target database and data source from config.
4. Fetch the data source and confirm the configured fields exist.
5. Draft the task if the request is vague or contains multiple possible interpretations.
6. Create the page with the four-section body format using `notion-create-pages` only after the target and fields are clear.
7. Report the created task title and URL.

Create database-backed subtasks only when the user explicitly asks for subtasks, child tasks, linked tasks, or separate trackable task rows. Do not infer subtasks from a multi-step task, ticket, checklist, acceptance criteria, or obvious child work. If the user gives child work without explicitly asking for subtasks, place it in the parent task's `How To Do It` section instead. If the user's intent is ambiguous, ask whether they want linked subtasks or just steps in the task body.

When the user explicitly asks for database-backed subtasks:

1. Create the parent Personal Task first.
2. Create each subtask as a separate page in the same Personal Tasks data source.
3. Give every subtask the same four-section body format.
4. Set each subtask's `Parent Task` relation to the parent page URL.
5. Update the parent task's `Subtasks` relation with the created subtask page URLs.
6. Preserve any existing parent `Subtasks` relation values when adding new subtasks; append the new subtask URLs instead of replacing existing ones.
7. If the parent cannot be created, do not create orphan subtasks.
8. If either relation update fails, report the created page URL and the failed relation field.

Use this property mapping shape for `notion-create-pages`; field names come from config:

```json
{
  "parent": {"data_source_id": "configured-personal-tasks-data-source-id"},
  "pages": [
    {
      "properties": {
        "Name": "Pay internet bill",
        "Status": "Not started",
        "Priority": "High",
        "date:Due Date:start": "2026-06-01",
        "date:Due Date:is_datetime": 0,
        "userDefined:URL": "https://example.com"
      }
    }
  ]
}
```

Omit optional properties when they do not apply. For date ranges, include both `date:Due Date:start` and `date:Due Date:end`. Use the configured `write_fields.url` value, currently `userDefined:URL`, for the `URL` property because Notion treats `URL` as a special property name.

Use this relation property mapping when creating or updating subtasks after the parent task URL is known:

```json
{
  "Parent Task": ["parent-task-page-url"]
}
```

After each subtask exists, fetch the parent task and update its `Subtasks` relation with the full set of existing subtask URLs plus the newly created subtask URLs:

```json
{
  "Subtasks": [
    "existing-subtask-page-url",
    "new-subtask-page-url"
  ]
}
```

Use page URLs for relation values, matching the data source schema's JSON array of related page URLs. Do not rely on `Parent Task` to automatically populate `Subtasks`; write both sides explicitly.

## Update Workflow

1. Identify the task by exact title, URL, page ID, or user-provided context.
2. If more than one task matches, ask the user to choose.
3. Fetch the matching page or data source schema before writing.
4. Update only the fields the user requested.
5. When updating page content, preserve or migrate the body into the four-section format unless the user explicitly asks for another layout.
6. Report the updated fields and URL.

Common status updates:

- `done`, `complete`, `finished` -> `Done`
- `start`, `working on`, `in progress` -> `In progress`
- `waiting`, `blocked`, `on hold` -> `Waiting`
- `not started`, `todo`, `to do` -> `Not started`

## Review Workflow

Summarize Personal Tasks in this order:

1. Overdue tasks.
2. Due today.
3. Upcoming tasks sorted by `Due Date`.
4. No-date active tasks grouped by `Status`.
5. Completed tasks only if requested.

List subtasks alongside regular tasks in the appropriate section; do not indent them under parent tasks.

Use this summary format:

```markdown
**Personal Tasks**

**Overdue / Due Today**
1. **[Task Name](url)** (Priority) [Status] — **Due Date**
2. **[Task Name](url)** (Priority) [Status] — **Due Date**

**Due [day name or date]**
1. **[Task Name](url)** (Priority) [Status] — **Due Date**

**No Date**
1. **[Task Name](url)** (Priority) [Status]
```

Rules:
- Omit `(Priority)` when priority is none.
- Use `[Status]` exactly as it appears in Notion.
- Omit `— **Due Date**` when there is no due date.
- Use numbered items under each section header.
- Keep section headers only when there are matching tasks.

If there are no matching tasks, say `No matching Personal Tasks found.`

## Quality Bar

- Keep personal task records lightweight.
- Use the four-section body consistently so Personal Tasks are scannable.
- Keep `How To Do It` practical and short; do not over-plan simple tasks.
- Do not turn simple personal tasks into engineering tickets.
- Preserve the user's wording when it is already clear.
- Ask before adding fields, views, or database schema changes.
- Never write to School Tasks, Coding Tasks, Notes, or other databases while using this template.
