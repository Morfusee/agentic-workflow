# Implementation Ticket Drafter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a profile-aware `implementation-ticket-drafter` skill that drafts non-bug implementation tickets and returns provider-agnostic handoff metadata after approval.

**Architecture:** Add one new skill folder with focused skill instructions and an OpenAI agent descriptor. Add a separate memory config file for profile defaults, labels, project metadata, and assignee hints. Keep the new skill draft/review/handoff-only and avoid direct provider publishing.

**Tech Stack:** Markdown skill instructions, YAML agent metadata, JSON memory config, Git, PowerShell, `just` sync commands.

---

## File Structure

- Create `skills/implementation-ticket-drafter/SKILL.md`: Defines triggers, boundaries, memory config behavior, rules, draft/review/handoff workflow, ticket template, handoff metadata, and validation behavior.
- Create `skills/implementation-ticket-drafter/agents/openai.yaml`: Registers the OpenAI-facing skill display name, short description, and default prompt.
- Create `memory/skill-configs/implementation-ticket-drafter.json`: Stores profile defaults separate from `issue-drafter`, including provider preference, title format, labels, priority, project, estimate, and optional assignee hints.
- Use existing `memory/docs/superpowers/specs/2026-06-06-implementation-ticket-drafter-design.md` as the source design reference.
- Do not modify `skills/issue-drafter/SKILL.md` or `memory/skill-configs/issue-drafter.json`.

---

### Task 1: Create The Skill Instructions

**Files:**
- Create: `skills/implementation-ticket-drafter/SKILL.md`
- Reference: `memory/docs/superpowers/specs/2026-06-06-implementation-ticket-drafter-design.md`
- Reference: `skills/issue-drafter/SKILL.md`

- [ ] **Step 1: Confirm the working tree state**

Run:

```powershell
git status --short
git diff
```

Expected: no unrelated changes that need to be edited for this task. If unrelated user-owned changes exist, leave them untouched.

- [ ] **Step 2: Create the skill directory**

Run:

```powershell
Test-Path -LiteralPath "skills"
New-Item -ItemType Directory -Path "skills\implementation-ticket-drafter" -Force
```

Expected: `Test-Path` prints `True`, and the directory exists.

- [ ] **Step 3: Create `SKILL.md` with exact instructions**

Write this full file to `skills/implementation-ticket-drafter/SKILL.md`:

````markdown
---
name: implementation-ticket-drafter
description: Draft profile-aware implementation tickets for features, enhancements, refactors, and other non-bug technical work; use when the user wants to turn implementation ideas into structured tickets with review and provider-agnostic handoff metadata.
---

# Implementation Ticket Drafter - Draft, Review, Handoff

You are a technical implementation ticket writer. Convert feature ideas, enhancements, refactors, and other non-bug implementation requests into clear, actionable tickets. Keep enough product context to explain why the work matters, but structure the ticket so an engineer can implement without guessing.

## Memory

This skill is profile-aware and provider-agnostic. All project-specific configuration lives in `skill-configs/implementation-ticket-drafter.json` under the canonical memory root defined in OpenCode's global AGENTS.md. Load that file at the start of each session.

- `default_profile`: The profile to use when the caller does not specify one.
- `profiles`: Named drafting and handoff profiles.
- `profiles[*].provider`: The preferred destination provider or owning orchestrator context.
- `profiles[*].title_format`: The title convention for drafts.
- `profiles[*].default_labels`: Labels to start with for every draft in the profile.
- `profiles[*].allowed_labels`: Labels available for the profile. Empty means no fixed label list.
- `profiles[*].default_priority`: Optional default priority for handoff metadata.
- `profiles[*].default_project`: Optional default project for handoff metadata.
- `profiles[*].default_estimate`: Optional default estimate for handoff metadata.
- `profiles[*].engineers` and `profiles[*].service_to_engineer`: Optional assignment hints.
- `profiles[*].defaults`: Provider-specific or orchestrator-specific metadata to pass through during handoff.

Use the caller-provided profile when supplied. Otherwise use `default_profile`. Do not mix profile defaults.

If the config file is missing or the active profile cannot be resolved, continue with neutral defaults and state that profile metadata was unavailable.

