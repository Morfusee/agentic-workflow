# Phased PRD Ticket Workflow

## Phase Selection

Start by reading the invocation and available artifacts.

- If the user provides raw requirements and no handoff, start Phase 1.
- If the user provides `phase-1-handoff.md`, start Phase 2 setup and ask for the PMS destination.
- If the user provides `phase-2-subphase-NN-handoff.md`, continue the next listed development subphase.
- If the user provides only `prd.md`, create a Phase 2 setup handoff before ticket generation unless the PMS destination is already clear.

Do not proceed when the required artifact is missing. Ask for the handoff path or PRD path.

## Phase 1 Requirements Loop

Collect enough detail to make the PRD useful for ticket generation.

Cover these areas:

- Problem statement and desired outcome.
- Target users and user journeys.
- In-scope and out-of-scope behavior.
- Functional requirements.
- Non-functional requirements.
- Data, API, integration, migration, or permissions needs.
- UX, copy, analytics, accessibility, and observability needs.
- Dependencies, risks, assumptions, and rollout constraints.
- Definition of done and success metrics.

Use `$grill-me` whenever requirements are broad, risky, internally inconsistent, or likely to drive expensive implementation mistakes. Ask questions one at a time and preserve the recommended answer from each branch when accepted.

Continue until the PRD can support ticket generation without executor guesswork. Do not over-question decisions already clear from the user's materials.

## Major Concern Detection

Pause and run another `$grill-me` pass when any of these appear:

- Undefined primary user or buyer.
- Unclear product goal or measurable outcome.
- Conflicting scope statements.
- Missing security, privacy, migration, or data ownership decisions.
- A dependency that can block implementation.
- A technology or architecture assumption that affects most tickets.
- Acceptance criteria that cannot be tested.

## PRD Structure

Write `prd.md` with these sections:

```markdown
# <Product Or Feature Name> PRD

## Summary
## Goals
## Non-Goals
## Users And Use Cases
## Scope
## Requirements
## User Experience Notes
## Data, API, And Integration Notes
## Non-Functional Requirements
## Dependencies
## Risks And Mitigations
## Acceptance Criteria
## Ticket Generation Guidance
## Open Questions
```

Use direct language. After drafting, invoke `$avoid-ai-writing` in rewrite mode, apply the rewrite, then save the final PRD.

## Phase 1 Handoff Contents

Write `phase-1-handoff.md` with:

- Suggested skill: `$ticket-prd-planner`.
- Current phase completed: Phase 1.
- Next phase: Phase 2 setup.
- PRD path.
- Project slug.
- Known constraints and resolved decisions.
- Remaining open questions, if any.
- Instruction to ask the user where tickets should be created.

End the user-facing response by telling the user to start a new chat with this handoff path.

## Phase 2 Setup

Before creating tickets, ask the user to choose the PMS destination unless it is already explicit in the handoff.

Accepted destinations:

- Linear.
- ClickUp.
- Notion.
- Another destination only when the user names it and usable tooling or instructions exist.

Resolve destination-specific location details before publishing, such as Linear team/project, ClickUp list, or Notion database/project.

If the PRD omits a major architecture or stack decision, ask only that decision. Otherwise infer execution phases from the PRD.

## Development Phase Planning

Create a complete ordered list of development/execution subphases before creating the first subphase tickets.

Each subphase should have:

- Objective.
- Dependencies.
- Included ticket themes.
- Expected provider ticket count.
- Exit criteria.

Store the overall list in `ticket-index.md`. Do not put every future ticket body in a handoff.

## Current Subphase Ticket Creation

For one subphase per chat, create provider tickets that include:

- Title.
- Context and objective.
- Implementation requirements.
- Dependencies and ordering.
- Definition of done.
- Verification or QA notes.
- Links back to the PRD and related tickets.

Do not include personally identifiable information in ticket bodies unless it is essential to the ticket's context or implementation (e.g., an explicitly required configuration value, a required environment variable name, or a shared resource identifier). Never include local filesystem paths, user home directory paths, machine hostnames, IP addresses, email addresses, or API keys. The provider ticket store is shared; local paths and PII are meaningless to other readers and leak environmental details.

Use the destination orchestrator or provider tool appropriate to the selected PMS. If provider creation is not possible, produce provider-ready ticket drafts and state exactly what blocked publishing.

## Subphase Handoff Contents

Write `phase-2-subphase-NN-handoff.md` with:

- Suggested skill: `$ticket-prd-planner`.
- PMS destination and required project/list/database location.
- PRD path.
- Ticket index path.
- Current subphase number and name.
- Current subphase outcome.
- Provider ticket IDs/URLs created in this subphase.
- Next subphase number and name.
- Next subphase objective, dependencies, and any decision needed.

Do not include full ticket bodies once tickets have been created in the provider. The provider is the ticket store.

## Ticket Index

Maintain `ticket-index.md` as the source of truth for the overall ticket plan.

Use this structure:

```markdown
# <Project> Ticket Index

## Source Artifacts
- PRD: <path>

## PMS Destination
- Provider: <Linear | ClickUp | Notion | Other>
- Location: <team/project/list/database>

## Development Phases
| Phase | Status | Objective | Ticket References |
|---|---|---|---|
| 01 | Done | <objective> | <links> |
| 02 | Next | <objective> | Pending |
```

Update the status after each subphase.

## Completion

When all subphases are complete, save a final handoff or summary that includes:

- PRD path.
- Ticket index path.
- PMS destination.
- All phase statuses.
- Any unresolved risks or follow-up decisions.

Tell the user no further phase handoff is required unless they want implementation prep or execution support.
