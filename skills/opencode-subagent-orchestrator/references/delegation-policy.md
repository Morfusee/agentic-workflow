# Delegation Policy

Use this reference when deciding whether and how to hand work from Codex to OpenCode.

## Cost Classification

`cheap`
- One or two small file reads.
- A direct explanation or command result.
- A tiny edit where Codex already has enough context.
- Any task where delegation overhead is larger than the work.

`expensive`
- Large codebase inspection or many files.
- Repetitive searches, comparisons, or validation passes.
- Drafting long artifacts from source material.
- Nontrivial implementation where a subagent can prepare a scoped patch.
- Tasks likely to consume meaningful Codex quota.

`unsafe-to-delegate`
- Secrets, credentials, or private tokens are central to the task.
- The requested action mutates external services or production systems.
- The repo is too dirty to isolate subagent changes.
- The user explicitly wants Codex only.

## Task Splitting

Prefer narrow objectives:
- "Inspect auth middleware and identify where session expiry is handled."
- "Draft a minimal patch for `src/foo.ts` only."
- "Compare these two approaches and list risks."

Avoid broad objectives:
- "Fix the whole app."
- "Refactor auth."
- "Make the code better."

## Model Selection

Prefer the first available configured model that satisfies capability:

1. Free/cheapest model for read-only search, inspect, summarize, validate, and draft fragments.
2. Cheap stronger model for small patches or multi-file reasoning.
3. Stronger fallback only when cheaper models fail or are unavailable.

If `opencode-go` returns a billing error, record it as unavailable for the current session and retry with the next configured model.

## Fresh Retry Rule

If the first subagent output is poor, do not let that same output anchor the next attempt. Start a fresh OpenCode invocation with a revised prompt and only the critique needed to steer away from the failure.
