---
name: standup-generator
description: Generate a spoken stand-up script from structured work items, explicit next-day plans, and explicit evidence, with strict attribution and chronology rules. Use when the user wants an agnostic stand-up script from tickets, tasks, notes, or mixed sources without source-specific assumptions.
---

# Stand-up Generator

Generate stand-up narration from selected work items only. Stay source-agnostic and treat input evidence as the only truth.

## Inputs

- Require selected work items plus supporting evidence for each item.
- Accept mixed sources (tickets, docs, manual tasks, notes) when each item has title, status, activity date, and evidence notes.
- Require explicit plan evidence for any forward-looking section; if requested but missing, ask one focused clarification instead of guessing.
- If evidence is missing for material claims, ask one focused clarification instead of guessing.

## Script Principles

1. Build narrative from evidence, not prior stand-up prose.
2. Keep chronology strict per item from earliest relevant action to current state.
3. Convert event logs into natural speech with concrete verbs and outcomes.
4. Enforce attribution: never claim the speaker implemented/fixed work without explicit evidence.
5. For tester-only evidence, use testing/verification language only.
6. Stay factual, conversational, and concise; avoid hype and filler.

## Output Contract

- Start with `Yesterday, I ...`.
- Include `Today, I plan to ...` only from user-provided plan text or other explicit plan evidence.
- Walk selected items in chronological order.
- Avoid internal IDs in spoken narration unless the user explicitly asks.
- End with blocker line:
- Default: `No major blockers right now.`
- Replace only when blockers are explicitly provided by the user or evidence.

## Rules

1. Never fabricate missing actions, ownership, reasons, or outcomes.
2. Prefer detail over over-compression when several meaningful steps exist.
3. Keep uncertain statements literal and scoped to known facts.
4. Never infer next-day plans from remaining open work, unselected work, or carry-over items.
5. If rerunning, ignore old script text and regenerate from selected evidence.
6. Allow wrappers to add source-specific formatting/selection behavior while preserving these principles.
