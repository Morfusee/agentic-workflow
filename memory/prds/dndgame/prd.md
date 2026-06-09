# DnDGame PRD

## Summary

DnDGame is a local OpenCode-powered Dungeons & Dragons game runner. The first release should let a player set up a campaign, create or load characters, run a text-first session through OpenCode agents, and persist game state in SQLite through a local OpenCode plugin.

The product combines three pieces: OpenCode agents for DM and player behavior, deterministic plugin tools for state and dice operations, and a simplified D&D 5e rules layer for fair resolution. The v0 target is local play. VPS-hosted multiplayer is a later milestone.

## Goals

- Ship a playable local v0 that runs inside an OpenCode project.
- Provide setup automation for required agents, skills, rules files, campaign files, and SQLite database state.
- Let a player define a campaign theme, character sheet, and optional rules overrides before play starts.
- Persist campaign, character, world, event, action, inventory, reputation, combat, and session state outside easily-spoiled player-facing text.
- Use deterministic plugin tools for dice rolls, validation, state reads, state writes, and game-log updates.
- Keep D&D resolution transparent by having the server or plugin roll dice and expose the mechanical result.
- Support the main gameplay modes: exploration, combat, social interaction, downtime, and exploration skill challenges.
- Enforce v0 structural guardrails for character sheets and dungeons before they enter active game state.
- Produce session continuation material so a campaign can resume cleanly after a break.

## Non-Goals

- v0 does not need VPS-hosted multiplayer or real-time coordination across separate PCs.
- v0 does not need a full TUI or graphical map renderer.
- v0 does not need a complete D&D 5e rules engine.
- v0 does not need support for every class, spell, monster, item, feat, race, or published sourcebook.
- v0 does not need a full ruleset editor or clean-slate custom rulebook builder.
- v0 does not need post-v0 AI semantic validation for character or dungeon quality.
- v0 does not need hidden background simulation where events happen in real time without player interaction.

## Users And Use Cases

Primary user:

- A player who wants to play a mechanics-driven D&D-style game through OpenCode without needing deep D&D rules knowledge.

Secondary users:

- A future group leader who starts a shared campaign for multiple players.
- A future player who controls one character through a player agent on another machine.

Use cases:

- Create a new OpenCode project and install the DnDGame plugin, agents, skills, rules references, and database.
- Generate or manually write campaign setup files such as `CHARACTER.md`, `THEME.md`, `MAP.md`, and `RULES.md`.
- Start a campaign from a campaign seed with tone, premise, main quest, opening hook, and initial scene.
- Take natural-language actions and have the DM agent resolve them using checks, dice, resources, and game state.
- Move through exploration, combat, social, and downtime scenes without losing state.
- Save a session and resume from a recap and persisted state.

## Scope

### v0 scope

- OpenCode plugin loaded from project or config plugin paths.
- Bun-compatible plugin code that can register custom tools and hooks.
- SQLite database creation and migration for local game state.
- Agent and skill setup for DM, player, and validation behavior.
- Simplified rules reference based on D&D 5e levels 1 through 5.
- One fixed simplified ruleset with a `rules_mode: strict | loose` flag.
- Character setup with structural validation for resources, failure conditions, and tradeoffs.
- Campaign setup with theme, tone, premise, main quest, opening hook, and optional map/rules inputs.
- Dungeon setup with graph-based room validation.
- Event and action tracking.
- Transparent dice rolling for d20 checks, attacks, saving throws, initiative, damage, random encounters, and percentile tables.
- Core gameplay mode support for exploration, combat, social, and downtime.
- Skill challenge support as an exploration sub-state.
- Rest mechanics for short and long rests.
- Session logging, recap generation, and continuation state.

### Later scope

- VPS-hosted HTTP or MCP server for multiplayer.
- Cross-machine player agents.
- TUI panels and state-specific UI.
- AI semantic validation for meaning, believability, proportionality, solvability, spatial coherence, and thematic integrity.
- Ruleset templates, add/remove rule modules, and full homebrew ruleset authoring.
- Broader spell, class, item, monster, and campaign content libraries.

## Requirements

### Project setup

