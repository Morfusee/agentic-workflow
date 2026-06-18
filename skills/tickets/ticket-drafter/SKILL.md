---
name: ticket-drafter
description: Draft profile-aware technical tickets for defects, regressions, production problems, feature work, enhancements, refactors, migrations, and other implementation work. Use when turning loose input into an engineer-ready ticket with draft classification, review, iteration, and provider-agnostic handoff metadata. Do not publish directly; provider orchestrators own Linear, ClickUp, Notion, or other writes.
---

# Ticket Drafter

Draft engineer-ready technical tickets from loose input. Classify the request, resolve the profile, draft the right ticket shape, review with the user, then return normalized handoff metadata after approval.

## Quick Start

1. Load `skill-configs/ticket-drafter.json` from the canonical memory root.
2. Resolve the caller-provided profile, or use `default_profile`.
3. Classify the request as `defect` or `implementation`.
4. Draft using the matching profile defaults and the templates in [formats.md](references/formats.md).
5. Ask the user to review the draft.
6. After explicit approval, return the final Markdown plus handoff metadata. Do not publish.

## Config Contract

Use one active profile only. Do not mix defaults between profiles or draft types.

- `profiles[*].provider`: preferred provider context.
- `profiles[*].publisher`: provider orchestrator that owns writes.
- `profiles[*].draft_types.defect`: defaults for defects, regressions, broken behavior, production problems, and investigations.
- `profiles[*].draft_types.implementation`: defaults for planned features, enhancements, refactors, migrations, integrations, removals, and cleanup.
- `profiles[*].engineers` and `profiles[*].service_to_engineer`: optional assignment hints.
- `profiles[*].defaults`: provider-specific metadata to pass through during handoff.

If config, profile, or draft type cannot be resolved, continue with neutral defaults and state that profile metadata was unavailable.

## Classification

- Use `defect` for bugs, regressions, broken behavior, production problems, missing expected behavior, failure-oriented feedback, and problem investigations.
- Use `implementation` for planned features, enhancements, refactors, migrations, integrations, removals, cleanup, and other non-bug technical work.
- If the request mixes independent work, list candidate tickets and ask which one to draft first.
- If classification is unclear, ask one focused clarification.

## Drafting Rules

- Do not fabricate requirements, reproduction steps, dependencies, risks, estimates, project names, labels, assignees, or provider fields.
- Follow the active draft type's `title_format`; otherwise use a concise imperative title.
- Start with `default_labels`. Add only labels supported by `allowed_labels` when that list is non-empty.
- Choose services only from the active draft type's `services`; do not force a service prefix.
- Suggest assignees only when profile evidence supports the suggestion.
- Use `Not specified` in Markdown and `null` in handoff metadata for unknown optional values.
- Honor explicit caller format overrides, such as ClickUp's Description -> Scope -> Deliverable convention.

## Defect Mode

Use direct fix language such as `Fix`, `Restore`, `Prevent`, `Update`, or `Investigate`. Avoid user-story framing. Focus on what is broken and how it should work. Ask for missing reproduction, expected behavior, or actual behavior when those are necessary to produce an actionable ticket.

Use the defect template and sample in [formats.md](references/formats.md).

## Implementation Mode

Use direct implementation language such as `Add`, `Update`, `Create`, `Refactor`, `Integrate`, `Migrate`, or `Remove`. Do not use defect sections such as `Steps to Reproduce`, `Expected vs Actual`, or `The Problem` unless the ticket is reclassified as a defect.

Use the implementation template and sample in [formats.md](references/formats.md).

## Review And Handoff

Present the draft and ask the user to review it. Iterate on wording, scope, labels, priority, services, assignee hints, sections, and ticket splitting until the user is satisfied.

Return handoff metadata only after an explicit approval signal such as `approved`, `looks good`, `handoff`, `ready to publish`, or `create it through the provider`.

Use the handoff schema in [formats.md](references/formats.md). Do not call Linear, ClickUp, Notion, or other provider creation tools from this skill.
