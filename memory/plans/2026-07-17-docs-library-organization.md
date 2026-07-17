# Documentation Library Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `memory/docs/` into a topic-first curated library while leaving all agent-generated material under `memory/docs/superpowers/` untouched.

**Architecture:** Keep `memory/docs/` as the boundary between curated documents and agent working artifacts. Move the six user-facing documents into `library/infrastructure/` and `library/developer-tools/`, then add small intent-based indexes at the root, library, and topic levels. Preserve every moved document byte-for-byte.

**Tech Stack:** Markdown, Git, PowerShell verification

---

## File Map

**Create:**

- `memory/docs/README.md` — distinguishes the curated library from agent working artifacts.
- `memory/docs/library/README.md` — serves as the main user-facing documentation index.
- `memory/docs/library/infrastructure/README.md` — describes infrastructure documents and when to use them.
- `memory/docs/library/developer-tools/README.md` — describes Git and editor workflow documents.

**Relocate without content changes:**

- `memory/docs/infrastructure/current-services.md` → `memory/docs/library/infrastructure/current-services.md`
- `memory/docs/infrastructure/dokploy-service-deployment.md` → `memory/docs/library/infrastructure/dokploy-service-deployment.md`
- `memory/docs/infrastructure/server-provisioning.md` → `memory/docs/library/infrastructure/server-provisioning.md`
- `memory/docs/proxmox-opnsense-network-design.md` → `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md`
- `memory/docs/git-worktree-guide.md` → `memory/docs/library/developer-tools/git-worktree-guide.md`
- `memory/docs/lazygit-lazyvim-cheatsheet.md` → `memory/docs/library/developer-tools/lazygit-lazyvim-cheatsheet.md`

**Protected:**

- `memory/docs/superpowers/**` — do not modify, move, rename, or index.

### Task 1: Build the infrastructure section

**Files:**

- Create: `memory/docs/library/infrastructure/README.md`
- Relocate: the four infrastructure documents listed in the file map

- [ ] **Step 1: Relocate the infrastructure documents with `apply_patch`**

Move each file to its exact destination without changing its Markdown content. Do not alter headings, frontmatter, whitespace, or references inside the files.

- [ ] **Step 2: Create the infrastructure index**

Create `memory/docs/library/infrastructure/README.md` with exactly this content:

```markdown
# Infrastructure

Documentation for servers, networking, deployments, and currently running services.

## Choose a document

- [Current services](current-services.md) — inventory the services and containers that exist before migration or maintenance work.
- [Server provisioning](server-provisioning.md) — follow the standard flow for preparing a new server.
- [Dokploy service deployment](dokploy-service-deployment.md) — deploy and expose an application through Dokploy, Traefik, and Cloudflare.
- [Proxmox and OPNsense network design](proxmox-opnsense-network-design.md) — build the private VM network, firewall, NAT, DHCP, DNS, and public forwarding architecture.

## Quick routing

- Need to understand what is already running? Open **Current services**.
- Preparing a new machine? Open **Server provisioning**.
- Shipping an application? Open **Dokploy service deployment**.
- Configuring Proxmox networking or OPNsense? Open **Proxmox and OPNsense network design**.
```

- [ ] **Step 3: Verify infrastructure document integrity**

Run:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath `
  'memory\docs\library\infrastructure\current-services.md', `
  'memory\docs\library\infrastructure\dokploy-service-deployment.md', `
  'memory\docs\library\infrastructure\server-provisioning.md', `
  'memory\docs\library\infrastructure\proxmox-opnsense-network-design.md' |
  Select-Object Path,Hash
```

Expected hashes:

```text
current-services.md                    DC818ADBF75B2BF7165A1E1551569D17BB029F44550151DA63176C6ED6832752
dokploy-service-deployment.md          CF11ECA91B864DE68C95CE2E47F4E24558B80A7723605AB5950F910F61F6AEC0
server-provisioning.md                 5FD93CE910A443568872679374DFB4F5054C0CA9B8A6FF276ACB9005F27F46D6
proxmox-opnsense-network-design.md     937C29698BB0F706AA15CF6834E9EB2469ADE2D3D9C67778D738D731B487554F
```

- [ ] **Step 4: Commit the infrastructure section**

```powershell
git add -- 'memory/docs/infrastructure' 'memory/docs/proxmox-opnsense-network-design.md' 'memory/docs/library/infrastructure'
git commit -m "docs: organize infrastructure library"
```

### Task 2: Build the developer-tools section

**Files:**

- Create: `memory/docs/library/developer-tools/README.md`
- Relocate: the two developer-tool documents listed in the file map

- [ ] **Step 1: Relocate both developer-tool documents with `apply_patch`**

Move each file to its exact destination without changing its Markdown content.

- [ ] **Step 2: Create the developer-tools index**

Create `memory/docs/library/developer-tools/README.md` with exactly this content:

```markdown
# Developer Tools

Practical references for Git worktrees, LazyGit, LazyVim, and recovery workflows.

## Choose a document

- [Git worktree guide](git-worktree-guide.md) — understand worktree behavior, branch setup, remote tracking, and a safe repeatable workflow.
- [LazyGit and LazyVim cheatsheet](lazygit-lazyvim-cheatsheet.md) — quickly find editor shortcuts, staging and rebasing actions, worktree commands, and recovery steps.

## Quick routing

