# Commit Command

Use for `/ticket-implementation-flow commit` and `/ticket-implementation-flow commit [ticket]`.

## Steps

1. Inspect `git status`, `git diff`, and staged diff.
2. Identify whether the current conversation has a prior ticket context.
3. If the command includes `[ticket]`, carry that ticket into the notification stage.
4. Use `$git-commit` to stage the intended implementation changes and create the commit.
5. If the active flow selected ticket notification, proceed to the comment command with the resolved ticket.
6. If no notification target exists, report the commit outcome in chat only.

## Rules

- Do not commit unrelated user-owned changes.
- Do not expose commit hashes in ticket comments.
- If hooks fail, fix the issue and create a new commit attempt through `$git-commit`; do not amend unless explicitly requested.
