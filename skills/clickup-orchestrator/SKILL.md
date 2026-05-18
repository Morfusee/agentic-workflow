---
name: clickup-orchestrator
description: Route and orchestrate ClickUp-specific workflows through one entry point. Use when the user asks for ClickUp ticket dump creation, stand-up generation from ClickUp dumps, full ClickUp stand-up flow, ClickUp-context issue drafting, or ClickUp-context QA comment formatting.
---

# ClickUp Orchestrator

Route and execute ClickUp workflows from one entry point.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `dump-creation`: collect ClickUp activity and write a ticket dump.
2. `standup-from-dump`: read dump, select tickets, generate spoken stand-up, update dump.
3. `full-flow`: run dump creation then stand-up from that dump.
4. `issue-draft`: route to `$issue-drafter` only when request is clearly ClickUp-contextual. Instruct `$issue-drafter` to output the final draft in the ClickUp ticket format convention defined below (Description → Scope → Deliverable) instead of the default bug-report format.
5. `qa-comment`: route to `$qa-comment-formatter` when the user provides QA results, pass/fail checks, or test observations to format into a ClickUp ticket comment. If the request includes a ClickUp task ID or task URL, pass it through as `clickup_task_id` so the formatter publishes directly to that task.

If confidence is low, ask one focused clarification.

## ClickUp Ticket Format Convention

When creating or drafting ClickUp tickets (whether directly or via `$issue-drafter`), apply the following formatting rules derived from the workspace's Sprint-list ticket conventions.

### Ticket Naming

- Use imperative, action-oriented titles: verb-first, concise, no trailing period.
- Examples: `Implement email header template`, `Analyze Lambda Function Errors in Enrollment Workflows`, `Define Traffic Light Thresholds for Operational KPIs`.

### Description Format

```
## Description
<1-2 sentence purpose and context>

## Scope
- actionable work item
- actionable work item

## Deliverable
- concrete acceptance criteria / definition of done
```

- **## Description**: what the ticket is about, brief context. Keep to 1-2 sentences.
- **## Scope**: bullet list of specific work items to complete. Use imperative action verbs.
- **## Deliverable**: bullet list of concrete acceptance criteria. These answer "how do we know this is done?"
- Use `##` (H2) for all section headers in the description body. Do not use `**bold**` headers.
- Separate sections with a blank line.

## Agent Execution Contract

- This skill owns per-date agent spawning.
- Single-date request: spawn one agent.
- Date-range request: expand to daily dates and spawn one agent per date in parallel.
- Pass through model and reasoning effort when provided.
- In orchestrated mode, do not spawn nested agents from child branches unless explicitly requested.

## Full-Flow Contract

For each date branch:

1. Run `dump-creation` for that exact date.
2. If successful, run `standup-from-dump` against that produced dump.
3. Pass through explicit stand-up selection intent when provided.
4. On dump failure for a date, stop that date branch and continue others.

## dump-creation Branch

Create one daily Markdown dump of relevant ClickUp task activity and print a concise grouped summary.

### Prerequisites

- A ClickUp integration must be active so ClickUp task, comment, and status tools are available.
- Use ClickUp tools as source of truth. Do not infer or fabricate ticket facts.

### Execution Steps

1. Resolve target date and requested range.
   - Use explicit user date (`yesterday`, `2026-05-14`) for filename when provided.
   - Otherwise use current local date for filename.
   - Filter by user-provided range when present.
   - Fetch all relevant tasks when no range is provided.

2. Apply activity-first inclusion logic.
   - Include a task only when the user's own activity occurred within the requested range.
   - Qualifying activities:
     - user commented on the task
     - user changed task status
     - user explicitly marked task closed
     - explicit assignment event in-range (not watching/following)
     - task created by user only when create event is in-range
   - Exclude tasks with no qualifying in-range user activity.

3. Apply status handling after activity filtering.
   - First filter by qualifying user activity in-range.
   - Include all statuses by default after activity qualification.
   - Apply explicit status restriction only when user requests a subset.
   - Deduplicate by task identifier across activity sources.

4. Compute activity date per task.
   - Use timestamp of qualifying user activity causing inclusion.
   - Prefer explicit user status-change timestamp.
   - Otherwise use user comment timestamp.
   - Otherwise explicit assignment event timestamp.
   - Otherwise created date only when creation qualifies.
   - Use updated date only when it clearly reflects allowed user actions.

5. Compute attribution and role per task.
   - Identify initial dev assignee/owner from explicit history when available.
   - Identify testing-only activity actors from explicit test/verification actions.
   - Set `My role for this task` as `dev-owner`, `contributor`, or `tester-only`.
   - Mark `tester-only` when in-range user activity is only testing/verification/testing comments and no explicit in-range dev evidence exists.
   - Do not infer implementation authorship from comments/testing/QA-only updates.
   - Mark `contributor` only with explicit user development evidence and user is not initial dev owner.
   - Mark `dev-owner` only with explicit evidence that user is initial dev assignee/owner.

6. Group summary data with full date-range coverage.
   - For requested ranges, evaluate every day in the range.
   - Emit every day in `# Grouped Summary`, even with no tasks.
   - For empty days print `- No qualifying tasks.`.
   - Group by activity date `YYYY-MM-DD`, then by status.

7. Build output path and prevent overwrite.
   - Root path: `memory/tickets/clickup/`.
   - Week folder: `YYYY-W##` (ISO week).
   - File format: `YYYY-MM-DD-ticket-dump.md`.
   - Create missing directories.
   - Do not overwrite; use suffixes `-1`, `-2` on collisions.

