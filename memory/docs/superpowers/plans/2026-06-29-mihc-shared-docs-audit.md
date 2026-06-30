# MIHC Shared Docs Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the MIHC monorepo's shared docs audit trail while preserving its existing Next.js conventions and application code.

**Architecture:** Keep durable documentation at the monorepo root under `docs/`. The project-specific `nextjs/AGENTS.md` will reference that shared location with explicit `../docs/` paths; `nextjs/code-style.md` remains untouched.

**Tech Stack:** Markdown, PowerShell, Git

---

## File Structure

- Create directory: `$HOME/Documents/Programming/mihc/docs/brainstorm/` — shared location for durable brainstorm records.
- Create directory: `$HOME/Documents/Programming/mihc/docs/plans/` — shared location for execution plans.
- Modify: `$HOME/Documents/Programming/mihc/nextjs/AGENTS.md` — add the shared docs source and audit-trail instructions while preserving all current content.
- Preserve unchanged: `$HOME/Documents/Programming/mihc/nextjs/code-style.md` — retain its existing root and `src/` layout guidance exactly.

### Task 1: Protect Existing Repository Work

**Files:**
- Inspect: `$HOME/Documents/Programming/mihc/nextjs/AGENTS.md`
- Preserve: `$HOME/Documents/Programming/mihc/nextjs/code-style.md`

- [ ] **Step 1: Record the pre-change worktree state**

Run from `$HOME/Documents/Programming/mihc`:

```powershell
git status --short
git diff --
```

Expected: existing changes, if any, are identified and treated as user-owned work.

- [ ] **Step 2: Confirm the intended directories and files**

```powershell
Test-Path -LiteralPath .\docs
Test-Path -LiteralPath .\docs\brainstorm
Test-Path -LiteralPath .\docs\plans
Test-Path -LiteralPath .\nextjs\docs
```

Expected before implementation: root `docs/` is `True`; the two requested subdirectories and `nextjs/docs/` are `False` unless the user created them after this plan was written.

### Task 2: Create the Shared Empty Directories

**Files:**
- Create directory: `$HOME/Documents/Programming/mihc/docs/brainstorm/`
- Create directory: `$HOME/Documents/Programming/mihc/docs/plans/`

- [ ] **Step 1: Create only the requested root directories**

```powershell
New-Item -ItemType Directory -Force -Path .\docs\brainstorm, .\docs\plans
```

Expected: both directories exist; no placeholder files and no `nextjs/docs/` directory are created.

- [ ] **Step 2: Verify directory placement**

```powershell
[pscustomobject]@{
  Brainstorm = Test-Path -LiteralPath .\docs\brainstorm -PathType Container
  Plans = Test-Path -LiteralPath .\docs\plans -PathType Container
  NextjsDocs = Test-Path -LiteralPath .\nextjs\docs -PathType Container
} | Format-List
```

Expected: `Brainstorm` and `Plans` are `True`; `NextjsDocs` is `False`.

### Task 3: Add the Shared Docs Audit Directive

**Files:**
- Modify: `$HOME/Documents/Programming/mihc/nextjs/AGENTS.md`

- [ ] **Step 1: Add the shared docs source of truth**

Under `## Source of Truth`, add this list item without changing the existing entries:

```md
- `../docs/` (shared project references, brainstorms, plans, agreements, and durable working notes)
```

- [ ] **Step 2: Add one audit-trail section before `## Repository Context`**

Use this exact content, preserving the existing Next.js 16 warning and all other rules:

```md
## Docs Audit Trail

Agents must treat `../docs/` as the repository source of truth for shared project references, brainstorms, plans, agreements, and other durable working notes.

Agents must check relevant files under `../docs/` before planning or implementing changes.

Brainstorms must be saved under `../docs/brainstorm/`. Capture the full useful conversation trail, including context, options considered, decisions, rejected paths, and open questions. Do not rely on chat history as the only audit trail.

Plans must be saved under `../docs/plans/`. Each plan must distill the concrete implementation path from the related brainstorm or agreement, including scope, steps, validation, risks, and unresolved questions.

If the user and agent reach a concrete agreement, the agent must ask whether to write it as a Markdown file under `../docs/`. When the agreement is a brainstorm, use `../docs/brainstorm/`; when it is an execution plan, use `../docs/plans/`; otherwise use the most relevant `../docs/` subfolder.

This repository-local directive overrides any global or parent `AGENTS.md` instruction that would place brainstorms, plans, or durable project notes outside this repository.

---
```

### Task 4: Verify the Surgical Change

**Files:**
- Verify: `$HOME/Documents/Programming/mihc/nextjs/AGENTS.md`
- Verify unchanged: `$HOME/Documents/Programming/mihc/nextjs/code-style.md`

- [ ] **Step 1: Verify directive count and preserved warning**

```powershell
$agents = Get-Content -LiteralPath .\nextjs\AGENTS.md -Raw
if ([regex]::Matches($agents, '(?m)^## Docs Audit Trail\r?$').Count -ne 1) { throw 'Expected exactly one docs audit directive.' }
if ($agents -notmatch 'This is NOT the Next.js you know') { throw 'Next.js 16 warning was not preserved.' }
if ($agents -notmatch '\.\./docs/brainstorm/' -or $agents -notmatch '\.\./docs/plans/') { throw 'Shared docs paths are missing.' }
```

Expected: command exits successfully with no output.

- [ ] **Step 2: Verify the tracked diff**

```powershell
git diff -- .\nextjs\AGENTS.md .\nextjs\code-style.md
git status --short
```

Expected: the diff shows only the intentional additions to `nextjs/AGENTS.md`; `nextjs/code-style.md` and application files are absent. Empty directories do not appear in Git status.

- [ ] **Step 3: Confirm all requested filesystem state**

```powershell
if (-not (Test-Path -LiteralPath .\docs\brainstorm -PathType Container)) { throw 'Missing docs/brainstorm.' }
if (-not (Test-Path -LiteralPath .\docs\plans -PathType Container)) { throw 'Missing docs/plans.' }
if (Test-Path -LiteralPath .\nextjs\docs) { throw 'nextjs/docs must not exist.' }
```

Expected: command exits successfully with no output.
