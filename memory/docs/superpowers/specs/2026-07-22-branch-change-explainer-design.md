# Branch Change Explainer Skill Design

## Goal

Create a model-invoked `branch-change-explainer` skill that produces an exhaustive, evidence-backed explanation of committed changes on the current branch. Its committed scope is the direct merge base with `origin/main` through `HEAD`; working-tree and staged changes are inspected separately and never folded into that report.

## Invocation

Use the skill when a user asks to explain, document, compare, or write an exhaustive report for the current branch, its commits, or its PR changes. Keep it model-invoked so natural requests such as “explain this branch” can reach it without requiring the user to remember the skill name.

## Execution contract

1. Confirm the current directory is a Git repository and `origin/main` resolves. Do not silently choose a different base.
2. Compute the committed comparison range:

   ```bash
   BASE=$(git merge-base HEAD origin/main)
   ```

3. Inspect the committed range with:

   ```bash
   git diff --stat "$BASE" HEAD
   git diff "$BASE" HEAD
   git log --reverse --format=fuller "$BASE"..HEAD
   ```

4. Inspect uncommitted state independently with:

   ```bash
   git diff
   git diff --cached
   git status --short
   ```

5. Read affected files, relevant callers, tests, schemas, configuration, and infrastructure definitions as needed to explain behavior.
6. Separate observed facts from inferences, assumptions, and unresolved unknowns. Cite commits, files, symbols, and commands where useful.

PowerShell users may use the shell-equivalent `$BASE = git merge-base HEAD origin/main` and pass `$BASE` to the same Git commands.

## Output contract

Always emit these headings in this order:

1. Executive overview
2. Branch and base information
3. Commit-by-commit narrative
4. Changes grouped by feature or subsystem
5. Detailed file-by-file explanation
6. Data-flow and request-flow changes
7. Database or schema changes
8. API contract changes
9. UI and user-visible behavior changes
10. Configuration and infrastructure changes
11. Removed or replaced behavior
12. Tests added or changed
13. Compatibility and migration concerns
14. Risks, assumptions, and unresolved work
15. Before-versus-after architecture
16. Suggested PR description

Use “None identified” when a section has no evidence. Do not infer a change merely because a category is listed. Explicitly state that working-tree and staged changes are excluded from the committed branch report, and summarize them separately when present.

## Approach rejected

Do not add a helper script or separate report-template file. Native Git commands are sufficient, and a single focused `SKILL.md` keeps the behavior visible and easy to maintain.

## Validation

- Confirm the skill folder contains the required `SKILL.md` and valid frontmatter with only `name` and `description`.
- Confirm the name is lowercase, hyphenated, and under 64 characters.
- Search the completed skill for every required output heading and both committed/uncommitted command groups.
- Run the repository’s available skill validation command if present.
- Re-check `git diff` and `git status` before finishing; preserve unrelated user-owned changes.
