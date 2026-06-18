---
name: review-orchestrator
description: Coordinates implementation reviews across focused reviewer skills and aggregates results into tracker-ready checks. Use when reviewing completed implementation work against requirements, acceptance criteria, code quality standards, current branch changes, diffs, or provider-backed tickets/tasks.
---

# Review Orchestrator

Coordinate post-implementation review without owning any single review specialty.

## Entry Points

- Standalone: invoked directly to review current branch changes, a diff, or a provider-backed ticket/task implementation.

## Core Workflow

1. Gather review context: requirements, acceptance criteria, provider IDs/URLs, changed files, current diff or committed range, implementation notes, and verification output.
2. Load `references/reviewer-contract.md` and `references/reviewer-selection.md`.
3. Select reviewers:
   - Always run `$requirements-reviewer`.
   - Run `$react-quality-review` only when React/TypeScript project evidence is present or the caller explicitly requests it.
4. Use `$skill-orchestrator-go` to run selected reviewers in parallel when more than one reviewer is selected.
5. Give each reviewer read-only scope and require the reviewer contract output.
6. Review every reviewer result for evidence, scope compliance, and contract compliance before accepting it.
7. Aggregate accepted `checks` into one result set. Preserve reviewer names in check descriptions or notes when useful.
8. Determine aggregate status:
   - `PASS` when all accepted checks pass.
   - `FAIL` when any accepted check fails.
   - `PARTIAL` when checks are mixed or at least one check is partial.
   - `BLOCKED` when all accepted checks are blocked or review cannot proceed.
9. Report results only. Do not block commits, change provider status, or modify code unless the user explicitly asks.
10. When a provider review comment is requested, pass the aggregated `checks`, `overall_status`, review scope, notes, and provider context to `$ticket-review-comment-drafter`.

## Rules

- Do not treat automated tests as a substitute for requirements review.
- Do not publish provider comments unless the user or invoking flow explicitly requested review-comment publication.
- Do not invoke frontend UI review skills unless the user asks or the selected reviewer rules require them.
- Keep review separate from implementation notification. `$ticket-review-comment-drafter` owns review comments; implementation-update comments belong to the implementation workflow that produced the changes.
- If reviewers disagree, report the conflict and prefer the result with stronger file-level evidence.

## Supporting References

- `references/reviewer-contract.md` defines input and output contracts for reviewer skills.
- `references/reviewer-selection.md` defines reviewer auto-detection rules.
