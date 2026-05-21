---
date: 2026-05-21
type: research
tags: [git, worktree, dev-workflow, ai-agents]
related: []
---

# Git Worktree Session Notes

## Goal

Create a separate Git worktree for AI-agent work so the main repo stays clean while the agent can work in an isolated folder/branch.

## Key Concepts

A Git worktree is a separate working folder connected to the same Git repository.

Each worktree can only have **one branch checked out at a time**, but it still has access to the repository's local and remote branches.

Example structure:

```txt
C:/Users/mrqvp/Documents/Programming/website
  → main workspace, usually on main

C:/Users/mrqvp/Documents/Programming/website-agent
  → AI-agent workspace, usually on an agent/task branch
```

## LazyGit Worktree Options

When LazyGit shows:

```txt
Create worktree from ref
Create worktree from ref (detached)
Cancel
```

Use:

```txt
Create worktree from ref
```

for normal coding work.

Avoid:

```txt
Create worktree from ref (detached)
```

unless only inspecting/testing a specific commit or branch without intending to commit normally.

## Recommended AI Worktree Setup

Create a new worktree based from `main` or `origin/main`.

Recommended base ref:

```txt
origin/main
```

Recommended worktree path:

```txt
C:/Users/mrqvp/Documents/Programming/website-agent
```

Recommended branch naming:

```txt
agent/workspace
```

or task-specific:

```txt
agent/llms-txt-cms
```

Equivalent command:

```bash
git worktree add ../website-agent -b agent/workspace origin/main
```

## Fetch All Branches

Before creating worktrees or selecting remote branches, fetch everything:

```bash
git fetch --all --prune
```

Then inspect all branches:

```bash
git branch -a
```

## Important Worktree Rule

The same local branch cannot normally be checked out in multiple worktrees at the same time.

Example:

```txt
website/        → main
website-agent/  → main
```

This will usually be blocked.

Instead, create a new branch from `main`:

```bash
git worktree add ../website-agent -b agent/workspace main
```

## Switching Branches Inside a Worktree

A worktree can switch between branches, but only if the target branch is not already checked out in another worktree.

Example:

```bash
git switch feat/some-branch
```

If the branch is already active elsewhere, Git will reject it.

## Push Error Encountered

Error:

```txt
fatal: The upstream branch of your current branch does not match
the name of your current branch.
```

Cause:

The local branch was tracking a different upstream branch, likely `origin/main`, instead of a remote branch with the same name.

Example mismatch:

```txt
local:  feat/CU-86d32pnat-cms-managed-content-served-at-llmstxt
remote: origin/main
```

## Fix Current Branch

Run:

```bash
git push -u origin HEAD
```

This pushes the current branch to `origin` using the same branch name and sets the upstream correctly.

After that, normal push should work:

```bash
git push
```

## Permanent Git Config Recommendation

Configure Git globally so future pushes behave correctly for feature/worktree branches:

```bash
git config --global push.default current
git config --global push.autoSetupRemote true
```

Verify:

```bash
git config --global push.default
git config --global push.autoSetupRemote
```

Expected:

```txt
current
true
```

## Avoid This Unless Intentional

Do not use:

```bash
git push origin HEAD:main
```

unless intentionally pushing the current branch directly to remote `main`.

That command means:

```txt
Push my current branch's commits into origin/main.
```

This is risky for feature branches or AI-agent branches.

## Practical Workflow

1. Stay on `main` in the original repo.
2. Fetch all branches:

```bash
git fetch --all --prune
```

3. Create a worktree from `origin/main`.
4. Give the worktree a new branch name like:

```txt
agent/workspace
```

5. Open the worktree folder in the AI agent/editor.
6. Let the agent work there.
7. Push with:

```bash
git push
```

or first-time push:

```bash
git push -u origin HEAD
```

## Recommended Mental Model

```txt
Branch = timeline of commits
Worktree = physical folder showing one branch
```

For AI-agent work, prefer:

```bash
git worktree add ../repo-agent-task -b agent/task-name origin/main
```
