# Commit Command

Use for `/ticket-implementation-flow commit` and `/ticket-implementation-flow commit [ticket]`.

## Steps

1. Inspect `git status`, `git diff`, and staged diff.
2. Identify whether the current conversation has a prior ticket context.
3. If the command includes `[ticket]`, treat that ticket as context for the notification prompt.
4. Use `$git-commit` to stage the intended implementation changes and create the commit.
5. After a successful commit, check whether ticket/provider context exists.
6. If ticket/provider context exists, ask the user whether to proceed to the comment command with the resolved ticket. If the flow has already reached its terminal stage (completed), ask at most once per session — after the user responds, do not ask again for subsequent commits in the same session.
7. If the user agrees, proceed to the comment command.
8. If the user declines, report the commit outcome in chat only.
9. If no ticket/provider context exists, report the commit outcome in chat only.

## Notification Prompt Rule

After `/ticket-implementation-flow commit`, do not silently stop after committing when ticket/provider context exists. Always ask whether to post the implementation comment.

Exception: after the flow reaches its terminal stage (completed), the prompt is shown at most once per session. If the user declines, do not ask again for the remainder of the session. The user may still explicitly invoke `/ticket-implementation-flow comment`.

Ticket/provider context includes a ticket ID, ticket URL, provider issue fetched during the flow, ticket context from a handoff, or a branch/current-task context that clearly maps to a ticket.

Use this prompt:

`Commit created. I have ticket context for [ticket]. Should I post the implementation comment now?`

## Rules

- Do not commit unrelated user-owned changes.
- Do not expose commit hashes in ticket comments.
- If hooks fail, fix the issue and create a new commit attempt through `$git-commit`; do not amend unless explicitly requested.
