---
name: implementation-prep
description: Prepare a development ticket for implementation — classify work type, generate branch names, resolve worktree setup, decide whether brainstorming is needed, and produce an implementation plan summary for user approval before any code is written. Invoke only when explicitly called by another skill (e.g., notion-orchestrator) or when the user issues the slash command `/implementation-prep`. Do not auto-trigger from general "I want to implement this" requests.
---

# Implementation Prep

## Overview

Prepare a development ticket for implementation. Analyze the ticket, classify the work type, generate a branch name, resolve worktree preferences, and decide whether the task warrants the brainstorming skill before producing an implementation plan summary. Do not write code, create branches, or modify worktrees until the user explicitly approves the plan.

**Announce at start:** "I'm using the implementation-prep skill to prepare this ticket for implementation."

## Boundaries

- Analyze and prepare tickets only. Do not implement code.
- Do not create branches, modify worktrees, or write files until the user confirms.
- Do not publish tickets to providers, draft new tickets, or hand off to other workflows.
- If the ticket is clearly a bug report, investigation, or defect, recommend `$ticket-drafter` for drafting or `$ticket-codebase-investigator` for codebase investigation instead.

## Integration With Other Skills

- **brainstorming** — invoked when the ticket is large, ambiguous, architecture-impacting, cross-cutting, or risky.
- **using-git-worktrees** — invoked after approval to set up the isolated workspace.
- **writing-plans** — invoked after brainstorming produces an approved design spec.
- **git-commit** — invoked for creating the implementation branch.

---

## Workflow

Work through these phases in order. Do not skip phases.

### Phase 1 — Ticket Intake

Read and analyze the provided ticket. Extract the following:

1. **Ticket ID** — the unique identifier (e.g., `CU-123`, `LIN-456`, `PROJ-789`). Look for explicit IDs first. If none is present, infer one from the ticket title using a short kebab-case slug (e.g., `add-dark-mode`).
2. **Work summary** — a 1-2 sentence restatement of what the ticket asks for.
3. **Scope indicators** — files, modules, systems, or user flows mentioned.

If the ticket is too vague to classify, ask one focused clarification question before continuing.

### Phase 2 — Work Type Classification

Classify the work into exactly one type using these criteria:

| Type | Prefix | When to Use |
|------|--------|-------------|
| Fix | `fix/` | Bug fixes, regressions, broken behavior, error resolution, incorrect output |
| Feature | `feat/` | New functionality, new UI, new API behavior, new user-facing capability |
| Refactor | `refactor/` | Restructuring, cleanup, simplification, internal improvement without behavior change |

**Decision rules:**
- If the ticket describes something that is currently broken or not working as intended → `fix/`
- If the ticket adds something that doesn't currently exist → `feat/`
- If the ticket improves existing code without changing what it does → `refactor/`
- When in doubt, ask the user to confirm.

### Phase 3 — Branch Name Generation

Generate a branch name using this format:

```
[type]/[ticket-id]-[short-kebab-case-summary]
```

**Rules:**
- `type` is one of `fix`, `feat`, `refactor`
- `ticket-id` is the extracted or inferred ID in its original case
- `summary` is 2-5 words in kebab-case describing the core change

**Examples:**
- `feat/CU-123-add-navbar-mega-menu`
- `fix/LIN-456-resolve-login-timeout`
- `refactor/PROJ-789-simplify-auth-middleware`

If the ticket has no explicit ID, use the inferred slug as both the ID and summary:
- `feat/add-dark-mode`

### Phase 4 — Worktree Decision

Ask the user: "Do you want to use a Git worktree for this work?"

If the user says **no**, skip to Phase 5 and note: "Working in the current branch."

If the user says **yes**, ask: "Use an existing worktree or create a new one?"

- **Existing:** Note the existing worktree path. Skip creation.
- **New:** Propose a safe worktree name and path based on the branch name.

Worktree path conventions follow the `using-git-worktrees` skill:
- Default location: `.worktrees/<branch-name>` at the project root
- Verify the directory is gitignored or add it before creation

Do not create the worktree now. Note the recommendation and proceed.

