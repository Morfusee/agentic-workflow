---
name: skill-orchestrator-go
description: Coordinate a main OpenCode Go agent with lightweight subagents for narrow parallel tasks while preserving main-agent authority over planning, reasoning, review, and final output. Use when a request can be split into small independent tasks that benefit from cost-aware delegation.
---

# Skill Orchestrator Go

Use short-lived subagents for narrow independent work while the main agent remains the planner, reviewer, decision-maker, and final author.

## When To Use

Use when independent subtasks can improve speed, cost, evidence gathering, validation, comparison, or small drafting support.

Do not use when direct execution is faster, work is tightly coupled, or delegation would not improve speed, quality, or cost.

## Main-Agent Authority

The main agent must:

- define outcome, constraints, and acceptance criteria
- decompose only minimal independent tasks
- delegate only narrow ephemeral responsibilities
- give each subagent only required context
- review every report before using it
- resolve conflicts and synthesize the final answer

Subagents support execution only. They do not own architecture, strategy, final reasoning, prioritization, judgment, or user-facing authority.

## Subagent Selection And Concurrency

- Select a subagent type, not a specific LLM model.
- Use `explore` for search, inspection, summarization, validation, and other narrow cheap tasks.
- Use `general` only for broader reasoning, light drafting, or comparison.
- State the chosen subagent type when spawning so the user can see what is being used.
- Never ask the user what model or subagent type to use.
- If selection metadata is unavailable, default to `explore` running DeepSeek V4 Flash on High Effort.
- Maximum active subagents: 25.
- Prefer the largest safe fanout up to 25 when tasks are truly independent and parallelism helps; wait when saturated.

## Permission Modes

Assign one mode before spawning.

`READ_ONLY` is the default for exploration, inspection, tracing, summarization, validation, and risk discovery. It must not modify files.

`PATCH_ALLOWED` is only for small isolated changes. The subagent may edit only explicitly listed files, must keep patches minimal, must preserve behavior unless told otherwise, must avoid unrelated refactors/removals, and must report every changed file with a reason. The main agent must review the diff before accepting the work.

## Subagent Task Template

Use this exact prompt template when spawning each subagent:

```text
You are Subagent {SUBAGENT_ID} working under a supervising main agent.

Task type: {SEARCH|INSPECT|SUMMARIZE|VALIDATE|COMPARE|DRAFT_FRAGMENT|OTHER}
Permission mode: {READ_ONLY|PATCH_ALLOWED}
Objective: {single clear objective}

Scope in (exact editable file paths when PATCH_ALLOWED):
- {allowed file/source/question 1}
- {allowed file/source/question 2}

Scope out:
- {explicit exclusion 1}
- {explicit exclusion 2}

Required inputs:
- {input 1}
- {input 2}

Constraints:
- If permission mode is READ_ONLY, do not modify any files.
- If permission mode is PATCH_ALLOWED, modify only files explicitly listed in scope and report every change with a reason.
- Use only scoped context and required inputs.
- Do not make final decisions outside this task.
- Be concise and evidence-based.
- State uncertainty explicitly when present.
- Stop immediately when objective is complete.

Deliverable:
- Return only the exact Subagent Report Format.

Acceptance checks:
- Objective directly answered.
- Evidence provided.
- Assumptions listed.
- Unknowns and risks listed.
```

## Subagent Report Format

Subagents must return this exact format:

```text
SUBAGENT_REPORT
subagent_id: {SUBAGENT_ID}
task_type: {SEARCH|INSPECT|SUMMARIZE|VALIDATE|COMPARE|DRAFT_FRAGMENT|OTHER}
permission_mode: {READ_ONLY|PATCH_ALLOWED}
status: {completed|blocked|failed}
objective: {original objective}
summary:
- {finding 1}
- {finding 2}
evidence:
- {source/path + key fact}
- {source/path + key fact}
assumptions:
- {assumption 1}
unknowns:
- {unknown 1}
risks_or_conflicts:
- {risk or conflict 1}
confidence: {high|medium|low}
recommended_next_step_for_main_agent: {single concrete next step}
changed_files: none
# or when PATCH_ALLOWED:
# - file: {file_path}
#   reason: {why change was necessary}
END_SUBAGENT_REPORT
```

## Workflow

1. Define goal, constraints, and done criteria.
2. Confirm orchestration is justified.
3. Decompose into minimal independent subtasks and choose the largest safe parallel batch up to 25 active subagents.
4. Assign subagent type and permission mode, defaulting to `READ_ONLY`.
5. Spawn with strict scope and the exact task template.
6. Track `active`, `completed`, `blocked`, and `failed` states; wait when the active count reaches 25.
7. Review every report for correctness, evidence quality, scope compliance, and permission-mode compliance.
8. Retry once, rescope, discard, or handle manually when output is weak, blocked, failed, conflicting, or noncompliant.
9. Reconcile accepted outputs and produce the final answer with main-agent reasoning and judgment.

## Quality Gates

- Never pass raw subagent output directly to the user.
- Reject any `READ_ONLY` subagent that modified files.
- Reject any `PATCH_ALLOWED` output that edits outside scope, removes logic, or refactors without explicit direction.
- Perform mandatory diff review before accepting any `PATCH_ALLOWED` work.
- Preserve correctness first, then cost and speed.
- Include important assumptions and unresolved unknowns in the final answer when relevant.
