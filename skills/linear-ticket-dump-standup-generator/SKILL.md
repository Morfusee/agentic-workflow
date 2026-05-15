---
name: linear-ticket-dump-standup-generator
description: Read the latest ticket dump Markdown file, let the user choose tickets, generate a spoken stand-up script, and update the same dump file in place. Use when the user asks to prepare stand-up from existing dump data, select tickets for stand-up, or finalize a ticket dump with a script.
---

# Ticket Dump Stand-up Script Generator

Read the latest compatible ticket dump, collect a selection from the user, generate a natural stand-up script, and finalize the same dump file in place.

Use the dump file as source of truth. Do not query Linear unless the user explicitly asks.

## Execution Steps

1. Locate the latest compatible dump file.
- Search under `memory/tickets/`.
- Prefer the latest ISO week folder `YYYY-W##`.
- Inside that folder, prefer the most recent `YYYY-MM-DD-ticket-dump.md`.
- If none exists, report the missing dump and ask the user to run the dump creator skill first.

2. Show source file and available tickets.
- Print the dump file path that will be used.
- Parse the `# All Scraped Tickets` section for the full ticket pool.
- If `# Selected Tickets` exists, parse it as the selected-ticket index for reruns, then resolve full details from `# All Scraped Tickets`.
- Display a numbered list with ticket ID, title, status, and activity date.

3. Ask for selection with this exact prompt.
- `Which tickets do you want to include in your stand-up? You can reply with ticket numbers, ticket IDs, or all.`

4. Interpret ticket selection.
- Accept `all`.
- Accept numeric list matching displayed numbers.
- Accept ticket IDs.
- Accept clear natural-language selections.
- If ambiguous, ask a short clarification and do not guess.

5. Generate stand-up script from selected tickets only.
- Treat existing `# Stand-up Script` text as output-only; never use it as input evidence.
- Build the script from selected ticket sections and their activity flow/comments.
- Use selected-ticket data as the only evidence source.
- For each selected ticket, infer and state:
- Starting point: how/why the ticket began from the earliest relevant activity and notes.
- Current state: where the ticket stands now based on latest status and latest meaningful activity, blended naturally into the same paragraph.
- Keep chronology strict per ticket; use `Activity flow` itself as the narrative backbone and include all meaningful middle steps.
- Write objective statements from explicit data points (status, activity date, timeline events, comments, activity notes, test results), while allowing practical wording that makes the update clear to listeners.
- Prefer concrete action wording tied to evidence and transform event types into spoken updates:
- Ticket creation: use natural non-identifier phrasing such as `I created a ticket to address [issue]` or `I created a ticket for [problem area]`.
- Comments: never narrate as `I posted/commented`; instead state the content/update directly.
- Testing: narrate as `I tested ...` and include the concrete result.
- Cancel/revise/scope/status change events: state plainly that the ticket was cancelled/revised/re-scoped/moved and include the stated reason/details when present.
- Include comment content and relevant details matter-of-factly; do not omit important specifics.
- For `Done` tickets with verification evidence:
- If the ticket is bug-oriented (fix/error/issue/broken/incorrect), describe outcome as fixed.
- If the ticket is feature/enhancement-oriented (add/implement/enable/new behavior), describe outcome as implemented.
- Avoid repetitive phrasing like `current state is ...`; weave outcome/state into the ticket narrative sentence.
- If data is missing for a step, state only what is known and continue; do not fill gaps.
- Keep language conversational but factual; avoid fluff, hype, and report-style labels.
- Keep structure simple:
- Start with `Yesterday, I ...`.
- Walk ticket-by-ticket in chronological order using selected tickets.
- Do not use ticket numbers or unique identifiers in the spoken script.
- Apply blocker rule:
- Default blocker line: `No major blockers right now.`
- Replace only when blockers are explicitly provided by the user or clearly indicated by selected ticket context.

6. Update the same dump file in place.
- Add stand-up section at the top as the finalized signal.
- Keep a lightweight `# Selected Tickets` section as references only.
- Do not duplicate full ticket description/comments/timeline in `# Selected Tickets`.
- Keep full `# All Scraped Tickets` section containing selected and unselected tickets.
- Preserve original scraped ticket history.
- If selection is `all`, include all tickets in the selected reference list.

## Updated Dump Contract

Use this structure:

```md
# Stand-up Script

Yesterday, I [state only actions supported by selected-ticket data, in chronological order].

I also [continue with remaining selected tickets using explicit actions and outcomes from selected-ticket data only].

No major blockers right now.

---

# Selected Tickets

- [TICKET-ID]: [Ticket title]
  - Status: [status]
  - Activity date: [YYYY-MM-DD]
  - URL: [Linear URL]
  - Reference: `# All Scraped Tickets` -> `## [TICKET-ID]: [Ticket title]`
  - Stand-up relevance: [Why this ticket was selected for stand-up]

---

# All Scraped Tickets

[Keep all scraped ticket details here, including selected and unselected tickets.]
```

## Rules

1. Keep this skill standalone as long as a compatible dump exists.
2. Preserve structure so downstream skills can parse reliably.
3. Do not remove, truncate, or rewrite factual ticket history.
4. If context is incomplete, state limitation briefly and ask only necessary clarification.
5. Keep selected and unselected tickets preserved in the updated file.
6. Use `# Selected Tickets` as a reference/index layer only; keep full ticket payload only in `# All Scraped Tickets`.
7. Do not collapse a ticket to only its most recent activity when earlier same-range activities exist.
8. Keep selected-ticket activity flow chronological and complete at a practical stand-up level.
9. Do not over-compress the stand-up narrative when multiple ticket activities exist; include a clear walkthrough of what happened.
10. Prefer detail over brevity by default, unless the user explicitly asks for a shorter script.
11. On reruns, avoid recency bias by ignoring previous script prose and re-deriving narrative from selected-ticket references plus `# All Scraped Tickets` data only.
12. For each selected ticket, preserve the complete practical activity chain in spoken form; never omit known middle steps between start and current state.
13. Keep inference limited to start/current-state framing and event-to-speech conversion grounded in selected-ticket evidence; when uncertain, stay literal to ticket data.