- The system must install or generate the required OpenCode plugin, agents, skills, rules files, and database scaffolding.
- The setup flow must tell the user when OpenCode needs to restart so new plugin, agent, or skill files are loaded.
- The plugin must expose tool calls for deterministic game functions instead of asking agents to mutate files or state directly.
- The generated project structure should separate player-facing content, hidden game state, rules references, and agent behavior instructions.

### Plugin and persistence

- The backend must run as an OpenCode plugin in a Bun-compatible process.
- The plugin must create and use a local SQLite database for durable state.
- The plugin must expose tools for state lookup, state mutation, dice rolling, validation, event logging, action logging, and session recap storage.
- State that would spoil unrevealed content, including hidden map details, traps, NPC secrets, and future encounters, must not be written into player-facing Markdown.
- The database must preserve enough history for the DM agent to account for earlier actions when generating later consequences.

### Game setup

- The player must be able to provide campaign theme and character inputs manually through files or through agent-assisted generation.
- The system must support optional `MAP.md` and `RULES.md` inputs.
- The DM setup process must generate campaign content from the accepted theme and rules, including world map details, town/NPC/shop seeds, spells or class options, and starting scenario data.
- Generated hidden content must be persisted in SQLite rather than placed entirely in player-readable files.

### Ruleset

- v0 must use one simplified D&D 5e ruleset covering character levels 1 through 5.
- v0 must support `rules_mode: strict | loose`.
- Strict mode should follow the simplified rules reference unless no rule applies.
- Loose mode should let the DM agent adjudicate plausible creative actions using the closest mechanic and a reasonable DC.
- The rules reference must cover d20 checks, ability modifiers, proficiency, skills, advantage/disadvantage, initiative, action economy, attacks, damage, critical hits, saving throws, death saves, rests, and common dice notation.

### Dice and probability

- Dice rolls must be handled by plugin tools, not silently invented by the DM agent.
- The system must support d4, d6, d8, d10, d12, d20, and d100.
- The system must support expressions such as `XdN + M` and keep-highest or keep-lowest where required by character generation or rules.
- Roll results must include the raw die result, modifiers, final total, target DC or AC when applicable, and pass/fail outcome.
- Player-visible rolls should be broadcast or logged openly. Hidden rolls may exist for cases such as enemy stealth or NPC deception, but the PRD treats them as optional and must not block v0.

### Character creation and validation

- Character sheets must include resources, failure conditions, and tradeoffs.
- Each resource must include `type`, `max`, `current`, `regen_rate`, and `regen_interval`.
- Each failure condition must include `trigger`, `effect`, and `recovery`.
- Each tradeoff must include `strength` and `weakness`.
- Missing required character fields must cause a hard rejection with a clear message naming the missing field.
- The server-side structural validator must run before a character enters active game state.
- Post-v0 AI validation may evaluate meaningfulness, believability, and proportionality, but v0 only requires structural validation.

### Dungeon creation and validation

- Dungeons must be represented as connected room graphs.
- Every dungeon must include an entrance, completion condition, at least two rooms, and a theme tag.
- Each room must include `id`, `name`, `description`, `entrance`, `completion`, and `connections`.
- Exactly one room should be treated as the entrance room in v0.
- At least one room must be a completion room.
- No room may be orphaned.
- A valid path must exist from the entrance room to every completion room.
- Dungeon theme must match the campaign seed theme tag.
- Invalid dungeons must be rejected with the reason and a fix suggestion.

### Gameplay loop

- The game must support setup, character creation, session beginning, gameplay, and session wrap-up.
- The DM agent must introduce the setting and immediate premise before the main loop starts.
- The main loop must process events and actions.
- An event is a meaningful location, scene, encounter, or stateful situation.
- An action is a player prompt that changes game progression or state.
- Prompts that ask for help, clarification, recap, rules explanation, or out-of-game utility should not be logged as in-game actions.
- The DM agent must account for influential prior actions when generating later reactions, reputation shifts, NPC hostility, and pseudo-emergent consequences.

### Gameplay modes

- Exploration mode must allow free-form player actions, DM narration, travel, dungeon movement, searching, hazards, random encounters, passive checks, and skill challenges.
- Combat mode must enforce initiative order, rounds, turns, action economy, monster turns, player turns, reactions, death saves, escape, surrender, and combat end conditions.
- Social mode must support NPC dialogue, NPC attitudes, persuasion, deception, intimidation, insight, reputation, and attitude shifts.
- Downtime mode must support shopping, crafting, training, research, repairing, resting, spell preparation where applicable, and other low-pressure activities.
- Skill challenges must live inside exploration as a sub-state with required successes before a failure threshold.

