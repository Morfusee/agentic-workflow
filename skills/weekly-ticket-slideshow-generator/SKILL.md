---
name: weekly-ticket-slideshow-generator
description: Transform weekly ticket dumps and stand-up scripts into an objective weekly presentation brief for $slideshow-generator. Use when weekly work needs to be pulled from dump files, normalized, and turned into clear presentation-ready information that shows what the user actually worked on last week without directly authoring the final slideshow HTML.
---

# Weekly Ticket Slideshow Generator

Transform weekly ticket evidence into an objective weekly presentation brief and hand that brief to `$slideshow-generator`.

## Core Objective

1. Answer five audience questions:
- what happened this week
- why it mattered
- what changed because of the work
- what still needs attention
- what happens next
2. Show what the user actually worked on last week, using the dumps as the main evidence source.
3. Treat ticket dumps and stand-up scripts as evidence, not as slide copy.
4. Pull forward enough concrete ticket and task detail that the team can see the real work performed.
5. Avoid flattening the week into only high-level themes when specific work detail is what gives the update value.
3. Produce clear, usable presentation input rather than the final slide HTML.
4. Keep the output objective, evidence-based, and easy for another skill to render.
5. Leave slide layout, visual treatment, and final HTML composition to `$slideshow-generator`.

## Weekly Narrative Rules

1. Infer the weekly story from repeated activity, status movement, comments, verification, blockers, dependencies, and follow-up work.
2. Choose structure based on the requested depth instead of forcing a grouped-summary default.
3. When the user asks for in-depth coverage of each ticket or task, preserve ticket-level sections and make those sections the primary shape of the brief.
4. Group related tickets only when that grouping still preserves clear ticket-by-ticket visibility inside the section.
5. Prioritize tickets that show meaningful progress, repeated attention, QA validation, important investigation, cross-team dependency, or next-step relevance.
6. Keep technical detail in supporting notes unless it is necessary for the audience to understand the work performed, the decision made, or the outcome reached.
7. Avoid making the brief sound like a Jira export, bug triage log, or stand-up transcript.
8. Make every briefing section communicate one clear message.
9. Avoid motivational, celebratory, persuasive, or inflated phrasing.
10. Prefer factual framing over interpretive hype.
11. When the week contains substantial concrete work, prefer a more detailed section over a vague summary.
12. If a ticket has enough source material to explain the problem, the action taken, validation, and end state, include all four in the brief instead of collapsing that ticket into a one-line mention.
13. If the week contains many distinct tickets, it is acceptable for the brief to use one primary section per ticket.
14. Never include dates, days, or periods of inactivity (e.g., "Friday inactive", "no progress", "no activity", or similar).
15. Exclude any mention of days where no work occurred. The brief must represent only actual work performed.
16. Do not use inactivity as a narrative device, contrast, or framing. Only active work items belong in the brief.

## Data Interpretation Rules

1. Treat comments, status changes, assignments, and repeated references as importance signals.
2. Treat completed tickets as outcome evidence.
3. Treat in-review tickets as validation or handoff evidence.
4. Treat in-progress tickets as active execution.
5. Treat todo tickets as upcoming work only when they connect directly to the week's narrative.
6. Treat blockers and dependencies as context, not drama.
7. Treat technical errors as supporting detail unless the main point of the work was investigation.
8. Treat ticket descriptions, acceptance notes, reproductions, validations, and follow-up comments as evidence of what was actually done.
9. If several tickets belong to the same product area or workflow, summarize them together, but preserve ticket-level detail inside that grouped section when it helps the audience see the actual work.
10. Zoom in on specific tickets when any of the following is true:
- the user spent repeated attention across the week on the same item
- the work involved investigation, reproduction, validation, or technical clarification
- the ticket changed state in a meaningful way because of the user's work
- the ticket is needed to explain what was completed versus what is still pending
- the ticket is representative of a broader cluster and makes the cluster easier to understand
11. Make user impact explicit when the work affected experience, reliability, QA confidence, release readiness, or operational clarity.
12. Include stand-up-only work only when it strengthens the narrative and does not contradict ticket evidence.
13. Prefer evidence of work performed over broad labels such as `support`, `cleanup`, or `follow-up` unless the underlying detail is unavailable.
14. For each prioritized ticket, capture:
- the concrete problem or failure
- what the user did with the ticket
- what changed or was verified
- what state the ticket ended in
- what still needs to happen, if anything
15. Do not downgrade a ticket with rich evidence into a short thematic mention when the audience would lose understanding of the actual work.
16. Discard any daily dump entries that state inactivity, no progress, or absence of work. Do not let them enter the brief.
17. When merging ticket activity across days, preserve only events that represent actual work, state change, or meaningful update.

## Handoff Structure

