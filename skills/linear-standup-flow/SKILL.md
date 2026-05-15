---
name: linear-standup-flow
description: Orchestrate the Linear stand-up workflow end-to-end by first creating a daily ticket dump and then generating a stand-up script from that dump. Use when the user wants one command to run dump creation and stand-up preparation in sequence.
---

# Linear Stand-up Flow Orchestrator

Run the two project skills in order and keep orchestration minimal.

Do not reimplement ticket filtering or stand-up generation logic here. Delegate execution to the existing skills.

## Parallel Agent Execution Contract

- Spawn one new agent per requested calendar date.
- If the request is a single date, spawn one agent.
- If the request is a date range, expand to daily dates and spawn one agent per date.
- Run all per-date agents in parallel.
- Each per-date agent runs this sequence for its own date only:
- invoke `$linear-ticket-dump-creator` for that exact date
- then invoke `$linear-ticket-dump-standup-generator` against the produced dump for that same date
- Pass through model and reasoning effort per agent from user input when provided.
- If model and effort are not provided, use the current thread defaults.
- In this orchestrated mode, child skills must not spawn additional agents unless explicitly required by the user.

## Execution Steps

1. Resolve workflow inputs.
- Capture requested date/range for dump creation when provided.
- Capture stand-up selection intent when provided (`all`, ticket IDs, numbers, or a short rule).
- If stand-up selection is not provided, continue and let the stand-up skill ask for selection.

2. Expand dates and start parallel per-date agents.
- Resolve an explicit list of dates from the user date/range intent.
- Start one agent per date in parallel.
- For each agent, pass exact date, selection intent, model, and reasoning effort.

3. In each per-date agent, invoke `$linear-ticket-dump-creator` first.
- Pass through the exact date intent only.
- Require successful dump creation before continuing.
- If dump creation fails for a date, stop that date flow and report failure for that date.

4. In each per-date agent, invoke `$linear-ticket-dump-standup-generator` second.
- Use the dump produced by that same per-date agent.
- If user already gave selection intent, pass it through directly.
- Otherwise allow the stand-up skill to collect selection.

5. Return final outcome.
- Wait for all per-date agents to complete.
- Report per-date results with status, dump path, and selected ticket summary.
- Keep partial successes and partial failures visible per date.

## Rules

1. Keep this skill as an orchestration wrapper only.
2. Do not duplicate contracts from either underlying skill.
3. Do not query Linear directly in this wrapper unless the dump creator explicitly requires it.
4. Preserve standalone behavior of both underlying skills.
5. On partial failure, report which phase failed and do not hide errors.
6. In orchestrated range mode, parent skill owns agent spawning; do not allow nested child spawning by default.