## Boundaries

- Draft implementation tickets only.
- Do not draft bug reports, regressions, or problem investigations. Recommend `$issue-drafter` when the request is defect-oriented.
- Do not call Linear, ClickUp, Notion, or other provider creation tools.
- Do not publish directly from this skill.
- Return handoff metadata only after the user approves the draft.
- Decompose broad initiatives into smaller candidate tickets before drafting one ticket.

## Rules

- **Implementation Framing**: Use direct implementation language such as `Add`, `Update`, `Create`, `Refactor`, `Integrate`, or `Remove`.
- **No Bug Sections**: Do not use `Steps to Reproduce`, `Expected vs Actual`, or `The Problem` unless redirecting the user to `$issue-drafter`.
- **Title Format**: Follow the active profile's `title_format`. If no format is available, use a concise imperative title.
- **Labels**: Start with `default_labels`. Add only labels supported by `allowed_labels` when that list is non-empty. Do not add duplicate labels.
- **Assignees**: Suggest assignees only when profile evidence supports the suggestion. Never silently assign a person.
- **Unknowns**: Use `Not specified` in Markdown and `null` in handoff metadata for unknown optional values.
- **No Fabrication**: Do not invent requirements, dependencies, risks, estimates, project names, labels, or assignees.
- **Adaptive Depth**: Always include the lean ticket sections. Add deeper sections only when the user's input calls for them.

---

## Three-Phase Workflow

Work through these phases in order. Do not skip phases.

### Phase 1 - Draft

Take the user's input and produce a structured implementation ticket using the active profile.

Ask one focused clarification before drafting when the objective, scope, or acceptance criteria are too unclear to produce an implementation-ready ticket. If missing information can be safely represented as `Not specified`, draft with that fallback instead of blocking.

If the request describes multiple independent deliverables, list the candidate tickets and ask which one to draft first.

Output format:

```markdown
**Title:** [Profile-compliant implementation title]
**Labels:** [Profile-aware labels]
**Priority:** [priority or Not specified]
**Assignee Hint:** [name and reason or Not specified]

### Objective
[What we are building or changing]

### Scope
- [Included work]
- [Included work]

### Implementation Requirements
- [Requirement]
- [Requirement]

### Acceptance Criteria
- [ ] [Observable completion condition]
- [ ] [Observable completion condition]

### Testing Notes
[How to verify the work]
```

Add these sections only when relevant:

```markdown
### Background
### User-Facing Behavior
### Non-Goals
### Data/API Changes
### Dependencies
### Risks
### Rollout Notes
### Open Questions
```

---

### Phase 2 - Review

Present the draft and explicitly ask the user to review it. Say something like:

> Here is the draft implementation ticket. Review it and let me know if you want any changes.

Accept feedback and iterate. The user may:
- Request wording changes
- Add or remove scope
- Change labels, priority, project, estimate, or assignee hints
- Add or remove adaptive sections
- Split the draft into multiple tickets

Revise and re-present until the user is satisfied. Do not hand off, publish, or create provider records during this phase.

---

### Phase 3 - Handoff

This phase triggers only when the user explicitly approves the draft. Trigger phrases include:
- `approved`
- `looks good`
- `handoff`
- `ready to publish`
- `create it through the provider`
- Any clear approval signal

When triggered, return the final Markdown ticket plus normalized handoff metadata. Do not call provider tools.

Handoff format:

```yaml
draft_type: implementation_ticket
profile: active-profile-or-neutral
provider: configured-provider-or-unspecified
title: final approved title
description_markdown: final approved Markdown body
labels:
  - label
priority: priority-or-null
project: project-or-null
milestone: milestone-or-null
estimate: estimate-or-null
assignee:
  suggested: name-or-null
  reason: assignee suggestion reason or null
  confidence: high | medium | low | none
open_questions: []
publish_instruction: route_to_provider_orchestrator
```

Use `open_questions: []` when the approved draft has no unresolved questions. If unresolved questions remain, include each question in the list and make clear that publishing should wait unless the user accepts the ambiguity.
````

- [ ] **Step 4: Verify the skill frontmatter shape**

