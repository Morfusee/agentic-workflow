# Implementation Ticket Drafter Design

## Purpose

Create a new skill named `implementation-ticket-drafter` for drafting feature, enhancement, refactor, and other non-bug implementation tickets.

The skill should take inspiration from `issue-drafter` by using a profile-aware draft, review, and approval workflow. It should not use bug-report framing. Its output should help an engineer understand what to build, why it matters, what is in scope, how completion will be verified, and what metadata should be handed to a publishing orchestrator.

## Scope

Add a new standalone skill under the repository-owned skill source of truth:

```text
skills/implementation-ticket-drafter/
```

Add a separate profile config under canonical memory:

```text
memory/skill-configs/implementation-ticket-drafter.json
```

The skill should draft implementation tickets and return provider-agnostic handoff metadata after approval. It must not publish directly to Linear, ClickUp, Notion, or any other provider.

## Non-Goals

- Do not modify `issue-drafter`.
- Do not reuse `memory/skill-configs/issue-drafter.json`.
- Do not include bug-specific sections such as `Steps to Reproduce` or `Expected vs Actual`.
- Do not call provider creation tools directly.
- Do not force every ticket into a large implementation spec when a lean draft is enough.

## Files

Create these skill files:

```text
skills/implementation-ticket-drafter/SKILL.md
skills/implementation-ticket-drafter/agents/openai.yaml
```

Create this memory config file:

```text
memory/skill-configs/implementation-ticket-drafter.json
```

The `SKILL.md` frontmatter must contain only:

```yaml
name: implementation-ticket-drafter
description: Draft profile-aware implementation tickets for features, enhancements, refactors, and other non-bug technical work; use when the user wants to turn implementation ideas into structured tickets with review and provider-agnostic handoff metadata.
```

The description should clearly distinguish this skill from `issue-drafter` by targeting feature implementation, enhancements, refactors, and non-bug technical work.

## Configuration

The new config should mirror useful profile concepts from `issue-drafter` while remaining separate.

Supported top-level fields:

```json
{
  "default_profile": "default",
  "profiles": {}
}
```

Supported profile fields:

```json
{
  "provider": "unspecified",
  "title_format": "[description]",
  "default_labels": [],
  "allowed_labels": [],
  "default_priority": null,
  "default_project": null,
  "default_estimate": null,
  "engineers": [],
  "service_to_engineer": {},
  "defaults": {}
}
```

`engineers` and `service_to_engineer` are optional assignment hints. The skill may suggest an assignee when profile data supports a clear inference from service, project, or area. It must not silently assign a person or claim certainty without profile evidence.

If the config file is missing, the skill should continue with neutral defaults, draft the ticket, and state that profile metadata was unavailable.

## Workflow

The skill uses a three-phase workflow.

### Phase 1: Draft

Convert the user's request into a structured implementation ticket using the active profile.

Ask for clarification before drafting when the objective, scope, or acceptance criteria are too unclear to produce an implementation-ready ticket. Do not fabricate requirements, dependencies, estimates, or assignees.

If the input is actually a bug report, regression, or problem investigation, recommend using `issue-drafter` instead.

If the request is too large for one ticket, decompose it into smaller candidate tickets and ask which one to draft first.

### Phase 2: Review

Present the draft and ask the user to review it. Accept wording changes, scope changes, metadata changes, or section changes. Re-present the draft until the user approves it.

Do not produce the final handoff package during review unless the user clearly approves the draft.

### Phase 3: Handoff

After approval, return the final Markdown ticket and structured provider-agnostic metadata. The handoff is intended for a provider-specific orchestrator or manual publishing step.

Do not call Linear, ClickUp, Notion, or other provider tools from this skill.

## Ticket Shape

The draft should use an adaptive section set.

Always include:

```markdown
**Title:** [Profile-compliant implementation title]
**Labels:** [Profile-aware labels]
**Priority:** [priority or Not specified]
**Assignee Hint:** [name/reason or Not specified]

### Objective
[What we are building or changing]

### Scope
- [Included work]
- [Included work]

### Implementation Requirements
- [Requirement]
- [Requirement]

### Acceptance Criteria
- [ ] [Observable completion condition]
- [ ] [Observable completion condition]

### Testing Notes
[How to verify the work]
```

Add these sections only when relevant:

```markdown
### Background
### User-Facing Behavior
### Non-Goals
### Data/API Changes
### Dependencies
### Risks
### Rollout Notes
### Open Questions
```

Use direct implementation language such as `Add`, `Update`, `Create`, `Refactor`, `Integrate`, or `Remove`. Avoid framing the ticket around what is broken unless the user is explicitly describing a defect.

Unknown values should appear as `Not specified` in Markdown.

## Handoff Contract

After approval, return metadata in this normalized shape:

```yaml
draft_type: implementation_ticket
profile: active-profile-or-neutral
provider: configured-provider-or-unspecified
title: final approved title
description_markdown: final approved Markdown body
labels:
  - label
priority: priority-or-null
project: project-or-null
milestone: milestone-or-null
estimate: estimate-or-null
assignee:
  suggested: name-or-null
  reason: assignee suggestion reason or null
  confidence: high | medium | low | none
open_questions:
  - remaining question when unresolved
publish_instruction: route_to_provider_orchestrator
```

Use `null` in metadata for unknown optional values. Keep `open_questions` empty when the approved ticket has no unresolved questions.

## Safety Rules

- Do not invent requirements, hidden dependencies, estimates, project names, labels, or assignees.
- Ask for clarification when missing information would materially change the implementation.
- Keep tickets implementation-ready but not over-specified.
- Preserve user-provided constraints and terminology where they improve clarity.
- Redirect bug reports to `issue-drafter` instead of forcing them into this workflow.
- Decompose broad initiatives before drafting one ticket.
- Return handoff metadata only after explicit draft approval.
- Never instruct direct provider publishing from this skill.

## Validation

After implementation:

- Confirm `skills/implementation-ticket-drafter/SKILL.md` exists.
- Confirm `SKILL.md` frontmatter contains only `name` and `description`.
- Confirm the trigger description targets non-bug implementation tickets.
- Confirm `skills/implementation-ticket-drafter/agents/openai.yaml` exists and references `$implementation-ticket-drafter`.
- Confirm `memory/skill-configs/implementation-ticket-drafter.json` exists and is separate from `issue-drafter` config.
- Confirm the skill instructs draft, review, and handoff behavior, not direct publishing.
- Confirm the ticket shape avoids bug-report sections.
- Run available repository validation or sync checks if present.
