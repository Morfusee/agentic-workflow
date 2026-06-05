---
name: ticket-dump-creator
description: Create source-agnostic ticket or task dump files from normalized provider facts. Use when Linear, ClickUp, or another provider orchestrator has collected work item activity and needs the common activity-first dump contract, grouped summary, memory path, and Markdown output generated without provider-specific retrieval.
---

# Ticket Dump Creator

Create one Markdown dump from normalized work item facts supplied by a provider orchestrator.

## Boundaries

- Own dump creation only.
- Do not call Linear, ClickUp, Notion, or other provider tools to discover facts.
- Treat normalized input from the caller as source evidence.
- Ask one focused clarification if required normalized facts are missing and no fallback value is allowed.
- Preserve provider vocabulary through caller-provided labels.

## Required Provider Context

The invoking orchestrator must provide:

```yaml
provider: linear | clickup
provider_display_name: Linear | ClickUp
item_label: ticket | task
item_collection_label: tickets | tasks
item_collection_heading: Tickets | Tasks
memory_subpath: memory/tickets/<provider>/
requested_range: <date, date range, or "all relevant tickets/tasks">
dump_file_date: YYYY-MM-DD
generated_timestamp: <timestamp>
```

Use `provider`, `item_label`, `item_collection_label`, and `item_collection_heading` exactly as supplied. Do not silently convert Linear tickets to tasks or ClickUp tasks to tickets.

## Required Normalized Item Fields

Each item must provide:

```yaml
id: <provider item id>
title: <item title>
status: <provider status>
activity_date: YYYY-MM-DD
url: <provider URL or "Not available">
initial_dev_assignee: <name or "Not available">
testing_actors: <comma-separated names or "None identified">
my_role: dev-owner | contributor | tester-only
inclusion_reasons:
  - Created by me | assigned to me | commented on by me | status changed by me
description: <full description or "No description provided.">
comments:
  - author: <name>
    timestamp: <timestamp>
    body: <comment body>
activity_timeline:
  - timestamp: <timestamp>
    type: created | assigned | commented | moved status | closed | tested
    summary: <brief factual summary>
in_range_day_mapping:
  - date: YYYY-MM-DD
    actions:
      - <qualifying user action with timestamp>
activity_notes: <brief factual summary>
```

Fallbacks allowed by this skill:

- `url`: `Not available`
- `initial_dev_assignee`: `Not available`
- `testing_actors`: `None identified`
- `description`: `No description provided.`
- `comments`: render `No comments found.` when empty

Do not invent missing `id`, `title`, `status`, `activity_date`, `my_role`, `inclusion_reasons`, `activity_timeline`, `in_range_day_mapping`, or `activity_notes`.

## Inclusion Rules

The provider orchestrator should already have applied these rules. Re-check the normalized input for consistency before writing:

1. Include only items with the user's qualifying in-range activity.
2. Qualifying activity includes user comments, user status changes, explicit in-range assignment events, explicit close or done events, and created-by-user events only when creation is in range.
3. Exclude items with no qualifying in-range user activity.
4. Include all statuses by default after activity qualification.
5. Apply status restrictions only when the caller says the user requested a subset.
6. Use the timestamp of qualifying user activity to determine `activity_date`.
7. Preserve separate same-day and cross-day qualifying user actions in `in_range_day_mapping`.

## Role Attribution Rules

- Use `dev-owner` only when explicit evidence shows the user was the initial dev assignee or owner.
- Use `contributor` only when explicit user development evidence exists and the user is not the initial dev owner.
- Use `tester-only` when in-range user activity is only testing, verification, or QA-style comments.
- Never infer implementation authorship from testing comments, QA-only updates, subscriptions, watching, or following.

## Output Path

Write one file under the canonical memory root:

```text
memory/tickets/<provider>/YYYY-W##/YYYY-MM-DD-ticket-dump.md
```

Use ISO week folders such as `2026-W23`. Create missing directories. Do not overwrite existing files; append suffixes such as `-1` and `-2` before `.md` on collisions.

## Chat Summary Contract

Print a concise grouped summary after writing the dump:

```md
[YYYY-MM-DD]

[Status]
- [ITEM-ID]: [Item title]

[Another Status]
- [ITEM-ID]: [Item title]
```

For requested ranges, include every day in the range even when no items qualify. For empty days, print `- No qualifying [item_collection_label].`

Always confirm the saved file path.

## Dump File Contract

Write this structure:

```md
# Ticket Dump

Generated: [generated_timestamp]
Requested range: [requested_range]
Dump file date: [dump_file_date]

---

# Grouped Summary

[YYYY-MM-DD]

## [Status]
- [ITEM-ID]: [Item title]

---

# Manual Tasks

Entries here are not tracked in [provider_display_name]. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## [TASK-ID]: [Task title]

Status: [Done / In Progress / To Do]
Activity date: [YYYY-MM-DD]
My role: dev-owner

### Description
[Task description or "No description provided."]

### Activity Notes
[Brief factual summary of work performed.]

---

# All Scraped [item_collection_heading]

## [ITEM-ID]: [Item title]

Status: [status]
Activity date: [YYYY-MM-DD]
URL: [provider URL or "Not available"]
Initial dev assignee: [name or "Not available"]
Testing actors: [comma-separated names or "None identified"]
My role for this [item_label]: [dev-owner / contributor / tester-only]

### Why this [item_label] was included
[Created by me / assigned to me / commented on by me / status changed by me]

### Description
[Full description or "No description provided."]

### Comments
#### [comment author] - [timestamp]
[comment body]

[Repeat per comment, or "No comments found."]

### Activity Timeline
- [timestamp] [activity type]: [summary]

### In-Range Day Mapping
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]

### Activity Notes
[Brief factual summary of meaningful user activity.]
```

## Rules

1. Do not fabricate item details, ownership, chronology, or outcomes.
2. Keep parsing and output structures stable for downstream stand-up workflows.
3. Preserve full activity detail; do not collapse distinct actions.
4. Keep all scraped items in the same file even when activity spans multiple days.
5. Keep the manual tasks section empty except for the template guidance text.
6. Do not query provider APIs during dump creation.
