# DnDGame Phase 2 Subphase 10 Handoff

- Suggested skill: `$prd-to-ticket-planner`
- PMS destination: Linear
- PMS location: Team `Hatudoggy`; no project
- PRD path: `$HOME\Documents\Programming\agentic-workflow\memory\prds\dndgame\prd.md`
- Ticket index path: `$HOME\Documents\Programming\agentic-workflow\memory\prds\dndgame\ticket-index.md`
- Current subphase: 10, Exploration, social, downtime, skill challenges, rests, inventory, economy, and reputation

## Current Subphase Outcome

Created Linear tickets for non-combat gameplay state contracts, exploration actions and skill challenge resolution, social interactions and reputation updates, downtime activities and rest recovery, inventory/currency/shop transactions, and non-combat gameplay plugin tools with verification coverage. The subphase preserves v0 constraints that exploration/social/downtime play remains free-form outside combat initiative, mechanical outcomes use deterministic plugin tooling, meaningful actions and state changes are durably logged, rests recover resources through simplified rules, inventory and economy mutations are validated, reputation remains durable across future consequences, and hidden state remains outside player-facing Markdown.

## Provider Ticket References

- HAT-55: https://linear.app/hatudoggy/issue/HAT-55/define-non-combat-gameplay-state-contracts
- HAT-56: https://linear.app/hatudoggy/issue/HAT-56/implement-exploration-actions-and-skill-challenge-resolution
- HAT-58: https://linear.app/hatudoggy/issue/HAT-58/implement-social-interactions-and-reputation-updates
- HAT-59: https://linear.app/hatudoggy/issue/HAT-59/implement-downtime-activities-and-rest-recovery
- HAT-57: https://linear.app/hatudoggy/issue/HAT-57/implement-inventory-currency-shops-and-transactions
- HAT-60: https://linear.app/hatudoggy/issue/HAT-60/expose-non-combat-gameplay-plugin-tools-and-verification-coverage

## Next Subphase

- Next subphase: 11, DM, player, and validator agent prompts and supporting skills
- Objective: Implement the OpenCode DM, player, and validator agent prompts and supporting skills so agents use deterministic plugin tools, respect hidden-state boundaries, enforce validation and setup guardrails, and guide the player through v0 gameplay without direct state mutation.
- Dependencies: Subphase 01 project scaffolding and OpenCode plugin setup, Subphase 03 deterministic plugin tools, Subphase 04 simplified v0 rules configuration, Subphase 05 character validation/state, Subphase 06 campaign setup/session start, Subphase 07 dungeon validation, Subphase 08 gameplay mode/action logging, Subphase 09 combat systems, and Subphase 10 non-combat gameplay systems.
- Decision needed: None currently identified from the PRD or current handoff.

## Next Chat Instruction

Start a fresh chat and invoke `$prd-to-ticket-planner` with this handoff path to continue subphase 11 ticket creation.
