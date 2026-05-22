---
date: 2026-05-21
type: workflow
tags: [workflow, parallelization, codebase-analysis, ticket-analysis, agent-orchestration]
related: [2026-05-21-clickup-epics-unassigned-task-analysis]
---

# Parallel Codebase Investigation Workflow

Reusable workflow for spawning parallel agents to investigate multiple tickets/issues against a codebase, producing structured root-cause analysis and implementation plans.

## When to Use

- Triaging or grooming a batch of unassigned/unsized tickets against a codebase
- Generating implementation estimates and root-cause analysis for N tickets in parallel
- Replacing sequential ticket-by-ticket investigation with a single parallel fan-out
- Any scenario where you have 3+ tickets and want deep codebase-aware analysis per ticket

## Architecture

```
                   ┌─────────────────────────────────┐
                   │     Main Agent (Orchestrator)    │
                   │  - Fetches ticket list           │
                   │  - Spawns 1 codebase explorer    │
                   │  - Spawns N ticket investigators │
                   │  - Collates results              │
                   └──────┬──────────┬────────────────┘
                          │          │
              ┌───────────┘          └───────────┐
              ▼                                  ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│  Agent 0: Codebase      │    │  Agents 1..N: Per-Ticket     │
│  Explorer               │    │  Investigators               │
│                         │    │                              │
│  - Tech stack           │    │  Each receives:              │
│  - Directory structure  │    │  - Full ticket details       │
│  - Framework/libs       │    │  - Codebase summary          │
│  - Component patterns   │    │  - Task: investigate         │
│  - Routing structure    │    │    relevant code paths       │
│  - Existing features    │    │                              │
│                         │    │  Each returns:               │
│  Returns: comprehensive │    │  - Root causes               │
│  codebase summary       │    │  - Concrete fixes            │
└────────┬────────────────┘    │  - Key files to touch        │
         │                     │  - Effort estimate           │
         │                     │  - Implementation plan       │
         │                     └──────────┬───────────────────┘
         │                                │
         └────────────┬───────────────────┘
                      ▼
         ┌────────────────────────┐
         │  Collated Output:      │
         │  Per-ticket analysis   │
         │  with implementation   │
         │  plans and estimates   │
         └────────────────────────┘
```

## Step-by-Step Execution

### Step 1: Fetch Tickets

Use the source system (ClickUp, Linear, Jira, etc.) to get the list of tickets. Filter to unassigned or the subset you want to investigate.

**ClickUp example:**
```
clickup_filter_tasks(list_ids=["..."], include_closed=false)
```

Store the ticket IDs, titles, descriptions, and any existing metadata.

### Step 2: Spawn Codebase Explorer (Parallel with Step 3)

Spawn one explore agent to understand the codebase. This runs in parallel with ticket investigators.

**Prompt template:**
```
Explore the codebase at <repo_path> thoroughly. I need to understand:

1. What kind of project this is (tech stack, framework, languages)
2. The directory structure (top-level and key subdirectories)
3. What features/modules exist
4. Package.json or similar config files to understand dependencies and scripts
5. Any existing component patterns, routing, state management
6. The overall architecture (frontend? backend? fullstack?)

Return a comprehensive summary of the codebase including:
- Project type and tech stack
- Key directories and their purposes
- Framework and major libraries used
- Routing structure
- Component patterns
- Any existing feature areas or modules
```

Use `subagent_type: "explore"` with `"very thorough"` thoroughness level.

### Step 3: Spawn Per-Ticket Investigators (Parallel with Step 2)

For each ticket, spawn one explore agent. **All agents run simultaneously.** Each agent receives:

1. The ticket's full details (title, description, status, etc.)
2. A tailored investigation prompt based on the ticket's content
3. The codebase path to investigate

**Generic prompt template:**
```
You are investigating the codebase at <repo_path> to understand how to implement 
(or debug, or analyze) this ticket:

TICKET: <title>
DESCRIPTION: <description>

Investigate and return a detailed high-level overview covering:

1. [Investigation area 1 specific to the ticket]
2. [Investigation area 2 specific to the ticket]
3. [Investigation area 3 specific to the ticket]
4. [What files need to be created/modified — list exact paths]
5. [Potential implementation approach — step-by-step using existing conventions]
6. [Potential root causes — if it's a bug/performance issue]
7. [Effort estimate and risk assessment]

Return all findings in a structured format. Be thorough — read actual file contents, 
not just glob results. Look at existing patterns in the codebase that can be 
followed or extended.
```

Use `subagent_type: "explore"` with `"very thorough"` thoroughness level.

### Step 4: Collate Results

Once all agents return, compile findings into:

1. **Per-ticket structured analysis** with:
   - Root causes
   - Concrete fixes in priority order
   - Exact files to create/modify
   - Effort estimates
   - Implementation steps

2. **Summary ranking** — sort tickets by effort (fastest first), annotated with risk level.

### Step 5: Document Output

Write findings as a note or report. Reference this workflow note as the source method.

---

## Prompt Engineering Guidelines

### For Bug/Performance Tickets

Tailor the investigation areas to the specific problem:

```
1. [Symptom patterns]: Search the codebase for the area causing the symptom. 
   Use grep for relevant imports, patterns, configurations.
2. [Existing mitigations]: Check if partial fixes already exist.
3. [Root cause tree]: What are the 2-5 most likely causes? For each, provide 
   code evidence.
4. [Fix priority list]: Rank fixes by impact-to-effort ratio. List exact files 
   and line ranges for each fix.
```

