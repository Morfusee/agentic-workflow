# Workflow Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Linear, ClickUp, and Notion orchestrator skills with one `workflow-orchestrator` skill that routes `/skill [provider] [prompt]` workflows.

**Architecture:** Keep `SKILL.md` as a thin provider parser and safety contract. Move shared ticket workflow behavior into one common reference and provider-specific behavior into provider references, with Notion domain templates preserved as separate references.

**Tech Stack:** Markdown skills, YAML agent metadata, PowerShell validation, Git.

---

### Task 1: Create the Unified Skill Shell

**Files:**
- Create: `skills/workflow-orchestrator/SKILL.md`
- Create: `skills/workflow-orchestrator/agents/openai.yaml`

- [ ] **Step 1: Create `SKILL.md` with frontmatter and entrypoint rules**

Write frontmatter with only `name` and `description`. Add concise instructions for provider parsing, low-confidence clarification, reference loading, execution order, and safety.

- [ ] **Step 2: Create `agents/openai.yaml`**

Add quoted display metadata and a default prompt that explicitly references `$workflow-orchestrator`.

### Task 2: Migrate Shared Ticket Workflow Rules

**Files:**
- Create: `skills/workflow-orchestrator/references/common-ticket-workflows.md`

- [ ] **Step 1: Extract common ticket rules**

Add shared instructions for dump creation, stand-up generation, full-flow ranges, ticket drafting, review comments, weekly slideshow routing, publishing approval, no-fabrication rules, and outcome reporting.

### Task 3: Migrate Provider References

**Files:**
- Create: `skills/workflow-orchestrator/references/providers/linear.md`
- Create: `skills/workflow-orchestrator/references/providers/clickup.md`
- Create: `skills/workflow-orchestrator/references/providers/notion.md`

- [ ] **Step 1: Migrate Linear**

Move Linear branches, retrieval steps, normalization fields, carry-over stand-up behavior, weekly slideshow support, and Linear-specific rules into `linear.md`.

- [ ] **Step 2: Migrate ClickUp**

Move ClickUp branches, retrieval steps, normalization fields, carry-over stand-up behavior, ticket format convention, and ClickUp-specific rules into `clickup.md`.

- [ ] **Step 3: Migrate Notion**

Move Notion routing, config contract, location/domain resolution, implementation-prep handoff, draft-first writes, write safety, and chat summary contract into `notion.md`.

### Task 4: Move Notion Domain Templates

**Files:**
- Create: `skills/workflow-orchestrator/references/notion/personal-tasks-template.md`
- Create: `skills/workflow-orchestrator/references/notion/coding-projects-template.md`

- [ ] **Step 1: Copy the existing templates**

Move Personal Tasks and Coding Projects template content under the new skill.

- [ ] **Step 2: Update template-local references**

Change references from `skill-configs/notion-orchestrator.json` to `memory/skill-configs/notion-orchestrator.json` and from "Notion Orchestrator" to "Workflow Orchestrator" where doing so does not imply a config rename.

### Task 5: Remove Old Orchestrator Skills

**Files:**
- Delete: `skills/linear-orchestrator/`
- Delete: `skills/clickup-orchestrator/`
- Delete: `skills/notion-orchestrator/`

- [ ] **Step 1: Delete migrated skill folders**

Remove the old provider-specific orchestrator folders after the new references exist.

### Task 6: Validate and Commit

**Files:**
- Validate: `skills/workflow-orchestrator/**`
- Validate: `skills/linear-orchestrator/`
- Validate: `skills/clickup-orchestrator/`
- Validate: `skills/notion-orchestrator/`

- [ ] **Step 1: Run structural checks**

Run:

```powershell
Test-Path .\skills\workflow-orchestrator\SKILL.md
Test-Path .\skills\workflow-orchestrator\agents\openai.yaml
Test-Path .\skills\workflow-orchestrator\references\common-ticket-workflows.md
Test-Path .\skills\workflow-orchestrator\references\providers\linear.md
Test-Path .\skills\workflow-orchestrator\references\providers\clickup.md
Test-Path .\skills\workflow-orchestrator\references\providers\notion.md
Test-Path .\skills\workflow-orchestrator\references\notion\personal-tasks-template.md
Test-Path .\skills\workflow-orchestrator\references\notion\coding-projects-template.md
Test-Path .\skills\linear-orchestrator
Test-Path .\skills\clickup-orchestrator
Test-Path .\skills\notion-orchestrator
```

Expected: new files return `True`; old folders return `False`.

- [ ] **Step 2: Check old self-references**

Run:

```powershell
rg '\$linear-orchestrator|\$clickup-orchestrator|\$notion-orchestrator' .\skills\workflow-orchestrator
```

Expected: no matches.

- [ ] **Step 3: Check git diff**

Run:

```powershell
git diff --stat
git status --short
```

Expected: only the new workflow orchestrator, removed old orchestrators, and this implementation plan are changed.

- [ ] **Step 4: Commit**

Run:

```powershell
git add .\skills\workflow-orchestrator .\skills\linear-orchestrator .\skills\clickup-orchestrator .\skills\notion-orchestrator .\memory\docs\superpowers\plans\2026-06-12-workflow-orchestrator.md
git commit -m "feat(skills): add workflow orchestrator"
```
