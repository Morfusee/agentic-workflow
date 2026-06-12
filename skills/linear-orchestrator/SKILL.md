---
name: linear-orchestrator
description: Linear entrypoint. Use when the user names Linear or a Linear issue and wants ticket dumps, stand-ups, technical ticket drafts, weekly slideshow prep, review/QA comments, or direct Linear publishing. Routes to provider-agnostic helper skills after collecting Linear context.
---

# Linear Orchestrator

Route and execute Linear workflows from one entry point.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `dump-creation`: collect Linear activity and write a ticket dump.
2. `standup-from-dump`: read dump, select tickets, capture an explicit next-day plan if provided, generate spoken stand-up, update dump.
3. `full-flow`: run dump creation then stand-up from that dump.
4. `ticket-draft`: route to `$ticket-drafter` only when request is clearly Linear-contextual and describes a defect, regression, production problem, feature, enhancement, refactor, or other technical ticket.
5. `weekly-slideshow`: route to `$weekly-ticket-slideshow-generator` only when request is clearly Linear-contextual.
6. `review-comment`: route to `$ticket-review-comment-drafter` when the user provides code review findings, implementation review notes, QA results, pass/fail checks, or test observations to draft into a Linear ticket comment. If the request includes a Linear issue ID, ticket identifier, or issue URL, pass it through as `linear_issue_id` so the drafter publishes directly to that issue.

If confidence is low, ask one focused clarification.

## ticket-draft Branch

Route Linear-context defect, regression, production problem, feature, enhancement, refactor, and other technical ticket requests to `$ticket-drafter`.

- Instruct `$ticket-drafter` to use the `linear_workspace` profile and classify the request as `defect` or `implementation`.
- Let `$ticket-drafter` own draft, review, iteration, and provider-agnostic handoff metadata.
- Do not create a Linear issue until the user approves the ticket draft and explicitly asks to create or publish it.
- After approval, map the handoff metadata into Linear fields using Linear tools: title, description, labels, priority, project, estimate, and confirmed assignee when available.
- If required Linear publish fields are missing, ask one focused clarification before creating the issue.

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

Collect Linear activity, normalize qualifying issues, invoke `$ticket-dump-creator`, and print the grouped summary returned by that skill.

### Prerequisites

- A Linear integration must be active so Linear issue, comment, and status tools are available.
- Use Linear tools as source of truth. Do not infer or fabricate ticket facts.
- Load `$ticket-dump-creator` after Linear facts are collected and normalized.

### Linear Retrieval Steps

1. Resolve target date and requested range.
- Use explicit user date (`yesterday`, `2026-05-14`) for filename when provided.
- Otherwise use current local date for filename.
- Filter by user-provided range when present.
- Fetch all relevant tickets when no range is provided.

2. Resolve current user.
- Use `get_user` with `me` and store user id/email.

3. Collect candidate issues without assignee bias.
- Use `list_issues` with `createdAt` at range start.
- Use `list_issues` with `updatedAt` at range start.
- Merge and deduplicate candidates by ticket identifier.

4. Load full evidence for each candidate.
- Load detail via `get_issue`.
- Load comments via `list_comments`.
- Determine qualifying user activity from explicit issue/comment evidence.
- Do not rely on a single search endpoint as sole source.

5. Apply Linear-specific activity filtering before normalization.
- Include a ticket only when the user's own activity occurred within the requested range.
- Qualifying activities:
- user commented on the ticket
- user changed ticket status (`In Progress`, `In Review`, `Done`, `Todo`)
- user explicitly marked ticket `Done`
- explicit assignment event in-range, not subscription or watching
- ticket created by user only when create event is in-range
- Exclude tickets with no qualifying in-range user activity.

6. Normalize each qualifying Linear issue for `$ticket-dump-creator`.
- Set `provider: linear`.
- Set `provider_display_name: Linear`.
- Set `item_label: ticket`.
- Set `item_collection_label: tickets`.
- Set `item_collection_heading: Tickets`.
- Set `memory_subpath: memory/tickets/linear/`.
- Set `requested_range` to the resolved user-requested range or `all relevant tickets`.
- Set `dump_file_date` to the resolved filename date.
- Set `generated_timestamp` to the current local timestamp.
- For every item, provide all required normalized fields from `$ticket-dump-creator`.

7. Preserve Linear attribution semantics while normalizing.
- Identify initial dev assignee/owner from explicit history when available.
- Identify testing-only activity actors from explicit test/verification actions.
- Set `my_role` as `dev-owner`, `contributor`, or `tester-only`.
- Mark `tester-only` when in-range user activity is only testing/verification/testing comments and no explicit in-range dev evidence exists.
- Do not infer implementation authorship from comments/testing/QA-only updates.
- Mark `contributor` only with explicit user development evidence and user is not initial dev owner.
- Mark `dev-owner` only with explicit evidence that user is initial dev assignee/owner.

8. Invoke `$ticket-dump-creator`.
- Pass only normalized provider context and normalized qualifying items.
- Let `$ticket-dump-creator` own grouped summary formatting, output path creation, collision handling, dump file structure, and chat summary reporting.

9. Prompt stand-up ticket selection immediately after successful dump creation.
- Keep the grouped summary and saved path output unchanged.
- Unless user explicitly asked for dump-only behavior, immediately present a selectable list in the same run.
- Build selectable list from:
  - current dump `# All Scraped Tickets`
  - current dump `# Manual Tasks`
  - carry-over tickets from `# Unselected Tickets` in the most recent previous dump, previous day or earlier in the same ISO week folder
- Show one numbered list, grouped visually: current dump items first, then carry-over items.
- Prefix carry-over entries with `[Carry-over]`.
- After listing items, ask the exact stand-up selection prompt:
- `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all. To add a manual task not tracked in Linear, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]". To add a next-day plan, describe it as "Plan: [what you intend to work on next]".`

## standup-from-dump Branch

Read latest dump, let user choose items, generate spoken stand-up via `$standup-generator`, and update the same dump file.

### Prerequisites

- A compatible dump file exists under the canonical Linear dump path defined in OpenCode's global AGENTS.md.
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
- Show current dump tickets and manual tasks as a numbered list.
- Show carry-over unselected tickets from previous dumps as bullets.
- For manual tasks, prefix ID display with `[Manual]`.
- For carry-over unselected tickets from previous dumps, prefix ID display with `[Carry-over]`.
- Group visually: current dump's tickets first, then carry-over bullets.

3. Collect selection with exact prompt.
- `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all. To add a manual task not tracked in Linear, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]". To add a next-day plan, describe it as "Plan: [what you intend to work on next]".`

4. Interpret selection.
- Accept `all`, numeric indexes, ticket IDs, and clear natural-language selections.
- Parse new manual tasks from `Manual: [title] -- [status] [description]`.
- Parse explicit next-day plan from `Plan: [what you intend to work on next]`.
- Assign next manual ID as `MANUAL-###`.
- Default status to `Done` and description to `No description provided.` when omitted.
- If ambiguous, ask one short clarification.

5. Build normalized input for `$standup-generator`.
- Convert each selected ticket/manual task into source-agnostic evidence:
- title, status, activity date
- role/ownership metadata
- chronology evidence (activity flow, notes, comments, test results)
- Pass the explicit next-day plan only if the user provides it.
- Do not infer next-day plans from open, remaining, or unselected work.
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
