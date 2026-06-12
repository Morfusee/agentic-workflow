# Skill Index

Use this as the routing map before loading a skill. Prefer the narrowest skill that matches the user's request.

## Primary Entrypoints

| Need | Use | Notes |
| --- | --- | --- |
| Work with Linear tickets, dumps, stand-ups, review comments, or Linear ticket drafts | `workflow-orchestrator` | Use `/skill linear [prompt]`; routes to Linear provider workflows and ticket helper skills. |
| Work with ClickUp tasks, dumps, stand-ups, review comments, or ClickUp ticket drafts | `workflow-orchestrator` | Use `/skill clickup [prompt]`; routes to ClickUp provider workflows and ticket helper skills. |
| Create or update Notion pages, tasks, or Coding Projects Tracker items | `workflow-orchestrator` | Use `/skill notion [prompt]`; handles Notion schema, domains, and placement. |
| Improve a frontend interface or product UI | `impeccable` | UI/UX critique, redesign, polish, and frontend visual quality. |
| Refactor existing code without behavior changes | `refactor` | Surgical maintainability improvements. |
| Commit current changes | `git-commit` | Conventional commit staging and message workflow. |
| Hand off current context to another agent | `handoff` | Conversation and work-state compaction. |

## Ticket And Work Planning

| Need | Use | Notes |
| --- | --- | --- |
| Draft a bug, regression, production issue, feature, enhancement, refactor, or implementation ticket | `ticket-drafter` | Classifies the request as defect or implementation, then returns reviewed handoff metadata. |
| Investigate tracker tickets against a codebase | `ticket-codebase-investigator` | Returns root causes, file evidence, and effort estimates. |
| Create a PRD and split it into ticket phases | `ticket-prd-planner` | Requirements gathering through phased ticket plans. |
| Draft code review, implementation review, or QA results as a tracker comment | `ticket-review-comment-drafter` | Review and QA comments only; not for new ticket creation. |

## Implementation Flow

| Stage | Use | Purpose |
| --- | --- | --- |
| Clarify ambiguous or creative work before implementation | `brainstorming` | Turn fuzzy ideas into an approved design/spec. |
| Turn an approved spec into an implementation plan | `writing-plans` | Produce task-by-task engineering instructions before coding. |
| Prepare an approved Notion Coding Projects ticket for implementation | `implementation-prep` | Usually routed by `workflow-orchestrator`; classifies work, branch/worktree strategy, and brainstorming need. |
| Create an isolated worktree for feature work | `using-git-worktrees` | Keep implementation work separate from the current workspace. |
| Stress-test a plan through questioning | `grill-me` | Use for adversarial plan/design review, often inside PRD work. |

## Reporting And Presentations

| Need | Use | Notes |
| --- | --- | --- |
| Create normalized ticket dump files from provider facts | `ticket-dump-creator` | Usually called by `workflow-orchestrator` after Linear or ClickUp facts are collected. |
| Generate a spoken stand-up script from selected work items | `standup-generator` | Source-agnostic stand-up narration. |
| Prepare weekly ticket work for a slideshow | `weekly-ticket-slideshow-generator` | Produces a presentation brief, not final HTML. |
| Create a RevealJS slide deck | `revealjs-presenter` | Final presentation authoring. |

## Specialized Utilities

| Need | Use | Notes |
| --- | --- | --- |
| Browser automation, screenshots, scraping, web QA, or Electron automation | `agent-browser` | Prefer this over generic web tools for interactive browser work. |
| Remove AI writing patterns from prose | `avoid-ai-writing` | Audit-only or rewrite mode. |
| Maintain repo-owned config sync and symlinks | `config-symlink-maintainer` | Use for OpenCode, Codex, Neovim, skills, and memory sync work. |
| Review React/TypeScript code quality | `react-quality-review` | Checklist-based review, not general refactoring. |
| Create or update a skill in this repo | `write-a-skill` | Skill authoring only. |
| Capture or organize notes | `note-taking` | General note workflow. |
| Delegate independent work to OpenCode subagents | `skill-orchestrator-go` | OpenCode-specific. Use only for parallelizable, narrow subtasks. |

## Routing Rules

- Start with `workflow-orchestrator` when the request names Linear, ClickUp, or Notion.
- Use `ticket-drafter` for defect and implementation ticket drafts.
- Use `brainstorming` before `writing-plans` when the design is not settled.
- Use `implementation-prep` only for approved Coding Projects implementation handoff or explicit `/implementation-prep` requests.
- Do not load multiple planning skills at once; move stage by stage.
- Hide or purge skills that are not clear enough to describe in this index.