8. Write one dump file per run.
   - Keep all scraped tasks in same file even when activity spans multiple days.
   - Write `No description provided.` when description is missing.
   - Write `No comments found.` when comments are missing.
   - Preserve full activity detail; do not collapse distinct actions.
   - If user has multiple qualifying same-day actions on a task, keep separate timestamped entries.
   - If user has qualifying actions on different in-range days for same task, preserve all with timestamps and reflect each day in grouped summary.

9. Print grouped summary to chat and confirm saved file path.

10. Use fallback-safe ClickUp retrieval strategy.
    - Resolve current user via `clickup_resolve_assignees` with `["me"]` and store user id/name/email.
    - Collect candidate tasks using multiple approaches:
      - `clickup_filter_tasks` with relevant filters (date, assignee, status).
      - `clickup_search` by keyword/user name for broader coverage.
    - Merge and deduplicate candidates by task identifier.
    - For each candidate, load detail via `clickup_get_task`.
    - For each candidate, load comments via `clickup_get_task_comments`.
    - Determine qualifying user activity from explicit task/comment evidence.
    - Do not rely on a single search endpoint as sole source.

### Chat Summary Contract

Use this exact style:

`[YYYY-MM-DD]`

`[Status]`
- `[TASK-ID]: [Task title]`

`[Another Status]`
- `[TASK-ID]: [Task title]`

### Dump File Contract

Use this structure:

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

## [TASK-ID]: [Task title]

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
- [timestamp] [activity type...]

### In-Range Day Mapping
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]

### Activity Notes
[Brief factual summary of meaningful user activity on this task. Use explicit action verbs like `tested`, `commented`, `moved to [status]`, `closed`.]
```

## standup-from-dump Branch

Read latest dump, let user choose items, generate spoken stand-up via `$standup-generator`, and update the same dump file.

### Prerequisites

- A compatible dump file exists under `memory/tickets/clickup/`.
- Prefer latest ISO week folder `YYYY-W##` and latest `YYYY-MM-DD-ticket-dump.md`.
- If no compatible dump exists, report that and instruct user to run dump creation.

### Unselected Task Carry-Over

Tasks not selected for stand-up persist across days. Any task in `# Unselected Tasks` of a previous dump reappears as a selectable item in future stand-up prompts until the user selects it.

### Execution Steps

1. Resolve dump file.
   - Print exact dump path used.
   - Parse `# All Scraped Tasks`, `# Manual Tasks`, and `# Unselected Tasks`.
   - If present, parse `# Selected Tasks` as rerun index only.
   - Also scan the most recent previous dump file (previous day or earlier in the same week folder) for `# Unselected Tasks`. Merge those carry-over tasks into the selectable list so nothing falls through the cracks across days.

2. Present selectable items.
   - Show one numbered list with scraped tasks, manual tasks, and carry-over unselected tasks.
   - For manual tasks, prefix ID display with `[Manual]`.
   - For carry-over unselected tasks from previous dumps, prefix ID display with `[Carry-over]`.
   - Group visually: current dump's tasks first, then carry-over tasks.

3. Collect selection with exact prompt.
   - `Which tasks do you want to include in your stand-up? You can reply with task numbers, task IDs, or all. To add a manual task not tracked in ClickUp, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]".`

4. Interpret selection.
   - Accept `all`, numeric indexes, task IDs, and clear natural-language selections.
   - Parse new manual tasks from `Manual: [title] -- [status] [description]`.
   - Assign next manual ID as `MANUAL-###`.
   - Default status to `Done` and description to `No description provided.` when omitted.
   - If ambiguous, ask one short clarification.

5. Build normalized input for `$standup-generator`.
   - Convert each selected task/manual task into source-agnostic evidence:
     - title, status, activity date
     - role/ownership metadata
     - chronology evidence (activity flow, notes, comments, test results)
   - Pass only selected items as evidence.
   - Treat existing `# Stand-up Script` prose as output-only, never evidence.

6. Generate script via base principles.
   - Apply `$standup-generator` narrative, chronology, attribution, and blocker rules.
   - Keep script conversational and factual.
   - Do not speak task IDs unless user explicitly asks.

7. Update dump file in place.
   - Write `# Stand-up Script` at top.
   - Keep `# Selected Tasks` as a lightweight reference/index.
   - Write `# Unselected Tasks` with all tasks not selected this run (from both current dump and carry-over pool). Each entry records the source dump date, status as of that date, role, and activity notes. This section replaces any previous `# Unselected Tasks` — selected items are removed, unselected items carry forward.
   - Preserve full `# All Scraped Tasks` unchanged as historical source.
   - Append new entries to `# Manual Tasks`; never remove/rewrite existing entries.

### Updated Dump Contract

Use this structure:

```md
# Stand-up Script

Yesterday, I [evidence-based narrative generated from selected items].

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

## Outcome Reporting

- Continue processing remaining dates when one date branch fails.
- At end of run, print per-date results with:
  - status (`success` or `failed`)
  - dump or output path when available
  - concise failure reason when failed

## Rules

1. Do not fabricate task details, ownership, chronology, or outcomes.
2. Keep this skill as the single ClickUp workflow entrypoint.
3. Keep parsing and output structures stable for downstream consumers.
4. Never treat watching as assignment.
5. Never infer implementation authorship from testing/comments/QA-only evidence.
6. For dump branch, include every day in requested range, including empty days.
7. For stand-up branch, never query ClickUp unless user explicitly asks.
8. For full-flow ranges, keep partial successes visible and do not hide per-date failures.
