---
name: linear-ticket-dump-creator
description: Scrape and organize relevant Linear ticket activity into a daily Markdown dump file for later automation. Use when the user asks to collect ticket activity, create a ticket dump, summarize work by date and status, or save a reusable activity snapshot from Linear for stand-up prep. Include only tickets where the user's own activity falls in the requested date range.
---

# Linear Ticket Roundup and Dump Creator

Create one daily Markdown dump of relevant Linear ticket activity and print a concise grouped summary.

Use Linear plugin/tools as source of truth. Do not infer or fabricate ticket facts.

## Agent Execution Contract

- Default behavior: spawn one new agent per requested date and run those per-date agents in parallel.
- Single-date request: spawn one agent.
- Date-range request: expand to daily dates and spawn one agent per date in parallel.
- Pass through model and reasoning effort per agent from user input when provided, otherwise use current thread defaults.
- Parent-orchestrated mode: if invoked by `$linear-standup-flow` with an explicit single-date handoff, do not spawn another agent; execute inline for that single date only.

## Execution Steps

1. Resolve target date and requested range.
- Use explicit user date (`yesterday`, `2026-05-14`, etc.) for filename when provided.
- Otherwise use current local date for filename.
- Filter by user-provided range when present.
- Fetch all relevant tickets when no range is provided.
- In standalone range mode, fan out to one per-date agent and run remaining steps per date in each agent.

2. Apply activity-first inclusion logic.
- Include a ticket only when the user's own activity occurred within the requested range.
- Treat these as qualifying user activities:
- The user commented on the ticket.
- The user changed the ticket status (for example moved to `In Progress`, `In Review`, `Done`, `Todo`).
- The user explicitly marked the ticket as `Done`.
- The user was explicitly assigned to the ticket in-range (assignment event; do not treat subscription/watching as assignment).
- Ticket creation by the user counts only when the create event itself is inside the requested range.
- Exclude tickets with no qualifying in-range user activity, even if the ticket is currently assigned to the user or recently updated by others.

3. Apply status handling after activity filtering.
- First filter by qualifying user activity in-range.
- Include all statuses by default after activity qualification.
- Apply explicit status restrictions only when the user requests a status subset.
- Deduplicate by ticket identifier across all activity sources.
 
4. Compute activity date per ticket.
- Use the timestamp of the qualifying user activity that caused inclusion.
- Prefer explicit user status-change timestamp when available.
- Otherwise use user comment timestamp when comment activity caused inclusion.
- Otherwise use explicit assignment event timestamp when assignment activity caused inclusion.
- Otherwise use created date only when ticket creation is the qualifying in-range activity.
- Use updated date only when it clearly reflects one of the allowed user actions above.

5. Compute attribution and role per ticket.
- Identify initial development assignee/owner from explicit ticket history when available.
- Identify testing-only activity actors from explicit test or verification actions.
- Determine `My role for this ticket` as one of: `dev-owner`, `contributor`, `tester-only`.
- Mark `tester-only` when the user's in-range activity is only testing, verification, or comments about testing and there is no explicit in-range development evidence by the user.
- Do not infer implementation authorship from comments, test verification, or QA-only updates.
- Mark `contributor` only when explicit development evidence by the user exists but the user is not the initial dev owner.
- Mark `dev-owner` only when explicit evidence shows the user as the initial development assignee/owner.

6. Group summary data with full date-range coverage.
- When a requested range is provided, explicitly evaluate each day in the range.
- Emit every day in the requested range in `# Grouped Summary`, even if no qualifying tickets exist that day.
- For empty days, print the date header followed by `- No qualifying tickets.`.
- Group ticket entries by activity date `YYYY-MM-DD` and then by status.
- Within each date, group by status.
- Keep summary concise and readable.

7. Build output path and prevent overwrite.
- Root path: `memory/tickets/`.
- Week folder format: `YYYY-W##` (ISO week).
- File format: `YYYY-MM-DD-ticket-dump.md`.
- Create missing directories.
- Do not overwrite existing dump files.
- If filename exists, write a suffixed variant like `YYYY-MM-DD-ticket-dump-1.md`, `...-2.md`.

8. Write one dump file for the run.
- Keep all scraped tickets in the same file even when activity spans multiple days.
- Include every required section in the dump format.
- Write `No description provided.` when description is missing.
- Write `No comments found.` when comments are missing.
- Preserve activity detail. Do not collapse multiple same-day user actions into one generic summary.
- If the user performed two or more qualifying actions on the same ticket in-range, include each action as a separate entry with timestamp.
- If the user performed qualifying actions on different in-range days for the same ticket, preserve all actions with timestamps and reflect them under each applicable day in grouped summary output.

9. Print grouped summary to chat and confirm the saved file path.

10. Use Linear tools with a fallback-safe retrieval strategy.
- Resolve current user via `get_user` with `me` and store user id/email as actor identity.
- Collect candidate issues for the requested date range without assignee bias:
- Call `list_issues` with `createdAt` at range start and team scope when available.
- Call `list_issues` with `updatedAt` at range start and team scope when available.
- Merge and deduplicate candidates by ticket identifier.
- For each candidate issue, load detail via `get_issue`.
- For each candidate issue, load comments via `list_comments`.
- Determine qualifying user activity from explicit evidence in issue fields and comments.
- Do not rely on a single research/search endpoint as the only source of ticket activity.

## Chat Summary Contract

Use this exact style:

`[YYYY-MM-DD]`

`[Status]`
- `[TICKET-ID]: [Ticket title]`

`[Another Status]`
- `[TICKET-ID]: [Ticket title]`

## Dump File Contract

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

## Rules

1. Do not fabricate ticket details.
2. Keep printed summary concise.
3. Keep dump complete and parseable.
4. Keep this skill standalone and independent from stand-up generation.
5. Keep one dump file per run even when activity spans multiple days.
6. Include all scraped ticket details in `# All Scraped Tickets`.
7. Do not treat subscription/watching as assignment.
8. Exclude any ticket where qualifying user activity does not fall in the requested range.
9. Do not truncate or simplify user activity history when writing activity sections.
10. Do not replace `tested` with softer wording like `confirmed`; use the direct action verb that matches what happened.
11. Do not attribute implementation authorship to the user without explicit development evidence by the user.
12. Treat comments, test verification, and QA-only activity as non-implementation evidence unless paired with explicit development actions.
13. When a requested range is provided, include every day in that range in grouped summaries, including days with no qualifying tickets.
14. In parent-orchestrated single-date mode, do not spawn nested agents unless explicitly requested.
