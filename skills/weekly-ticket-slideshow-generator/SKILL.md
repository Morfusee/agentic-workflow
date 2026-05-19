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
- what remains open
- what is still being tracked
2. Show what the user actually worked on last week, using the dumps as the main evidence source.
3. Treat ticket dumps and stand-up scripts as evidence, not as slide copy.
4. Pull forward enough concrete ticket and task detail that the team can see the real work performed.
5. Avoid flattening the week into only high-level themes when specific work detail is what gives the update value.
3. Produce clear, usable presentation input rather than the final slide HTML.
4. Keep the output objective, evidence-based, and easy for another skill to render.
5. Leave slide layout, visual treatment, and final HTML composition to `$slideshow-generator`.

## Weekly Narrative Rules

1. Infer the weekly story from repeated activity, status movement, comments, verification, blockers, dependencies, and carried-over work.
2. Choose structure based on the requested depth instead of forcing a grouped-summary default.
3. When the user asks for in-depth coverage of each ticket or task, preserve ticket-level sections and make those sections the primary shape of the brief.
4. Group related tickets only when that grouping still preserves clear ticket-by-ticket visibility inside the section.
5. Prioritize tickets that show meaningful progress, repeated attention, QA validation, important investigation, cross-team dependency, or open-item relevance.
6. Keep technical detail in supporting notes unless it is necessary for the audience to understand the work performed, the decision made, or the outcome reached.
7. Avoid making the brief sound like a Jira export, bug triage log, or stand-up transcript.
8. Make every briefing section communicate one clear message.
9. Avoid motivational, celebratory, persuasive, or inflated phrasing.
10. Prefer factual framing over interpretive hype.
11. When the week contains substantial concrete work, prefer a more detailed section over a vague summary.
12. If a ticket has enough source material to explain the problem, the action taken, validation, and end state, include all four in the brief instead of collapsing that ticket into a one-line mention.
13. If the week contains many distinct tickets, it is acceptable for the brief to use one primary section per ticket.
14. Never include dates, days of the week, or temporal markers of any kind in the brief. This is a weekly summary report. Do not reference specific dates (e.g., "May 11", "2026-05-11"), days of the week (e.g., "Monday", "Friday"), or relative time anchors (e.g., "on the first day", "earlier this week"). The brief communicates what happened, not when it happened. This rule applies to all section content, presenter notes, work detail, and supporting evidence.
15. Exclude any mention of days where no work occurred. The brief must represent only actual work performed. Drop inactive days entirely at the ingestion step.
16. Do not use inactivity as a narrative device, contrast, or framing. Only active work items belong in the brief.

## Data Interpretation Rules

1. Treat comments, status changes, assignments, and repeated references as importance signals.
2. Treat completed tickets as outcome evidence.
3. Treat in-review tickets as validation or handoff evidence.
4. Treat in-progress tickets as active execution.
5. Treat todo tickets as incomplete work only when they connect directly to the week's narrative.
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
- what remains open, if anything
15. Do not downgrade a ticket with rich evidence into a short thematic mention when the audience would lose understanding of the actual work.
16. Discard any daily dump entries that state inactivity, no progress, or absence of work. Do not let them enter the brief.
17. When merging ticket activity across days, preserve only events that represent actual work, state change, or meaningful update.
18. Treat manual tasks from the `# Manual Tasks` section as work evidence with the same weight as tickets. Include them in the weekly narrative when they represent meaningful work, using only title, status, and activity notes as evidence.

## Handoff Structure

