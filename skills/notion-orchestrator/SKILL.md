---
name: notion-orchestrator
description: Route and orchestrate Notion-specific workflows through one entry point. Use when the user asks to create, draft, update, review, or place Notion content, especially Personal Tasks or Coding Projects Tracker tickets, and ask for the target page, database, or project when it is not specified or safely inferred.
---

# Notion Orchestrator

Route and execute Notion workflows from one entry point.

## Config Contract

Load `skill-configs/notion-orchestrator.json` from the canonical memory root defined in OpenCode's global AGENTS.md at the start of every Notion workflow.

The config owns volatile Notion facts:

- domain names and trigger hints
- database, data source, tracker page, and parent page URLs
- field names and write aliases
- default statuses and allowed statuses, priorities, and tags
- template keys and external draft profiles

Reference templates own behavior. Do not put drafting prose, Markdown section instructions, or multi-step workflow logic into config.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `domain-resolution`: resolve the configured Notion domain before any draft, review, update, or write.
2. `personal-task-draft`: convert loose personal task input into a reviewed Notion-ready task draft.
3. `personal-task-create`: create an approved personal task in the Personal Tasks database.
4. `personal-task-update`: update an existing personal task's title, status, due date, priority, URL, relation, or structured body.
5. `personal-task-review`: fetch Personal Tasks and summarize active work, upcoming deadlines, or completed work.
6. `coding-ticket-draft`: draft a Coding Projects Tracker technical ticket using `$issue-drafter` and the configured draft profile.
7. `coding-ticket-create`: create an approved Coding Projects Tracker task in the configured shared Tasks data source.
8. `coding-ticket-update`: update an existing Coding Projects task's fields, project relation, or Markdown body.
9. `coding-ticket-review`: fetch Coding Projects tasks for a selected project and summarize active work.
10. `location-resolution`: resolve the target Notion page, database, data source, or project before any write.

If confidence is low, ask one focused clarification.

## Location Resolution Contract

- Ask where to implement the change when the user did not specify a destination and the destination cannot be safely inferred.
- Safely infer Personal Tasks only when the request clearly says personal task, personal reminder, errand, habit, goal, or non-school task.
- Safely infer Coding Projects only when the request clearly says coding project, coding ticket, technical ticket, project task, or names a configured Coding Projects Tracker project.
- Do not infer School Tasks, Notes, or other databases from a generic task request.
- When multiple plausible Notion targets exist, present concise options with names and URLs if known.
- Before writing to a page or database, fetch the target and verify that its schema or page content matches the intended operation.
- Use Notion tools as source of truth. Do not fabricate page IDs, database IDs, data source IDs, views, or property names.

## Domain Resolution Contract

Use the loaded config's `domains` map to resolve Notion workflows.

- Match explicit user wording against domain names and configured trigger hints.
- If the request is a technical issue or bug but mentions Notion/Coding Projects, choose `coding_projects`.
- If the request is a lightweight personal reminder/task, choose `personal_tasks`.
- If multiple domains match or confidence is low, ask one focused clarification.
- If a configured domain references a template this skill does not know, stop and report the unsupported template key.

## Domain Templates

Use the relevant template from `references/` for formatting and field mapping.

Current supported templates:

- `references/personal-tasks-template.md`: Personal Tasks drafting, creation, updating, and review.
- `references/coding-projects-template.md`: Coding Projects Tracker technical ticket drafting, creation, updating, and review.

Future domains, such as coding tasks or notes, must be added as new reference templates inside this skill folder. Do not create a separate skill for each Notion domain unless the user explicitly asks.

## Personal Tasks Contract

Load `references/personal-tasks-template.md` before drafting, creating, updating, or reviewing Personal Tasks.

Personal Task pages and database-backed subtasks must use the four-section body from the template: `What It Is`, `How To Do It`, `Requirements`, and `Notes`.

Personal Tasks targets are configured in `skill-configs/notion-orchestrator.json` under `domains.personal_tasks`. Treat config values as the only cached target source. Re-fetch before writes and fall back to Notion search for the configured domain name if a fetch fails.

## Coding Projects Contract

Load `references/coding-projects-template.md` before drafting, creating, updating, or reviewing Coding Projects Tracker tasks.

Coding Projects technical tickets must use the Linear-style issue body from `$issue-drafter`: `The Problem`, `Steps to Reproduce`, `Technical Requirements`, `Expected vs Actual`, and `Acceptance Criteria`.

Coding Projects targets are configured in `skill-configs/notion-orchestrator.json` under `domains.coding_projects`. Treat config values as the only cached target source. Re-fetch before writes and fall back to Notion search for the configured domain name if a fetch fails.

Always resolve the project relation before creating a Coding Projects task. Ask which project to connect when the request does not specify exactly one configured project.

Do not publish Coding Projects tasks directly from `$issue-drafter`; use `$issue-drafter` only to draft approved issue Markdown and use this skill for Notion schema validation and page creation.

## Draft-First Writes

- For ambiguous or multi-field user input, draft the Notion entry first and ask the user to review it.
- Publish only after a clear approval signal such as `create it`, `add it`, `publish`, `looks good`, or equivalent.
- For simple direct commands with all required fields present, create or update without a review round if the target is clear.
- Never create sample data unless the user explicitly asks.
- For Coding Projects, the target is not clear until the project relation is resolved.

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
