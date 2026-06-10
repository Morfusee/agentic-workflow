# Handoff: DnDGame v0 — HAT-18 Implementation Planning

**Date:** 2026-06-10
**Next session focus:** Brainstorm and plan the implementation of HAT-18 ("Create minimal OpenCode plugin shell and registration path")

---

## Conversation Summary

The user asked to discover available Linear tickets in the DnDGame Hatudoggy project they could start working on. After initial confusion (the Linear API was returning truncated results), the full ticket list was uncovered: HAT-15 through HAT-70, all in "Todo" status, with only HAT-16 ("Scaffold DnDGame OpenCode plugin project structure") marked "Done."

The user wanted to work sequentially from the beginning. After filtering out documentation-only tickets (HAT-17, HAT-69, HAT-70), **HAT-18** was recommended as the best first implementation ticket to pick up.

The user confirmed and now wants to plan HAT-18's implementation using brainstorming before writing any code.

## Current Project State

- **Repo:** `C:\Users\mrqvp\Documents\Programming\DnDGame`
- **Linear Team:** Hatudoggy (HAT)
- **User:** Mark (c684c9a8-fc1c-4356-886f-55084b6e7ec8)
- **Completed:** HAT-16 (scaffolding)
- **Blocked:** HAT-17 (needs HAT-15, HAT-16, HAT-18 all done)

## Ticket of Focus

### HAT-18: Create minimal OpenCode plugin shell and registration path

- **URL:** https://linear.app/hatudoggy/issue/HAT-18
- **Priority:** Medium
- **Status:** Todo (unstarted), moved from Backlog on 2026-06-10
- **Blocked by:** HAT-16 (Done)
- **Blocks:** HAT-19 (SQLite schema), HAT-20 (migration runner), HAT-23 (tool contracts), HAT-17 (docs)

**Summary:** Create the smallest viable OpenCode plugin for DnDGame. Register a plugin identity and a minimal health/version tool so loading can be verified after restart. Define the custom tool registration pattern that later deterministic tools (dice, validation, SQLite access, gameplay) will use. Must surface clear restart instructions. Must NOT implement dice, validation, SQLite, or gameplay tools.

Full description is in the Linear issue (see URL above). Do not duplicate here.

### Key Constraints from PRD and Plans

- **PRD:** `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md`
- **Architecture:** `docs/architecture/ARCHITECTURE.md`
- **Initial plan:** `docs/plans/initial-plan.md`
- **Plugin reference:** `docs/brainstorms/2026-06-09-opencode-plugins.md` — describes OpenCode plugin loading (`.opencode/plugins/`, `opencode.json`, npm packages), hook events (`tool.execute.before`, `tool.execute.after`, `shell.env`, custom `tool`), and the `Plugin` type from `@opencode-ai/plugin`.
- **Agent behavior contracts:** `docs/specifications/agents-behaviour/AGENTS-BEHAVIOUR.md`
- **Development guidelines:** `docs/guidelines/GUIDELINES.md`

## What the Next Agent Should Do

1. **Load the brainstorming skill** to work through HAT-18's implementation approach with the user.
2. **Review the current repo state** — run `git status` and `git diff` to understand the existing scaffold (HAT-16 output).
3. **Read the plugin brainstorm doc** at `docs/brainstorms/2026-06-09-opencode-plugins.md` for OpenCode plugin conventions.
4. **Plan HAT-18 implementation** covering:
   - Where the plugin file lives (`.opencode/plugins/` vs `opencode.json` declaration vs npm package)
   - The minimal entry point and plugin function signature
   - Registration of a `health` or `version` verification tool
   - The tool registration pattern for downstream tickets
   - How to verify the plugin loaded (the manual/automated verification path)
   - Restart guidance for the user
   - Must NOT overlap with HAT-19 (SQLite), HAT-23 (tool contracts), HAT-24 (dice), or HAT-25 (state mutation).
5. **Capture the brainstorm output** using the `capture-brainstorm` skill to `docs/brainstorms/`.
6. **Do not write implementation code yet** — this session is planning only.

## Suggested Skills

The next agent should invoke these skills in order:

| Order | Skill | Purpose |
|-------|-------|---------|
| 1 | `brainstorming` | Explore HAT-18 implementation approach, design decisions, and tradeoffs |
| 2 | `capture-brainstorm` | Save the brainstorm output to `docs/brainstorms/` |
| 3 | `writing-plans` | (Optional) If the brainstorm calls for a formal plan before implementation |

## Artifacts to Reference (Do Not Duplicate)

| Artifact | Path/URL |
|----------|----------|
| HAT-18 issue | https://linear.app/hatudoggy/issue/HAT-18 |
| PRD | `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md` |
| Architecture docs | `docs/architecture/ARCHITECTURE.md` |
| Initial plan | `docs/plans/initial-plan.md` |
| OpenCode plugins brainstorm | `docs/brainstorms/2026-06-09-opencode-plugins.md` |
| Agent behaviour spec | `docs/specifications/agents-behaviour/AGENTS-BEHAVIOUR.md` |
| Development guidelines | `docs/guidelines/GUIDELINES.md` |
| Project specs | `docs/specifications/project-specs/PROJECT-SPECS.md` |
| HAT-16 (Done, scaffolding) | https://linear.app/hatudoggy/issue/HAT-16 |
| HAT-15 (Setup flow, parallel work) | https://linear.app/hatudoggy/issue/HAT-15 |
| HAT-17 (Docs, blocked) | https://linear.app/hatudoggy/issue/HAT-17 |

## Dependency Graph (Relevant Subset)

```
HAT-16 [DONE]
  ├── HAT-15 (setup flow) [Todo]
  │     └── HAT-17 [Todo]
  └── HAT-18 (plugin shell) [Todo] ← FOCUS
        ├── HAT-19 (SQLite schema) [Todo]
        ├── HAT-20 (migration runner) [Todo]
        ├── HAT-23 (tool contracts) [Todo]
        └── HAT-17 [Todo]
```