1. Produce information that maps cleanly into:
- title / subtitle
- weekly story
- executive snapshot
- activity flow
- priority work
- impact or insight
- next-week commitments
- closing position
2. Keep the structure explicit enough that `$slideshow-generator` can interpret it without re-reading raw dump files.
3. Include enough ticket and task detail inside each section that `$slideshow-generator` can build a substantive deck instead of padding a thin summary.
4. Include source-backed notes for each section so presenter script can be written from evidence rather than guesswork.
5. For any section that references specific work, name the relevant tickets and state what was actually done on them.
6. When using ticket-level sections, make the ticket ID and ticket title explicit in the section title or section summary.

## Language Rules

1. Use plain, concrete, and neutral language.
2. Avoid inspirational tone, inflated framing, or claims that overstate routine work.
3. Prefer verbs such as `fixed`, `verified`, `clarified`, `moved to review`, `grouped`, `closed`, and `carried over`.
4. Avoid language such as `transformative`, `major step`, `strong momentum`, `big win`, or similar framing unless the evidence clearly justifies it.
5. Keep summaries concise and factual.
6. Avoid polished or persuasive phrasing when a simpler sentence says the same thing.
7. Prefer straightforward weekly-report wording over presentation-slogan wording.
8. Prefer `worked on`, `checked`, `confirmed`, `documented`, `updated`, `reviewed`, `tested`, or `followed up` when those verbs describe the work more accurately than stronger wording.
9. Do not hide concrete work behind abstract phrasing such as `advanced the initiative` or `supported progress`.

## Output Contract

1. Output a structured weekly presentation brief, not the final slideshow HTML.
2. Make the brief usable as direct input to `$slideshow-generator`.
3. For each section, provide:
- section title
- objective summary
- why it matters
- supporting evidence
- work detail
- suggested presenter notes
- next action or takeaway when relevant
4. Preserve week context and major activity signals in the handoff.
5. Treat the handoff as the source-of-truth interpretation layer for the slideshow workflow.
6. Follow the example handoff shape in [`references/weekly-brief-example.md`](references/weekly-brief-example.md).
7. Write `suggested presenter notes` as readable paragraph prose, not bullet points.
8. Keep `suggested presenter notes` simple and factual so `$slideshow-generator` can turn them into natural spoken script without adding hype.
9. Use `work detail` to show the concrete tasks performed, validations made, findings recorded, or follow-through completed for the tickets in that section.
10. Include ticket IDs inside `work detail` whenever that helps the audience map the work back to actual items.
11. When a ticket is covered as its own section, structure `work detail` so it answers:
- what broke or needed attention
- what was done
- how it was checked
- what the current state is

## Execution Steps

1. Resolve target week under `memory/tickets/YYYY-W##/`.
2. Parse `# All Scraped Tickets` and stand-up script content from each daily dump.
3. Filter out any daily entries that describe inactivity, no progress, or no work performed. Drop them entirely before merging.
4. Merge same ticket IDs across the week and preserve chronological events.
5. Identify the strongest weekly themes and the tickets that best explain the actual work performed.
6. Decide whether the requested output should stay grouped or move to ticket-level sections, and prefer ticket-level sections when the user asks for in-depth coverage.
7. Build an objective weekly brief as structured narrative content, not as a chronological ticket list.
8. Keep wording audience-safe, evidence-based, and non-promotional.
9. Hand the resulting brief to `$slideshow-generator` for slide interpretation and HTML composition.
10. Do not take over slide rendering responsibilities unless the user explicitly asks for a combined workflow.

## Rules

1. Do not invent ticket facts that are not supported by the dumps or stand-up scripts.
2. Do not copy raw ticket dumps into the handoff summary.
3. Do not let the brief collapse into ticket-by-ticket reporting unless the source week truly supports that shape.
4. Prefer objective wording such as validated behavior, clarified workflow, documented issue, fixed display, moved to review, or pending follow-through.
5. Keep presenter-note inputs factual and readable.
6. Preserve original week context and chronology while summarizing, but do not summarize away the work detail that gives the team visibility.
7. Do not default to repository `scripts/`, `assets/`, or `output/` folders as the core mechanism.
8. Keep the role boundary clear:
- `$weekly-ticket-slideshow-generator` interprets dumps into structured information
- `$slideshow-generator` interprets structured information into slides
9. If a grouped section becomes too vague, add more concrete ticket detail instead of adding hype.
10. If a week contains several meaningful tickets in the same area, prefer a grouped section with detailed sub-work over a single bland summary sentence.
11. If the user asks to cover each ticket or task in depth, do not compress the week into only grouped overview slides.
12. Never mention days of inactivity, no progress, or absence of work in any section, note, or summary.
13. Do not use inactive days as contrast, pacing, or narrative framing. Remove them at the ingestion step.