1. Produce information that maps cleanly into:
- title / subtitle
- weekly story
- executive snapshot
- activity flow
- priority work
- impact or insight
- open items
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
10. Before finalizing the brief, pass all presenter notes, objective summaries, and narrative content through `$avoid-ai-writing` in detect mode at the `blog` context profile. Fix every P0 and P1 flag (chatbot artifacts, word-list violations, significance inflation, template phrases, `let's` constructions, bold overuse in notes, em dashes, generic closers, hedge-stacked predictions, promotional language, real/actual adjective inflation, future-narrative closers). P2 flags (transition overuse, uniform sentence length, copula avoidance, numbered-list inflation, rhetorical question openers) should be checked and fixed when the pattern is unambiguous. The brief must read as factual internal reporting, not as AI-generated prose.

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
- takeaway when relevant
4. Preserve week context and major activity signals in the handoff.
5. Treat the handoff as the source-of-truth interpretation layer for the slideshow workflow.
6. Follow the example handoff shape in [`references/weekly-brief-example.md`](references/weekly-brief-example.md).
7. Write `suggested presenter notes` as substantive spoken paragraphs, not bullet points. Each note block must contain enough detail that a presenter can deliver real information to the audience without needing to invent material on the spot.
8. Vary presenter note length based on the section's purpose and information density. Do not force every note to the same length:
- **Light sections** (title slide, executive snapshot, closing position, simple stat summaries): write 1-3 sentences. These slides are visual cues that need brief context, not extended narration. Do not pad thin content.
- **Standard sections** (weekly story overview, activity flow, net effect summary): write 2-4 sentences covering what the section shows, why it matters, and the key takeaway.
- **Heavy sections** (detailed ticket breakdowns, priority work with multiple tickets, impact analysis): write 3-5 sentences covering the problem, the action taken, the validation or result, the current state, and what remains open. These slides carry the most evidence and need the most context.
9. Keep `suggested presenter notes` factual and information-rich so `$slideshow-generator` can turn them into natural spoken script without adding hype or padding thin input.
9. Use `work detail` to show the concrete tasks performed, validations made, findings recorded, or follow-through completed for the tickets in that section.
10. Include ticket IDs inside `work detail` whenever that helps the audience map the work back to actual items.
11. When a ticket is covered as its own section, structure `work detail` so it answers:
- what broke or needed attention
- what was done
- how it was checked
- what the current state is

## Execution Steps

1. Resolve target week under `tickets/linear/YYYY-W##/` in the canonical memory root defined in OpenCode's global AGENTS.md.
2. Parse `# All Scraped Tickets`, `# Selected Tickets`, `# Manual Tasks`, and stand-up script content from each daily dump. When any dump in the week contains a `# Selected Tickets` section, use the selected ticket IDs as an inclusion filter — only tickets that appear in at least one `# Selected Tickets` section across the week are included in the brief. When no `# Selected Tickets` section exists in any dump, fall back to including all tickets from `# All Scraped Tickets`. Never include tickets listed only in `# Unselected Tickets` unless they also appear in `# Selected Tickets`.
3. Filter out any daily entries that describe inactivity, no progress, or no work performed. Drop them entirely before merging.
4. Merge same ticket IDs and manual task IDs across the week and preserve chronological events.
5. Identify the strongest weekly themes and the tickets that best explain the actual work performed.
6. Decide whether the requested output should stay grouped or move to ticket-level sections, and prefer ticket-level sections when the user asks for in-depth coverage.
7. Build an objective weekly brief as structured narrative content, not as a chronological ticket list.
8. Keep wording audience-safe, evidence-based, and non-promotional.
9. Run all presenter notes, summaries, and narrative prose through `$avoid-ai-writing` in detect mode at the `blog` context profile. Fix every P0 and P1 flag before finalizing. Check P2 flags and fix unambiguous patterns. Remove chatbot artifacts, word-list violations (`delve`, `leverage`, `robust`, `seamless`, etc.), significance inflation, template phrases, `let's` constructions, generic closers, hedge-stacked predictions, and promotional language. The brief must read as plain factual internal reporting.
10. Hand the resulting brief to `$slideshow-generator` for slide interpretation and HTML composition. Inject the output path `tickets/linear/YYYY-W##/weekly-slideshow.html` under the canonical memory root defined in OpenCode's global AGENTS.md so the generated file lands alongside the ticket dumps for that week.
11. Do not take over slide rendering responsibilities unless the user explicitly asks for a combined workflow.

## Rules

1. Do not invent ticket or task facts that are not supported by the dumps or stand-up scripts.
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
14. Treat manual tasks from the `# Manual Tasks` section as equal work evidence alongside scraped tickets.
15. When manual tasks share a theme or area with tickets, group them together in the same brief section.
16. Keep manual task narrative in the brief factual and brief, using only title, status, and activity notes as evidence.
17. Vary presenter note depth proportionally to the section. Light overview sections get short, direct notes. Heavy ticket-breakdown sections get fuller notes with context, evidence, and resolution. Do not write a long note for a thin slide or a thin note for an evidence-rich slide.
