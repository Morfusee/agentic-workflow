# HAT-21 Nine-Table Access Layer Correction Design

## Goal

Bring HAT-21 from partial access-layer coverage to ticket-aligned domain coverage while preserving the current 9-table SQLite schema.

## Context

The current branch implements access helpers for the existing schema tables:

- `weapons`
- `enemies`
- `items`
- `spells`
- `npcs`
- `scenes`
- `events`
- `actions`
- `consequences`

The HAT-21 ticket asks for access modules across broader DnDGame persistence domains. This correction will not expand the schema or add migrations. Instead, it will add domain-specific access modules over the existing tables, using structured JSON discriminators and explicit access functions.

## Non-Goals

- Do not add new SQLite tables.
- Do not change migration behavior.
- Do not replace the existing access modules.
- Do not add generic catch-all state mutation APIs.
- Do not write player-facing files from the state layer.

## Architecture

The correction adds focused modules under `code/.opencode/plugins/dnd-game/db/access/`. Each module owns one persistence domain and exposes narrow operations for that domain. The underlying storage can remain JSON-backed, but consumers should not need to know which table stores each domain record.

New modules:

- `types.ts`: shared access-layer row/result types and JSON helpers.
- `campaigns.ts`: campaign container and campaign settings access.
- `characters.ts`: character records and mutable resources.
- `rules.ts`: active rules config and rules mode access.
- `world.ts`: hidden world state and player-safe location lookup APIs.
- `dungeons.ts`: dungeon records, room records, and room connections.
- `dice-rolls.ts`: transparent dice roll records.
- `inventory.ts`: inventory items and currency balances.
- `reputation.ts`: NPC, faction, and location relationship records.
- `combat.ts`: combat encounters and initiative entries.
- `quests.ts`: quests and objectives.
- `session-logs.ts`: session logs and recaps.

Existing modules remain in place:

- `reference.ts`: reference catalog records.
- `scenes.ts`: generic scene/location helpers.
- `events.ts`: events and player actions.
- `consequences.ts`: consequences and state effects.
- `transactions.ts`: generic and grouped transaction helpers.

## Storage Mapping

The access layer will use stable JSON discriminator fields so domain records can be queried and filtered consistently.

| Domain | Existing Table | Discriminators |
| --- | --- | --- |
| Campaigns | `events` | `domain: "campaign"`, `kind: "campaign"` |
| Campaign settings | `events` | `domain: "campaign"`, `kind: "settings"` |
| Characters | `npcs` | `domain: "character"`, `kind: "player" | "companion" | "npc"` |
| Character resources | `consequences` | `type: "character-resource"`, `target: characterId` |
| Rules config | `events` | `domain: "rules"`, `kind: "config"` |
| Hidden world state | `scenes` | `domain: "hidden-world"`, `visibility: "hidden"` |
| Locations | `scenes` | `domain: "location"`, `visibility: "player-safe" | "hidden"` |
| Dungeons | `scenes` | `domain: "dungeon"` |
| Dungeon rooms | `scenes` | `domain: "dungeon-room"`, `dungeonId` |
| Room connections | `consequences` | `type: "room-connection"`, `target: dungeonId` |
| Dice rolls | `events` | `domain: "dice-roll"`, `actionId`, `eventId` |
| Inventory items | `items` | `domain: "inventory-item"`, `ownerType`, `ownerId` |
| Currency balances | `consequences` | `type: "currency-balance"`, `target: ownerId` |
| Reputation | `consequences` | `type: "reputation"`, `target: targetId` |
| Combat encounters | `events` | `domain: "combat"`, `kind: "encounter"` |
| Initiative entries | `consequences` | `type: "initiative-entry"`, `target: encounterId` |
| Quests | `events` | `domain: "quest"` |
| Quest objectives | nested in quest JSON | `objectives: []` |
| Session logs | `events` | `domain: "session-log"` |
| Session recaps | `events` | `domain: "session-recap"` |

## Access API Rules

- Each module must expose explicit create/read/update operations for its domain.
- Functions should accept typed or otherwise explicit input objects.
- Functions should return stable structured objects suitable for future OpenCode tool responses.
- Missing records should throw deterministic `Error` messages for mutating operations.
- Read operations that are expected to miss may return `null`.
- No module should expose a generic `setState`, `updateRecord`, or `mutateJson` operation to future tool consumers.

## Hidden State Separation

Hidden world state APIs must be separate from player-safe APIs.

Required hidden APIs:

- Create or update hidden world records.
- Read hidden world records by ID or campaign scope.
- Read hidden dungeon or room details when DM/system tools need them.

Required player-safe APIs:

- Read player-safe location data.
- Query player-safe locations by campaign or region.
- Read player-safe dungeon room data.

Player-safe APIs must strip fields that reveal hidden data, including secrets, hidden exits, unrevealed NPC motives, DCs, future hooks, runtime discoveries, and hidden consequences.

## Integrity Checks

The access layer must enforce obvious invariants not guaranteed by the 9-table schema:

- Referenced domain records must exist before dependent records are written.
- Resource values, item quantities, and currency balances must not become negative.
- Status values must be known values for the domain.
- Room connections must reference two rooms in the same dungeon.
- Initiative entries must reference combatants in the encounter.
- Quest objective updates must reference existing objectives.
- Active rules config and active session lookups must be deterministic.
- Player-safe APIs must not return hidden fields.

## Transactions

Keep the existing `withTransaction` helper.

Add one grouped transaction helper that proves the access layer can apply multi-step state changes atomically. The grouped helper should create an event, log a player action, and add at least one state update or consequence. If any write fails, all writes in the group must roll back.

## Verification

Expand `code/.opencode/check-database.ts` as the branch's integration verification script.

The verification script must:

- Create a temporary migrated database through `initializeDatabase`.
- Exercise at least one create/read/update flow for every HAT-21 persistence domain represented by the new modules.
- Confirm hidden world records are available through hidden APIs.
- Confirm hidden fields are not returned by player-safe APIs.
- Confirm grouped transaction rollback removes all writes from a forced failure.
- Continue to verify the existing access-layer behavior for reference records, scenes, events/actions, consequences, and generic transactions.

## Success Criteria

- The schema remains at 9 tables.
- Every HAT-21 listed domain has an explicit access module or explicit domain section.
- Hidden APIs and player-safe APIs are separated.
- Common create/read/update flows are covered for the domain modules.
- Obvious integrity checks exist in the access layer.
- No direct file writes occur from access modules.
- `bun run check:db` passes from `code/.opencode`.

## Self-Review

- Placeholder scan: no placeholder requirements remain.
- Internal consistency: the design consistently targets the current 9-table implementation and excludes schema expansion.
- Scope check: the work is large but focused on one subsystem, the HAT-21 SQLite access layer correction.
- Ambiguity check: the chosen storage strategy is explicit, and player-safe versus hidden APIs are defined separately.
