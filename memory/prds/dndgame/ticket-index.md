# DnDGame Ticket Index

## Source Artifacts

- PRD: `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md`
- Phase 1 handoff: `C:\Users\mrqvp\Documents\Programming\agentic-workflow\memory\prds\dndgame\phase-1-handoff.md`

## PMS Destination

- Provider: Linear
- Location: Team `Hatudoggy`; no project

## Development Phases

| Phase | Status | Objective | Ticket References |
|---|---|---|---|
| 01 | Done | Establish project scaffolding, local OpenCode plugin shell, setup asset layout, and setup verification docs. | [HAT-16](https://linear.app/hatudoggy/issue/HAT-16/scaffold-dndgame-opencode-plugin-project-structure), [HAT-18](https://linear.app/hatudoggy/issue/HAT-18/create-minimal-opencode-plugin-shell-and-registration-path), [HAT-15](https://linear.app/hatudoggy/issue/HAT-15/add-dndgame-setup-flow-for-local-project-assets), [HAT-17](https://linear.app/hatudoggy/issue/HAT-17/document-v0-local-development-and-setup-verification) |
| 02 | Done | Design and implement SQLite schema, migrations, and state access layer for durable local game state. | [HAT-19](https://linear.app/hatudoggy/issue/HAT-19/define-dndgame-sqlite-schema-and-migration-contract), [HAT-20](https://linear.app/hatudoggy/issue/HAT-20/implement-sqlite-migration-runner-and-database-initialization), [HAT-21](https://linear.app/hatudoggy/issue/HAT-21/build-sqlite-state-access-layer-for-dndgame-domain-state), [HAT-22](https://linear.app/hatudoggy/issue/HAT-22/add-persistence-test-fixtures-and-sqlite-verification-coverage) |
| 03 | Done | Add deterministic plugin tools for dice, logs, validation, state lookup, and state mutation. | [HAT-23](https://linear.app/hatudoggy/issue/HAT-23/define-deterministic-dndgame-plugin-tool-contracts), [HAT-24](https://linear.app/hatudoggy/issue/HAT-24/implement-transparent-dice-rolling-plugin-tool), [HAT-25](https://linear.app/hatudoggy/issue/HAT-25/implement-state-lookup-and-state-mutation-plugin-tools), [HAT-26](https://linear.app/hatudoggy/issue/HAT-26/implement-event-action-and-session-log-plugin-tools), [HAT-27](https://linear.app/hatudoggy/issue/HAT-27/implement-validation-entry-point-plugin-tools) |
| 04 | Done | Build simplified v0 rules reference and `rules_mode: strict | loose` configuration. | [HAT-28](https://linear.app/hatudoggy/issue/HAT-28/implement-rules-mode-configuration-for-strict-and-loose-adjudication), [HAT-29](https://linear.app/hatudoggy/issue/HAT-29/define-simplified-dndgame-v0-rules-reference-structure), [HAT-30](https://linear.app/hatudoggy/issue/HAT-30/create-starter-core-content-catalogs-for-v0-rules-support), [HAT-31](https://linear.app/hatudoggy/issue/HAT-31/wire-rules-reference-into-deterministic-tool-and-validation-flows) |
| 05 | Done | Implement character creation, structural validation, and character state persistence. | [HAT-34](https://linear.app/hatudoggy/issue/HAT-34/define-starter-core-character-input-and-state-contracts), [HAT-33](https://linear.app/hatudoggy/issue/HAT-33/implement-deterministic-character-structural-validation), [HAT-32](https://linear.app/hatudoggy/issue/HAT-32/persist-active-character-state-and-gameplay-resources), [HAT-35](https://linear.app/hatudoggy/issue/HAT-35/expose-character-creation-and-activation-plugin-tools) |
| 06 | Done | Implement campaign setup, hidden world generation storage, and session start flow. | [HAT-36](https://linear.app/hatudoggy/issue/HAT-36/define-campaign-setup-input-and-state-contracts), [HAT-37](https://linear.app/hatudoggy/issue/HAT-37/persist-hidden-campaign-world-generation-state), [HAT-38](https://linear.app/hatudoggy/issue/HAT-38/expose-campaign-setup-and-hidden-world-generation-tools), [HAT-39](https://linear.app/hatudoggy/issue/HAT-39/implement-first-session-start-flow) |
| 07 | Done | Implement dungeon graph model and deterministic dungeon validation. | [HAT-40](https://linear.app/hatudoggy/issue/HAT-40/define-dungeon-graph-input-and-state-contracts), [HAT-41](https://linear.app/hatudoggy/issue/HAT-41/implement-deterministic-dungeon-graph-validation), [HAT-42](https://linear.app/hatudoggy/issue/HAT-42/expose-dungeon-setup-and-validation-plugin-tools), [HAT-43](https://linear.app/hatudoggy/issue/HAT-43/persist-dungeon-graph-rooms-and-connections-in-sqlite-state) |
| 08 | Done | Implement gameplay mode state machine and event/action logging. | [HAT-44](https://linear.app/hatudoggy/issue/HAT-44/define-gameplay-mode-state-and-transition-contracts), [HAT-45](https://linear.app/hatudoggy/issue/HAT-45/add-mode-aware-event-and-action-logging-context), [HAT-46](https://linear.app/hatudoggy/issue/HAT-46/implement-meaningful-action-detection-and-utility-prompt-exclusion), [HAT-47](https://linear.app/hatudoggy/issue/HAT-47/implement-durable-gameplay-mode-transition-state-machine), [HAT-48](https://linear.app/hatudoggy/issue/HAT-48/expose-gameplay-mode-and-action-logging-plugin-tools) |
| 09 | Done | Implement combat loop, initiative, action economy, reactions, and combat end handling. | [HAT-49](https://linear.app/hatudoggy/issue/HAT-49/define-combat-encounter-state-and-initiative-contracts), [HAT-50](https://linear.app/hatudoggy/issue/HAT-50/implement-combat-encounter-start-and-initiative-ordering), [HAT-53](https://linear.app/hatudoggy/issue/HAT-53/implement-combat-turn-enforcement-and-action-economy-tracking), [HAT-51](https://linear.app/hatudoggy/issue/HAT-51/implement-supported-v0-combat-actions-reactions-and-death-saves), [HAT-52](https://linear.app/hatudoggy/issue/HAT-52/implement-combat-end-conditions-and-mode-transition-integration), [HAT-54](https://linear.app/hatudoggy/issue/HAT-54/expose-combat-plugin-tools-and-verification-coverage) |
| 10 | Done | Implement exploration, social, downtime, skill challenges, rests, inventory, economy, and reputation. | [HAT-55](https://linear.app/hatudoggy/issue/HAT-55/define-non-combat-gameplay-state-contracts), [HAT-56](https://linear.app/hatudoggy/issue/HAT-56/implement-exploration-actions-and-skill-challenge-resolution), [HAT-58](https://linear.app/hatudoggy/issue/HAT-58/implement-social-interactions-and-reputation-updates), [HAT-59](https://linear.app/hatudoggy/issue/HAT-59/implement-downtime-activities-and-rest-recovery), [HAT-57](https://linear.app/hatudoggy/issue/HAT-57/implement-inventory-currency-shops-and-transactions), [HAT-60](https://linear.app/hatudoggy/issue/HAT-60/expose-non-combat-gameplay-plugin-tools-and-verification-coverage) |
| 11 | Done | Implement DM, player, and validator agent prompts and supporting skills. | [HAT-63](https://linear.app/hatudoggy/issue/HAT-63/define-dndgame-agent-and-skill-behavior-contracts), [HAT-61](https://linear.app/hatudoggy/issue/HAT-61/implement-dm-agent-prompt-for-tool-mediated-v0-gameplay), [HAT-65](https://linear.app/hatudoggy/issue/HAT-65/implement-player-agent-prompt-and-gameplay-support-skills), [HAT-64](https://linear.app/hatudoggy/issue/HAT-64/implement-validator-agent-prompt-for-setup-and-state-guardrails), [HAT-62](https://linear.app/hatudoggy/issue/HAT-62/wire-agent-assets-into-setup-flow-and-add-prompt-verification-coverage) |
| 12 | Done | Implement session recap, continuation, testing, and v0 playtest hardening. | [HAT-66](https://linear.app/hatudoggy/issue/HAT-66/implement-session-end-recap-generation-and-continuation-persistence), [HAT-67](https://linear.app/hatudoggy/issue/HAT-67/implement-campaign-resume-flow-from-continuation-state), [HAT-68](https://linear.app/hatudoggy/issue/HAT-68/add-full-path-setup-to-gameplay-integration-verification), [HAT-69](https://linear.app/hatudoggy/issue/HAT-69/create-v0-playtest-scenario-fixtures-and-hardening-checklist), [HAT-70](https://linear.app/hatudoggy/issue/HAT-70/prepare-v0-release-readiness-docs-and-final-acceptance-sweep) |

## Subphase 01 Tickets

- HAT-16: Scaffold DnDGame OpenCode plugin project structure
- HAT-18: Create minimal OpenCode plugin shell and registration path
- HAT-15: Add DnDGame setup flow for local project assets
- HAT-17: Document v0 local development and setup verification

## Subphase 02 Tickets

- HAT-19: Define DnDGame SQLite schema and migration contract
- HAT-20: Implement SQLite migration runner and database initialization
- HAT-21: Build SQLite state access layer for DnDGame domain state
- HAT-22: Add persistence test fixtures and SQLite verification coverage

## Subphase 03 Tickets

- HAT-23: Define deterministic DnDGame plugin tool contracts
- HAT-24: Implement transparent dice rolling plugin tool
- HAT-25: Implement state lookup and state mutation plugin tools
- HAT-26: Implement event, action, and session log plugin tools
- HAT-27: Implement validation entry point plugin tools

## Subphase 04 Tickets

- HAT-28: Implement rules mode configuration for strict and loose adjudication
- HAT-29: Define simplified DnDGame v0 rules reference structure
- HAT-30: Create Starter Core content catalogs for v0 rules support
- HAT-31: Wire rules reference into deterministic tool and validation flows

## Subphase 05 Tickets

- HAT-34: Define Starter Core character input and state contracts
- HAT-33: Implement deterministic character structural validation
- HAT-32: Persist active character state and gameplay resources
- HAT-35: Expose character creation and activation plugin tools

## Subphase 06 Tickets

- HAT-36: Define campaign setup input and state contracts
- HAT-37: Persist hidden campaign world generation state
- HAT-38: Expose campaign setup and hidden world generation tools
- HAT-39: Implement first session start flow

## Subphase 07 Tickets

- HAT-40: Define dungeon graph input and state contracts
- HAT-41: Implement deterministic dungeon graph validation
- HAT-42: Expose dungeon setup and validation plugin tools
- HAT-43: Persist dungeon graph rooms and connections in SQLite state

## Subphase 08 Tickets

- HAT-44: Define gameplay mode state and transition contracts
- HAT-45: Add mode-aware event and action logging context
- HAT-46: Implement meaningful action detection and utility prompt exclusion
- HAT-47: Implement durable gameplay mode transition state machine
- HAT-48: Expose gameplay mode and action logging plugin tools

## Subphase 09 Tickets

- HAT-49: Define combat encounter state and initiative contracts
- HAT-50: Implement combat encounter start and initiative ordering
- HAT-53: Implement combat turn enforcement and action economy tracking
- HAT-51: Implement supported v0 combat actions, reactions, and death saves
- HAT-52: Implement combat end conditions and mode transition integration
- HAT-54: Expose combat plugin tools and verification coverage

## Subphase 10 Tickets

- HAT-55: Define non-combat gameplay state contracts
- HAT-56: Implement exploration actions and skill challenge resolution
- HAT-58: Implement social interactions and reputation updates
- HAT-59: Implement downtime activities and rest recovery
- HAT-57: Implement inventory, currency, shops, and transactions
- HAT-60: Expose non-combat gameplay plugin tools and verification coverage

## Subphase 11 Tickets

- HAT-63: Define DnDGame agent and skill behavior contracts
- HAT-61: Implement DM agent prompt for tool-mediated v0 gameplay
- HAT-65: Implement player agent prompt and gameplay support skills
- HAT-64: Implement validator agent prompt for setup and state guardrails
- HAT-62: Wire agent assets into setup flow and add prompt verification coverage

## Subphase 12 Tickets

- HAT-66: Implement session-end recap generation and continuation persistence
- HAT-67: Implement campaign resume flow from continuation state
- HAT-68: Add full-path setup-to-gameplay integration verification
- HAT-69: Create v0 playtest scenario fixtures and hardening checklist
- HAT-70: Prepare v0 release readiness docs and final acceptance sweep

## Phase 2 Completion

- Status: Complete
- All 12 planned DnDGame development subphases have provider tickets in Linear.
- Next step: Optional implementation prep or execution support.