### For Feature Tickets

Tailor for implementation planning:

```
1. [Existing patterns to follow]: Find analogous features already in the codebase. 
   Read their files to understand conventions.
2. [Dependency chain]: What existing modules, types, or utilities will the feature 
   depend on?
3. [Files to create/modify]: List exact paths. Mark which are new vs. edits.
4. [Implementation steps]: Step-by-step following existing conventions. Include 
   config registration, type generation, route setup.
```

### For CMS/Content Tickets

Tailor for no-code vs. code split:

```
1. [Existing blocks/features inventory]: List what already exists that can handle 
   the requirement.
2. [Gap analysis]: What CANNOT be done with existing primitives?
3. [New development needed]: If gaps exist, what new blocks/modules are needed 
   and how many files?
4. [No-code proportion]: Estimate what % is pure content configuration vs. 
   development.
```

---

## Expected Agent Output Format

Each per-ticket agent should return a report with these sections:

```markdown
## 1. [Investigation Area]
Findings with file paths and line numbers as evidence.

## 2. Root Causes (if applicable)
| # | Cause | Evidence |
|---|-------|----------|

## 3. Concrete Fixes / Implementation Steps
| Priority | File | Change | Impact |
|----------|------|--------|--------|

## 4. Files to Create/Modify
Complete list with absolute paths.

## 5. Effort Estimate & Risk
Time range and confidence level.
```

---

## Constraints & Rules

1. **All per-ticket agents + codebase explorer spawn in a single message** — maximize parallelism.
2. **Agents are read-only** — they investigate and report, never modify code.
3. **One agent per ticket** — do not combine multiple tickets into one agent.
4. **Each agent gets the full ticket text** — do not summarize the ticket for the agent; pass through the original description, links, and attachments.
5. **Agents must read actual file contents** — glob patterns alone are not sufficient. Agents should use Read on key files.
6. **Collation happens after all agents return** — do not report partial results.

---

## Adaptation Notes

### For Different Issue Trackers

| Tracker | Ticket Fetch Tool | ID Format |
|---------|-------------------|-----------|
| ClickUp | `clickup_filter_tasks`, `clickup_get_task` | Short IDs like `86d32m54w` |
| Linear | `linear_list_issues`, `linear_get_issue` | Team-key IDs like `LIN-123` |
| GitHub | `gh issue list`, issue API | Numeric `#123` |
| Jira | Jira API / MCP tools | Project-key IDs like `PROJ-123` |

### For Different Codebase Sizes

| Size | Explorer Thoroughness | Per-Ticket Focus |
|------|----------------------|-------------------|
| Small (<100 files) | "quick" | Broader scanning |
| Medium (100-500 files) | "medium" | Targeted by ticket domain |
| Large (500+ files) | "very thorough" | Narrow, focused on relevant paths only |

### For Different Ticket Counts

| Count | Strategy |
|-------|----------|
| 1-2 tickets | Sequential is fine; parallelize only if >1 minute of investigation each |
| 3-8 tickets | Full parallel fan-out (this workflow) |
| 9+ tickets | Batch into groups of 4-6; run batches sequentially, tickets within batch in parallel |

---

## Example: The ClickUp Epics Run

This workflow was tested against 4 unassigned tickets in the mmdc-web Epics board. Summary:

| Agent | Ticket | Type | Result |
|-------|--------|------|--------|
| Explorer | (codebase) | Architecture survey | Full codebase summary returned |
| Investigator 1 | LLMs.txt | Feature | 3-file implementation plan, ~30 min estimate |
| Investigator 2 | Mockup Recreation | CMS/Content | Block inventory, gap analysis, 0-8 hr estimate |
| Investigator 3 | Render-Blocking CSS | Performance | 5 root causes, 5 prioritized fixes, 1-3 hr estimate |
| Investigator 4 | JS Execution Time | Performance | 5 root causes, 5 prioritized fixes, 4-8+ hr estimate |

Full output in: `2026-05-21-clickup-epics-unassigned-task-analysis.md`

Total wall-clock time: ~60 seconds for all 5 agents to return.

---

## Output Collation Template

When collating results into a final report, use this structure:

```markdown
---
date: <YYYY-MM-DD>
type: research
tags: [<tracker>, <project>, task-analysis, <domain>]
related: [parallel-codebase-investigation-workflow]
---

# <Board/Project> — Task Analysis

**Source:** <tracker> <board/list name>
**Context:** <repo name> (<repo path>)
**Stack:** <key technologies>

Of N tickets, M are <filter criterion>. Ranked by implementation effort (fastest first):

---

## N. `<ticket_id>` — <title>

**Status:** <status>
**URL:** <ticket_url>
**Estimate:** <time range>

**Description:** <1-liner>

### Root Causes / Findings
| # | Cause | Evidence |
|---|-------|----------|

### Fixes / Implementation Plan
| Priority | File | Change | Impact |
|----------|------|--------|--------|

### Key Files
- `<path>` — <purpose>

---

## Summary Ranking

| Rank | Ticket ID | Ticket | Effort | Risk |
|------|-----------|--------|--------|------|
```
