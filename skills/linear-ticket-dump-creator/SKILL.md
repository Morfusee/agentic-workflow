---
name: linear-ticket-dump-creator
description: Scrape and organize relevant Linear ticket activity into a daily Markdown dump file for later automation. Use when the user asks to collect ticket activity, create a ticket dump, summarize work by date and status, or save a reusable activity snapshot from Linear for stand-up prep. Include only tickets where the user's own activity falls in the requested date range.
---

# Linear Ticket Roundup and Dump Creator

Create one daily Markdown dump of relevant Linear ticket activity and print a concise grouped summary.

Use Linear plugin/tools as source of truth. Do not infer or fabricate ticket facts.

## Execution Steps

1. Resolve target date and requested range.
- Use explicit user date (`yesterday`, `2026-05-14`, etc.) for filename when provided.
- Otherwise use current local date for filename.
- Filter by user-provided range when present.
- Fetch all relevant tickets when no range is provided.

2. Apply activity-first inclusion logic.
- Include a ticket only when the user's own activity occurred within the requested range.
- Treat these as qualifying user activities:
- The user commented on the ticket.
- The user changed the ticket status (for example moved to `In Progress`, `In Review`, `Done`, `Todo`).
- The user explicitly marked the ticket as `Done`.
- The user was explicitly assigned to the ticket in-range (assignment event; do not treat subscription/watching as assignment).
- Ticket creation by the user counts only when the create event itself is inside the requested range.
- Exclude tickets with no qualifying in-range user activity, even if the ticket is currently assigned to the user or recently updated by others.

3. Apply status filtering after activity filtering.
- First filter by qualifying user activity in-range.
- Then keep only statuses `Done`, `In Review`, `In Progress`, `Todo` unless the user explicitly asks to include other statuses.
- Deduplicate by ticket identifier across all activity sources.

4. Compute activity date per ticket.
- Use the timestamp of the qualifying user activity that caused inclusion.
- Prefer explicit user status-change timestamp when available.
- Otherwise use user comment timestamp when comment activity caused inclusion.
- Otherwise use explicit assignment event timestamp when assignment activity caused inclusion.
- Otherwise use created date only when ticket creation is the qualifying in-range activity.
- Use updated date only when it clearly reflects one of the allowed user actions above.

5. Group summary data.
- Group by activity date `YYYY-MM-DD`.
- Within each date, group by status.
- Keep summary concise and readable.

6. Build output path and prevent overwrite.
- Root path: `memory/tickets/`.
- Week folder format: `YYYY-W##` (ISO week).
- File format: `YYYY-MM-DD-ticket-dump.md`.
- Create missing directories.
- Do not overwrite existing dump files.
- If filename exists, write a suffixed variant like `YYYY-MM-DD-ticket-dump-1.md`, `...-2.md`.

7. Write one dump file for the run.
- Keep all scraped tickets in the same file even when activity spans multiple days.
- Include every required section in the dump format.
- Write `No description provided.` when description is missing.
- Write `No comments found.` when comments are missing.
- Preserve activity detail. Do not collapse multiple same-day user actions into one generic summary.
- If the user performed two or more qualifying actions on the same ticket in-range, include each action as a separate entry with timestamp.

8. Print grouped summary to chat and confirm the saved file path.

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

### Why this ticket was included
[Created by me / assigned to me / commented on by me / status changed by me / meaningful activity inferred]

### Description
[Full ticket description or "No description provided."]

### Comments
#### [comment author] - [timestamp]
[comment body]

[Repeat per comment, or "No comments found."]

### Activity Timeline
- [timestamp] [activity type: created / assigned / commented / moved to In Progress / moved to In Review / moved to Done / moved to Todo / tested]
- [timestamp] [activity type...]

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
