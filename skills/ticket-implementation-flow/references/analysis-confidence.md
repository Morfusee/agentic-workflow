# Analysis With Confidence Level

Use this reference for the required two-phase analysis gate.

## Phase 1: Analysis And Confidence

Produce one combined analysis. Keep the analysis concise, evidence-based, and implementation-oriented. The output must end with the Phase 2 gate prompt, but the assistant must stop there unless the user explicitly agrees to continue.

```md
## Analysis With Confidence Level

| Area | Details |
| --- | --- |
| **Requirements Summary** | **Goal:** [Restate the ticket, task, or prompt in implementation terms.]<br><br>**Expected outcome:** [Describe the concrete repo change or deliverable.]<br><br>**Non-goals / boundaries:** [Mention anything that should not be changed, if known.] |
| **Source Evidence** | **Relevant files / references:**<br>`[file/path]` — [Why this file matters.]<br>`[file/path]` — [Why this file matters.]<br><br>**Observed pattern:** [Summarize the existing convention, architecture, or implementation pattern found.] |
| **Likely Implementation Plan** | **Planned steps:**<br>1. [Specific step with files when known.]<br>2. [Specific step with expected code/docs change.]<br>3. [Specific validation or test.]<br><br>**Expected files touched:**<br>- `[file/path]` — [Expected change.]<br>- `[file/path]` — [Expected change.] |
| **Confidence Level** | **Score:** [1-5]/5<br><br>**Reason:** [Brief reason tied to requirements, code evidence, known patterns, and remaining uncertainty.]<br><br>**Confidence drivers:**<br>- **Positive:** [What makes this safe or straightforward.]<br>- **Risk:** [What could reduce confidence.] |
| **Complexity / Risk** | **Complexity:** [Low / Medium / High]<br><br>**Main risk drivers:**<br>- [Risk driver 1.]<br>- [Risk driver 2.]<br><br>**Mitigation:** [How the plan reduces risk.] |
| **Brainstorming Decision** | **Required:** [Yes / No]<br><br>**Reason:** [Why brainstorming is or is not required.]<br><br>**Trigger matched:** [Feature/design tradeoff, multi-subsystem work, ambiguous requirements, architecture impact, or low-risk docs/config-only task.] |
| **Branch Plan** | **Prefix:** `[prefix]/`<br>**Branch:** `[prefix]/[ticket-id-or-short-slug]`<br><br>**Reason:** [Why this prefix matches the work: `feat`, `fix`, `refactor`, `docs`, `chore`, etc.] |
| **Worktree Strategy** | **Recommended:** [current worktree / existing worktree / new worktree]<br><br>**Reason:** [Safety rationale based on current repository state, pending changes, branch risk, or parallel work.] |
```

After the table, output this paragraph exactly:

```md
**Proceed:** Do you want to proceed to Phase 2, where I’ll ask how far you want this flow to run and confirm branch/worktree details?
```

Stop after this output unless the user explicitly agrees to Phase 2.

## Confidence Scale

* `1/5`: Do not proceed safely. Core requirements, repository context, or access are missing.
* `2/5`: Proceed only with strong handholding. Ambiguity, broad impact, or unknown architecture dominates.
* `3/5`: Feasible with caveats. Scope is moderate or some assumptions need confirmation.
* `4/5`: Confident. Clear implementation path, known patterns, and manageable risk.
* `5/5`: Very confident. Small, well-scoped, strongly evidenced, and easy to verify.

## Brainstorming Decision

Require `$brainstorming` when any of these are true:

* The work creates features, adds behavior, modifies behavior, or has design tradeoffs.
* The task spans multiple subsystems or 3 or more meaningful files/modules.
* Requirements are ambiguous, UX/product-facing, architecture-impacting, or high-risk.
* The implementation requires choosing between viable approaches.

Skip brainstorming only when the work is a narrow, clearly specified mechanical fix, docs/config-only change, or low-risk maintenance task where no design decision is needed.

## Phase 2: Execution Mode And Setup

Ask the user to choose one execution mode:

1. Proceed with the whole flow without handholding, and notify through the ticket comment once implementation is done.
2. Proceed with branch creation only, then hand off to the developer with implementation steps.
3. Proceed through implementation only, leave reviewable uncommitted changes, then ask whether to commit.
4. Proceed through commit, then notify the user in the chat thread instead of commenting on the ticket.

Then ask for:

* Base branch for the new branch.
* Branch name override, if any.
* Worktree choice when the current worktree is not clearly safe.

Use the answers to select the terminal stage:

* Mode 1 terminal stage: ticket comment after commit.
* Mode 2 terminal stage: branch ready plus handoff steps.
* Mode 3 terminal stage: uncommitted implementation ready for review, then ask whether to commit.
* Mode 4 terminal stage: chat notification after commit, no ticket comment.
