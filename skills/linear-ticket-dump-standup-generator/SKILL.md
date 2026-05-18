---
name: linear-ticket-dump-standup-generator
description: Read the latest Linear ticket dump Markdown file, let the user choose tickets, generate a spoken stand-up script, and update the same dump file in place. Use when the user wants stand-up generation specifically from `memory/tickets/` dump files. This skill is a specialized superset wrapper over $standup-generator.
---

# Linear Ticket Dump Stand-up Generator

Use this skill as a wrapper around `$standup-generator`. Keep all base stand-up principles from `$standup-generator`, then add Linear dump-specific selection and file update behavior.

## Wrapper Contract

1. Delegate script-generation principles to `$standup-generator`.
2. Add source-specific behavior for Linear dump discovery, ticket/manual-task selection, and in-place dump updates.
3. If wrapper behavior conflicts with base principles, preserve base principles and ask one focused clarification.

## Prerequisites

- A compatible dump file exists under `memory/tickets/`.
- Prefer the latest ISO week folder `YYYY-W##` and latest `YYYY-MM-DD-ticket-dump.md`.
- If no compatible dump exists, report that and instruct the user to run `$linear-ticket-dump-creator`.

## Execution Steps

1. Resolve dump file.
- Print the exact dump path used.
- Parse `# All Scraped Tickets` and `# Manual Tasks`.
- If present, parse `# Selected Tickets` as rerun index only.

2. Present selectable items.
- Show one numbered list with scraped tickets and manual tasks.
- For manual tasks, prefix ID display with `[Manual]`.

3. Collect selection with this exact prompt.
- `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all. To add a manual task not tracked in Linear, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]".`

4. Interpret selection.
- Accept `all`, numeric indexes, ticket IDs, and clear natural-language selections.
- Parse new manual tasks from `Manual: [title] -- [status] [description]`.
- Assign next manual ID as `MANUAL-###`.
- Default status to `Done` and description to `No description provided.` when omitted.
- If ambiguous, ask one short clarification.

5. Build normalized input for `$standup-generator`.
- Convert each selected ticket/manual task into source-agnostic work-item evidence:
- title, status, activity date
- role/ownership metadata
- chronology evidence (activity flow, notes, comments, test results)
- Pass only selected items as evidence.
- Treat existing `# Stand-up Script` prose as output-only, never evidence.

6. Generate script via base principles.
- Apply all `$standup-generator` narrative, chronology, attribution, and blocker rules.
- Keep script conversational and factual.
- Do not speak ticket IDs unless the user explicitly asks.

7. Update dump file in place.
- Write `# Stand-up Script` at top.
- Keep `# Selected Tickets` as a lightweight reference/index.
- Preserve full `# All Scraped Tickets` section unchanged as historical source.
- Append new entries to `# Manual Tasks`; never remove/rewrite existing entries.

## Updated Dump Contract

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

# Manual Tasks

[Keep all manual tasks here. Append new entries; preserve existing ones.]

---

# All Scraped Tickets

[Keep all scraped ticket details here, including selected and unselected tickets.]
```

## Rules

1. Keep this skill standalone whenever a compatible dump exists.
2. Keep this skill as a specialized superset wrapper of `$standup-generator`.
3. Never query Linear unless the user explicitly asks.
4. Preserve structure so downstream skills can parse reliably.
5. Do not remove, truncate, or rewrite factual ticket history.
6. On reruns, re-derive from selected-item evidence plus `# All Scraped Tickets`; ignore old stand-up prose.
7. In parent-orchestrated single-date mode from `$linear-standup-flow`, execute inline and do not spawn nested agents unless explicitly requested.
