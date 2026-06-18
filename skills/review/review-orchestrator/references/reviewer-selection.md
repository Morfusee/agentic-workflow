# Reviewer Selection

Use these rules to choose reviewers for `$review-orchestrator`.

## Default Reviewers

Always run:

- `$requirements-reviewer` for functional coverage against requirements and acceptance criteria.

## React/TypeScript Quality Reviewer

Run `$react-quality-review` when any of these are true:

- Changed files include `.tsx` or `.jsx` files.
- `package.json` includes React, Next.js, Remix, Vite React, or similar React dependencies.
- The repository has React-oriented standards such as `CODE_STANDARDS.md` that mention React, hooks, JSX, accessibility, or component patterns.
- The caller explicitly requests code quality review for React/TypeScript work.

Do not run `$react-quality-review` for backend-only, docs-only, config-only, or non-React changes unless explicitly requested.

## Caller Overrides

Respect explicit reviewer requests from the user or invoking flow.

If a requested reviewer is unavailable, report it as a blocked review dimension instead of substituting another reviewer silently.
