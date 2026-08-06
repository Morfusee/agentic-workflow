---
name: review-orchestrator
description: Coordinates implementation reviews across focused reviewer skills and aggregates results into tracker-ready checks. Use when reviewing completed implementation work against requirements, acceptance criteria, code quality standards, current branch changes, diffs, or provider-backed tickets/tasks.
---

# Review Orchestrator

Coordinate post-implementation review without owning any single review specialty.

## Entry Points

- Standalone: invoked directly to review current branch changes, a diff, or a provider-backed ticket/task implementation.

## Core Workflow

1. Gather review context: requirements, acceptance criteria, provider IDs/URLs, changed files, current diff or committed range, implementation notes, and verification output. Scope the diff to only the target branch changes (e.g., `git diff main...HEAD` or the equivalent base-branch comparison) to minimize token usage.
2. Load `references/reviewer-contract.md` and `references/reviewer-selection.md`.
3. Select reviewers:
   - Always run `$requirements-reviewer` and `$thermos`.
   - Run `$react-quality-review` only when React/TypeScript project evidence is present or the caller explicitly requests it.
4. Run all selected reviewers in parallel: spawn every selected reviewer as its own subagent via the task tool (`explore` type), all in one batch. Do not wait between spawns and do not run reviewers sequentially, regardless of how many are selected.
   - Do not pin a model or variant on reviewer subagents. Unpinned subagents inherit the main agent's current model and reasoning effort (variant) automatically; pinning would break that inheritance.
   - State the main agent's current model and reasoning effort in every reviewer prompt. Reviewers must confirm their effective model and effort in their result. Re-run any reviewer whose result reports a different model or effort before accepting its output.
5. Give each reviewer read-only scope and require the reviewer contract output.
6. Review every reviewer result for evidence, scope compliance, and contract compliance before accepting it.
7. Aggregate accepted `checks` into one result set. Preserve reviewer names in check descriptions or notes when useful.
8. Determine aggregate status:
   - `PASS` when all accepted checks pass.
   - `FAIL` when any accepted check fails.
   - `PARTIAL` when checks are mixed or at least one check is partial.
   - `BLOCKED` when all accepted checks are blocked or review cannot proceed.
9. Write the aggregated review to `$HOME/Documents/Programming/agentic-workflow/memory/reviews/YYYY-MM-DD-<brief-descriptor>-review.md`. Use today's date and a short kebab-case descriptor of the review subject. The file must contain `overall_status`, every `check` with `status`/`expected`/`actual`, review scope, reviewer names, and notes.
10. Report results only. Do not block commits, change provider status, or modify code unless the user explicitly asks.
11. When a provider review comment is requested, pass the aggregated `checks`, `overall_status`, review scope, notes, and provider context to `$ticket-review-comment-drafter`.

## Rules

- Remember and apply every instruction, requirement, and acceptance criterion throughout the review. Do not drop or skip any check item during aggregation.
- Do not treat automated tests as a substitute for requirements review.
- Do not publish provider comments unless the user or invoking flow explicitly requested review-comment publication.
- Do not invoke frontend UI review skills unless the user asks or the selected reviewer rules require them.
- Keep review separate from implementation notification. `$ticket-review-comment-drafter` owns review comments; implementation-update comments belong to the implementation workflow that produced the changes.
- Limit every review to only the changes on the target branch. Never review the entire repository or files not touched by the branch diff. Use the smallest possible diff (e.g., `git diff <base>...HEAD`) and pass only the changed files and their relevant context to reviewers. This minimizes token usage across all reviewer subagents.
- If reviewers disagree, report the conflict and prefer the result with stronger file-level evidence.
- Never pin reviewer subagents to a fixed model or variant. They must inherit the main agent's current model and reasoning effort so every reviewer runs with the same quality bar as the main agent.

## Supporting References

- `references/reviewer-contract.md` defines input and output contracts for reviewer skills.
- `references/reviewer-selection.md` defines reviewer auto-detection rules.
