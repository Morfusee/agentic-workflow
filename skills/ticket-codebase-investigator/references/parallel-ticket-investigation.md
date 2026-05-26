# Parallel Ticket Investigation

Use this reference for multi-ticket codebase investigations.

## When To Fan Out

Fan out when there are 3 or more independent tickets and each ticket needs codebase reading, root-cause analysis, or effort estimation.

Keep the main agent responsible for source-system fetches, final judgment, and output collation. Subagents should be read-only investigators.

## Agent Layout

- Codebase survey agent: summarize stack, routing, module boundaries, scripts, tests, and common implementation patterns.
- Per-ticket agents: investigate one ticket each with the full ticket text and relevant repository path.

## Per-Ticket Prompt Template

```text
Investigate the codebase at <repo_path> for this ticket.

Ticket:
<full ticket text, URL, status, source-system fields>

Return:
1. Relevant existing patterns and exact files read.
2. Root causes or implementation gaps, with file paths and line references when possible.
3. Concrete implementation steps using existing conventions.
4. Files to create or edit.
5. Validation plan.
6. Effort estimate and risk.

Stay read-only. Do not modify code or tickets.
```

## Collation Template

```markdown
# <Board or Project> - Ticket Investigation

Source: <tracker and filter>
Repository: <repo path>
Checked: <date>

## Ranked Summary

| Rank | Ticket | Effort | Risk | Why |
|---|---|---|---|---|

## <ticket id> - <title>

Status: <status>
URL: <url>
Estimate: <time>
Risk: <low/medium/high>

### Findings
Evidence-backed findings.

### Implementation Plan
Exact changes and files.

### Validation
Commands, manual checks, or acceptance checks.

### Open Questions
Only unresolved items that affect implementation.
```
