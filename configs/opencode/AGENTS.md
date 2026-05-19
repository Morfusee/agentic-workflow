# Global OpenCode Rules

## Core Principle

These rules apply across all repositories, even when a repository has its own AGENTS.md.

Preserve user-owned work.

## Canonical Memory Root

All memory-backed workflows must resolve under `${HOME}/Documents/Programming/agentic-workflow/memory`.

Treat that path as authoritative for OpenCode memory reads and writes.

Do not introduce alternate memory roots in downstream skills; they must follow this rule.

The current working tree, current git diff, and previous changes made in the session must be treated as intentional user-owned work unless the user explicitly asks to remove, revert, replace, or refactor them.

## Change Preservation

When the user asks for a follow-up change, implement it on top of the current implementation.

Do not remove, undo, simplify away, rename, or rewrite previous changes unless explicitly requested.

Never interpret a new request as permission to reset the solution.

If the new request conflicts with existing changes, stop and explain the conflict instead of silently deleting prior work.

## Patch Discipline

Use minimal, surgical diffs.

Only edit files and code paths required by the current request.

Do not rewrite entire components, functions, files, or modules when a smaller patch is sufficient.

Avoid formatting-only churn outside the touched area.

Do not perform opportunistic cleanup unless explicitly requested.

## Required Workflow Before Editing

Before making code changes:

1. Run `git status`.
2. Run `git diff`.
3. Identify existing modified files and existing user-owned changes.
4. Preserve those changes while implementing the new request.

## Required Workflow Before Finishing

Before responding as complete:

1. Run `git diff`.
2. Confirm the requested change was added.
3. Confirm previous user-owned changes are still present.
4. Confirm no unrelated files or code paths were changed.
5. Summarize only the intentional changes.

## Default Behavior

Prefer additive changes over replacements.

Prefer editing the smallest necessary block.

Ask only if the requested change would require removing or materially changing previous work.
