---
name: linear-orchestrator
description: Route and orchestrate Linear-specific workflows through one entry point. Use when the user asks for Linear ticket dump creation, stand-up generation from Linear dumps, full Linear stand-up flow, Linear-context issue drafting, Linear-context weekly ticket slideshow preparation, or Linear-context QA comment formatting.
---

# Linear Orchestrator

Route and execute Linear workflows from one entry point.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `dump-creation`: collect Linear activity and write a ticket dump.
2. `standup-from-dump`: read dump, select tickets, generate spoken stand-up, update dump.
3. `full-flow`: run dump creation then stand-up from that dump.
4. `issue-draft`: route to `$issue-drafter` only when request is clearly Linear-contextual.
5. `weekly-slideshow`: route to `$weekly-ticket-slideshow-generator` only when request is clearly Linear-contextual.
6. `qa-comment`: route to `$qa-comment-formatter` when the user provides QA results, pass/fail checks, or test observations to format into a Linear ticket comment. If the request includes a Linear issue ID, ticket identifier, or issue URL, pass it through as `linear_issue_id` so the formatter publishes directly to that issue.

If confidence is low, ask one focused clarification.

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

Create one daily Markdown dump of relevant Linear ticket activity and print a concise grouped summary.

### Prerequisites

- A Linear integration must be active so Linear issue, comment, and status tools are available.
- Use Linear tools as source of truth. Do not infer or fabricate ticket facts.

### Execution Steps

1. Resolve target date and requested range.
- Use explicit user date (`yesterday`, `2026-05-14`) for filename when provided.
- Otherwise use current local date for filename.
- Filter by user-provided range when present.
- Fetch all relevant tickets when no range is provided.

2. Apply activity-first inclusion logic.
- Include a ticket only when the user's own activity occurred within the requested range.
- Qualifying activities:
- user commented on the ticket
- user changed ticket status (`In Progress`, `In Review`, `Done`, `Todo`)
- user explicitly marked ticket `Done`
- explicit assignment event in-range (not subscription/watching)
- ticket created by user only when create event is in-range
- Exclude tickets with no qualifying in-range user activity.

3. Apply status handling after activity filtering.
- First filter by qualifying user activity in-range.
- Include all statuses by default after activity qualification.
- Apply explicit status restriction only when user requests a subset.
- Deduplicate by ticket identifier across activity sources.

4. Compute activity date per ticket.
- Use timestamp of qualifying user activity causing inclusion.
- Prefer explicit user status-change timestamp.
- Otherwise use user comment timestamp.
- Otherwise explicit assignment event timestamp.
- Otherwise created date only when creation qualifies.
- Use updated date only when it clearly reflects allowed user actions.

5. Compute attribution and role per ticket.
- Identify initial dev assignee/owner from explicit history when available.
- Identify testing-only activity actors from explicit test/verification actions.
- Set `My role for this ticket` as `dev-owner`, `contributor`, or `tester-only`.
- Mark `tester-only` when in-range user activity is only testing/verification/testing comments and no explicit in-range dev evidence exists.
- Do not infer implementation authorship from comments/testing/QA-only updates.
- Mark `contributor` only with explicit user development evidence and user is not initial dev owner.
- Mark `dev-owner` only with explicit evidence that user is initial dev assignee/owner.

6. Group summary data with full date-range coverage.
- For requested ranges, evaluate every day in the range.
- Emit every day in `# Grouped Summary`, even with no tickets.
- For empty days print `- No qualifying tickets.`.
- Group by activity date `YYYY-MM-DD`, then by status.

7. Build output path and prevent overwrite.
- Root path: `memory/tickets/linear/`.
- Week folder: `YYYY-W##` (ISO week).
- File format: `YYYY-MM-DD-ticket-dump.md`.
- Create missing directories.
- Do not overwrite; use suffixes `-1`, `-2` on collisions.

8. Write one dump file per run.
- Keep all scraped tickets in same file even when activity spans multiple days.
- Write `No description provided.` when description is missing.
- Write `No comments found.` when comments are missing.
- Preserve full activity detail; do not collapse distinct actions.
- If user has multiple qualifying same-day actions on a ticket, keep separate timestamped entries.
- If user has qualifying actions on different in-range days for same ticket, preserve all with timestamps and reflect each day in grouped summary.

9. Print grouped summary to chat and confirm saved file path.

10. Use fallback-safe Linear retrieval strategy.
- Resolve current user via `get_user` with `me` and store user id/email.
- Collect candidate issues without assignee bias:
- `list_issues` with `createdAt` at range start
- `list_issues` with `updatedAt` at range start
- Merge and deduplicate candidates by ticket identifier.
- For each candidate, load detail via `get_issue`.
- For each candidate, load comments via `list_comments`.
- Determine qualifying user activity from explicit issue/comment evidence.
- Do not rely on a single search endpoint as sole source.

