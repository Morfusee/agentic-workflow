---
name: thermos
description: Double thermo-nuclear review — runs security/correctness and code-quality audits in parallel, then synthesizes findings. Use for thermos or combined branch audits. Invocable by review-orchestrator as a reviewer.
---

# Thermos

Sub-orchestrator that runs `$thermo-nuclear-review` and `$thermo-nuclear-code-quality-review` in parallel, then synthesizes findings into a single verdict. Works standalone or as a reviewer invoked by `$review-orchestrator` — the workflow is the same either path.

## Workflow

1. Gather the branch-scoped diff (`git diff main...HEAD`). Pass only changed files and their immediate context.
2. Load `$thermo-nuclear-review` and `$thermo-nuclear-code-quality-review`.
3. Run both reviews in parallel using `task` subagents (type `general`). Pass each subagent the full skill instructions plus the scoped diff. Do not run sequentially unless parallel execution is unavailable.
4. Collect both `REVIEWER_RESULT` blocks. Reject any result lacking the contract block.
5. Synthesize into a unified verdict:

| Rule | Logic |
|---|---|
| **Deduplicate** | Merge overlapping findings. A bug that also degrades maintainability is one finding. Mark `source: both`. |
| **Weight overlaps** | Findings surfaced by both reviewers carry higher severity. |
| **Resolve disagreements** | Prefer the result with stronger file-level evidence. Note unresolved conflicts in `notes`. |
| **Overall status** | `FAIL` if either reviewer returned `FAIL`. `PASS` only if both returned `PASS`. `PARTIAL` if mixed or incomplete. |
| **Confidence** | Floor of the two reviewer confidences. Raise only when both agree on a finding. |

Surface only the unified verdict, highest-signal findings, and unresolved conflicts. Do not restate individual reviewer summaries if they are already visible.

## Output Contract

```text
REVIEWER_RESULT
reviewer: thermos
overall_status: {PASS|FAIL|PARTIAL|BLOCKED}
checks:
- description: {deduplicated and weighted finding}
  status: {PASS|FAIL|PARTIAL|BLOCKED}
  expected: {expected behavior or standard}
  actual: {file-backed observation with paths and line numbers}
  source: {thermo-nuclear-review|thermo-nuclear-code-quality-review|both}
notes:
- {synthesis observations, overlapping findings, unresolved conflicts}
confidence: {high|medium|low}
END_REVIEWER_RESULT
```
