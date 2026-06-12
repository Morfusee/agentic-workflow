# Coding Projects Template

Use this template for Coding Projects Tracker technical tickets only.

## Configuration Contract

Load `memory/skill-configs/notion-orchestrator.json` from the canonical memory root before using this template. Resolve the `coding_projects` domain and verify its configured values against Notion before writes.

Expected domain shape:

- `kind`: `technical_issue`
- `template`: `linear_issue_markdown`
- `draft_profile`: a `$ticket-drafter` profile name, currently `notion_coding_projects`
- `tracker_page`: parent Coding Projects Tracker page
- `projects`: Projects database and data source mapping
- `tasks`: Tasks database, data source, and field mapping
- `defaults.status`: default task status
- `allowed_statuses`, `allowed_priorities`, `allowed_tags`: Notion schema values expected by this domain
- `tag_mapping`: source label to Notion `Tags` mapping

Do not hardcode tracker IDs in this reference file. Use the config, then fetch Notion to verify the page and data source schemas still match.

## Database Contract

The current Coding Projects Tracker uses one shared Tasks data source and project-specific linked views.

When creating a coding ticket:

1. Create the task page in the configured Tasks data source.
2. Set the configured task title field to the approved ticket title.
3. Set the configured status field to the configured default status unless the user explicitly asks for another valid status.
4. Set the configured project relation field to the selected project page URL.
5. Set the configured tags field using mapped Notion tags.
6. Set priority, due date, assignee, parent, or subtasks only when the user provides them or explicitly asks.

The per-project task databases shown inside project pages are linked database views. Do not create tasks inside those linked view database URLs as if they were separate data sources; use the shared Tasks data source from config.

## Project Selection

Always resolve the target project before drafting or creating a Coding Projects ticket.

- If the user names exactly one project and it matches a Projects row, use it after confirming the Notion fetch result.
- If the user does not name a project, ask which project to connect the ticket to.
- If multiple projects could match, show concise choices with project names and URLs.
- If no project matches, ask whether to create a new project or choose an existing one. Do not create a project unless the user explicitly asks.

Use this prompt style when a project is missing:

```markdown
Which Coding Projects Tracker project should this ticket be connected to?

Options I found:
1. [Project name] - [status/priority if available]
2. [Project name] - [status/priority if available]
```

## Drafting Contract

Use `$ticket-drafter` as the technical ticket drafting engine with the configured `draft_profile`. Defect drafts must keep the same Markdown section shape used for Linear issues:

```markdown
### The Problem

[Direct statement of what is broken, missing, or needed.]

### Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Technical Requirements

- [Technical requirement 1]
- [Technical requirement 2]

### Expected vs Actual

- **Expected:** [Expected behavior]
- **Actual:** [Current behavior]

### Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

For feature work with no bug reproduction, let `$ticket-drafter` classify the request as `implementation` and use its implementation ticket body. Do not invent reproduction steps.

## Tag Mapping

Map issue labels or inferred issue type into Notion `Tags` using the configured `tag_mapping`.

Default mapping intent:

- Bug or fix work -> `Fix`
- New functionality -> `Feature`
- Refactoring or cleanup -> `Refactor`
- Release or deployment work -> `Release`

Use only tags that exist in the fetched Tasks schema. If the mapped tag is missing from the schema, stop and report the mismatch rather than writing a malformed task.

## Create Workflow

1. Load Workflow Orchestrator Notion config.
2. Resolve the `coding_projects` domain.
3. Fetch the tracker page.
4. Fetch the configured Projects and Tasks data sources.
5. Verify configured field names exist and configured status/tag/priority values are valid.
6. Resolve or ask for the target project.
7. Draft via `$ticket-drafter` using the configured `draft_profile`.
8. Present the draft and ask the user to review it.
9. Create only after a clear approval signal such as `create it`, `add it`, `publish`, `looks good`, or equivalent.
10. Create the page in the configured Tasks data source with the approved Markdown as page content.
11. Report the created task title, selected project, and URL.

Use this property mapping shape for `notion-create-pages`; field names come from config:

```json
{
  "parent": {"data_source_id": "configured-tasks-data-source-id"},
  "pages": [
    {
      "properties": {
        "Task name": "Implement project-level task creation",
        "Status": "Not Started",
        "Tags": ["Feature"],
        "Project": ["selected-project-page-url"],
        "Priority": "Medium",
        "date:Due:start": "2026-06-01",
        "date:Due:is_datetime": 0
      },
      "content": "### The Problem\n\n..."
    }
  ]
}
```

Omit optional properties when they do not apply. For a single due date, set only `date:Due:start` and `date:Due:is_datetime`; set `date:Due:end` only when the user explicitly asks for a date range.

## Update Workflow

1. Identify the task by exact title, URL, page ID, Notion ID, or user-provided project context.
2. If more than one task matches, ask the user to choose.
3. Fetch the matching task page and Tasks data source before writing.
4. Update only the requested properties or content sections.
5. Preserve the issue-style Markdown body unless the user explicitly asks for another layout.
6. Preserve existing project relations unless the user explicitly asks to move the task to another project.

Common status updates:

- `done`, `complete`, `finished` -> `Done`
- `start`, `working on`, `in progress` -> `In Progress`
- `archive`, `hide`, `old` -> `Archived`
- `not started`, `todo`, `to do` -> `Not Started`

## Review Workflow

When reviewing Coding Projects tasks, ask for or infer one project first. Summarize in this order:

1. In Progress tasks.
2. Not Started tasks with due dates sorted by `Due`.
3. Not Started tasks without due dates.
4. Done or Archived tasks only if requested.
5. Parent tasks with subtasks grouped underneath when relation data is available.

Use this summary format:

```markdown
**Coding Projects: [Project name]**

**In Progress**
- [Priority] [Task] - due [date or no date]

**Not Started**
- [date/no date] [Priority] [Task] [Tags]

**Subtasks**
- [Parent Task]
- [Status] [Priority] [Subtask]
```

If there are no matching tasks, say `No matching Coding Projects tasks found for [Project name].`

## Quality Bar

- Keep technical ticket content identical in spirit to Linear issue drafts.
- Ask for project selection before writing.
- Use Notion relation values as page URLs.
- Do not invent project rows, tags, statuses, assignees, deadlines, or requirements.
- Do not publish directly from `$ticket-drafter`; Notion writes belong to `$workflow-orchestrator`.
- Stop on schema mismatch instead of writing partial data.
