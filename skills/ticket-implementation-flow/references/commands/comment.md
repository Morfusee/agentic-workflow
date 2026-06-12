# Comment Command

Use for `/ticket-implementation-flow comment [ticket]` or when the main flow reaches ticket notification.

## Steps

1. Resolve the ticket/task target from prior context or the command argument.
2. Inspect the current branch name.
3. Inspect committed branch changes against the selected base branch or upstream branch.
4. Summarize what changed in 2-4 concise bullets.
5. Include notes only when there are relevant limitations, validation gaps, or follow-up context.
6. Include required actions such as review, QA, deployment, or verification.
7. Publish with the provider tool selected by `$workflow-orchestrator` or return the comment body when no provider tool is available.

## Rules

- Do not comment if implementation changes are only uncommitted, unless the user explicitly invoked this command.
- After the flow has reached its terminal stage (completed), do not auto-trigger this command; only run when explicitly invoked via `/ticket-implementation-flow comment`.
- Do not mention developer names.
- Do not include commit hashes.
- Do not use emojis.
- Keep the comment brief.
