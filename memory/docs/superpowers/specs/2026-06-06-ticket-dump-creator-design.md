# Ticket Dump Creator Design

## Purpose

Extract shared ticket dump creation behavior from the Linear and ClickUp orchestrators into a reusable skill named `ticket-dump-creator`.

The extraction should reduce duplicated dump instructions while preserving provider-specific retrieval logic in the existing orchestrators.

## Scope

Create a source-agnostic dump creation skill that owns the common dump contract after provider facts have been collected and normalized.

Update `workflow-orchestrator` and `workflow-orchestrator` to invoke the shared skill for dump writing. Keep each orchestrator as the public entrypoint for its provider.

Do not change `workflow-orchestrator` for this refactor. The current Notion workflow does not perform activity-first ticket dump creation. A Notion dump workflow can be added later as a separate behavior if needed.

## Non-Goals

- Do not extract stand-up-from-dump behavior in this change.
- Do not centralize Linear or ClickUp API retrieval logic.
- Do not add Notion task dump behavior.
- Do not change existing dump output semantics beyond moving common instructions into the shared skill.

## Recommended Architecture

Create `skills/ticket-dump-creator/SKILL.md`.

The new skill owns:

- activity-first inclusion rules
- status handling after activity filtering
- activity date selection
- role attribution rules
- grouped summary structure
- ISO week output path contract
- collision-safe file creation
- Markdown dump file structure
- chat summary reporting

The existing provider orchestrators own:

- user/date/range resolution
- provider-specific source-of-truth retrieval
- provider-specific fallback search strategy
- normalization of retrieved facts into the shared input contract
- invoking `$ticket-dump-creator`
- provider-specific downstream workflows outside dump creation

## Shared Skill Contract

`ticket-dump-creator` accepts normalized work items and provider vocabulary from the invoking orchestrator.

Required provider context:

```yaml
provider: linear | clickup
item_label: ticket | task
item_collection_label: tickets | tasks
memory_subpath: memory/tickets/<provider>/
requested_range: <date or date range>
dump_file_date: YYYY-MM-DD
```

Required normalized item fields:

```yaml
items:
  - id: <provider item id>
    title: <item title>
    status: <provider status>
    activity_date: YYYY-MM-DD
    url: <provider URL or Not available>
    initial_dev_assignee: <name or Not available>
    testing_actors: <comma-separated names or None identified>
    my_role: dev-owner | contributor | tester-only
    inclusion_reasons:
      - created by me | assigned to me | commented on by me | status changed by me
    description: <full description or No description provided.>
    comments:
      - author: <name>
        timestamp: <timestamp>
        body: <comment body>
    activity_timeline:
      - timestamp: <timestamp>
        type: <created | assigned | commented | moved status | closed | tested>
        summary: <brief factual summary>
    in_range_day_mapping:
      - date: YYYY-MM-DD
        actions:
          - <qualifying user action with timestamp>
    activity_notes: <brief factual summary>
```

The skill should reject or ask for clarification when required normalized facts are missing and cannot be represented with the existing fallback text.

## Output Contract

The shared skill writes one Markdown dump file under:

```text
memory/tickets/<provider>/YYYY-W##/YYYY-MM-DD-ticket-dump.md
```

It must create missing directories, avoid overwriting existing files, and use suffixes such as `-1` and `-2` on collisions.

The dump structure remains stable:

```md
# Ticket Dump

Generated: [timestamp]
Requested range: [range or fallback text]
Dump file date: [YYYY-MM-DD]

---

# Grouped Summary

[YYYY-MM-DD]

## [Status]
- [ITEM-ID]: [Item title]

---

# Manual Tasks

Entries here are not tracked in [provider display name]. Add tasks directly during stand-up selection. The dump creator writes this section empty; the stand-up generator appends tasks here.

---

# All Scraped [Tickets|Tasks]

## [ITEM-ID]: [Item title]

Status: [status]
Activity date: [YYYY-MM-DD]
URL: [URL or Not available]
Initial dev assignee: [name or Not available]
Testing actors: [names or None identified]
My role for this [ticket|task]: [dev-owner / contributor / tester-only]

### Why this [ticket|task] was included
[reasons]

### Description
[description]

### Comments
[comments or No comments found.]

### Activity Timeline
[timeline]

### In-Range Day Mapping
[mapping]

### Activity Notes
[notes]
```

The chat summary remains grouped by activity date and status.

## Linear Orchestrator Changes

Keep Linear-specific retrieval instructions in `workflow-orchestrator`:

- resolve current user through Linear tools
- collect candidates without assignee bias
- load issue detail and comments
- determine qualifying user activity from explicit Linear evidence
- avoid relying on one search endpoint as sole source

Replace the duplicated dump creation contract with instructions to normalize Linear issues into the shared contract and invoke `$ticket-dump-creator`.

Linear should pass `item_label: ticket`, `item_collection_label: tickets`, and `memory_subpath: memory/tickets/linear/`.

## ClickUp Orchestrator Changes

Keep ClickUp-specific retrieval instructions in `workflow-orchestrator`:

- resolve current user through ClickUp tools
- collect candidate tasks through filtered task lookup and search
- load task detail and comments
- determine qualifying user activity from explicit ClickUp evidence
- avoid relying on one search endpoint as sole source

Replace the duplicated dump creation contract with instructions to normalize ClickUp tasks into the shared contract and invoke `$ticket-dump-creator`.

ClickUp should pass `item_label: task`, `item_collection_label: tasks`, and `memory_subpath: memory/tickets/clickup/`.

## Notion Orchestrator Decision

Do not modify `workflow-orchestrator` in this refactor.

Reason: the current Notion orchestrator routes Notion content creation, drafting, updates, and reviews. It does not create activity-first ticket dumps. Including Notion now would either add new behavior or force an artificial abstraction.

## Safety Rules

- Preserve existing dump semantics for Linear and ClickUp.
- Keep provider facts source-of-truth based and explicit.
- Do not fabricate ticket details, ownership, chronology, or outcomes.
- Preserve downstream parsing stability for stand-up workflows.
- Make the shared skill provider-agnostic but not provider-retrieval-aware.

## Validation

After implementation:

- Validate `SKILL.md` frontmatter for the new skill.
- Compare Linear and ClickUp dump contracts before and after extraction for semantic parity.
- Check that existing orchestrators still mention their provider-specific retrieval strategies.
- Run repository skill sync or validation commands if available.
- Run `git diff` and confirm only intended skill/spec files changed.
