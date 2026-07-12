---
name: git-commit
description: Execute git commits with Conventional Commits, intelligent staging, and safe push-failure triage. Use when the user asks to commit changes, create a git commit, mentions "/commit", or requires the commit workflow to push and diagnose GitHub permission or account errors.
---

# Git Commit with Conventional Commits

## Overview

When this skill is invoked, **always commit the current changes**. Never stop at analysis or a draft — execute `git commit`. Ask the user if anything is unclear (type, scope, staging), but the end goal is always a commit.

Create standardized, semantic git commits using the Conventional Commits specification. Analyze the actual diff to determine appropriate type, scope, and message.

Only push when the user or the calling workflow explicitly requests a push. If a requested push fails, follow the permission and account recovery workflow below before reporting failure.

## Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

## Breaking Changes

```
# Exclamation mark after type/scope
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## Workflow

### 1. Analyze Diff

```bash
# If files are staged, use staged diff
git diff --staged

# If nothing staged, use working tree diff
git diff

# Also check status
git status --porcelain
```

### 2. Stage Files (if needed)

If nothing is staged or you want to group changes differently:

```bash
# Stage specific files
git add path/to/file1 path/to/file2

# Stage by pattern
git add *.test.*
git add src/components/*

# Interactive staging
git add -p
```

**Never commit secrets** (.env, credentials.json, private keys).

### 3. Generate Commit Message

Analyze the diff to determine:

- **Type**: What kind of change is this?
- **Scope**: What area/module is affected?
- **Description**: One-line summary of what changed (present tense, imperative mood, <72 chars)

### 4. Execute Commit

```bash
# Single line
git commit -m "<type>[scope]: <description>"

# Multi-line with body/footer
git commit -m "$(cat <<'EOF'
<type>[scope]: <description>

<optional body>

<optional footer>
EOF
)"
```

### 5. Recover from a Requested Push Failure

Capture the complete `git push` error, then perform this self-check before changing authentication:

1. Is this an authentication or authorization failure? Treat `403`, `permission denied`, `write access ... not granted`, `authentication failed`, `could not read Username`, `repository not found` for an expected private repository, and SSH `publickey` errors as possible auth failures. Treat non-fast-forward/rejected updates, branch-policy or hook failures, DNS/network/TLS failures, and missing refs as different problems; do not switch accounts for them.
2. Is the remote hosted on GitHub or a GitHub Enterprise host? Inspect it with `git remote get-url <remote>`.
3. If it is a GitHub auth failure, check whether `gh` is available with `gh --version`. If so, inspect accounts with `gh auth status --hostname <host>`; never use `--show-token` or `gh auth token`.
4. Does the same host have another already-authenticated account that is plausibly authorized for this repository? Switch only when there is one clear candidate. If candidates are ambiguous, ask the user which account to use.

For a clear candidate account:

```bash
gh auth switch --hostname <host> --user <user>
```

If the remote uses HTTPS, make Git use the selected GitHub CLI credentials:

```bash
gh auth setup-git --hostname <host>
```

Verify the selected identity with `gh api user --hostname <host>`, then retry the same push once. Do not assume `gh auth switch` changes an SSH key; for SSH remotes, report that the GitHub CLI account and SSH identity are separate and ask the user to select or configure the correct key.

Do not run `gh auth login`, request tokens, or switch to an ambiguous account without user approval. Never print, copy, or include authentication tokens in output. If no suitable authenticated account exists, or the retry fails, stop and report the remote, active account if safely available, exact non-secret error, and the required user action (authenticate, grant repository access, configure SSH, or choose another account). Do not loop through accounts or retry indefinitely.

## Best Practices

- One logical change per commit
- Present tense: "add" not "added"
- Imperative mood: "fix bug" not "fixes bug"
- Reference issues: `Closes #123`, `Refs #456`
- Keep description under 72 characters

## Git Safety Protocol

- NEVER update unrelated git config; the only permitted config change is `gh auth setup-git --hostname <host>` during the HTTPS GitHub recovery path above
- NEVER run destructive commands (--force, hard reset) without explicit request
- NEVER skip hooks (--no-verify) unless user asks
- NEVER force push to main/master
- NEVER push unless the user or calling workflow explicitly requests it
- NEVER switch GitHub accounts blindly; inspect the remote and `gh auth status` first
- If commit fails due to hooks, fix and create NEW commit (don't amend)