- Need to create, switch, or repair a worktree? Open **Git worktree guide**.
- Need a keyboard shortcut or Git recovery command? Open **LazyGit and LazyVim cheatsheet**.
```

- [ ] **Step 3: Verify developer-tool document integrity**

Run:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath `
  'memory\docs\library\developer-tools\git-worktree-guide.md', `
  'memory\docs\library\developer-tools\lazygit-lazyvim-cheatsheet.md' |
  Select-Object Path,Hash
```

Expected hashes:

```text
git-worktree-guide.md             A809471F9B4B61F39B77F2C97E005C88C84945041CB4CF526AB8867CAB4ED430
lazygit-lazyvim-cheatsheet.md     7EE8FCEDA73A5A422EBA28768784A18C1D7368209DDBCE750D1223C5B1607FAD
```

- [ ] **Step 4: Commit the developer-tools section**

```powershell
git add -- 'memory/docs/git-worktree-guide.md' 'memory/docs/lazygit-lazyvim-cheatsheet.md' 'memory/docs/library/developer-tools'
git commit -m "docs: organize developer tools library"
```

### Task 3: Add the documentation entry points

**Files:**

- Create: `memory/docs/README.md`
- Create: `memory/docs/library/README.md`

- [ ] **Step 1: Create the root directory map**

Create `memory/docs/README.md` with exactly this content:

```markdown
# Documentation

Use this directory as the entry point for long-lived documentation and agent working artifacts.

## Where to go

- [Documentation library](library/) — curated guides and references organized by topic. Start here when you need to learn or perform a task.
- `superpowers/` — agent-generated design specifications and implementation plans. Treat these as working history rather than the primary documentation library.
```

- [ ] **Step 2: Create the curated library index**

Create `memory/docs/library/README.md` with exactly this content:

```markdown
# Documentation Library

Choose the area that best matches what you are trying to do.

## Browse by topic

### [Infrastructure](infrastructure/)

Use for server provisioning, current-service inventories, Dokploy deployments, Proxmox, OPNsense, networking, firewalling, and DNS.

### [Developer tools](developer-tools/)

Use for Git worktrees, LazyGit, LazyVim, branch workflows, and recovery commands.
```

- [ ] **Step 3: Verify every navigation link**

Run:

```powershell
$missingLinks = @()
Get-ChildItem -LiteralPath 'memory\docs' -Recurse -File -Filter 'README.md' | ForEach-Object {
  $readme = $_
  [regex]::Matches((Get-Content -LiteralPath $readme.FullName -Raw), '\]\(([^)#]+)\)') | ForEach-Object {
    $target = $_.Groups[1].Value
    if ($target -notmatch '^[a-z]+://' -and -not (Test-Path -LiteralPath (Join-Path $readme.DirectoryName $target))) {
      $missingLinks += "$($readme.FullName) -> $target"
    }
  }
}
if ($missingLinks.Count -gt 0) { $missingLinks; exit 1 }
'All README links resolve.'
```

Expected:

```text
All README links resolve.
```

- [ ] **Step 4: Commit the entry points**

```powershell
git add -- 'memory/docs/README.md' 'memory/docs/library/README.md'
git commit -m "docs: add documentation library navigation"
```

### Task 4: Verify the completed organization

**Files:**

- Verify: `memory/docs/**`
- Protect: `memory/docs/superpowers/**`

- [ ] **Step 1: Confirm the final curated tree**

Run:

```powershell
Get-ChildItem -LiteralPath 'memory\docs' -Recurse -File |
  Where-Object { $_.FullName -notlike '*\superpowers\*' } |
  ForEach-Object { $_.FullName.Replace((Resolve-Path '.').Path + '\', '') }
```

Expected files:

```text
memory\docs\README.md
memory\docs\library\README.md
memory\docs\library\developer-tools\README.md
memory\docs\library\developer-tools\git-worktree-guide.md
memory\docs\library\developer-tools\lazygit-lazyvim-cheatsheet.md
memory\docs\library\infrastructure\README.md
memory\docs\library\infrastructure\current-services.md
memory\docs\library\infrastructure\dokploy-service-deployment.md
memory\docs\library\infrastructure\proxmox-opnsense-network-design.md
memory\docs\library\infrastructure\server-provisioning.md
```

- [ ] **Step 2: Confirm old loose locations are gone**

Run:

```powershell
$oldPaths = @(
  'memory\docs\infrastructure\current-services.md',
  'memory\docs\infrastructure\dokploy-service-deployment.md',
  'memory\docs\infrastructure\server-provisioning.md',
  'memory\docs\proxmox-opnsense-network-design.md',
  'memory\docs\git-worktree-guide.md',
  'memory\docs\lazygit-lazyvim-cheatsheet.md'
)
$remaining = $oldPaths | Where-Object { Test-Path -LiteralPath $_ }
if ($remaining) { $remaining; exit 1 }
'No old document locations remain.'
```

Expected:

```text
No old document locations remain.
```

- [ ] **Step 3: Confirm `superpowers/` is untouched**

Run:

```powershell
git status --short -- 'memory/docs/superpowers'
git diff --exit-code -- 'memory/docs/superpowers'
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Check the final diff and repository state**

Run:

```powershell
git diff --check
git status --short --untracked-files=all
```

Expected: no whitespace errors. Only intentional documentation-library changes may appear before their corresponding commits; after all three commits, the working tree should be clean.
