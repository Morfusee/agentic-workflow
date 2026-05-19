---
name: skill-orchestrator-go
description: Coordinate a main OpenCode Go agent with lightweight subagents for narrow parallel tasks while preserving main-agent authority over planning, reasoning, review, and final output. Use when a request can be split into small independent tasks that benefit from cost-aware delegation.
---

# Skill Name
skill-orchestrator-go

# Purpose
Enable a main OpenCode Go agent to supervise short-lived subagents for small isolated tasks, then review and synthesize all accepted outputs into one final result.

# When To Use
Use this skill when:
- Work can be split into small independent units.
- Parallel execution can reduce latency or cost.
- The main agent needs evidence gathering, validation, comparison, or small drafting support.

Do not use this skill when:
- The task is tiny and direct execution is faster.
- Work is tightly coupled and cannot be safely isolated.
- Delegation would not improve speed, quality, or cost.

# Core Behavior
The main agent is the only planner, reviewer, and final decision-maker.

Main agent responsibilities:
- Define outcome, constraints, and acceptance criteria.
- Break work into minimal independent responsibilities.
- Delegate only narrow ephemeral tasks to subagents.
- Provide each subagent only required context.
- Review every subagent report before using any output.
- Resolve conflicts and synthesize final output.

Subagents provide temporary execution support only.

# Model Selection Rule
The main agent selects a subagent type, not a specific LLM model. The subagent type determines which underlying OpenCode Go model handles the task.

Rules:
- Prefer `explore` subagent type for narrow cheap tasks (search, inspect, summarize, validate).
- Prefer `general` subagent type only when the subtask requires broader capability (light drafting, comparison with reasoning).
- Proactively state the chosen subagent type when spawning each subagent so the user can see what is being used.
- Never ask the user what model or subagent type to use.
- If subagent type selection metadata is unavailable, default to `explore` running DeepSeek V4 Flash on High Effort.

# Concurrency Rule
Maximum concurrent subagents: 25 active at once.

Rules:
- Maintain an active subagent count at all times.
- If active count is 25, stop spawning new subagents.
- Wait for one or more active subagents to report completion, failure, or blocked status before spawning more.
- Spawn in parallel only when tasks are truly independent and parallelism is useful.
- Do not impose any soft cap below 25 when additional parallel fanout is beneficial.
- When parallelization helps, prefer the largest safe fanout up to the hard cap rather than conservative low fanout.

# Subagent Responsibility Rules
Subagents can:
- Search, inspect, summarize, validate, compare, and draft a small section.
- Return structured evidence, assumptions, and unknowns.
- Flag risks and conflicts.

Subagents cannot:
- Make high-level architecture or strategy decisions.
- Own final reasoning, prioritization, or judgment.
- Produce the final user-facing answer as authority.
- Expand scope beyond assigned boundaries.

# Subagent Permission Modes
The main agent assigns each subagent one permission mode before spawning it.

## READ_ONLY
Use for exploration, codebase inspection, dependency tracing, summarization, validation, and risk discovery.

Rules:
- The subagent must not modify files.
- The subagent must only report findings.
- This is the default mode.

## PATCH_ALLOWED
Use only for small, isolated, incremental code changes.

Rules:
- The subagent may modify only files explicitly listed in scope.
- The subagent must preserve all existing behavior unless the objective explicitly says otherwise.
- The subagent must not refactor unrelated code.
- The subagent must not remove existing logic, styles, tests, or comments unless explicitly instructed.
- The subagent must keep the patch minimal.
- The subagent must report every changed file and explain why each change was necessary.
- The main agent must review the diff before accepting the work.

# Subagent Task Template
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

# Subagent Report Format
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

# Main Agent Workflow
1. Define goal, constraints, and done criteria.
2. Decide if subagent orchestration is justified.
3. Decompose into minimal independent subtasks.
4. Decide the largest safe parallel batch for the independent subtasks, up to 25 active subagents.
5. Mark each subtask as delegate or keep in main agent, defaulting to READ_ONLY.
6. Assign a permission mode (READ_ONLY or PATCH_ALLOWED) to each delegated subtask.
7. For each delegated subtask, verify the current cheapest suitable OpenCode Go model.
8. Spawn subagents with strict scope and the required template.
9. Track subagent states: `active`, `completed`, `blocked`, `failed`.
10. Enforce the 25-active limit and wait when saturated.
11. Review each report for correctness, scope compliance, evidence quality, and mode compliance.
12. Retry, rescope, discard, or manually handle low-quality outputs.
13. Reconcile accepted outputs and run additional subagents only when needed.
14. Produce the final answer with main-agent reasoning and judgment.

# Quality Control Rules
- Never pass raw subagent output directly to the user.
- Accept outputs only when evidence and scope compliance are adequate.
- If output quality is low, choose one:
  - discard,
  - retry once with clearer tighter instructions,
  - or resolve manually in the main agent.
- If reports conflict, the main agent resolves conflicts explicitly before synthesis.
- If a subagent fails or blocks, either reassign, narrow scope further, or proceed with transparent gaps.
- Prefer correctness first, then cost and speed.
- Reject any READ_ONLY subagent that modified files.
- Reject any PATCH_ALLOWED output that edits files outside its explicit scope.
- Reject any PATCH_ALLOWED output that removes or refactors code without explicit direction.
- Perform a mandatory diff review before accepting any PATCH_ALLOWED subagent's work.

# Final Output Rules
- Final answer is authored by the main agent only.
- Synthesize accepted findings into one coherent result.
- Include important assumptions and unresolved unknowns when relevant.
- Reflect decisions made by the main agent, not by subagents.
- Keep the final response aligned with user intent, constraints, and quality bar.
