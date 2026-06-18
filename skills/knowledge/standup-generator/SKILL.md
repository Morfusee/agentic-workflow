---
name: standup-generator
description: Generate a spoken stand-up script from selected work items, next-day plans, and explicit evidence. Use after ticket/task facts are collected from dumps, notes, or mixed sources. Does not retrieve provider data itself.
---

# Stand-up Generator

Generate stand-up narration from selected work items only. Stay source-agnostic and treat input evidence as the only truth.

## Inputs

- Require selected work items plus supporting evidence for each item.
- Require an explicit next-day plan when the user wants a forward-looking section.
- Accept mixed sources (tickets, docs, manual tasks, notes) as long as each item has a title, status, activity date, and evidence notes.
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
- Include an explicit `Today, I plan to ...` line only from user-provided plan text or other explicit plan evidence.
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
5. If a next-day plan is requested but not supplied, ask one focused clarification instead of guessing.
6. If rerunning, ignore old script text and regenerate from selected evidence.
7. Allow wrappers (for specific data sources) to add formatting/selection behavior while preserving these principles.
