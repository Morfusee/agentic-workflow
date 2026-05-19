---
name: linear-orchestrator
description: Route and orchestrate Linear-specific workflows through one entry point. Use when the user asks for Linear ticket dump creation, stand-up generation from Linear dumps, full Linear stand-up flow, Linear-context issue drafting, Linear-context weekly ticket slideshow preparation, or Linear-context QA comment formatting.
---

# Linear Orchestrator

Route Linear workflows from one entry point. Infer intent heuristically; ask one focused clarification when confidence is low.

## Intent Routing

1. `dump-creation`: collect Linear activity and write a ticket dump. Read [`references/dump-standup-contract.md`](references/dump-standup-contract.md) before executing.
2. `standup-from-dump`: read a dump, let the user select items, pass selected evidence to `$standup-generator`, then update the dump. Read the contract reference first.
3. `full-flow`: run `dump-creation`, then `standup-from-dump` against the produced dump. For ranges, run each date branch independently and preserve partial results.
4. `issue-draft`: route to `$issue-drafter` only when the request is clearly Linear-contextual.
5. `weekly-slideshow`: route to `$weekly-ticket-slideshow-generator` only when the request is clearly Linear-contextual.
6. `qa-comment`: route to `$qa-comment-formatter` for QA results, pass/fail checks, or test observations. If a Linear issue ID, identifier, or URL is present, pass it as `linear_issue_id` so the formatter can publish directly.

## Execution Contract

- This skill owns per-date agent spawning.
- Single-date request: spawn one agent. Date range: expand to daily dates and spawn one agent per date in parallel.
- Pass through model/reasoning effort when provided.
- In orchestrated mode, child branches must not spawn nested agents unless explicitly requested.
- All dump, stand-up, and weekly slideshow memory interactions must stay under the canonical memory root defined in OpenCode global `AGENTS.md`.
- Linear dump creation prompts stand-up selection immediately unless the user explicitly asks for dump-only behavior.

## Non-Negotiables

1. Do not fabricate ticket details, ownership, chronology, outcomes, blockers, or plans.
2. Keep this as the single Linear workflow entry point.
3. Preserve dump headings and field names from the contract reference for downstream parsing.
4. Never treat subscription/watching as assignment.
5. Never infer implementation authorship from testing, comments, or QA-only evidence.
6. For dump ranges, include every day in the range, including empty days.
7. For stand-up-from-dump, never query Linear unless the user explicitly asks.
8. For full-flow ranges, show per-date successes/failures and continue remaining dates when one branch fails.