### Chat Summary Contract

Use this exact style:

`[YYYY-MM-DD]`

`[Status]`
- `[TICKET-ID]: [Ticket title]`

`[Another Status]`
- `[TICKET-ID]: [Ticket title]`

### Dump File Contract

Use this structure:

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

## [TASK-ID]: [Task title]

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
- [timestamp] [activity type...]

### In-Range Day Mapping
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]
- [YYYY-MM-DD]: [list of qualifying user actions with timestamps]

### Activity Notes
[Brief factual summary of meaningful user activity on this ticket. Use explicit action verbs like `tested`, `commented`, `moved to In Progress`, `moved to Done`.]
```

## standup-from-dump Branch

Read latest dump, let user choose items, generate spoken stand-up via `$standup-generator`, and update the same dump file.

### Prerequisites

- A compatible dump file exists under `memory/tickets/linear/`.
- Prefer latest ISO week folder `YYYY-W##` and latest `YYYY-MM-DD-ticket-dump.md`.
- If no compatible dump exists, report that and instruct user to run dump creation.

### Unselected Ticket Carry-Over

Tickets not selected for stand-up persist across days. Any ticket in `# Unselected Tickets` of a previous dump reappears as a selectable item in future stand-up prompts until the user selects it.

### Execution Steps

1. Resolve dump file.
- Print exact dump path used.
- Parse `# All Scraped Tickets`, `# Manual Tasks`, and `# Unselected Tickets`.
- If present, parse `# Selected Tickets` as rerun index only.
- Also scan the most recent previous dump file (previous day or earlier in the same week folder) for `# Unselected Tickets`. Merge those carry-over tickets into the selectable list so nothing falls through the cracks across days.

2. Present selectable items.
- Show one numbered list with scraped tickets, manual tasks, and carry-over unselected tickets.
- For manual tasks, prefix ID display with `[Manual]`.
- For carry-over unselected tickets from previous dumps, prefix ID display with `[Carry-over]`.
- Group visually: current dump's tickets first, then carry-over tickets.

3. Collect selection with exact prompt.
- `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all. To add a manual task not tracked in Linear, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]".`

4. Interpret selection.
- Accept `all`, numeric indexes, ticket IDs, and clear natural-language selections.
- Parse new manual tasks from `Manual: [title] -- [status] [description]`.
- Assign next manual ID as `MANUAL-###`.
- Default status to `Done` and description to `No description provided.` when omitted.
- If ambiguous, ask one short clarification.

5. Build normalized input for `$standup-generator`.
- Convert each selected ticket/manual task into source-agnostic evidence:
- title, status, activity date
- role/ownership metadata
- chronology evidence (activity flow, notes, comments, test results)
- Pass only selected items as evidence.
- Treat existing `# Stand-up Script` prose as output-only, never evidence.

6. Generate script via base principles.
- Apply `$standup-generator` narrative, chronology, attribution, and blocker rules.
- Keep script conversational and factual.
- Do not speak ticket IDs unless user explicitly asks.

7. Update dump file in place.
- Write `# Stand-up Script` at top.
- Keep `# Selected Tickets` as a lightweight reference/index.
- Write `# Unselected Tickets` with all tickets not selected this run (from both current dump and carry-over pool). Each entry records the source dump date, status as of that date, role, and activity notes. This section replaces any previous `# Unselected Tickets` — selected items are removed, unselected items carry forward.
- Preserve full `# All Scraped Tickets` unchanged as historical source.
- Append new entries to `# Manual Tasks`; never remove/rewrite existing entries.

### Updated Dump Contract

Use this structure:

```md
# Stand-up Script

Yesterday, I [evidence-based narrative generated from selected items].

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

## Outcome Reporting

- Continue processing remaining dates when one date branch fails.
- At end of run, print per-date results with:
- status (`success` or `failed`)
- dump or output path when available
- concise failure reason when failed

## Rules

1. Do not fabricate ticket details, ownership, chronology, or outcomes.
2. Keep this skill as the single Linear workflow entrypoint.
3. Keep parsing and output structures stable for downstream consumers.
4. Never treat subscription/watching as assignment.
5. Never infer implementation authorship from testing/comments/QA-only evidence.
6. For dump branch, include every day in requested range, including empty days.
7. For stand-up branch, never query Linear unless user explicitly asks.
8. For full-flow ranges, keep partial successes visible and do not hide per-date failures.
