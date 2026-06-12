# Skill Index

Use this as the routing map before loading a skill. Prefer the narrowest skill that matches the user's request.

## Primary Entrypoints

| Need | Use | Notes |
| --- | --- | --- |
| Work with Linear tickets, dumps, stand-ups, QA comments, or Linear ticket drafts | `linear-orchestrator` | Provider-specific entrypoint. It routes to ticket helper skills. |
| Work with ClickUp tasks, dumps, stand-ups, QA comments, or ClickUp ticket drafts | `clickup-orchestrator` | Provider-specific entrypoint. It routes to ticket helper skills. |
| Create or update Notion pages, tasks, or Coding Projects Tracker items | `notion-orchestrator` | Provider-specific entrypoint. Use for Notion schema and placement. |
| Improve a frontend interface or product UI | `impeccable` | UI/UX critique, redesign, polish, and frontend visual quality. |
| Refactor existing code without behavior changes | `refactor` | Surgical maintainability improvements. |
| Commit current changes | `git-commit` | Conventional commit staging and message workflow. |
| Hand off current context to another agent | `handoff` | Conversation and work-state compaction. |

## Ticket And Work Planning

| Need | Use | Avoid When |
| --- | --- | --- |
| Draft a bug, regression, production issue, or problem investigation ticket | `issue-drafter` | The work is a planned feature or refactor. |
| Draft a feature, enhancement, refactor, or non-bug implementation ticket | `implementation-ticket-drafter` | The request is a defect report or broken behavior. |
| Investigate tracker tickets against a codebase | `ticket-codebase-investigator` | The user only wants a clean ticket draft. |
| Create a PRD and split it into ticket phases | `prd-to-ticket-planner` | The user already has an implementation-ready ticket. |
| Format QA results as a tracker comment | `qa-comment-formatter` | The user needs a new ticket, not a QA update. |

## Implementation Flow

| Stage | Use | Purpose |
| --- | --- | --- |
| Clarify ambiguous or creative work before implementation | `brainstorming` | Turn fuzzy ideas into an approved design/spec. |
| Turn an approved spec into an implementation plan | `writing-plans` | Produce task-by-task engineering instructions before coding. |
| Prepare an approved Notion Coding Projects ticket for implementation | `implementation-prep` | Classify work, choose branch/worktree strategy, and decide whether brainstorming is needed. |
| Create an isolated worktree for feature work | `using-git-worktrees` | Keep implementation work separate from the current workspace. |
| Stress-test a plan through questioning | `grill-me` | Use for adversarial plan/design review, often inside PRD work. |

## Reporting And Presentations

| Need | Use | Notes |
| --- | --- | --- |
| Create normalized ticket dump files from provider facts | `ticket-dump-creator` | Usually called by Linear or ClickUp orchestrators. |
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

- Start with provider orchestrators when the request names Linear, ClickUp, or Notion.
- Use `issue-drafter` for defects and `implementation-ticket-drafter` for planned work.
- Use `brainstorming` before `writing-plans` when the design is not settled.
- Use `implementation-prep` only for approved Coding Projects implementation handoff or explicit `/implementation-prep` requests.
- Do not load multiple planning skills at once; move stage by stage.
- Hide or purge skills that are not clear enough to describe in this index.
