---
name: clickup-orchestrator
description: Route and orchestrate ClickUp-specific workflows through one entry point. Use when the user asks for ClickUp ticket dump creation, stand-up generation from ClickUp dumps, full ClickUp stand-up flow, ClickUp-context issue drafting, or ClickUp-context QA comment formatting.
---

# ClickUp Orchestrator

Route ClickUp workflows from one entry point. Infer intent heuristically; ask one focused clarification when confidence is low.

## Intent Routing

1. `dump-creation`: collect ClickUp activity and write a ticket dump. Read [`references/dump-standup-contract.md`](references/dump-standup-contract.md) before executing.
2. `standup-from-dump`: read a dump, let the user select items, pass selected evidence to `$standup-generator`, then update the dump. Read the contract reference first.
3. `full-flow`: run `dump-creation`, then `standup-from-dump` against the produced dump. For ranges, run each date branch independently and preserve partial results.
4. `issue-draft`: route to `$issue-drafter` only when the request is clearly ClickUp-contextual. Instruct it to use the ClickUp convention below instead of the default bug-report format.
5. `qa-comment`: route to `$qa-comment-formatter` for QA results, pass/fail checks, or test observations. If a ClickUp task ID/URL is present, pass it as `clickup_task_id` so the formatter can publish directly.

## Execution Contract

- This skill owns per-date agent spawning.
- Single-date request: spawn one agent. Date range: expand to daily dates and spawn one agent per date in parallel.
- Pass through model/reasoning effort when provided.
- In orchestrated mode, child branches must not spawn nested agents unless explicitly requested.
- All dump and stand-up memory interactions must stay under the canonical memory root defined in OpenCode global `AGENTS.md`.

## ClickUp Ticket Format

Use this only when creating or drafting ClickUp tickets directly or via `$issue-drafter`.

- Title: imperative, action-oriented, concise, no trailing period.
- Body: no blank lines; bold section headers; `Scope` and `Deliverable` use `- ` bullets.

```md
**Description**
<1-2 sentence purpose and context>
**Scope**
- actionable work item
- actionable work item
**Deliverable**
- concrete acceptance criteria / definition of done
```

## Non-Negotiables

1. Do not fabricate task details, ownership, chronology, outcomes, blockers, or plans.
2. Keep this as the single ClickUp workflow entry point.
3. Preserve dump headings and field names from the contract reference for downstream parsing.
4. Never treat watching/following as assignment.
5. Never infer implementation authorship from testing, comments, or QA-only evidence.
6. For dump ranges, include every day in the range, including empty days.
7. For stand-up-from-dump, never query ClickUp unless the user explicitly asks.
8. For full-flow ranges, show per-date successes/failures and continue remaining dates when one branch fails.
