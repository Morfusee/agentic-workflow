---
name: workflow-orchestrator
description: Unified provider workflow entrypoint for Linear, ClickUp, Notion, and ticket implementation flows. Use when the user invokes "/skill [provider] [prompt]", "/workflow-orchestrator implement [ticket-or-task]", names Linear, ClickUp, or Notion, or wants ticket dumps, stand-ups, technical ticket drafts, implementation, review comments, weekly ticket slideshows, Notion task creation, Notion task updates, or provider publishing workflows.
---

# Workflow Orchestrator

Route provider-specific productivity workflows from one skill.

## Provider Command Contract

Treat this skill as the entrypoint for commands shaped like:

```text
/skill [provider] [prompt]
/workflow-orchestrator implement [ticket-or-task]
```

When the command starts with `implement`, resolve the ticket, task, URL, or prompt context and route to `$ticket-implementation-flow`.

Supported providers:

- `linear`
- `clickup`
- `notion`

If the first argument is a supported provider, route to that provider. If no provider is supplied, infer the provider only when the request clearly names Linear, ClickUp, or Notion. If multiple providers match or confidence is low, ask one focused clarification.

For Notion, accept an optional domain after the provider:

- `personal-tasks`
- `coding-projects`

When no Notion domain is supplied, use the Notion provider reference's domain-resolution rules.

## Reference Loading

Load references only as needed:

1. Load `references/common-ticket-workflows.md` for ticket dumps, stand-ups, technical ticket drafting, review comments, weekly slideshow prep, or provider publishing.
2. Load the selected provider reference:
   - `references/providers/linear.md`
   - `references/providers/clickup.md`
   - `references/providers/notion.md`
3. For Notion domain work, load the required template:
   - `references/notion/personal-tasks-template.md`
   - `references/notion/coding-projects-template.md`

Do not load every provider reference when the provider is already clear.

## Intent Routing

After provider resolution, infer one provider-supported intent branch from the selected provider reference.

Common branches include:

- `dump-creation`
- `standup-from-dump`
- `full-flow`
- `ticket-draft`
- `implementation-flow`
- `review-comment`
- `weekly-slideshow`
- provider-specific creation, update, review, publishing, or location-resolution branches

If confidence is low, ask one focused clarification before reading, drafting, or writing.

## Execution Rules

- Use provider tools as source of truth. Do not fabricate provider IDs, URLs, schema fields, task facts, ownership, chronology, outcomes, or write targets.
- For `/workflow-orchestrator implement [ticket-or-task]`, resolve provider-backed ticket/task context first when possible, then invoke `$ticket-implementation-flow` with normalized requirements and any provider comment target.
- Preserve draft-first publishing gates. Do not create provider records from a draft until the user approves the draft and asks to create, publish, add, or equivalent.
- Preserve provider terminology in user-facing prompts: Linear uses tickets/issues, ClickUp uses tasks, Notion uses tasks/pages/databases according to the selected domain.
- Keep provider-specific dump and stand-up formats stable for downstream consumers.
- Route provider-agnostic drafting and artifact generation through helper skills named in the common reference.
- For date ranges, keep partial successes visible and report per-date failures.
- For Notion writes, fetch and validate the target immediately before writing, and stop on schema mismatch.

## Provider Extension Contract

To add a provider:

1. Add a provider reference under `references/providers/<provider>.md`.
2. Add provider aliases to the Supported providers list.
3. Define provider branches, tool prerequisites, retrieval rules, normalization fields, publishing rules, and outcome reporting.
4. Reuse `references/common-ticket-workflows.md` for shared ticket workflows instead of duplicating them.
5. Add provider-specific config under the canonical memory root only when volatile external facts are required.
