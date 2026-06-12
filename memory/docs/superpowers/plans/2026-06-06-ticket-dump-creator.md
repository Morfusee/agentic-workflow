# Ticket Dump Creator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract shared Linear and ClickUp dump creation behavior into a reusable `ticket-dump-creator` skill while preserving provider-specific retrieval logic in the existing orchestrators.

**Architecture:** Add one provider-agnostic skill that owns dump inclusion rules, normalized input requirements, output paths, Markdown structure, and chat summary behavior. Update Linear and ClickUp orchestrators so their dump branches collect provider facts, normalize them, and invoke `$ticket-dump-creator`; leave Notion unchanged.

**Tech Stack:** Markdown skill files in `skills/`, repository skill conventions from `AGENTS.md`, PowerShell validation commands, Git diff review.

---

## File Structure

- Create: `skills/ticket-dump-creator/SKILL.md`
- Modify: `skills/workflow-orchestrator/references/providers/linear.md`
- Modify: `skills/workflow-orchestrator/references/providers/clickup.md`
- Do not modify: `skills/workflow-orchestrator/references/providers/notion.md`
- Reference: `memory/docs/superpowers/specs/2026-06-06-ticket-dump-creator-design.md`

`skills/ticket-dump-creator/SKILL.md` is responsible for the shared dump creation contract only. It must not contain Linear or ClickUp API retrieval instructions.

`skills/workflow-orchestrator/references/providers/linear.md` remains responsible for Linear intent routing, Linear retrieval, Linear normalization, stand-up-from-dump, issue drafting, weekly slideshow, and QA comment routing.

`skills/workflow-orchestrator/references/providers/clickup.md` remains responsible for ClickUp intent routing, ClickUp retrieval, ClickUp ticket formatting convention, ClickUp normalization, stand-up-from-dump, issue drafting, and QA comment routing.

---

### Task 1: Create Shared Ticket Dump Creator Skill

**Files:**
- Create: `skills/ticket-dump-creator/SKILL.md`

- [ ] **Step 1: Confirm the skill does not already exist**

Run: `Test-Path -LiteralPath "skills\ticket-dump-creator\SKILL.md"`

Expected: `False`

- [ ] **Step 2: Create the skill directory**

Run: `New-Item -ItemType Directory -Path "skills\ticket-dump-creator"`

Expected: command succeeds and creates the directory.

- [ ] **Step 3: Add `SKILL.md` with the shared contract**

Create `skills/ticket-dump-creator/SKILL.md` with this complete content:

```markdown
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
```

- [ ] **Step 4: Verify frontmatter shape**

Run: `Get-Content -LiteralPath "skills\ticket-dump-creator\SKILL.md" -TotalCount 5`

Expected output begins with exactly:

```text
---
name: ticket-dump-creator
description: Create source-agnostic ticket or task dump files from normalized provider facts. Use when Linear, ClickUp, or another provider orchestrator has collected work item activity and needs the common activity-first dump contract, grouped summary, memory path, and Markdown output generated without provider-specific retrieval.
---
```

- [ ] **Step 5: Commit the shared skill when commits are authorized**

If the user has explicitly authorized commits for the implementation session, run:

```bash
git add skills/ticket-dump-creator/SKILL.md
git commit -m "feat(skills): add ticket dump creator"
```

If commits are not authorized, do not commit. Record that the commit step was skipped due to missing authorization.

---

### Task 2: Update Linear Dump Creation Branch

**Files:**
- Modify: `skills/workflow-orchestrator/references/providers/linear.md:40-223`

- [ ] **Step 1: Review current Linear dump branch**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\linear.md" -Pattern "## dump-creation Branch|## standup-from-dump Branch" -Context 0,2`

Expected: both headings are present, and `## dump-creation Branch` appears before `## standup-from-dump Branch`.

- [ ] **Step 2: Replace only the Linear dump branch**

Replace the content from `## dump-creation Branch` up to, but not including, `## standup-from-dump Branch` with:

```markdown
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
```

- [ ] **Step 3: Verify the Linear stand-up branch was not edited**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\linear.md" -Pattern "## standup-from-dump Branch|### Unselected Ticket Carry-Over|# Selected Tickets|# Unselected Tickets"`

Expected: all four patterns are still present.

- [ ] **Step 4: Verify Linear now references the shared skill**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\linear.md" -Pattern "ticket-dump-creator|memory/tickets/linear|item_label: ticket"`

Expected: all three patterns are present.

- [ ] **Step 5: Commit the Linear orchestrator change when commits are authorized**

If the user has explicitly authorized commits for the implementation session, run:

```bash
git add skills/workflow-orchestrator/references/providers/linear.md
git commit -m "refactor(linear): delegate dump creation"
```

If commits are not authorized, do not commit. Record that the commit step was skipped due to missing authorization.

---

### Task 3: Update ClickUp Dump Creation Branch

**Files:**
- Modify: `skills/workflow-orchestrator/references/providers/clickup.md:66-237`

- [ ] **Step 1: Review current ClickUp dump branch**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\clickup.md" -Pattern "## dump-creation Branch|## standup-from-dump Branch" -Context 0,2`

Expected: both headings are present, and `## dump-creation Branch` appears before `## standup-from-dump Branch`.

- [ ] **Step 2: Replace only the ClickUp dump branch**

Replace the content from `## dump-creation Branch` up to, but not including, `## standup-from-dump Branch` with:

```markdown
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
```

- [ ] **Step 3: Verify the ClickUp stand-up branch was not edited**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\clickup.md" -Pattern "## standup-from-dump Branch|### Unselected Task Carry-Over|# Selected Tasks|# Unselected Tasks"`

Expected: all four patterns are still present.

