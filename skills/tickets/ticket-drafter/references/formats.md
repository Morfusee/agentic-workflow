# Ticket Drafter Formats

Use these templates after resolving the active profile and draft type.

## Defect Template

```markdown
**Title:** [Profile-compliant technical title]
**Labels:** [Profile-aware labels]
**Priority:** [priority or Not specified]
**Assignee Hint:** [name and reason or Not specified]

### The Problem
[Direct quote or 1-sentence summary of the regression]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Technical Requirements
- [Technical detail]
- [Technical detail]

### Expected vs Actual
- **Expected:** [How the system should behave]
- **Actual:** [How it is currently failing]

### Acceptance Criteria
- [ ] [Observable fix condition]
- [ ] [Observable fix condition]
```

Use `Not applicable.` for a section only when it truly does not apply. Do not invent reproduction steps.

## Implementation Template

```markdown
**Title:** [Profile-compliant implementation title]
**Labels:** [Profile-aware labels]
**Priority:** [priority or Not specified]
**Assignee Hint:** [name and reason or Not specified]

### Objective
[What we are building or changing]

### Scope
- [Included work]
- [Included work]

### Implementation Requirements
- [Requirement]
- [Requirement]

### Acceptance Criteria
- [ ] [Observable completion condition]
- [ ] [Observable completion condition]

### Testing Notes
[How to verify the work]
```

Add optional sections only when relevant: `Background`, `User-Facing Behavior`, `Non-Goals`, `Data/API Changes`, `Dependencies`, `Risks`, `Rollout Notes`, `Open Questions`.

## Handoff Schema

```yaml
draft_type: defect_ticket | implementation_ticket
profile: active-profile-or-neutral
provider: configured-provider-or-unspecified
publisher: configured-publisher-or-null
title: final approved title
description_markdown: final approved Markdown body
labels:
  - label
priority: priority-or-null
project: project-or-null
milestone: milestone-or-null
estimate: estimate-or-null
assignee:
  suggested: name-or-null
  reason: assignee suggestion reason or null
  confidence: high | medium | low | none
open_questions: []
publish_instruction: route_to_provider_orchestrator
```

Use `open_questions: []` when the approved draft has no unresolved questions. If unresolved questions remain, include each question and state that publishing should wait unless the user accepts the ambiguity.

## Implementation Sample

```markdown
**Title:** Add export controls to ticket dump review
**Labels:** Feature
**Priority:** Not specified
**Assignee Hint:** Not specified

### Objective
Add export controls to the ticket dump review workflow so users can generate a portable summary from selected tickets.

### Scope
- Add an export action to the ticket dump review view.
- Support Markdown export for selected tickets and manual tasks.
- Include ticket title, status, activity notes, URL, and stand-up relevance in the export.

### Implementation Requirements
- Reuse the existing selected-ticket parsing logic.
- Generate export content without mutating the source dump.
- Show a clear error when no tickets are selected.

### Acceptance Criteria
- [ ] Users can export selected tickets as Markdown.
- [ ] Exported content includes all selected tickets and manual tasks.
- [ ] Export fails gracefully when there is no selection.

### Testing Notes
Verify with a dump containing provider tickets, manual tasks, and carry-over items.
```

## Defect Sample

```markdown
**Title:** Fix missing carry-over tickets in stand-up selection
**Labels:** Bug
**Priority:** 3
**Assignee Hint:** Not specified

### The Problem
Carry-over tickets from the previous dump are not appearing in the next stand-up selection prompt.

### Steps to Reproduce
1. Create a ticket dump with at least one unselected ticket.
2. Generate a stand-up without selecting that ticket.
3. Run stand-up selection from the next dump in the same week.

### Technical Requirements
- Read `# Unselected Tickets` from the most recent previous dump.
- Merge carry-over tickets into the selectable list.
- Avoid duplicating tickets already present in the current dump.

### Expected vs Actual
- **Expected:** Unselected tickets from the previous dump appear as `[Carry-over]` options.
- **Actual:** Only tickets from the current dump are shown.

### Acceptance Criteria
- [ ] Previous unselected tickets appear in future stand-up prompts.
- [ ] Carry-over tickets are labeled with `[Carry-over]`.
- [ ] Duplicate tickets are not shown twice.
```