### Turn and state management

- Combat must lock mechanical actions to the current initiative actor.
- Exploration, social, and downtime may accept free-form actions without strict initiative.
- The DM agent may interrupt non-combat play when a trap, encounter, environmental change, passive discovery, or NPC reaction occurs.
- Combat reactions must be trigger-based and limited to one reaction per round.
- The server/plugin must track mode transitions such as exploration to combat, combat to exploration, exploration to downtime, downtime to exploration, and any mode into or out of social dialogue.
- The DM agent must declare mode changes through explicit state updates.

### Combat mechanics

- Combat starts when the DM declares an encounter and initiative is rolled for every creature.
- Initiative must use `d20 + DEX modifier`, sorted from highest to lowest.
- Each creature turn must support one action, movement, one bonus action when granted by a feature or spell, and one reaction per round when triggered.
- Player actions must be resolved through attack rolls, saving throws, ability checks, spell effects, or DM adjudication using the closest supported mechanic.
- Combat must end when enemies or players are defeated, enemies flee, enemies surrender, the party escapes, or aggression is otherwise resolved.
- v0 should include a small supported set of common combat actions: attack, cast supported spell, dash, disengage, dodge, help, hide, ready, search, use object, grapple, shove, and opportunity attack.

### Skills, spells, martial actions, and resources

- The rules layer must include the 18 D&D skills and their default ability associations.
- Character state must track proficiency bonus, proficient skills, expertise or special modifiers where supported, and passive scores where needed.
- v0 should cap spell support at level 5 characters and spells up to level 3.
- v0 should include a small curated spell list rather than a full spell compendium.
- Spellcasting state must track ability, save DC, spell attack bonus, slots, cantrips, known spells, prepared status where applicable, and concentration.
- Martial resource state must support common class resources such as Action Surge, Second Wind, Rage, Ki, Sneak Attack, Divine Smite slots, and Lay on Hands where those classes are included in v0.
- Resting must reset or recover resources according to short-rest and long-rest rules.

### Inventory, economy, reputation, and progression

- Inventory must track items, equipment, spells or abilities where applicable, and consumables.
- Currency must support copper, silver, gold, and platinum at minimum.
- Shops must support buying and selling common gear and consumables.
- Reputation must track player standing with individual NPCs, towns, or factions when actions affect them.
- Progression may use XP or milestone leveling, but v0 should prefer milestone leveling unless later tickets choose XP explicitly.

### Session continuity

- The system must save current state at session end.
- The DM agent must produce a recap or continuation document from the session log and current state.
- Resuming a session must reload campaign state, current scene, active quests, character state, and unresolved consequences.

## User Experience Notes

- The experience is text-first inside OpenCode.
- The user should not need to know D&D rules to play; agents should explain requested rolls and outcomes briefly when needed.
- The DM agent should be directive during early setup and the first session, then more reactive as the player gains context.
- The DM should not block plausible creative actions just because no exact rule exists. In loose mode, it should find the closest mechanic, set a DC, roll through the plugin, and narrate the outcome.
- Dice transparency matters. Players should see enough mechanics to trust the result.
- Hidden information should stay hidden until discovered.

## Data, API, And Integration Notes

- OpenCode plugin loading follows OpenCode plugin conventions: local project plugins in `.opencode/plugins/`, global plugins in the user config plugin directory, and package plugins declared in `opencode.json`.
- The plugin should use OpenCode plugin hooks and custom tool definitions for game operations.
- SQLite is the v0 state store.
- The schema should model campaigns, characters, resources, rules configuration, locations, dungeons, rooms, connections, events, actions, dice rolls, inventory, reputation, combat encounters, initiative order, quests, session logs, and recaps.
- Tools should return structured results that agents can cite in narration without needing direct database access.
- Later VPS multiplayer can reuse the same domain model through an HTTP or MCP service, but that must not complicate v0 unless a ticket explicitly starts that milestone.

## Non-Functional Requirements