- [ ] **Step 4: Verify ClickUp now references the shared skill**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\clickup.md" -Pattern "ticket-dump-creator|memory/tickets/clickup|item_label: task"`

Expected: all three patterns are present.

- [ ] **Step 5: Commit the ClickUp orchestrator change when commits are authorized**

If the user has explicitly authorized commits for the implementation session, run:

```bash
git add skills/workflow-orchestrator/references/providers/clickup.md
git commit -m "refactor(clickup): delegate dump creation"
```

If commits are not authorized, do not commit. Record that the commit step was skipped due to missing authorization.

---

### Task 4: Validate Skill Metadata And Scope

**Files:**
- Inspect: `skills/ticket-dump-creator/SKILL.md`
- Inspect: `skills/workflow-orchestrator/references/providers/linear.md`
- Inspect: `skills/workflow-orchestrator/references/providers/clickup.md`
- Inspect: `skills/workflow-orchestrator/references/providers/notion.md`

- [ ] **Step 1: Confirm the new skill folder follows naming rules**

Run: `Test-Path -LiteralPath "skills\ticket-dump-creator\SKILL.md"`

Expected: `True`

- [ ] **Step 2: Confirm only allowed frontmatter keys exist**

Run: `Get-Content -LiteralPath "skills\ticket-dump-creator\SKILL.md" -TotalCount 4`

Expected output:

```text
---
name: ticket-dump-creator
description: Create source-agnostic ticket or task dump files from normalized provider facts. Use when Linear, ClickUp, or another provider orchestrator has collected work item activity and needs the common activity-first dump contract, grouped summary, memory path, and Markdown output generated without provider-specific retrieval.
---
```

- [ ] **Step 3: Confirm Notion was not changed**

Run: `git diff -- skills/workflow-orchestrator/references/providers/notion.md`

Expected: no output.

- [ ] **Step 4: Confirm provider retrieval stayed out of the shared skill**

Run: `Select-String -Path "skills\ticket-dump-creator\SKILL.md" -Pattern "clickup_get_task|clickup_search|list_issues|get_issue|list_comments|get_user"`

Expected: no matches.

- [ ] **Step 5: Confirm provider orchestrators still include retrieval strategies**

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\linear.md" -Pattern "list_issues|get_issue|list_comments|get_user"`

Expected: matches for Linear retrieval tools.

Run: `Select-String -Path "skills\workflow-orchestrator\references\providers\clickup.md" -Pattern "clickup_filter_tasks|clickup_search|clickup_get_task|clickup_get_task_comments|clickup_resolve_assignees"`

Expected: matches for ClickUp retrieval tools.

- [ ] **Step 6: Check for accidental unfinished-marker text**

Run: `Select-String -Path "skills\ticket-dump-creator\SKILL.md","skills\workflow-orchestrator\references\providers\linear.md","skills\workflow-orchestrator\references\providers\clickup.md" -Pattern "T`BD|TO`DO|place`holder|imple`ment later"`

Expected: no matches.

---

### Task 5: Final Diff Review

**Files:**
- Review: `skills/ticket-dump-creator/SKILL.md`
- Review: `skills/workflow-orchestrator/references/providers/linear.md`
- Review: `skills/workflow-orchestrator/references/providers/clickup.md`
- Review: `memory/docs/superpowers/specs/2026-06-06-ticket-dump-creator-design.md`
- Review: `memory/docs/superpowers/plans/2026-06-06-ticket-dump-creator.md`

- [ ] **Step 1: Review changed file list**

Run: `git status --short`

Expected changed files are limited to:

```text
?? memory/docs/superpowers/specs/2026-06-06-ticket-dump-creator-design.md
?? memory/docs/superpowers/plans/2026-06-06-ticket-dump-creator.md
?? skills/ticket-dump-creator/
 M skills/workflow-orchestrator/references/providers/linear.md
 M skills/workflow-orchestrator/references/providers/clickup.md
```

If the spec and plan were already committed or intentionally staged earlier, their status may differ. Do not revert them.

- [ ] **Step 2: Review full diff**

Run: `git diff -- skills/workflow-orchestrator/references/providers/linear.md skills/workflow-orchestrator/references/providers/clickup.md`

Expected: Linear and ClickUp dump branches delegate to `$ticket-dump-creator`; stand-up branches remain present.

- [ ] **Step 3: Review untracked skill content**

Run: `Get-Content -LiteralPath "skills\ticket-dump-creator\SKILL.md"`

Expected: the file contains only the shared dump creation contract and no provider API retrieval logic.

- [ ] **Step 4: Commit final documentation and any uncommitted implementation changes when commits are authorized**

If commits are authorized and previous task commits were skipped, make one logical commit for the remaining related skill extraction files:

```bash
git add skills/ticket-dump-creator/SKILL.md skills/workflow-orchestrator/references/providers/linear.md skills/workflow-orchestrator/references/providers/clickup.md memory/docs/superpowers/specs/2026-06-06-ticket-dump-creator-design.md memory/docs/superpowers/plans/2026-06-06-ticket-dump-creator.md
git commit -m "refactor(skills): extract ticket dump creator"
```

If commits are not authorized, leave changes uncommitted and report the exact changed files.

---

## Self-Review Checklist

- Spec coverage: Tasks create `ticket-dump-creator`, update Linear, update ClickUp, leave Notion unchanged, validate metadata, and review diffs.
- Unfinished-marker scan: The plan contains no unspecified implementation steps.
- Type consistency: Provider context fields are consistent across the spec, shared skill content, Linear normalization instructions, and ClickUp normalization instructions.
- Scope check: The plan extracts dump creation only and does not extract stand-up-from-dump behavior.