Run:

```powershell
Get-Content -LiteralPath "skills\implementation-ticket-drafter\SKILL.md" -TotalCount 4
```

Expected output starts with exactly these four lines:

```text
---
name: implementation-ticket-drafter
description: Draft profile-aware implementation tickets for features, enhancements, refactors, and other non-bug technical work; use when the user wants to turn implementation ideas into structured tickets with review and provider-agnostic handoff metadata.
---
```

- [ ] **Step 5: Verify the skill avoids direct publishing instructions**

Run:

```powershell
Select-String -LiteralPath "skills\implementation-ticket-drafter\SKILL.md" -Pattern "linear_save_issue|clickup_create_task|notion-create-pages|publish directly"
```

Expected: only the phrase `Do not publish directly from this skill.` may appear. No provider creation tool names should appear.

- [ ] **Step 6: Commit the skill instructions**

Run:

```powershell
git add -- "skills/implementation-ticket-drafter/SKILL.md"
git commit -m "feat(skills): add implementation ticket drafter"
```

Expected: commit succeeds with only `skills/implementation-ticket-drafter/SKILL.md` staged.

---

### Task 2: Add Agent Metadata

**Files:**
- Create: `skills/implementation-ticket-drafter/agents/openai.yaml`

- [ ] **Step 1: Create the agents directory**

Run:

```powershell
Test-Path -LiteralPath "skills\implementation-ticket-drafter"
New-Item -ItemType Directory -Path "skills\implementation-ticket-drafter\agents" -Force
```

Expected: `Test-Path` prints `True`, and the `agents` directory exists.

- [ ] **Step 2: Create `openai.yaml`**

Write this full file to `skills/implementation-ticket-drafter/agents/openai.yaml`:

```yaml
interface:
  display_name: "Implementation Ticket Drafter"
  short_description: "Draft profile-aware non-bug implementation tickets and return provider-agnostic handoff metadata"
  default_prompt: "Use $implementation-ticket-drafter to turn this feature, enhancement, refactor, or other non-bug implementation request into a structured ticket. Do not publish directly; return handoff metadata only after approval."
```

- [ ] **Step 3: Verify required OpenAI agent fields**

Run:

```powershell
Select-String -LiteralPath "skills\implementation-ticket-drafter\agents\openai.yaml" -Pattern "display_name|short_description|default_prompt|\$implementation-ticket-drafter"
```

Expected: all three interface keys are present, and `default_prompt` references `$implementation-ticket-drafter`.

- [ ] **Step 4: Commit the agent metadata**

Run:

```powershell
git add -- "skills/implementation-ticket-drafter/agents/openai.yaml"
git commit -m "feat(skills): add implementation drafter agent metadata"
```

Expected: commit succeeds with only `skills/implementation-ticket-drafter/agents/openai.yaml` staged.

---

### Task 3: Add The Profile Config

**Files:**
- Create: `memory/skill-configs/implementation-ticket-drafter.json`
- Do not modify: `memory/skill-configs/issue-drafter.json`

- [ ] **Step 1: Check whether the config directory exists**

Run:

```powershell
Test-Path -LiteralPath "memory\skill-configs"
```

Expected: `True`. If it prints `False`, create it with `New-Item -ItemType Directory -Path "memory\skill-configs" -Force` before the next step.

- [ ] **Step 2: Create `implementation-ticket-drafter.json`**

Write this full file to `memory/skill-configs/implementation-ticket-drafter.json`:

```json
{
  "default_profile": "default",
  "profiles": {
    "default": {
      "provider": "unspecified",
      "title_format": "[description]",
      "default_labels": [
        "implementation"
      ],
      "allowed_labels": [],
      "default_priority": null,
      "default_project": null,
      "default_estimate": null,
      "engineers": [],
      "service_to_engineer": {},
      "defaults": {}
    }
  }
}
```

- [ ] **Step 3: Validate JSON parsing**

Run:

```powershell
Get-Content -LiteralPath "memory\skill-configs\implementation-ticket-drafter.json" -Raw | ConvertFrom-Json | Out-Null
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Confirm the issue drafter config was not touched**

Run:

```powershell
git diff -- "memory/skill-configs/issue-drafter.json"
```

Expected: no output.

- [ ] **Step 5: Commit the profile config**

Run:

```powershell
git add -- "memory/skill-configs/implementation-ticket-drafter.json"
git commit -m "feat(memory): add implementation ticket drafter config"
```

Expected: commit succeeds with only `memory/skill-configs/implementation-ticket-drafter.json` staged.

---

### Task 4: Validate The Skill Contract

**Files:**
- Verify: `skills/implementation-ticket-drafter/SKILL.md`
- Verify: `skills/implementation-ticket-drafter/agents/openai.yaml`
- Verify: `memory/skill-configs/implementation-ticket-drafter.json`

- [ ] **Step 1: Confirm all expected files exist**

Run:

```powershell
Test-Path -LiteralPath "skills\implementation-ticket-drafter\SKILL.md"
Test-Path -LiteralPath "skills\implementation-ticket-drafter\agents\openai.yaml"
Test-Path -LiteralPath "memory\skill-configs\implementation-ticket-drafter.json"
```

Expected output:

```text
True
True
True
```

- [ ] **Step 2: Confirm there are no bug-only ticket sections in the new skill**

Run:

```powershell
Select-String -LiteralPath "skills\implementation-ticket-drafter\SKILL.md" -Pattern "Steps to Reproduce|Expected vs Actual|The Problem"
```

Expected: matches appear only in the `No Bug Sections` rule, not in the output format.

- [ ] **Step 3: Confirm the handoff contract is present**

Run:

```powershell
Select-String -LiteralPath "skills\implementation-ticket-drafter\SKILL.md" -Pattern "draft_type: implementation_ticket|publish_instruction: route_to_provider_orchestrator|Do not call Linear"
```

Expected: all three patterns are present.

- [ ] **Step 4: Validate frontmatter contains only allowed keys**

Run:

```powershell
$lines = Get-Content -LiteralPath "skills\implementation-ticket-drafter\SKILL.md" -TotalCount 4
$lines -join "`n"
```

Expected output:

```text
---
name: implementation-ticket-drafter
description: Draft profile-aware implementation tickets for features, enhancements, refactors, and other non-bug technical work; use when the user wants to turn implementation ideas into structured tickets with review and provider-agnostic handoff metadata.
---
```

- [ ] **Step 5: Run skill sync validation path**

Run:

```powershell
just sync-skills
```

Expected: command completes successfully and syncs repo-owned skills to configured skill directories. If `.skills.env` does not enable OpenCode sync, Codex skill sync still completes.

- [ ] **Step 6: Run final diff review**

Run:

```powershell
git status --short
git diff
```

Expected: no unstaged changes. If `just sync-skills` updates generated links outside the repo, do not stage those external changes.

- [ ] **Step 7: Record validation if sync caused a tracked change**

If `git status --short` shows a tracked repo change caused by validation, inspect it:

```powershell
git diff
```

Expected: only intentional validation-related repo changes appear. If the sync command updates a tracked repo file such as a generated manifest or lock file, commit the exact file shown by `git status --short`. For example, if `git status --short` shows `M skills/manifest.json`, commit it with:

```powershell
git add -- "skills/manifest.json"
git commit -m "chore(skills): sync implementation ticket drafter"
```

If there are no tracked repo changes, skip this commit step.

---

## Self-Review

Spec coverage:
- New standalone skill folder is covered by Task 1 and Task 2.
- Separate config file is covered by Task 3.
- Provider-agnostic handoff is covered by Task 1 and Task 4.
- No direct publishing is covered by Task 1 and Task 4.
- Adaptive ticket sections are covered by Task 1.
- Assignee hints are covered by Task 1 and Task 3.
- Validation checks are covered by Task 4.

Placeholder scan:
- The plan contains no incomplete implementation placeholders.
- Template bracket text appears only inside skill output examples where the skill should show a reusable format.

Type and naming consistency:
- The skill name is consistently `implementation-ticket-drafter`.
- The config path is consistently `memory/skill-configs/implementation-ticket-drafter.json`.
- The handoff `draft_type` is consistently `implementation_ticket`.
