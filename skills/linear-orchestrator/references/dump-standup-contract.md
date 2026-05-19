---
title: Linear Dump And Stand-Up Contract
---

# Linear Dump And Stand-Up Contract

Read this reference before running `dump-creation`, `standup-from-dump`, or `full-flow`.

## Dump Creation

Use Linear tools as source of truth. Do not infer ticket facts, ownership, chronology, or outcomes.

1. Resolve the target date/range. Use explicit user dates for filenames, otherwise current local date. Fetch all relevant tickets when no range is provided.
2. Include a ticket only when the user's own qualifying activity occurred in-range: comment, status change, explicit `Done`, explicit assignment, or ticket creation by the user. Subscription/watching never counts.
3. After activity filtering, include all statuses unless the user requests a subset. Deduplicate by ticket ID.
4. Compute activity date from the qualifying activity timestamp, preferring explicit status changes, then comments, assignment, qualifying creation, and only then updated date when it clearly reflects allowed user action.
5. Compute role from explicit evidence: `dev-owner`, `contributor`, or `tester-only`. Testing/comments/QA-only updates never imply implementation authorship.
6. For requested ranges, evaluate every day and emit empty days as `- No qualifying tickets.` Group by activity date, then status.
7. Write under the canonical memory root from OpenCode global `AGENTS.md`, using `tickets/linear/YYYY-W##/YYYY-MM-DD-ticket-dump.md`. Create directories and never overwrite; use `-1`, `-2`, etc.
8. Preserve full detail: all scraped tickets in one file, full descriptions/comments when available, distinct same-day actions, cross-day mappings, and timestamped activity timeline.
9. Print grouped summary to chat and confirm saved path.
10. Unless the user explicitly requested dump-only behavior, immediately present the stand-up selection prompt after dump creation while keeping grouped summary/path output unchanged.
11. Use fallback-safe retrieval: resolve current user with `get_user me`; collect candidates without assignee bias through `list_issues` by `createdAt` and `updatedAt`; merge/dedupe; load detail with `get_issue` and comments with `list_comments`; determine activity from explicit evidence.

Chat summary style:

```md
[YYYY-MM-DD]

[Status]
- [TICKET-ID]: [Ticket title]
```

Dump file structure:

```md
# Ticket Dump

Generated: [timestamp]
Requested range: [range or "all relevant tickets"]
Dump file date: [YYYY-MM-DD]

---

# Grouped Summary

[YYYY-MM-DD]

## [Status]
- [TICKET-ID]: [Ticket title]

---

# Manual Tasks

Entries here are not tracked in Linear. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

## [MANUAL-###]: [Task title]

Status: [Done / In Progress / To Do]
Activity date: [YYYY-MM-DD]
My role: dev-owner

### Description
[Task description or "No description provided."]

### Activity Notes
[Brief factual summary of work performed.]

---

# All Scraped Tickets

## [TICKET-ID]: [Ticket title]

Status: [status]
Activity date: [YYYY-MM-DD]
URL: [Linear URL or "Not available"]
Initial dev assignee: [name or "Not available"]
Testing actors: [comma-separated names or "None identified"]
My role for this ticket: [dev-owner / contributor / tester-only]

### Why this ticket was included
[Created by me / assigned to me / commented on by me / status changed by me]

### Description
[Full ticket description or "No description provided."]

### Comments
#### [comment author] - [timestamp]
[comment body]

[Repeat per comment, or "No comments found."]

### Activity Timeline
- [timestamp] [activity type: created / assigned / commented / moved to In Progress / moved to In Review / moved to Done / moved to Todo / tested]

### In-Range Day Mapping
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]

### Activity Notes
[Brief factual summary of meaningful user activity using explicit verbs such as `tested`, `commented`, `moved to In Progress`, `moved to Done`.]
```

## Stand-Up From Dump

Do not query Linear unless the user explicitly asks.

1. Resolve the latest compatible dump under the canonical memory root, preferring latest ISO week and latest `YYYY-MM-DD-ticket-dump.md`. Print exact path. If missing, ask user to run dump creation.
2. Parse `# All Scraped Tickets`, `# Manual Tasks`, `# Unselected Tickets`, and `# Selected Tickets` as rerun index only.
3. Also scan the most recent previous dump in the same week for `# Unselected Tickets`; carry those forward until selected.
4. Present one numbered list: current scraped/manual tickets first, then `[Carry-over]` unselected tickets. Prefix manual items with `[Manual]`.
5. Ask exactly: `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all. To add a manual task not tracked in Linear, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]". To add a next-day plan, describe it as "Plan: [what you intend to work on next]".`
6. Accept `all`, indexes, ticket IDs, and clear natural language. Parse `Manual:` and `Plan:` entries. Assign next manual ID as `MANUAL-###`; default missing manual status to `Done` and description to `No description provided.` Ask one short clarification if ambiguous.
7. Normalize only selected items for `$standup-generator`: title, status, activity date, role/ownership, chronology evidence, notes, comments, and test results. Pass explicit next-day plan only if provided. Never infer plans from open, remaining, or unselected work. Treat old `# Stand-up Script` prose as output-only.
8. Generate conversational factual script with `$standup-generator`; do not speak ticket IDs unless requested.
9. Update the same dump in place: write `# Stand-up Script` at top, keep `# Selected Tickets` as index, replace `# Unselected Tickets` with unselected current plus carry-over pool, preserve `# All Scraped Tickets`, and append new manual tasks without rewriting existing ones.

Updated dump structure:

```md
# Stand-up Script

Yesterday, I [evidence-based narrative generated from selected items].

Today, I plan to [explicit plan provided by the user].

No major blockers right now.

---

# Selected Tickets

- [TICKET-ID]: [Ticket title]
  - Status: [status]
  - Activity date: [YYYY-MM-DD]
  - URL: [Linear URL]
  - Reference: `# All Scraped Tickets` -> `## [TICKET-ID]: [Ticket title]`
  - Stand-up relevance: [Why selected]

- [MANUAL-###]: [Task title]
  - Status: [status]
  - Activity date: [YYYY-MM-DD]
  - Reference: `# Manual Tasks` -> `## [MANUAL-###]: [Task title]`
  - Stand-up relevance: [Why selected]

---

# Unselected Tickets

Carry-over tickets not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

- [TICKET-ID]: [Ticket title]
  - Source dump: [YYYY-MM-DD]
  - Status as of [YYYY-MM-DD]: [status]
  - Role: [dev-owner / contributor / tester-only]
  - Activity notes: [Brief summary of work done]

---

# Manual Tasks

[Keep all manual tasks here. Append new entries; preserve existing ones.]

---

# All Scraped Tickets

[Keep all scraped ticket details here, including selected and unselected tickets.]
```

## Range And Outcome Reporting

- Single-date request: spawn one agent. Date range: expand daily and spawn one agent per date in parallel.
- Full flow per date: dump creation, then stand-up from produced dump; stop that date branch on dump failure and continue others.
- End with per-date `success`/`failed`, path when available, and concise failure reason.
