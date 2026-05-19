---
name: weekly-ticket-slideshow-generator
description: Transform weekly ticket dumps and stand-up scripts into an objective weekly presentation brief for $slideshow-generator. Use when weekly work needs to be pulled from dump files, normalized, and turned into clear presentation-ready information that shows what the user actually worked on last week without directly authoring the final slideshow HTML.
---

# Weekly Ticket Slideshow Generator

Transform weekly ticket evidence into a structured presentation brief, then hand that brief to `$slideshow-generator`. Stop at the interpretation layer; do not render final HTML unless explicitly asked for a combined workflow.

## Objective

Answer five questions from evidence:

- what happened
- why it mattered
- what changed
- what remains open
- what is still being tracked

Use ticket dumps and stand-up scripts as evidence, not slide copy. Show concrete work performed; do not flatten a substantial week into vague themes.

## Evidence Rules

1. Resolve the target week under `tickets/linear/YYYY-W##/` in the canonical memory root defined in OpenCode global `AGENTS.md`.
2. Parse `# All Scraped Tickets`, `# Selected Tickets`, `# Manual Tasks`, and stand-up script content from each daily dump.
3. If any dump has `# Selected Tickets`, include only tickets selected at least once across the week. Otherwise include all tickets from `# All Scraped Tickets`. Never include tickets listed only in `# Unselected Tickets`.
4. Treat `# Manual Tasks` as equal work evidence when meaningful, using only title, status, and activity notes.
5. Merge same ticket/manual IDs across the week while preserving only events that represent actual work, state change, validation, decision, blocker/dependency, or meaningful update.
6. Drop inactivity, no-progress, and no-work entries at ingestion. Never mention inactive days or use inactivity as framing.
7. Do not include dates, days of week, or temporal markers in brief content, presenter notes, work detail, or supporting evidence.
8. Do not invent facts, impact, work performed, status movement, plans, blockers, or outcomes.

## Interpretation Rules

1. Choose grouped or ticket-level structure based on requested depth and evidence density.
2. Preserve ticket/task-level visibility when the user asks for in-depth coverage or when the audience would lose understanding from a broad summary.
3. Group related tickets only when each included ticket remains visible enough to show the actual work.
4. Prioritize tickets with repeated attention, meaningful status movement, QA validation, investigation, cross-team dependency, open-item relevance, or representative detail for a broader cluster.
5. For each prioritized ticket/task, capture problem or need, user action, validation/change, current state, and remaining open work when present.
6. Treat blockers and dependencies as context, not drama.
7. Keep technical detail only when it explains the work, decision, outcome, or unresolved state.

## Handoff Contract

Produce a structured weekly presentation brief, not HTML. Follow the handoff shape in [`references/weekly-brief-example.md`](references/weekly-brief-example.md).

Include enough detail for `$slideshow-generator` to render without re-reading raw dumps:

- title and subtitle
- weekly story
- executive snapshot
- activity flow
- priority work
- impact or insight
- open items
- closing position

For each section, provide section title, objective summary, why it matters, supporting evidence, work detail, suggested presenter notes, and takeaway when relevant. Name relevant tickets/tasks in sections that reference specific work.

Presenter notes must be factual paragraph prose, not bullets. Vary note depth by section: light sections get brief context, standard sections explain the message and takeaway, heavy ticket sections cover problem, action, validation/result, state, and open work.

## Language Rules

1. Use plain, concrete, neutral internal-reporting language.
2. Prefer verbs such as `worked on`, `checked`, `confirmed`, `documented`, `updated`, `reviewed`, `tested`, `followed up`, `fixed`, `verified`, `clarified`, `moved to review`, `closed`, and `carried over`.
3. Avoid motivational, celebratory, persuasive, inflated, promotional, or presentation-slogan wording.
4. Do not hide concrete work behind abstract phrases like `advanced the initiative` or `supported progress`.
5. Before finalizing the brief, run presenter notes, summaries, and narrative prose through `$avoid-ai-writing` in detect mode with the `blog` context profile. Fix all P0/P1 flags and unambiguous P2 issues.

## Execution

1. Read weekly dumps and build the evidence set using the rules above.
2. Identify the strongest weekly story and the tickets/tasks that explain the work performed.
3. Build the structured brief from evidence, preserving detail proportional to the requested depth.
4. Run the anti-AI-writing check and revise flagged prose.
5. Hand the brief to `$slideshow-generator` and inject output path `tickets/linear/YYYY-W##/weekly-slideshow.html` under the canonical memory root.

## Non-Negotiables

1. Do not copy raw dumps into the brief.
2. Do not summarize away meaningful ticket/task detail.
3. Do not render slides unless explicitly asked.
4. Keep `$weekly-ticket-slideshow-generator` as evidence interpretation and `$slideshow-generator` as slide composition.
5. Keep manual tasks factual and brief; group them with related tickets when useful.
