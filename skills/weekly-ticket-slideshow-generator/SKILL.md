---
name: weekly-ticket-slideshow-generator
description: Transform weekly ticket dumps and stand-up scripts into a presentation-grade Reveal.js deck. Use when weekly work needs to be interpreted into a clear story of what happened, why it mattered, what changed, what still needs attention, and what happens next, and have the LLM generate the final HTML directly.
---

# Weekly Ticket Slideshow Generator

Transform weekly ticket evidence into a presentation-grade weekly deck and have the LLM generate the final Reveal-style HTML directly.

## Core Objective

1. Answer five audience questions:
- what happened this week
- why it mattered
- what changed because of the work
- what still needs attention
- what happens next
2. Treat ticket dumps and stand-up scripts as evidence, not as slide copy.
3. Build a deck that feels intentional, audience-friendly, and visually useful.
4. Support spoken delivery instead of replacing it.
5. Default to direct HTML generation by the LLM instead of deterministic script rendering.

## Weekly Narrative Rules

1. Infer the weekly story from repeated activity, status movement, comments, verification, blockers, dependencies, and follow-up work.
2. Do not default to one slide per ticket.
3. Group related tickets into themes, workflows, systems, outcomes, or follow-through areas.
4. Prioritize tickets that show meaningful progress, repeated attention, QA validation, important investigation, cross-team dependency, or next-step relevance.
5. Keep technical detail in `speakerScript` unless it is necessary for the audience to understand impact.
6. Avoid making the deck sound like a Jira export, bug triage log, or stand-up transcript.
7. Make every content slide communicate one clear message.

## Data Interpretation Rules

1. Treat comments, status changes, assignments, and repeated references as importance signals.
2. Treat completed tickets as outcome evidence.
3. Treat in-review tickets as validation or handoff evidence.
4. Treat in-progress tickets as active execution.
5. Treat todo tickets as upcoming work only when they connect directly to the week's narrative.
6. Treat blockers and dependencies as context, not drama.
7. Treat technical errors as supporting detail unless the main point of the work was investigation.
8. If several tickets belong to the same product area or workflow, summarize them together.
9. Make user impact explicit when the work affected experience, reliability, QA confidence, release readiness, or operational clarity.
10. Include stand-up-only work only when it strengthens the narrative and does not contradict ticket evidence.

## Recommended Deck Flow

1. Title slide with week identifier and a concise subtitle summarizing the week's focus.
2. Weekly story slide with one clear summary of what the week was mainly about.
3. Executive snapshot slide with three to five concise activity themes.
4. Activity flow slide showing movement through states such as Todo, In Progress, In Review, and Done.
5. Priority work slide highlighting selected tickets that best represent the week.
6. Impact or insight slide explaining the non-obvious takeaway from the week's work.
7. Next-week commitments slide summarizing practical follow-through.
8. Closing slide reinforcing weekly outcome and immediate priorities.

## Slide Construction Rules

1. Keep slide text scannable within five to eight seconds.
2. Use short, presentation-grade summaries instead of raw ticket wording.
3. Ensure `speakerScript` explains the slide without restating its visible text.
4. Prefer fewer, stronger slides over many weak slides.
5. Avoid decorative charts or diagrams that add no explanatory value.
6. Vary slide purpose and structure so the deck does not feel repetitive.

## Output Contract

1. Generate the final slideshow HTML directly unless the user explicitly asks for an intermediate payload.
2. Use Reveal.js structure and author slides as presentation-grade HTML sections.
3. Include presenter notes or speaker-script support in the HTML when useful.
4. Keep slide composition intentionally non-deterministic:
- allow the LLM to choose layout emphasis
- allow the LLM to vary slide composition by week
- avoid locking the deck into a rigid template when the evidence suggests a better story shape
5. If a structured intermediate representation is useful for reasoning, treat it as private working structure rather than the required final deliverable.
6. Choose visuals only when they clarify sequence, grouping, dependency, impact, or next actions.

## Execution Steps

1. Resolve target week under `memory/tickets/YYYY-W##/`.
2. Parse `# All Scraped Tickets` and stand-up script content from each daily dump.
3. Merge same ticket IDs across the week and preserve chronological events.
4. Identify the strongest weekly themes and the few tickets that best represent them.
5. Build the deck as aggregate narrative content, not as a chronological ticket list.
6. Write the final Reveal-style HTML directly.
7. Keep wording objective, audience-safe, and outcome-focused.
8. Use scripts, assets, or deterministic renderer paths only if the user explicitly asks for them or if direct HTML generation is blocked.

## Rules

1. Do not invent ticket facts that are not supported by the dumps or stand-up scripts.
2. Do not copy raw ticket dumps into slide text.
3. Do not let the deck collapse into ticket-by-ticket reporting unless the source week truly supports that shape.
4. Prefer outcome-focused wording such as validated behavior, clarified workflow, prepared evidence, improved consistency, or moved toward review.
5. Keep presenter scripts polished, natural, and useful for live delivery.
6. Preserve original week context and chronology while summarizing aggressively.
7. Do not default to repository `scripts/`, `assets/`, or `output/` folders as the core mechanism.
8. Treat deterministic rendering as an optional fallback, not as the primary workflow.
