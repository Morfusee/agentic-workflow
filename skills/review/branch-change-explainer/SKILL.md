---
name: branch-change-explainer
description: Explain the committed changes on the current Git branch in an exhaustive, evidence-backed report. Use when the user asks to explain a branch, compare a branch with main, document PR changes, or produce a detailed branch-change overview.
---

# Branch Change Explainer

Produce a complete explanation of committed changes on the current branch. Keep the committed report strictly scoped to the direct merge base with `origin/main` through `HEAD`; inspect uncommitted and staged changes separately and never mix them into that scope.

## 1. Establish the scope

Run these checks from the repository root:

```bash
git status --short
git branch --show-current
git rev-parse --verify origin/main
git rev-parse HEAD
```

If `origin/main` cannot be resolved, stop and ask the user to provide or fetch the intended base. Do not silently substitute another ref.

Compute the merge base and use it for every committed-change command:

```bash
BASE=$(git merge-base HEAD origin/main)
```

On PowerShell, use `$BASE = git merge-base HEAD origin/main` and pass `$BASE` to the commands below.

## 2. Collect committed and uncommitted evidence separately

Run the committed-range commands exactly as follows:

```bash
git diff --stat "$BASE" HEAD
git diff "$BASE" HEAD
git log --reverse --format=fuller "$BASE"..HEAD
```

Use `git diff --name-status "$BASE" HEAD` when you need a compact inventory of added, modified, deleted, renamed, or copied files. Inspect individual commits with `git show --stat --format=fuller <commit>` or `git show <commit> -- <path>` when the chronological narrative needs more detail.

Then inspect the working tree independently:

```bash
git diff
git diff --cached
git status --short
```

Treat these working-tree and staged results as excluded from the committed branch report. State their presence and summarize them separately under the branch/base scope note. Do not attribute them to a commit or describe them as part of the branch architecture.

## 3. Trace the actual change

Read the affected files and follow relevant callers, callees, tests, schemas, configuration, and infrastructure definitions. Use the diff as the index, not as a substitute for reading the surrounding implementation.

For each claim:

- Tie it to a commit, file, symbol, command output, or observed behavior when possible.
- Distinguish facts from inferences.
- Record assumptions and unresolved questions instead of inventing intent.
- Account for renames, deletions, generated files, migrations, feature flags, and behavior replaced rather than merely added.
- Report tests that exist and tests actually run separately; do not imply validation that was not observed.
- If a requested category has no evidence, write `None identified` and briefly state what was checked.

## 4. Write the report

Emit every heading below in this order. Keep the report detailed but concrete; use tables for compact mappings and file inventories where helpful.

## Executive overview

Summarize the purpose, main behavioral result, major subsystems touched, and the most important caveat. Keep this section understandable without reading the rest of the report.

## Branch and base information

Record the current branch, `HEAD`, `origin/main`, merge-base SHA, commit count, comparison range, and whether the working tree or index has excluded changes. Make the committed-versus-uncommitted boundary explicit.

## Commit-by-commit narrative

Use the chronological `git log --reverse` output. For every commit in the range, explain its intent as evidenced by the patch, the files changed, how it depends on preceding commits, and any notable behavioral or structural effect.

## Changes grouped by feature or subsystem

Group related files and commits by actual feature, domain, or subsystem. Explain the problem or responsibility addressed, the implementation shape, and cross-cutting effects. Do not group only by directory if the behavior crosses directories.

## Detailed file-by-file explanation

Account for every path in the committed diff. For each file, state whether it was added, modified, deleted, renamed, or generated; explain the relevant symbols or sections; and connect it to the behavior or subsystem it affects.

## Data-flow and request-flow changes

Describe the before-and-after path for inputs, requests, events, state, persistence, responses, and errors when applicable. Include changed boundaries, transformations, validation, ordering, retries, caching, and authorization only when supported by the code.

## Database or schema changes

Cover migrations, tables, columns, indexes, constraints, ORM models, serialization schemas, seed data, backfills, and rollback behavior. If none are present, say so explicitly.

## API contract changes

Cover public and internal endpoints, methods, parameters, request/response shapes, status codes, events, CLI interfaces, and compatibility behavior. Distinguish implementation changes from externally observable contract changes.

## UI and user-visible behavior changes

Describe changed screens, components, interactions, loading and error states, accessibility behavior, copy, styling, and user workflows only when the committed code supports those claims. Include affected user roles or routes when identifiable.

## Configuration and infrastructure changes

Cover environment variables, config files, build tooling, dependencies, deployment manifests, CI, observability, permissions, and runtime assumptions. Note defaults and operational consequences.

## Removed or replaced behavior

List deleted code and behavior, renamed or replaced paths, removed fallbacks, changed defaults, and no-longer-supported flows. Explain what now handles the responsibility.

## Tests added or changed

List changed test files and the behaviors they cover. Report fixtures, mocks, snapshots, migrations, or test configuration changes. Separate static evidence of tests from commands actually executed and their results.

## Compatibility and migration concerns

Identify breaking changes, versioning, rollout order, data migration or backfill requirements, feature-flag sequencing, mixed-version behavior, rollback limits, and consumer impact. Do not label a change breaking without evidence.

## Risks, assumptions, and unresolved work

List concrete risks and assumptions linked to the diff or missing evidence. Include unresolved TODOs, unverified paths, incomplete migrations, missing tests, and external dependencies. Avoid generic risk boilerplate.

## Before-versus-after architecture

Give a compact comparison of the relevant architecture before and after the range: components, ownership, boundaries, data/request paths, and integration points. Use a small diagram only when it materially clarifies relationships.

## Suggested PR description

Write a copy-pasteable PR title and body derived only from the committed range. Include the problem, implementation, user or system impact, tests, migration notes, and known risks. Do not invent issue links, test results, or motivation.
