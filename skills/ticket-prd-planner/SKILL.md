---
name: ticket-prd-planner
description: Create phased PRDs and turn approved PRDs into provider-backed execution ticket plans. Use for product requirement discovery, PRD creation, grill-me refinement, phase splitting, and ticket generation across Linear, ClickUp, or Notion. Do not use for already-scoped single tickets.
---

# Ticket PRD Planner

## Purpose

Drive a multi-chat workflow that turns rough requirements into a clear PRD, then turns that PRD into executable development phases and provider-created tickets.

Use this skill only by explicit invocation. Each phase must end with a saved handoff document and an instruction to continue in a fresh chat with this skill plus that handoff path.

## Boundaries

- Do not skip phase handoffs, even when the next step seems obvious.
- Do not create tickets during Phase 1.
- Do not store full ticket bodies in subphase handoffs after ticket creation begins; store provider links/IDs, current subphase summary, and the next subphase target.
- Ask the user which PMS to use before Phase 2 ticket creation: Linear, ClickUp, Notion, or another explicit destination.
- Ask major unresolved decisions only when the PRD or handoff does not already answer them.
- Use the canonical memory root: `${HOME}/Documents/Programming/agentic-workflow/memory`.

## Required Skills

- Invoke `$grill-me` during Phase 1 to stress-test requirements, risks, contradictions, and major concerns.
- Invoke `$avoid-ai-writing` before saving the final PRD.
- Invoke the destination orchestrator when publishing tickets, such as `$linear-orchestrator`, `$clickup-orchestrator`, or `$notion-orchestrator`.

## Artifacts

Save artifacts under:

```text
${HOME}/Documents/Programming/agentic-workflow/memory/prds/<project-slug>/
```

Use these files:

- `prd.md` for the final PRD.
- `phase-1-handoff.md` for the PRD-to-ticket-planning handoff.
- `phase-2-subphase-NN-handoff.md` for ticket-planning subphase handoffs.
- `ticket-index.md` for provider ticket URLs/IDs and status across all subphases.

## Phase 1 - Requirements To PRD

1. Ingest requirements from user prompts, pasted data, files, or referenced artifacts.
2. Identify gaps, contradictions, risks, and major decisions.
3. Invoke `$grill-me` and run the clarification loop until requirements are implementation-ready.
4. Draft the PRD with goals, non-goals, users, scope, constraints, requirements, acceptance criteria, risks, dependencies, and ticket-generation guidance.
5. Invoke `$avoid-ai-writing` to clean the PRD before final save.
6. Save `prd.md` and `phase-1-handoff.md` under the project memory folder.
7. Tell the user to start a fresh chat and invoke this skill with the handoff path to continue Phase 2.

## Phase 2 - PRD To Execution Tickets

1. Load the PRD and the latest handoff document.
2. Ask where to create tickets before generating or publishing tickets.
3. Derive the full development/execution phase list from the PRD.
4. Work on exactly one development subphase per chat thread.
5. For the current subphase, create the necessary provider tickets with requirements, steps, dependencies, definition of done, and verification notes.
6. Update `ticket-index.md` with created ticket IDs/URLs.
7. Save a subphase handoff containing current subphase outcome, provider ticket references, and the next subphase target only.
8. Tell the user to start a fresh chat and invoke this skill with the new handoff path.
9. Repeat until all development subphases are planned and tickets exist.

## Handoff Rule

Every phase and subphase must end with this message shape:

```text
This phase is complete. Start a fresh chat and invoke `$ticket-prd-planner` with this handoff document: <path>. The next chat should continue with <next phase or subphase>.
```

## Detailed Protocol

Follow [Phased PRD Ticket Workflow](references/phased-prd-ticket-workflow.md) for PRD structure, handoff contents, ticket fields, and subphase rules.
