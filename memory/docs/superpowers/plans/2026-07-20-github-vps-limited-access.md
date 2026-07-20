# GitHub VPS Limited Access Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a standalone library guide for narrowly scoped GitHub access from a coding VPS.

**Architecture:** Create one focused infrastructure how-to containing the complete token, GitHub CLI, HTTPS Git, verification, and branch-protection workflow. Add only the minimum infrastructure-index entries needed to make the guide discoverable.

**Tech Stack:** Markdown, GitHub fine-grained personal access tokens, GitHub CLI, Git, POSIX shell

---

### Task 1: Create the standalone access guide

**Files:**
- Create: `memory/docs/library/infrastructure/github-vps-limited-access.md`

- [ ] **Step 1: Add library metadata and purpose**

Use this metadata and title:

```markdown
---
date: 2026-07-20
type: howto
tags: [github, vps, git, authentication, security]
related:
  - memory/docs/library/infrastructure/README.md
  - memory/docs/library/infrastructure/server-provisioning.md
---

# Limited GitHub Access for a Coding VPS
```

Open by explaining that the guide grants repository-scoped HTTPS access without giving the VPS full account or repository-administration privileges.

- [ ] **Step 2: Document fine-grained token creation**

Include the complete GitHub navigation path, token name, 30–90 day expiration, account resource owner, selected-repository access, and the instruction to select only repositories used from the VPS.

List `Contents: Read and write` and `Metadata: Read-only` as required. Mark Pull requests and Issues write access as optional. Keep Administration, Actions, Secrets, Webhooks, Environments, and Deployments at no access. Explain that Workflows write access is conditional on editing `.github/workflows/`.

- [ ] **Step 3: Document protected token storage and GitHub CLI authentication**

Include the exact directory, permission, token-file, profile-loading, and status commands supplied in the approved spec. Explain that the token file must contain only the token and that `GH_TOKEN` is used by GitHub CLI.

- [ ] **Step 4: Document HTTPS Git setup and verification**

Include `gh auth setup-git`, the HTTPS clone URL, the existing-remote replacement command, fetch, test-branch, file, commit, push, and optional `gh pr create --fill` commands. Use `YOUR_USERNAME`, `YOUR_REPOSITORY`, and `~/repository/YOUR_REPOSITORY` consistently.

- [ ] **Step 5: Document destructive boundaries and branch rulesets**

State that repository deletion should fail without Administration write permission. Also state that Contents write access can delete branches and force-push wherever repository rules allow it, and that GitHub has no permission for non-destructive pushes only.

Include the ruleset navigation path and require `Restrict deletions`, `Block force pushes`, and `Require a pull request before merging` for `main`. End with the practical token-plus-ruleset configuration and the warning not to add a normal account SSH key from the VPS.

- [ ] **Step 6: Verify the guide**

Run:

```powershell
rg -n "Contents|Metadata|Pull requests|Issues|Administration|Actions|Secrets|Webhooks|Environments|Deployments|Workflows|GH_TOKEN|setup-git|repo delete|--delete|--force|Restrict deletions|Block force pushes|Require a pull request|SSH key" memory/docs/library/infrastructure/github-vps-limited-access.md
git diff --check -- memory/docs/library/infrastructure/github-vps-limited-access.md
```

Expected: every security term appears and `git diff --check` reports no errors.

### Task 2: Add the guide to the infrastructure index

**Files:**
- Modify: `memory/docs/library/infrastructure/README.md`

- [ ] **Step 1: Add the related-document entry**

Add this frontmatter item without changing existing items:

```yaml
  - memory/docs/library/infrastructure/github-vps-limited-access.md
```

- [ ] **Step 2: Add document-list and quick-routing entries**

Add:

```markdown
- [Limited GitHub access for a coding VPS](github-vps-limited-access.md) — grant selected repositories narrowly scoped HTTPS access while protecting administrative operations and important branches.
```

Add this matching quick route:

```markdown
- Connecting a coding VPS to selected GitHub repositories? Open **Limited GitHub access for a coding VPS**.
```

- [ ] **Step 3: Verify the complete change**

Run:

```powershell
git diff --check
git diff -- memory/docs/library/infrastructure/README.md memory/docs/library/infrastructure/github-vps-limited-access.md
git status --short
```

Expected: the targeted diff contains the new guide and three index additions; pre-existing modified, deleted, and untracked files remain present and unchanged.
