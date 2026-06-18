# DnDGame Phase 2 Subphase 04 Handoff

- Suggested skill: `$prd-to-ticket-planner`
- PMS destination: Linear
- PMS location: Team `Hatudoggy`; no project
- PRD path: `$HOME\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md`
- Ticket index path: `$HOME\Documents\Programming\agentic-workflow\memory\prds\dndgame\ticket-index.md`
- Current subphase: 04, Rules reference and simplified v0 rules configuration

## Current Subphase Outcome

Created Linear tickets for the simplified DnDGame v0 rules reference, persisted `rules_mode: strict | loose` configuration, the Starter Core playable content catalogs, and rules lookup/validation integration with deterministic plugin tool flows. The first playable content slice decision was resolved as Starter Core: Fighter, Rogue, Cleric, Wizard; curated cantrips and level 1 through 3 spells; common starter gear and consumables; and goblins, bandits, wolves, skeletons, zombies, giant rats, and guards.

## Provider Ticket References

- HAT-28: https://linear.app/hatudoggy/issue/HAT-28/implement-rules-mode-configuration-for-strict-and-loose-adjudication
- HAT-29: https://linear.app/hatudoggy/issue/HAT-29/define-simplified-dndgame-v0-rules-reference-structure
- HAT-30: https://linear.app/hatudoggy/issue/HAT-30/create-starter-core-content-catalogs-for-v0-rules-support
- HAT-31: https://linear.app/hatudoggy/issue/HAT-31/wire-rules-reference-into-deterministic-tool-and-validation-flows

## Next Subphase

- Next subphase: 05, Character creation, character validation, and character state
- Objective: Implement character setup inputs, structural validation for required resources/failure conditions/tradeoffs, and persisted active character state that can use the Starter Core class, spell, resource, and rules references from Subphase 04.
- Dependencies: Subphase 02 SQLite schema and state access layer, Subphase 03 deterministic validation/state tools, and Subphase 04 rules reference, rules mode configuration, and Starter Core catalogs.
- Decision needed: None currently identified from the PRD or current handoff.

## Next Chat Instruction

Start a fresh chat and invoke `$prd-to-ticket-planner` with this handoff path to continue subphase 05 ticket creation.
