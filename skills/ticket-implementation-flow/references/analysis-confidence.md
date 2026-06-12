# Analysis With Confidence Level

Use this reference for the required two-phase analysis gate.

## Phase 1: Analysis And Confidence

Produce one combined analysis that includes the phase 2 prompt at the end.

```md
## Analysis With Confidence Level

| Area | Details |
| --- | --- |
| Requirements Summary | [Restate the ticket, task, or prompt in implementation terms.] |
| Source Evidence | `[file/path]`: [why it matters]<br>`[file/path]`: [why it matters] |
| Likely Implementation Plan | 1. [Specific step with files when known]<br>2. [Specific step]<br>3. [Specific validation] |
| Confidence Level | Score: [1-5]/5<br>Reason: [Brief reason tied to requirements, code evidence, and risk.] |
| Complexity / Risk | [Low/medium/high complexity and the main risk drivers.] |
| Brainstorming Decision | Required: [Yes/No]<br>Reason: [Why brainstorming is or is not required.] |
| Branch Plan | Prefix: `[prefix]/`<br>Branch: `[prefix]/[ticket-id]`<br>Reason: [Why this prefix matches the work.] |
| Worktree Strategy | Recommended: [current worktree / existing worktree / new worktree]<br>Reason: [Safety rationale based on current repository state.] |
| Proceed | Do you want to proceed to phase 2, where I'll ask how far you want this flow to run and confirm branch/worktree details? |
```

Stop after this output unless the user explicitly agrees to phase 2.

## Confidence Scale

- `1/5`: Do not proceed safely. Core requirements, repository context, or access are missing.
- `2/5`: Proceed only with strong handholding. Ambiguity, broad impact, or unknown architecture dominates.
- `3/5`: Feasible with caveats. Scope is moderate or some assumptions need confirmation.
- `4/5`: Confident. Clear implementation path, known patterns, and manageable risk.
- `5/5`: Very confident. Small, well-scoped, strongly evidenced, and easy to verify.

## Brainstorming Decision

Require `$brainstorming` when any of these are true:

- The work creates features, adds behavior, modifies behavior, or has design tradeoffs.
- The task spans multiple subsystems or 3 or more meaningful files/modules.
- Requirements are ambiguous, UX/product-facing, architecture-impacting, or high-risk.
- The implementation requires choosing between viable approaches.

Skip brainstorming only when the work is a narrow, clearly specified mechanical fix, docs/config-only change, or low-risk maintenance task where no design decision is needed.

## Phase 2: Execution Mode And Setup

Ask the user to choose one execution mode:

1. Proceed with the whole flow without handholding, and notify through the ticket comment once implementation is done.
2. Proceed with branch creation only, then hand off to the developer with implementation steps.
3. Proceed through implementation only, leave reviewable uncommitted changes, then ask whether to commit.
4. Proceed through commit, then notify the user in the chat thread instead of commenting on the ticket.

Then ask for:

- Base branch for the new branch.
- Branch name override, if any.
- Worktree choice when the current worktree is not clearly safe.

Use the answers to select the terminal stage:

- Mode 1 terminal stage: ticket comment after commit.
- Mode 2 terminal stage: branch ready plus handoff steps.
- Mode 3 terminal stage: uncommitted implementation ready for review, then ask whether to commit.
- Mode 4 terminal stage: chat notification after commit, no ticket comment.
