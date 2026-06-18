# Skill Index

Use this as the routing map before loading a skill. Repo source folders are categorized as `skills/<category>/<skill-name>/SKILL.md`; provider sync flattens them to `<provider-skills>/<skill-name>/`.

## Start Here

| Need | Use | Notes |
| --- | --- | --- |
| Linear, ClickUp, Notion, ticket dumps, stand-ups, review comments, or provider publishing | `workflow-orchestrator` | Main provider workflow entrypoint. |
| Draft a technical ticket from loose input | `ticket-drafter` | Produces provider-agnostic ticket handoff metadata. |
| Implement an approved ticket or scoped prompt | `ticket-implementation-flow` | Handles analysis, confidence gates, worktree setup, implementation, commit, and optional ticket notification. |
| Improve frontend UI or product UX | `impeccable` | Design, UX, accessibility, polish, and frontend visual quality. |
| Refactor code without changing behavior | `refactor` | Surgical maintainability improvements. |
| Commit current changes | `git-commit` | Conventional commit workflow. |
| Preserve context for another agent | `handoff` | Conversation and work-state compaction. |

## Tickets

| Skill | Use When | Notes |
| --- | --- | --- |
| `workflow-orchestrator` | The request names Linear, ClickUp, Notion, provider tasks, dumps, stand-ups, reviews, or provider publishing. | Routes to provider and ticket helper workflows. |
| `ticket-drafter` | Turning a defect, feature, enhancement, refactor, migration, or loose request into an engineer-ready ticket. | Draft only; provider orchestrators publish. |
| `ticket-prd-planner` | Creating a PRD, splitting phases, or turning product requirements into ticket plans. | For larger product planning, not already-scoped single tickets. |
| `ticket-implementation-flow` | Executing ticket or prompt implementation from requirements through code changes and optional commit/comment. | Often routed by `workflow-orchestrator`. |
| `ticket-review-comment-drafter` | Formatting code review, QA, or requirements-review results into tracker-ready comments. | Only changes status when explicitly requested. |
| `ticket-dump-creator` | Creating normalized Markdown ticket/task dump files from collected provider facts. | Called after provider facts are already gathered. |

## Planning

| Skill | Use When | Notes |
| --- | --- | --- |
| `brainstorming` | Creative or ambiguous feature work needs intent, requirements, and design clarified before implementation. | Use before coding when behavior is not settled. |
| `writing-plans` | A spec or requirements need to become a multi-step implementation plan. | Planning only; do not use for direct execution. |
| `grill-me` | A plan or design needs adversarial questioning and decision-tree pressure testing. | Good before PRD or implementation approval. |
| `using-git-worktrees` | Feature work needs isolation from the current workspace. | Uses native worktrees or fallback setup. |
| `refactor` | Existing code should be improved without behavior changes. | Less drastic than broad rewrites. |

## Review

| Skill | Use When | Notes |
| --- | --- | --- |
| `review-orchestrator` | Reviewing completed implementation work against requirements, diffs, tickets, or code quality criteria. | Coordinates focused reviewers and aggregates checks. |
| `react-quality-review` | Reviewing React/TypeScript for best practices, performance, accessibility, testing, and standards. | Review only, not refactoring. |
| `requirements-reviewer` | Producing evidence-backed pass/fail checks against acceptance criteria. | Good for ticket completion validation. |

## Ponytail

| Skill | Use When | Notes |
| --- | --- | --- |
| `ponytail` | The user asks for lazy mode, simplest solution, shortest path, YAGNI, or less over-engineering. | Biases toward the smallest working solution. |
| `ponytail-review` | The user wants a complexity-focused code review. | Diff-level review. |
| `ponytail-audit` | The user wants a whole-repo complexity audit. | Repo-level report. |
| `ponytail-debt` | The user wants every `ponytail:` shortcut/debt comment harvested into a ledger. | Report only. |
| `ponytail-help` | The user asks for ponytail commands or usage. | Quick reference. |

## Frontend

| Skill | Use When | Notes |
| --- | --- | --- |
| `impeccable` | Designing, redesigning, auditing, polishing, or improving frontend interfaces. | UX and visual quality specialist. |
| `agent-browser` | Browser automation, screenshots, scraping, web QA, website interaction, or Electron automation. | Prefer over generic web tools for interactive browsing. |
| `html` | Creating a self-contained HTML report, explainer, prototype, comparison, or artifact. | Not specifically diagram-first. |
| `html-diagram` | Creating a self-contained HTML architecture or stack diagram. | Diagram-first output. |
| `revealjs-presenter` | Creating RevealJS slide decks. | Final presentation authoring. |

## Knowledge

| Skill | Use When | Notes |
| --- | --- | --- |
| `standup-generator` | Generating a spoken stand-up script from selected work items and evidence. | Does not retrieve provider data itself. |
| `weekly-ticket-slideshow-generator` | Turning weekly ticket dumps and stand-up scripts into a presentation brief. | Feeds `revealjs-presenter`. |
| `note-taking` | Capturing, organizing, or retrieving structured notes. | General note workflow. |
| `teach` | The user asks to learn a concept or wants a lesson. | Writes teaching artifacts under `memory/teach/<topic>/`. |
| `avoid-ai-writing` | Auditing or rewriting prose to remove AI writing patterns. | Supports detection-only mode. |

## Tools

| Skill | Use When | Notes |
| --- | --- | --- |
| `config-symlink-maintainer` | Maintaining repo-owned config, symlinks, backups, or sync behavior for local tools. | Covers OpenCode, Codex, Neovim, skills, and memory sync. |
| `write-a-skill` | Creating or updating agent skills in this repo. | Follow repo skill structure rules. |
| `skill-orchestrator-go` | Coordinating parallel, independent OpenCode subagent tasks. | OpenCode-specific and hidden from Codex. |
| `git-commit` | Creating a Conventional Commit from current changes. | Stages intentionally and avoids unrelated changes. |
| `handoff` | Compacting active work into a handoff document. | Use when another agent will continue. |

## Routing Rules

- Keep repo source folders categorized as `skills/<category>/<skill-name>/SKILL.md`.
- Keep provider-facing skill directories flat; `scripts/sync_environment.py` links each discovered skill folder to `<provider-skills>/<skill-name>/`.
- Start with `workflow-orchestrator` when the request names Linear, ClickUp, or Notion.
- Use the narrowest skill that matches the request instead of loading a broad workflow by default.
- Use `brainstorming` before `writing-plans` when the desired behavior or design is not settled.
- Use `review-orchestrator` for implementation review, then `ticket-review-comment-drafter` only when the result needs tracker-ready formatting.
- Use ponytail skills only when the user asks for minimalism, over-engineering review, or the ponytail command family.
- Hide or purge skills that are not clear enough to describe in this index.
