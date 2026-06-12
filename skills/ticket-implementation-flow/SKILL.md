---
name: ticket-implementation-flow
description: Executes ticket or prompt implementation from requirements through codebase analysis, confidence scoring, branch/worktree setup, implementation, commit, and optional ticket notification. Use when workflow-orchestrator routes implementation work, when the user invokes /workflow-orchestrator implement, or when the user invokes /ticket-implementation-flow commit or /ticket-implementation-flow comment.
---

# Ticket Implementation Flow

Run provider-backed or prompt-backed implementation work through explicit confidence gates.

## Entry Points

- Normal: invoked by `$workflow-orchestrator` with normalized ticket/task context and optional provider comment target.
- Direct: `/ticket-implementation-flow commit [ticket]` or `/ticket-implementation-flow comment [ticket]` resumes the named command in `references/commands/`.
- Prompt-only: proceed without a provider target unless the user supplies one later.

## Core Workflow

1. Gather requirements from the ticket, task, or prompt. Preserve provider IDs, URLs, acceptance criteria, status, and user-provided constraints.
2. Inspect the repository before planning. Read real files that establish architecture, conventions, affected modules, tests, and similar implementations.
3. Produce `Analysis With Confidence Level` phase 1 using `references/analysis-confidence.md`; include the prompt asking whether to proceed to phase 2 in the same analysis.
4. Stop until the user explicitly agrees to proceed to phase 2.
5. In phase 2, ask the execution-mode, base-branch, branch override, and worktree questions from `references/analysis-confidence.md`.
6. If brainstorming is required, invoke `$brainstorming` and follow that skill completely. Resume this flow only after its approvals and outputs are available.
7. Create or switch to the approved branch/worktree. Invoke `$using-git-worktrees` only when creating a new worktree.
7.5. If provider context includes a ticket ID: toggle the ticket to an active implementation status and assign it to the current user. The connected user from the provider's MCP session is authoritative for the assignee. Resolve the correct status name from the provider's available statuses; prefer "In Progress" when it exists, otherwise pick the first active (non-todo, non-done) status. Skip the update when the ticket is already in an active implementation status and assigned to you. Report the outcome in the chat thread.
8. Implement the approved plan with minimal, targeted code changes.
9. Verify with the agreed tests or checks. If checks cannot run, report the limitation.
10. Commit only when the chosen execution mode allows it, using `$git-commit`.
11. Notify only when the chosen execution mode reaches notification or the user explicitly invokes the comment command.

## Branch And Worktree Rules

- Classify branch prefix from the analysis: `feat/`, `fix/`, `refactor/`, `release/`, `docs/`, `test/`, `chore/`, `build/`, `ci/`, or `perf/`.
- Default branch name is `[prefix]/[ticket-id]`. The user may override it.
- Ask for the base branch during phase 2.
- Prefer the current worktree when it is clean or low-risk. If meaningful existing changes are present, ask whether to use the current worktree, an existing worktree, or a new worktree.
- For an existing worktree, run `git worktree list` and present options for selection.
- For a new worktree, use `$using-git-worktrees`.
- If this flow created a worktree, do not clean it up unless the user asks after commit and verification.

## Implementation Rules

- Follow the approved implementation plan and any approved brainstorming outputs.
- Do not invoke `$agent-browser` or Playwright unless the user asks or the task cannot be verified reasonably without browser automation.
- Preserve unrelated user-owned changes. Never revert or rewrite work outside the approved scope.
- If new requirements conflict with the approved plan, stop and ask before changing direction.

## Commit Rules

- Use `$git-commit` for all commits.
- `/ticket-implementation-flow commit` commits current flow changes and then follows the notification prompt rule when ticket/provider context exists.
- After a successful `/ticket-implementation-flow commit`, if any ticket/provider context exists, always ask whether to proceed to the ticket comment stage.
- `/ticket-implementation-flow commit [ticket]` commits current changes and treats `[ticket]` as ticket/provider context when no prior flow context exists.
- Do not commit when the selected mode stops at reviewable unstaged or staged changes.

## Notification Rules

- Immediately before creating or updating any ticket implementation notification, freshly read `references/ticket-comment-format.md` and build the ticket comment body from that current file.
- Before publishing, self-check the comment against the freshly read template: first sentence, bold branch line, section headings, notes behavior, required action section, and the ban on developer names, commit hashes, emojis, and verbose implementation logs.
- Comment automatically only after this flow committed changes and the selected mode reaches ticket notification.
- Do not comment when changes are uncommitted unless the comment stage was explicitly invoked.
- `/ticket-implementation-flow comment [ticket]` may be invoked independently; inspect committed branch changes and comment on the resolved ticket.
- Never mention developer names, expose commit hashes, use emojis, or write verbose commentary in ticket comments.

## Supporting References

- `references/analysis-confidence.md` defines phase 1, phase 2, confidence scoring, and execution modes.
- `references/commands/commit.md` defines the commit resume command.
- `references/commands/comment.md` defines the comment resume command.
- `references/ticket-comment-format.md` defines the provider-facing notification format.
