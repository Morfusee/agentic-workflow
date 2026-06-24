# Stand-up Script

Yesterday, I hopped on a call with Ibrahim to discuss the frontend/backend stack and the packages we plan to use.

We specifically discussed whether we can use Next.js with BullMQ. We found out that it does not work well because BullMQ expects a non-serverless application that can handle long-running worker processes. Even with the standalone version of Next.js, the worker still needs to run outside of Next.js.

After that, I researched alternatives and found Inngest. It works well with Next.js because it can handle queues and job scheduling in a serverless-friendly way. Instead of relying on our backend server to run the queue, Inngest acts as the queueing engine itself.

Today, I plan to help finalize the overall application architecture before we proceed.

The blocker is that we need confirmation on the architecture: since we want to use Next.js as an all-in-one frontend and backend solution that can be packaged into one Docker image, can we use Next.js together with a self-hosted Inngest instance for queues and scheduled jobs?

---

# Selected Tasks

- [MANUAL-001]: Discuss frontend/backend stack and package direction with Ibrahim
  - Status: Done
  - Activity date: 2026-06-23
  - Reference: `# Manual Tasks` -> `## [MANUAL-001]: Discuss frontend/backend stack and package direction with Ibrahim`
  - Stand-up relevance: Captures the architecture discussion that shaped the stack decision.

- [MANUAL-002]: Evaluate BullMQ compatibility with Next.js
  - Status: Done
  - Activity date: 2026-06-23
  - Reference: `# Manual Tasks` -> `## [MANUAL-002]: Evaluate BullMQ compatibility with Next.js`
  - Stand-up relevance: Captures the finding that BullMQ requires worker processes outside the Next.js application.

- [MANUAL-003]: Research Inngest as an alternative queueing and scheduling option
  - Status: Done
  - Activity date: 2026-06-23
  - Reference: `# Manual Tasks` -> `## [MANUAL-003]: Research Inngest as an alternative queueing and scheduling option`
  - Stand-up relevance: Captures the proposed alternative that works better with Next.js and serverless-style execution.

- [MANUAL-004]: Finalize application architecture before proceeding
  - Status: In Progress
  - Activity date: 2026-06-23
  - Reference: `# Manual Tasks` -> `## [MANUAL-004]: Finalize application architecture before proceeding`
  - Stand-up relevance: Captures the current blocker and decision needed before implementation continues.

---

# Unselected Tasks

Carry-over tasks not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

No unselected tasks.

---

# Manual Tasks

## [MANUAL-001]: Discuss frontend/backend stack and package direction with Ibrahim

- Status: Done
- Activity date: 2026-06-23
- Evidence: Hopped on a call with Ibrahim to discuss the frontend/backend stack and packages to use.

## [MANUAL-002]: Evaluate BullMQ compatibility with Next.js

- Status: Done
- Activity date: 2026-06-23
- Evidence: Discussed with Ibrahim whether Next.js can be used with BullMQ. Found that BullMQ does not fit well because it expects non-serverless applications that can handle long-running worker processes. Even for standalone Next.js apps, the worker needs to run outside Next.js.

## [MANUAL-003]: Research Inngest as an alternative queueing and scheduling option

- Status: Done
- Activity date: 2026-06-23
- Evidence: Researched alternatives to BullMQ and found Inngest. Inngest works well with Next.js because it can handle queues and job scheduling while acting as the queueing engine itself instead of requiring the backend server to run worker processes.

## [MANUAL-004]: Finalize application architecture before proceeding

- Status: In Progress
- Activity date: 2026-06-23
- Evidence: The team wants to finalize the application architecture before proceeding. The open question is whether the stack can use Next.js as the frontend and backend, packaged into one Docker image, together with a self-hosted Inngest instance for queues and scheduled jobs.
- Blocker: Need confirmation that Next.js plus self-hosted Inngest is acceptable as the architecture before proceeding.

---

# All Scraped Tasks

No ClickUp tasks were scraped for this manual-only stand-up.
