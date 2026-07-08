---
name: agent-advisor
description: Delegate to ChatGPT Agent Advisor for advice, fixes, reviews, or better approaches.
disable-model-invocation: true
---

# Agent Advisor

User-invoked only. Delegate work to ChatGPT's Agent Advisor project. Invoke bare to infer the task from conversation, or with instructions: `/agent-advisor review this for edge cases`.

## Hard Constraints

- Stay inside Agent Advisor. No other project, thread, or page on chatgpt.com. Creating a fresh thread *inside* Agent Advisor is the only navigation allowed.
- Never tell Agent Advisor where the prompt came from. No "this is from OpenCode", no "connectivity test", no meta-commentary about the skill, invocation source, or tooling. Every prompt must stand on its own as if you composed it directly.

## Steps

1. Open Agent Advisor.
   Use Chrome DevTools with the existing browser profile. Navigate to chatgpt.com, select the Agent Advisor project. Create a thread inside it if none is active.
   Completion criterion: the active browser page sits inside Agent Advisor, ready for input.

2. Select the best model.
   Locate the intelligence/effort dropdown (typically labeled "Medium" or "High" near the model selector). Set it to the highest available tier.
   Completion criterion: the dropdown shows the maximum available effort level.

3. Infer the task.
   Read the session for the open problem: code in play, errors being chased, design unsettled, uncertainty the user holds. If the invocation carries appended instructions, those are the directive — still pull relevant code, error messages, and constraints from the session to anchor the prompt. If the invocation is bare, the task is whatever the conversation is stuck on.
   Completion criterion: a concrete, bounded problem is identified with enough surrounding context to anchor useful advice.

4. Delegate.
   Compose and send the prompt into Agent Advisor. Give the advisor only what it needs: the code, the error, the constraint, the goal. No mention of OpenCode, the skill, or how the prompt originated. No filler. No preamble.
   Completion criterion: the prompt is sent and Agent Advisor's response is visible.

5. Relay.
   Present the full response to the user. Code verbatim. Discursive advice summarized. Flag caveats or uncertainties the advisor noted.
   Completion criterion: the user has the complete advice in context.
