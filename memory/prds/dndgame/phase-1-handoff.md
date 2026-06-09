# DnDGame Phase 1 Handoff

- Suggested skill: `$prd-to-ticket-planner`
- Current phase completed: Phase 1, requirements to PRD
- Next phase: Phase 2 setup
- Project slug: `dndgame`
- PRD path: `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md`
- Artifact folder: `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame`

## Resolved decisions

- v0 targets the newer local OpenCode plugin plus SQLite architecture.
- VPS-hosted multiplayer and cross-machine player coordination are post-v0.
- The v0 backend is an OpenCode plugin running in a Bun-compatible process.
- SQLite is the v0 persistence layer.
- Agents should not invent dice rolls or mutate state directly. They should call deterministic plugin tools.
- v0 uses a simplified D&D 5e ruleset for levels 1 through 5.
- v0 includes a `rules_mode: strict | loose` flag instead of a full ruleset editor.
- Structural character and dungeon validation are in v0.
- AI semantic validation for balance, believability, solvability, and thematic judgment is post-v0.
- The archived VPS HTTP multiplayer plan is supporting context only where it does not conflict with the newer plugin plan.

## Known constraints

- Do not create tickets during Phase 1.
- Ask the user where to create tickets before Phase 2 ticket creation.
- Accepted destinations are Linear, ClickUp, Notion, or another explicit destination with usable tooling or instructions.
- Work on exactly one development subphase per chat thread after Phase 2 begins.
- Save each Phase 2 subphase handoff under this same folder.
- Do not store full ticket bodies in subphase handoffs after ticket creation starts. Store provider ticket IDs or URLs, outcome summary, and next subphase target.

## Remaining open questions for Phase 2

- Which PMS should receive tickets: Linear, ClickUp, Notion, or another destination?
- What project, team, list, database, or equivalent location should tickets be created in?
- Which classes, spells, items, and enemies are in the first playable content slice?
- Should v0 support hidden rolls for DM-only cases, expose all rolls, or defer hidden rolls?
- Should v0 use milestone leveling only, or include XP tracking?
- Which SQLite migration approach should implementation use?

## Suggested Phase 2 subphase list

1. Project scaffolding and OpenCode plugin setup.
2. SQLite schema, migrations, and state access layer.
3. Deterministic tool layer for dice, logs, validation, and state mutation.
4. Rules reference and simplified v0 rules configuration.
5. Character creation, character validation, and character state.
6. Campaign setup, hidden world generation storage, and session start.
7. Dungeon model and dungeon validation.
8. Gameplay mode state machine and event/action logging.
9. Combat loop, initiative, action economy, and reactions.
10. Exploration, social, downtime, skill challenges, rests, inventory, economy, and reputation.
11. DM/player/validator agent prompts and skills.
12. Session recap, continuation, testing, and v0 playtest hardening.

## Next chat instruction

Start Phase 2 setup by loading the PRD and this handoff. Ask the user where tickets should be created before deriving the provider-backed ticket plan or publishing any tickets.
