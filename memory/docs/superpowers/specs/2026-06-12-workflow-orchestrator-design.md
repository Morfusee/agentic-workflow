# Workflow Orchestrator Design

## Goal

Replace the separate `linear-orchestrator`, `clickup-orchestrator`, and `notion-orchestrator` skills with one provider-oriented skill that can route commands shaped like:

```text
/skill [provider] [prompt]
```

The new skill should make provider workflows easier to maintain and make future providers easy to add without creating one orchestration skill per provider.

## Scope

Create a new `skills/workflow-orchestrator/` skill that owns provider parsing, intent routing, shared ticket workflow rules, and provider reference loading.

Remove the old provider-specific orchestrator skill folders after their behavior is migrated:

- `skills/linear-orchestrator/`
- `skills/clickup-orchestrator/`
- `skills/notion-orchestrator/`

Preserve existing behavior for Linear, ClickUp, and Notion. Do not intentionally change dump formats, stand-up carry-over behavior, Notion schema safety, ticket drafting contracts, publishing approval gates, or helper skill handoffs.

## Skill Structure

Use this structure:

```text
skills/workflow-orchestrator/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── common-ticket-workflows.md
    ├── providers/
    │   ├── linear.md
    │   ├── clickup.md
    │   └── notion.md
    └── notion/
        ├── personal-tasks-template.md
        └── coding-projects-template.md
```

`SKILL.md` should stay lean and act as the entrypoint. Provider details should live in provider references. Notion's deep domain templates should remain separate because Personal Tasks and Coding Projects have distinct schema and drafting rules.

## Routing Design

The skill should parse the first argument after `/skill` as the provider when present:

- `linear`
- `clickup`
- `notion`

If no provider is supplied, infer the provider only when the user clearly names one. If multiple providers match or confidence is low, ask one focused clarification.

The skill should support examples like:

```text
/skill linear create my standup dump for yesterday
/skill clickup draft a ticket for the enrollment failure
/skill notion add a personal task to renew my passport
/skill notion coding-projects draft a bug for the sync issue
```

For Notion, allow the second argument to narrow the domain when present:

- `personal-tasks`
- `coding-projects`

When no Notion domain is supplied, use the existing Notion domain-resolution rules.

## Shared Workflow Rules

Move provider-neutral ticket workflow rules into `references/common-ticket-workflows.md`:

- draft technical tickets through `$ticket-drafter`
- draft review or QA comments through `$ticket-review-comment-drafter`
- create ticket dumps through `$ticket-dump-creator`
- generate spoken stand-ups through `$standup-generator`
- route weekly slideshow prep through `$weekly-ticket-slideshow-generator` when supported
- preserve draft-first publishing approval gates
- preserve no-fabrication rules for ticket details, ownership, chronology, and outcomes
- preserve partial-success reporting for date range runs

Linear and ClickUp provider references should define only the differences: tool names, activity retrieval rules, labels, memory subpaths, item terminology, publish field mapping, and provider-specific formatting conventions.

## Provider Behavior

### Linear

Preserve these branches:

- `dump-creation`
- `standup-from-dump`
- `full-flow`
- `ticket-draft`
- `weekly-slideshow`
- `review-comment`

Preserve the Linear dump path under `memory/tickets/linear/`, ticket terminology, assignment semantics, subscription/watching exclusion, and immediate post-dump stand-up selection prompt.

### ClickUp

Preserve these branches:

- `dump-creation`
- `standup-from-dump`
- `full-flow`
- `ticket-draft`
- `review-comment`

Preserve the ClickUp dump path under `memory/tickets/clickup/`, task terminology, watching exclusion, ClickUp ticket format convention, and list-resolution requirement before publishing.

### Notion

Preserve these branches:

- `domain-resolution`
- `personal-task-draft`
- `personal-task-create`
- `personal-task-update`
- `personal-task-review`
- `coding-ticket-draft`
- `coding-ticket-create`
- `coding-ticket-update`
- `coding-ticket-review`
- `coding-ticket-implement`
- `location-resolution`

Load Notion volatile facts from `memory/skill-configs/notion-orchestrator.json` initially to avoid an unnecessary config migration. The provider reference may name this as legacy config and can later support `workflow-orchestrator.json` if desired.

Preserve Notion write safety:

- fetch targets immediately before writes
- validate schemas and configured field names
- stop on schema mismatch
- prefer additive updates
- publish only after approval unless the command is simple and fully specified

## Migration Plan

1. Create `skills/workflow-orchestrator/`.
2. Write `SKILL.md` with provider parsing, intent routing, provider reference loading, and safety rules.
3. Add `agents/openai.yaml` with `$workflow-orchestrator` as the default prompt reference.
4. Move common ticket rules into `references/common-ticket-workflows.md`.
5. Migrate Linear instructions into `references/providers/linear.md`.
6. Migrate ClickUp instructions into `references/providers/clickup.md`.
7. Migrate Notion instructions into `references/providers/notion.md`.
8. Move Notion domain templates into `references/notion/`.
9. Remove the old provider-specific orchestrator folders.
10. Validate skill structure and frontmatter.

## Validation

Validate that:

- `skills/workflow-orchestrator/SKILL.md` exists.
- `SKILL.md` frontmatter has only `name` and `description`.
- skill name is lowercase, hyphenated, and under 64 characters.
- `agents/openai.yaml` strings are quoted.
- old orchestrator folders are removed.
- migrated references exist.
- no old `$linear-orchestrator`, `$clickup-orchestrator`, or `$notion-orchestrator` self-references remain except in historical config names or migration notes.

If no dedicated validation script exists, use shell checks and report that limitation.

## Risks

The main risk is making `SKILL.md` too large, which would weaken trigger quality and make future providers harder to slot in. Keep the entrypoint small and push provider detail into references.

The second risk is over-normalizing Notion. Treat Notion as a provider with its own domains, not as a ticket tracker clone.

The third risk is accidentally changing ticket dump or stand-up formats. Preserve those contracts exactly unless a later request explicitly changes them.
