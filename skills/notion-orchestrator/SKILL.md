---
name: notion-orchestrator
description: Route and orchestrate Notion-specific workflows through one entry point. Use when the user asks to create, draft, update, review, or place Notion content, especially Personal Tasks, and ask for the target page or database when it is not specified or safely inferred.
---

# Notion Orchestrator

Route and execute Notion workflows from one entry point.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `personal-task-draft`: convert loose personal task input into a reviewed Notion-ready task draft.
2. `personal-task-create`: create an approved personal task in the Personal Tasks database.
3. `personal-task-update`: update an existing personal task's title, status, due date, priority, URL, or structured body.
4. `personal-task-review`: fetch Personal Tasks and summarize active work, upcoming deadlines, or completed work.
5. `location-resolution`: resolve the target Notion page, database, or data source before any write.

If confidence is low, ask one focused clarification.

## Location Resolution Contract

- Ask where to implement the change when the user did not specify a destination and the destination cannot be safely inferred.
- Safely infer Personal Tasks only when the request clearly says personal task, personal reminder, errand, habit, goal, or non-school task.
- Do not infer School Tasks, Coding Tasks, Notes, or other databases from a generic task request.
- When multiple plausible Notion targets exist, present concise options with names and URLs if known.
- Before writing to a page or database, fetch the target and verify that its schema or page content matches the intended operation.
- Use Notion tools as source of truth. Do not fabricate page IDs, database IDs, data source IDs, views, or property names.

## Domain Templates

Use the relevant template from `references/` for formatting and field mapping.

Current supported template:

- `references/personal-tasks-template.md`: Personal Tasks drafting, creation, updating, and review.

Future domains, such as coding tasks or notes, must be added as new reference templates inside this skill folder. Do not create a separate skill for each Notion domain unless the user explicitly asks.

## Personal Tasks Contract

Load `references/personal-tasks-template.md` before drafting, creating, updating, or reviewing Personal Tasks.

Personal Task pages must use the four-section body from the template: `What It Is`, `How To Do It`, `Requirements`, and `Notes`.

Known Personal Tasks targets:

- Database: `https://www.notion.so/d176121a39804abb85be6e42bb83b7aa`
- Data source: `collection://c87de477-c2cd-4e76-ba7c-89086b5305d0`
- Parent page: `https://www.notion.so/f839c4af3611477ea4358285612e7fcf`

Treat these IDs as cached defaults, not permanent truth. Re-fetch before writes and fall back to Notion search for `Personal Tasks` if a fetch fails.

## Draft-First Writes

- For ambiguous or multi-field user input, draft the Notion entry first and ask the user to review it.
- Publish only after a clear approval signal such as `create it`, `add it`, `publish`, `looks good`, or equivalent.
- For simple direct commands with all required fields present, create or update without a review round if the target is clear.
- Never create sample data unless the user explicitly asks.

## Notion Write Safety

- Fetch the target page or data source immediately before any update.
- Prefer additive updates over replacing page content.
- When updating page content, use exact search-and-replace snippets from fresh `notion-fetch` output.
- If a database schema does not contain the required fields, stop and report the mismatch instead of writing partial or malformed entries.
- If a Notion MCP tool cannot perform a requested layout or view operation, complete the supported parts and report the exact limitation.

## Chat Summary Contract

After every write, report:

```md
Updated Notion:
- Target: [page/database name]
- Action: [created/updated/appended]
- URL: [Notion URL]
- Notes: [limitations or follow-up, or "None"]
```

For read-only reviews, summarize active work by status and due date, and include links when available.