### Phase 5 — Planning Decision

Decide whether the task requires the `brainstorming` skill.

**Route to brainstorming when ANY of these are true:**
- The ticket is large, ambiguous, or spans 3+ files/modules
- The change is architecture-impacting or cross-cutting
- The implementation requires tradeoff analysis
- The expected change could affect existing behavior in non-obvious ways
- The ticket lacks enough detail and needs clarification through dialogue
- The work involves new patterns, new libraries, or unfamiliar territory
- Risk of the change is medium or high

**Skip brainstorming (use mini plan) when ALL of these are true:**
- The ticket is small, well-defined, and scoped to 1-2 files
- The implementation path is obvious and low-risk
- No architectural decisions or tradeoffs are required
- The ticket has clear acceptance criteria

If brainstorming is required, stop here and present the routing decision. After brainstorming completes, resume at Phase 6.

If skipping brainstorming, proceed to Phase 6 with a mini plan.

### Phase 6 — Implementation Plan Summary

Produce a structured summary using this exact format:

```markdown
## Ticket Analysis
- **Ticket ID:** [extracted or inferred ID]
- **Work type:** [fix / feat / refactor]
- **Reasoning:** [1 sentence explaining the classification]
- **Proposed branch:** `[type]/[ticket-id]-[summary]`

## Worktree Setup
- **Use worktree:** [yes / no]
- **Existing or new:** [existing / new / n/a]
- **Suggested worktree path:** [path or n/a]

## Planning Decision
- **Brainstorming required:** [yes / no]
- **Reason:** [1 sentence]

## Implementation Plan
1. [Step 1 — specific, actionable, with file paths where known]
2. [Step 2]
3. [Step 3]

## Risks / Assumptions
- [Risk or assumption 1]
- [Risk or assumption 2 — use "None" if truly none]

## Confidence Level
- **[Low / Medium / High]**
- **Reason:** [1 sentence]

## Approval
Do you want me to proceed with this implementation?
```

### Phase 7 — Approval Gate

Present the summary and wait for explicit user approval.

**Approval signals:** "proceed", "yes", "approved", "looks good", "go ahead", "implement", "do it", "confirmed", "let's go"

**Do not proceed on:** "maybe", "let me think", silence, or any ambiguous response.

When the user approves:
1. Use `$using-git-worktrees` to set up the worktree (if requested).
2. Create the branch with the proposed name.
3. If brainstorming was flagged, invoke `$brainstorming` next.
4. Otherwise, begin implementation following the plan.

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Ticket missing ID | Infer kebab-case slug from title |
| Unclear fix vs. feat | Ask user to confirm |
| Ticket too vague | Ask one clarifying question, then classify |
| Multiple independent deliverables | List candidate tickets, ask which to prepare first |
| User declines worktree | Skip to Phase 5, work in current branch |
| User wants existing worktree | Note path, do not create |
| Brainstorming needed | Route to brainstorming, resume after design is approved |
| Quick low-risk task | Skip brainstorming, use mini plan |
| User approves | Set up worktree → create branch → begin implementation |

## Red Flags

**Never:**
- Create a branch before user approval
- Create or modify a worktree before user approval
- Write code before user approval
- Skip the approval gate
- Overengineer the workflow for small tickets
- Route to brainstorming for trivial, well-defined changes

**Always:**
- Extract or infer the ticket ID
- Justify the work type classification
- Propose a branch name following the convention
- Ask about worktree preference
- Decide on brainstorming vs. mini plan
- Present the full summary for approval
- Wait for explicit approval before acting

## Anti-Patterns

- **Classifying everything as `feat/`** — read the ticket carefully. Bug reports and cleanup tasks are common.
- **Generating branch names before understanding the ticket** — the summary must reflect the actual work.
- **Assuming worktree preference** — always ask. Some users work in-place.
- **Routing every ticket to brainstorming** — simple, well-defined changes don't need full design sessions.
- **Skipping the approval gate** — never assume consent. Present and wait.
- **Over-summarizing** — the implementation plan must have specific, actionable steps, not vague directions.