- Local setup must be repeatable from a clean project checkout.
- Database operations must be deterministic and auditable through logs.
- Tool responses must be explicit enough for agents to avoid inventing state.
- Hidden state must not leak into player-facing files or summaries.
- Validation errors must be understandable and fixable by a non-expert player.
- The implementation should favor small, testable modules over broad agent-only behavior.
- v0 should work without network access after dependencies are installed.
- The codebase should keep project specs, game design specs, and agent behavior specs separate.

## Dependencies

- OpenCode plugin API and custom tool support.
- Bun runtime for plugin execution.
- SQLite library or driver compatible with the chosen plugin implementation.
- Agent files for DM, player, and validator roles.
- D&D rules references derived from the project docs.
- Project setup files such as `opencode.json`, `.opencode/agents`, `.opencode/skills`, `rules/`, `characters/`, and game state storage.

## Risks And Mitigations

- Scope creep from full D&D 5e coverage: keep v0 capped to simplified levels 1 through 5 and a curated set of classes, spells, items, and actions.
- Conflict between local v0 and older VPS multiplayer plans: treat local OpenCode plugin plus SQLite as authoritative for v0; defer VPS multiplayer.
- Agent hallucination of state or rolls: require agents to call plugin tools for state mutation and dice rolls.
- Hidden content leakage: store secrets in SQLite and expose only discovered information through player-facing tools.
- Ambiguous rule adjudication: support strict and loose modes, and require the DM to cite the closest mechanic when using loose mode.
- Validation becoming too subjective: make v0 structural validation deterministic and defer AI judgment.
- Combat complexity delaying playability: start with common actions, transparent turns, and a small content library.

## Acceptance Criteria

- A clean project can run setup and produce required plugin, agent, skill, rules, campaign, and database scaffolding.
- OpenCode can load the DnDGame plugin after restart.
- The plugin can create and open the SQLite database.
- The plugin exposes deterministic tools for dice rolling, validation, state read/write, event logging, and action logging.
- A valid character sheet passes structural validation and enters game state.
- An invalid character sheet is rejected with a field-specific error.
- A valid dungeon graph passes structural validation and enters game state.
- An invalid dungeon graph is rejected with a reason and fix suggestion.
- A player can start a campaign from theme and character inputs.
- The DM agent can introduce a session and create the first scene.
- Player actions that affect game progression are logged as actions.
- Utility prompts are not logged as in-game actions.
- The system can roll and report d20 checks, initiative, attacks, damage, saving throws, and death saves.
- Exploration, combat, social, and downtime modes can be represented in state and transitioned explicitly.
- Combat enforces initiative order and one current actor at a time.
- Rest mechanics recover health and resources according to short-rest or long-rest rules.
- Session end saves state and produces a continuation recap.

## Ticket Generation Guidance

Create tickets in ordered subphases. Phase 2 must ask the user where tickets should be created before publishing any tickets.

Recommended development subphases:

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

Each ticket should include implementation requirements, dependencies, definition of done, verification notes, and a link back to this PRD.

## Open Questions

- Which PMS should Phase 2 use for ticket creation: Linear, ClickUp, Notion, or another destination?
- Which classes, spells, items, and enemies are in the first playable content slice?
- Should v0 expose hidden rolls, support hidden rolls only for DM-only cases, or defer hidden rolls entirely?
- Should v0 use milestone leveling only, or include XP tracking in the first release?
- Which SQLite schema migration approach should the implementation use?

## Source Documents

- `docs/plans/initial-plan.md`
- `docs/plans/archived/initial-plan.md`
- `docs/brainstorms/2026-06-09-opencode-plugins.md`
- `docs/brainstorms/2026-06-09-dnd-dice-probability-system.md`
- `docs/brainstorms/2026-06-06-initial-plan-review.md`
- `docs/brainstorms/2026-06-05-dnd-agent-game-architecture.md`
- `docs/brainstorms/2026-06-05-dnd-core-mechanics.md`
- `docs/brainstorms/2026-06-05-dnd-maps-goals-sessions.md`
- `docs/brainstorms/2026-06-05-dnd-three-pillars.md`
- `docs/brainstorms/2026-06-05-dnd-turns.md`
- `docs/brainstorms/2026-06-05-dnd-skills-spells-martial.md`
- `docs/specifications/game-design/dungeon-design.md`
- `docs/specifications/game-design/dungeon-guardrails.md`
- `docs/specifications/game-design/character-guardrails.md`
- `docs/specifications/agents-behaviour/validator.md`
