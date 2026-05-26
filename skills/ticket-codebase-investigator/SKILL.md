---
name: ticket-codebase-investigator
description: Investigate tracker tickets, issue batches, bug reports, or performance tasks against a real codebase and return source-aware root causes, implementation plans, effort estimates, and risk ranking. Use when the user asks to triage, size, groom, or analyze one or more Linear, ClickUp, Jira, GitHub, or similar tickets with code evidence.
---

# Ticket Codebase Investigator

Use this skill to turn tracker work into implementation-ready findings grounded in the repository.

## Workflow

1. Identify the source system, ticket IDs, requested filters, target repository, and expected output.
2. Load each ticket from the source system when connector tools are available. If the user supplied ticket text directly, use it as the source and preserve the original details.
3. Inspect the codebase before planning. Read actual files that establish framework, routing, component, data, deployment, or test patterns.
4. For 3 or more independent tickets, consider delegating read-only investigation with `$skill-orchestrator-go`. Use one codebase survey and one narrow investigator per ticket when parallel tools are available.
5. Confirm source-system details before acting on Chronicle, memories, or summaries. Treat those as discovery signals only.
6. Produce a compact report with evidence, exact files, likely implementation steps, effort, risk, and open questions.

## Investigation Rules

- Prefer existing repo patterns over generic advice.
- Read representative files, configs, tests, and analogous implementations before naming a fix.
- Separate code-required work from CMS/content/config-only work.
- Mark any source-system field that could not be confirmed.
- Do not modify code unless the user explicitly asks for implementation after the investigation.
- Do not create or update tickets unless the user explicitly requests publishing.

## Output Shape

For each ticket, include:

- Ticket ID and title.
- Source and date checked.
- Status, owner/assignee, and URL when available.
- Findings or root causes with file evidence.
- Implementation plan with exact files to create or edit.
- Validation plan.
- Effort estimate and risk.
- Open questions or blockers.

For batches, end with a ranked summary by effort, risk, and likely impact.

## Parallel Pattern

Use the detailed guide in `references/parallel-ticket-investigation.md` when the user asks for a batch investigation, grooming pass, or effort ranking across 3 or more tickets.
