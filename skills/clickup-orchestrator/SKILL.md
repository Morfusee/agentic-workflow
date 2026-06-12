---
name: clickup-orchestrator
description: ClickUp entrypoint. Use when the user names ClickUp or a ClickUp task and wants task dumps, stand-ups, technical ticket drafts, review/QA comments, or direct ClickUp task updates. Routes to provider-agnostic helper skills after collecting ClickUp context.
---

# ClickUp Orchestrator

Route and execute ClickUp workflows from one entry point.

## Intent Routing

Infer intent heuristically and route to one branch:

1. `dump-creation`: collect ClickUp activity and write a ticket dump.
2. `standup-from-dump`: read dump, select tickets, capture an explicit next-day plan if provided, generate spoken stand-up, update dump.
3. `full-flow`: run dump creation then stand-up from that dump.
4. `ticket-draft`: route to `$ticket-drafter` only when request is clearly ClickUp-contextual and describes a defect, regression, production problem, feature, enhancement, refactor, or other technical ticket. Instruct `$ticket-drafter` to output the final draft in the ClickUp ticket format convention defined below (Description -> Scope -> Deliverable) when creating ClickUp-facing ticket text.
5. `review-comment`: route to `$ticket-review-comment-drafter` when the user provides code review findings, implementation review notes, QA results, pass/fail checks, or test observations to draft into a ClickUp ticket comment. If the request includes a ClickUp task ID or task URL, pass it through as `clickup_task_id` so the drafter publishes directly to that task.

If confidence is low, ask one focused clarification.

## ticket-draft Branch

Route ClickUp-context defect, regression, production problem, feature, enhancement, refactor, and other technical ticket requests to `$ticket-drafter`.

- Instruct `$ticket-drafter` to use the `clickup_workspace` profile, classify the request as `defect` or `implementation`, and include ClickUp as the preferred provider context.
- Let `$ticket-drafter` own draft, review, iteration, and provider-agnostic handoff metadata.
- Preserve the ClickUp Ticket Format Convention when mapping an approved handoff into a ClickUp task description.
- Do not create a ClickUp task until the user approves the ticket draft and explicitly asks to create or publish it.
- After approval, map the handoff metadata into ClickUp fields using ClickUp tools: title, description, labels/tags, priority, list, project or folder context, estimate, and confirmed assignee when available.
- If the target ClickUp list is missing, ask which list to use before creating the task.

## ClickUp Ticket Format Convention

When creating or drafting ClickUp tickets, including via `$ticket-drafter`, apply the following formatting rules derived from the workspace's Sprint-list ticket conventions.

### Ticket Naming

- Use imperative, action-oriented titles: verb-first, concise, no trailing period.
- Examples: `Implement email header template`, `Analyze Lambda Function Errors in Enrollment Workflows`, `Define Traffic Light Thresholds for Operational KPIs`.

### Description Format

```
**Description**
<1-2 sentence purpose and context>
**Scope**
- actionable work item
- actionable work item
**Deliverable**
- concrete acceptance criteria / definition of done
```

- **Description**: what the ticket is about, brief context. Keep to 1-2 sentences.
- **Scope**: bulleted list of specific work items. Use `- ` markers and imperative action verbs.
- **Deliverable**: bulleted list of concrete acceptance criteria. Use `- ` markers. Answers "how do we know this is done?"
- Section headers use `**Bold**` formatting. Content starts immediately on the next line.
- No blank lines anywhere — headers, bullets, and content flow directly into each other.

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

Collect ClickUp activity, normalize qualifying tasks, invoke `$ticket-dump-creator`, and print the grouped summary returned by that skill.

### Prerequisites

- A ClickUp integration must be active so ClickUp task, comment, and status tools are available.
- Use ClickUp tools as source of truth. Do not infer or fabricate task facts.
- Load `$ticket-dump-creator` after ClickUp facts are collected and normalized.

### ClickUp Retrieval Steps

1. Resolve target date and requested range.
   - Use explicit user date (`yesterday`, `2026-05-14`) for filename when provided.
   - Otherwise use current local date for filename.
   - Filter by user-provided range when present.
   - Fetch all relevant tasks when no range is provided.

2. Resolve current user.
   - Use `clickup_resolve_assignees` with `["me"]` and store user id/name/email.

3. Collect candidate tasks using multiple approaches.
   - Use `clickup_filter_tasks` with relevant filters such as date, assignee, and status.
   - Use `clickup_search` by keyword or user name for broader coverage.
   - Merge and deduplicate candidates by task identifier.

4. Load full evidence for each candidate.
   - Load detail via `clickup_get_task`.
   - Load comments via `clickup_get_task_comments`.
   - Determine qualifying user activity from explicit task/comment evidence.
   - Do not rely on a single search endpoint as sole source.

5. Apply ClickUp-specific activity filtering before normalization.
   - Include a task only when the user's own activity occurred within the requested range.
   - Qualifying activities:
     - user commented on the task
     - user changed task status
     - user explicitly marked task closed
      - explicit assignment event in-range, not watching or following
     - task created by user only when create event is in-range
   - Exclude tasks with no qualifying in-range user activity.

6. Normalize each qualifying ClickUp task for `$ticket-dump-creator`.
   - Set `provider: clickup`.
   - Set `provider_display_name: ClickUp`.
   - Set `item_label: task`.
   - Set `item_collection_label: tasks`.
   - Set `item_collection_heading: Tasks`.
   - Set `memory_subpath: memory/tickets/clickup/`.
   - Set `requested_range` to the resolved user-requested range or `all relevant tasks`.
   - Set `dump_file_date` to the resolved filename date.
   - Set `generated_timestamp` to the current local timestamp.
   - For every item, provide all required normalized fields from `$ticket-dump-creator`.

7. Preserve ClickUp attribution semantics while normalizing.
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

## standup-from-dump Branch

Read latest dump, let user choose items, generate spoken stand-up via `$standup-generator`, and update the same dump file.

### Prerequisites

- A compatible dump file exists under the canonical ClickUp dump path defined in OpenCode's global AGENTS.md.
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
   - `Which tasks do you want to include in your stand-up? You can reply with task numbers, task IDs, or all. To add a manual task not tracked in ClickUp, describe it as "Manual: [task title] -- [Done / In Progress / To Do] [optional description]". To add a next-day plan, describe it as "Plan: [what you intend to work on next]".`

4. Interpret selection.
   - Accept `all`, numeric indexes, task IDs, and clear natural-language selections.
   - Parse new manual tasks from `Manual: [title] -- [status] [description]`.
   - Parse explicit next-day plan from `Plan: [what you intend to work on next]`.
   - Assign next manual ID as `MANUAL-###`.
   - Default status to `Done` and description to `No description provided.` when omitted.
   - If ambiguous, ask one short clarification.

5. Build normalized input for `$standup-generator`.
   - Convert each selected task/manual task into source-agnostic evidence:
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
