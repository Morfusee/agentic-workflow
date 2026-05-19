---
title: ClickUp Dump And Stand-Up Contract
---

# ClickUp Dump And Stand-Up Contract

Read this reference before running `dump-creation`, `standup-from-dump`, or `full-flow`.

## Dump Creation

Use ClickUp tools as source of truth. Do not infer task facts, ownership, chronology, or outcomes.

1. Resolve the target date/range. Use explicit user dates for filenames, otherwise current local date. Fetch all relevant tasks when no range is provided.
2. Include a task only when the user's own qualifying activity occurred in-range: comment, status change, explicit close, explicit assignment, or task creation by the user. Watching/following never counts.
3. After activity filtering, include all statuses unless the user requests a subset. Deduplicate by task ID.
4. Compute activity date from the qualifying activity timestamp, preferring explicit status changes, then comments, assignment, qualifying creation, and only then updated date when it clearly reflects allowed user action.
5. Compute role from explicit evidence: `dev-owner`, `contributor`, or `tester-only`. Testing/comments/QA-only updates never imply implementation authorship.
6. For requested ranges, evaluate every day and emit empty days as `- No qualifying tasks.` Group by activity date, then status.
7. Write under the canonical memory root from OpenCode global `AGENTS.md`, using `tickets/clickup/YYYY-W##/YYYY-MM-DD-ticket-dump.md`. Create directories and never overwrite; use `-1`, `-2`, etc.
8. Preserve full detail: all scraped tasks in one file, full descriptions/comments when available, distinct same-day actions, cross-day mappings, and timestamped activity timeline.
9. Print grouped summary to chat and confirm saved path.
10. Use fallback-safe retrieval: resolve current user with `clickup_resolve_assignees(["me"])`; collect candidates through both `clickup_filter_tasks` and `clickup_search`; merge/dedupe; load each task with `clickup_get_task` and comments with `clickup_get_task_comments`; determine activity from explicit evidence.

Chat summary style:

```md
[YYYY-MM-DD]

[Status]
- [TASK-ID]: [Task title]
```

Dump file structure:

```md
# Ticket Dump

Generated: [timestamp]
Requested range: [range or "all relevant tasks"]
Dump file date: [YYYY-MM-DD]

---

# Grouped Summary

[YYYY-MM-DD]

## [Status]
- [TASK-ID]: [Task title]

---

# Manual Tasks

Entries here are not tracked in ClickUp. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## [MANUAL-###]: [Task title]

Status: [Done / In Progress / To Do]
Activity date: [YYYY-MM-DD]
My role: dev-owner

### Description
[Task description or "No description provided."]

### Activity Notes
[Brief factual summary of work performed.]

---

# All Scraped Tasks

## [TASK-ID]: [Task title]

Status: [status]
Activity date: [YYYY-MM-DD]
URL: [ClickUp URL or "Not available"]
Initial dev assignee: [name or "Not available"]
Testing actors: [comma-separated names or "None identified"]
My role for this task: [dev-owner / contributor / tester-only]

### Why this task was included
[Created by me / assigned to me / commented on by me / status changed by me]

### Description
[Full task description or "No description provided."]

### Comments
#### [comment author] - [timestamp]
[comment body]

[Repeat per comment, or "No comments found."]

### Activity Timeline
- [timestamp] [activity type: created / assigned / commented / moved to [status] / closed / tested]

### In-Range Day Mapping
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]

### Activity Notes
[Brief factual summary of meaningful user activity using explicit verbs such as `tested`, `commented`, `moved to [status]`, `closed`.]
```

## Stand-Up From Dump

Do not query ClickUp unless the user explicitly asks.

1. Resolve the latest compatible dump under the canonical memory root, preferring latest ISO week and latest `YYYY-MM-DD-ticket-dump.md`. Print exact path. If missing, ask user to run dump creation.
2. Parse `# All Scraped Tasks`, `# Manual Tasks`, `# Unselected Tasks`, and `# Selected Tasks` as rerun index only.
3. Also scan the most recent previous dump in the same week for `# Unselected Tasks`; carry those forward until selected.
4. Present one numbered list: current scraped/manual tasks first, then `[Carry-over]` unselected tasks. Prefix manual items with `[Manual]`.
5. Ask exactly: `Which tasks do you want to include in your stand-up? You can reply with task numbers, task IDs, or all. To add a manual task not tracked in ClickUp, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]". To add a next-day plan, describe it as "Plan: [what you intend to work on next]".`
6. Accept `all`, indexes, task IDs, and clear natural language. Parse `Manual:` and `Plan:` entries. Assign next manual ID as `MANUAL-###`; default missing manual status to `Done` and description to `No description provided.` Ask one short clarification if ambiguous.
7. Normalize only selected items for `$standup-generator`: title, status, activity date, role/ownership, chronology evidence, notes, comments, and test results. Pass explicit next-day plan only if provided. Never infer plans from open, remaining, or unselected work. Treat old `# Stand-up Script` prose as output-only.
8. Generate conversational factual script with `$standup-generator`; do not speak task IDs unless requested.
9. Update the same dump in place: write `# Stand-up Script` at top, keep `# Selected Tasks` as index, replace `# Unselected Tasks` with unselected current plus carry-over pool, preserve `# All Scraped Tasks`, and append new manual tasks without rewriting existing ones.

Updated dump structure:

```md
# Stand-up Script

Yesterday, I [evidence-based narrative generated from selected items].

Today, I plan to [explicit plan provided by the user].

No major blockers right now.

---

# Selected Tasks

- [TASK-ID]: [Task title]
  - Status: [status]
  - Activity date: [YYYY-MM-DD]
  - URL: [ClickUp URL]
  - Reference: `# All Scraped Tasks` -> `## [TASK-ID]: [Task title]`
  - Stand-up relevance: [Why selected]

- [MANUAL-###]: [Task title]
  - Status: [status]
  - Activity date: [YYYY-MM-DD]
  - Reference: `# Manual Tasks` -> `## [MANUAL-###]: [Task title]`
  - Stand-up relevance: [Why selected]

---

# Unselected Tasks

Carry-over tasks not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- [TASK-ID]: [Task title]
  - Source dump: [YYYY-MM-DD]
  - Status as of [YYYY-MM-DD]: [status]
  - Role: [dev-owner / contributor / tester-only]
  - Activity notes: [Brief summary of work done]

---

# Manual Tasks

[Keep all manual tasks here. Append new entries; preserve existing ones.]

---

# All Scraped Tasks

[Keep all scraped task details here, including selected and unselected tasks.]
```

## Range And Outcome Reporting

- Single-date request: spawn one agent. Date range: expand daily and spawn one agent per date in parallel.
- Full flow per date: dump creation, then stand-up from produced dump; stop that date branch on dump failure and continue others.
- End with per-date `success`/`failed`, path when available, and concise failure reason.
