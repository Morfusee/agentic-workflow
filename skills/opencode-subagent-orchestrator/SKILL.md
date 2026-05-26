---
name: opencode-subagent-orchestrator
description: Use proactively when Codex should reduce quota or cost by delegating expensive implementation, research, inspection, validation, drafting, or patch tasks to OpenCode models through the local opencode CLI. Guides Codex as the main agent to estimate task cost, choose available cheap OpenCode models, hand off narrow subtasks, review returned work, retry with fresh subagents when needed, and compile final changes.
---

# OpenCode Subagent Orchestrator

Delegate expensive or quota-sensitive work from Codex to local OpenCode models while keeping Codex as the main agent.

## Core Rule

Keep Codex responsible for planning, model choice, review, final edits, final tests, and final user response. Treat OpenCode models as temporary subagents only.

## Decision Flow

1. Classify the user task:
   - `cheap`: answer directly in Codex when the task is small, low-token, or faster to do inline.
   - `expensive`: delegate when the task needs broad search, large file inspection, repeated validation, drafting, or nontrivial implementation.
   - `unsafe-to-delegate`: keep in Codex when secrets, destructive operations, production mutations, or ambiguous ownership are involved.
2. For expensive tasks, split work into narrow subagent objectives.
3. Select the cheapest suitable available model using `memory/skill-configs/opencode-models.json`.
4. Prefer `opencode/deepseek-v4-flash-free`, then `opencode-go/deepseek-v4-flash`, then configured fallbacks.
5. Invoke OpenCode with `scripts/invoke-opencode.ps1`.
6. Review every result before using it.
7. If a result is weak, spawn a fresh OpenCode run with a tighter prompt. Do not continue the same weak thread by default.
8. Apply or synthesize only accepted work, then run normal verification in Codex.

## Model Discovery

Use `scripts/list-models.ps1` before the first delegation in a session, when a model fails, or when the config may be stale.

If no preferred model is available:
- run `opencode models` for likely providers;
- if local discovery is insufficient and internet is available, quickly look up current OpenCode/provider model names;
- update `memory/skill-configs/opencode-models.json` before delegating.

## Delegation Modes

Use `READ_ONLY` by default for search, inspection, comparison, validation, and implementation planning.

Use `PATCH_ALLOWED` only when all are true:
- the subtask is isolated;
- exact editable files are known;
- the current git status is understood;
- Codex can review and reject the diff safely.

For `PATCH_ALLOWED`, scope the prompt to exact files and require a changed-files report. Codex must inspect the diff before accepting changes.

## Invocation

List available and preferred models:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File skills/opencode-subagent-orchestrator/scripts/list-models.ps1
```

Delegate a read-only inspection:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File skills/opencode-subagent-orchestrator/scripts/invoke-opencode.ps1 -TaskType INSPECT -PermissionMode READ_ONLY -Prompt "Inspect src/foo.ts and report likely causes of the failing test. Do not modify files."
```

Delegate an isolated patch:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File skills/opencode-subagent-orchestrator/scripts/invoke-opencode.ps1 -TaskType SMALL_PATCH -PermissionMode PATCH_ALLOWED -ScopeIn "src/foo.ts","tests/foo.test.ts" -Prompt "Fix the failing foo test by editing only the scoped files. Keep the patch minimal."
```

## Review Contract

Reject or retry OpenCode output when it:
- edits outside scope;
- omits evidence;
- makes broad architecture decisions;
- removes unrelated behavior;
- produces untested or incoherent changes;
- conflicts with repository patterns.

When retrying, start a new OpenCode run and provide:
- the original objective;
- the specific reason the prior result was rejected;
- stricter scope and acceptance checks.

Do not pass raw subagent output directly to the user. Summarize accepted work in Codex's own final answer.
