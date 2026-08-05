# Markdown2Share recursive collection authorization handoff

## Next-session objective

Implement the approved recursive collection authorization prerequisite in
`$HOME/Documents/Programming/markdown2share`. Follow the repository execution
plan task by task, verify it, and do not implement MCP application code.

## Authoritative artifacts

- Tracker-ready requirements and acceptance criteria:
  `$HOME/Documents/Programming/markdown2share/docs/plans/2026-08-04-recursive-collection-authorization-ticket.md`
- Approved execution plan:
  `$HOME/Documents/Programming/markdown2share/docs/plans/2026-08-04-recursive-collection-authorization-implementation-plan.md`
- Repository guidance:
  `$HOME/Documents/Programming/markdown2share/AGENTS.md`

Do not reconstruct or reinterpret the detailed authorization contract from
this handoff. Read the two approved artifacts completely and treat them as the
source of truth.

## Key approved decision

The nearest explicit collection assignment wins, including when it has a
lower rank than a farther ancestor assignment. Direct target roles retain
precedence over inherited roles.

## Scope boundary

- Implement recursive authorization for human roles and Shared collection
  discovery/navigation.
- Establish the canonical resolver future delegated-user MCP authorization
  must reuse.
- Keep MDP-30 and delegated-user MCP authorization blocked until the recursive
  implementation and tests pass.
- Do not implement MCP clients, tokens, scopes, routes, endpoints, move UI, or
  unrelated application behavior.

## Working-tree preservation

At handoff time, the repository already contains user-owned changes in:

- `nextjs/components/blocks/data-table/data-table-query-state.ts`
- `nextjs/features/documents/repositories/document-members.repository.ts`
- `nextjs/features/permissions/repositories/permissions.repository.ts`
- `nextjs/lib/trpc/server.tsx`
- `.githooks/`
- `nextjs/app/published/[documentId]/loading.tsx`

The permission repository overlaps the implementation plan. Inspect its
existing diff before editing and preserve those removals while layering the
recursive resolver on top. Do not reset, revert, or stage unrelated work.

The ticket and plan are also currently untracked repository files and must be
preserved.

## Suggested skills

- `executing-plans` for sequential implementation with review checkpoints.
- `subagent-driven-development` only if the user explicitly wants parallel
  agent execution.
- `requesting-code-review` after implementation and focused verification.
- `react-doctor` only if React files are changed; the approved plan should not
  require UI component changes.

## Completion evidence

Follow the commands and exit criteria in the implementation plan. Before the
final response, run `git diff`, confirm the pre-existing changes remain, and
report only the intentional recursive-authorization changes and verification
results.
