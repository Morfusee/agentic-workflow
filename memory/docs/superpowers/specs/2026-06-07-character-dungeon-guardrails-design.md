# Character & Dungeon Guardrails Design

**Date:** 2026-06-07
**Status:** draft
**Project:** DnDGame — multiplayer agent-driven D&D
**Related:** [plans/initial-plan.md](../../../../../../Documents/Programming/DnDGame/docs/plans/initial-plan.md)

## Purpose

Prevent players and agents from creating characters or dungeons that break the game's premise — while still allowing creative, complex, "cheesy" builds. The guardrail system uses a hybrid approach: structural constraints enforced by the server (deterministic), plus AI content evaluation by a validator agent (flexible).

## Core Principles

A valid character must exhibit at least one of:
1. **A resource limit** — mana, stamina, cooldowns, uses-per-rest, HP pool
2. **A failure condition** — a reachable state where the character is vulnerable or stops functioning
3. **A meaningful tradeoff** — strong in one area, weak in another

A valid dungeon must exhibit:
1. **Spatial coherence** — rooms connect logically; exits and paths make sense
2. **Solvability** — a path exists to completion with the tools available to the party
3. **Thematic integrity** — fits the campaign's established tone, world rules, and genre

## File Placement

```
docs/
└── specifications/
    ├── agents-behaviour/
    │   └── validator.md                # NEW: guardrail enforcer agent specification
    └── game-design/
        ├── character-creation.md        # existing (planned)
        ├── character-guardrails.md      # NEW: structural + AI rules for characters
        ├── dungeon-design.md            # NEW: dungeon creation specification
        └── dungeon-guardrails.md        # NEW: structural + AI rules for dungeons
```

## Character Guardrails

### Structural Layer (Server-Enforced)

The server rejects any character sheet missing these fields:

| Field | Type | Description |
|-------|------|-------------|
| `resources[]` | array, min 1 | Each resource has `type`, `max`, `current`, `regen_rate`, `regen_interval` |
| `failure_conditions[]` | array, min 1 | States where the character becomes vulnerable (HP=0, mana depleted, burnout, binding vow broken) |
| `tradeoffs[]` | array, min 1 | Explicit weakness paired to each significant strength |

**Structural check is deterministic** — missing fields = hard reject with message pointing to the missing field.

### AI Validation Layer (Validator Agent)

The validator agent evaluates each field against three principles:

| Principle | Check | Pass Example | Fail Example |
|-----------|-------|-------------|--------------|
| **Meaningfulness** | Is the resource genuinely constrained? | `max: 100, regen: 5/turn` | `max: 999999, regen: 999999/turn` |
| **Believability** | Is the failure condition reachable? | "If mana depletes, burnout triggers" | "Failure if the universe ends" |
| **Proportionality** | Does the tradeoff balance the strength? | "Untouchable BUT damage reduced 50%, mana efficiency halved" | "Untouchable BUT lose 1 HP per hour" |

**AI evaluation outcomes:**
- **PASS** — character enters game state
- **WARN** — borderline case, flagged for the leader player's manual review
- **FAIL** — hard reject with specific reasoning and a suggestion to fix

## Dungeon Guardrails

### Structural Layer (Server-Enforced)

The server rejects any dungeon definition missing these fields:

| Field | Type | Description |
|-------|------|-------------|
| `entrance` | string\|object | How players enter (location reference or narrative trigger) |
| `completion_condition` | string | What ends the dungeon (boss defeated, artifact retrieved, escape) |
| `rooms[]` | array, min 2 | Room definitions with `id`, `name`, `description`, `connections[]` |
| `theme_tag` | string | Must match the campaign seed's declared tone/world rules |

**Connectivity check:** The server verifies at least one navigable path exists from entrance room to completion condition. Orphaned rooms (no connections) are rejected.

### AI Validation Layer (Validator Agent)

| Principle | Check | Pass Example | Fail Example |
|-----------|-------|-------------|--------------|
| **Solvability** | Can the party complete the dungeon at their level? | DC 15 lockpicking with a level 3 rogue | "Door requires a level 99 wizard to open" |
| **Spatial coherence** | Do rooms make sense as a connected space? | Cave → tunnel → goblin warren → chieftain's chamber | "The door opens to the surface of the sun" |
| **Thematic integrity** | Does it fit the campaign's setting? | Medieval fantasy dungeon with traps and monsters | "Control center with holographic displays" in a goblin cave |

## Validation Pipeline

```
Player/Agent submits character or dungeon
         │
         ▼
  ┌─ STRUCTURAL CHECK (server) ──┐
  │ Required fields present?     │
  │ Min array lengths met?       │
  │ Dungeon: theme tag matches?  │
  │ Dungeon: path exists?        │
  └──────────────────────────────┘
         │
    ┌────┴────┐
    │ PASS    │ FAIL ──▶ reject with specific missing-field message
    └────┬────┘
         ▼
  ┌─ AI VALIDATION (validator agent) ──┐
  │ Character: meaningful/believable/  │
  │            proportional?           │
  │ Dungeon: solvable/coherent/        │
  │          thematic?                 │
  └────────────────────────────────────┘
         │
    ┌────┼────┐
    │    │    │
   PASS WARN FAIL
    │    │    │
    ▼    ▼    ▼
  Enter  Flag   Reject +
  game   for    reasoning +
  state  human  suggestion
         review to fix
```

## Integration with Existing Plan

Hooks into [initial-plan.md](../../../../../../Documents/Programming/DnDGame/docs/plans/initial-plan.md):

- **Step 0** (Game Setup): Theme tag is declared in campaign seed. Sets the baseline for thematic integrity checks.
- **Step 1** (Character Creation): Validation pipeline runs after player submits character sheet. Reject/flag before character enters `game/state.json`.
- **Step 3** (Gameplay): Dungeon design (whether DM-generated or discovered) passes through validation pipeline before being added to active game state.

## v0 Scope

- Ship with the structural layer fully implemented in the server
- The validator agent (`validator.md`) is defined as a specification, with the AI validation layer implementable as a follow-up
- In v0, the structural layer alone catches the most egregious submissions; AI validation can be added incrementally
