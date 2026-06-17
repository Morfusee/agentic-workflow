# HAT-21 Nine-Table Access Layer Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the missing HAT-21 domain access APIs over the current 9-table SQLite schema without adding migrations or new tables.

**Architecture:** Keep `weapons`, `enemies`, `items`, `spells`, `npcs`, `scenes`, `events`, `actions`, and `consequences` as the only persistence tables. Add focused domain modules under `code/.opencode/plugins/dnd-game/db/access/` that persist structured JSON with stable discriminators and return explicit access-layer objects. Expand `check-database.ts` as the integration verification script for all HAT-21 domains, hidden/player-safe separation, and grouped transaction rollback.

**Tech Stack:** Bun, `bun:sqlite`, Drizzle ORM, TypeScript modules, existing `bun run check:db` verification script.

---

## File Structure

- Create `code/.opencode/plugins/dnd-game/db/access/types.ts`: shared JSON row types, access result shapes, assertions, and player-safe sanitization helpers.
- Create `code/.opencode/plugins/dnd-game/db/access/campaigns.ts`: campaign records and campaign settings stored in `events` JSON rows.
- Create `code/.opencode/plugins/dnd-game/db/access/characters.ts`: character records in `npcs`, character resources in `consequences`.
- Create `code/.opencode/plugins/dnd-game/db/access/rules.ts`: rules config stored in `events`.
- Create `code/.opencode/plugins/dnd-game/db/access/world.ts`: hidden world records and player-safe location APIs stored in `scenes`.
- Create `code/.opencode/plugins/dnd-game/db/access/dungeons.ts`: dungeon and room records in `scenes`, room connections in `consequences`.
- Create `code/.opencode/plugins/dnd-game/db/access/dice-rolls.ts`: dice roll records in `events`.
- Create `code/.opencode/plugins/dnd-game/db/access/inventory.ts`: inventory items in `items`, currency balances in `consequences`.
- Create `code/.opencode/plugins/dnd-game/db/access/reputation.ts`: reputation records in `consequences`.
- Create `code/.opencode/plugins/dnd-game/db/access/combat.ts`: combat encounters in `events`, initiative entries in `consequences`.
- Create `code/.opencode/plugins/dnd-game/db/access/quests.ts`: quests and objectives in `events`.
- Create `code/.opencode/plugins/dnd-game/db/access/session-logs.ts`: session logs and recaps in `events`.
- Modify `code/.opencode/plugins/dnd-game/db/access/transactions.ts`: keep `withTransaction`, add grouped event/action/state helper.
- Modify `code/.opencode/plugins/dnd-game/db/access/index.ts`: export all new modules.
- Modify `code/.opencode/check-database.ts`: add integration checks for all new modules.

## Task 1: Shared Access Types And Helpers

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/access/types.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Test: `code/.opencode/check-database.ts`

- [ ] **Step 1: Add failing verification import**

Modify `code/.opencode/check-database.ts` imports to include the not-yet-created helper exports:

```ts
import {
  assertNonNegative,
  requireKnownStatus,
  stripHiddenFields,
} from "./plugins/dnd-game/db/access/types"
```

Add this verification block after `verifyActionsColumns(databasePath)`:

```ts
  const sanitized = stripHiddenFields({
    name: "Visible Room",
    secret: "Hidden lever",
    hiddenExits: ["north"],
    description: "A stone chamber.",
  })
  if ("secret" in sanitized || "hiddenExits" in sanitized || sanitized.description !== "A stone chamber.") {
    throw new Error("stripHiddenFields failed to remove hidden data")
  }
  assertNonNegative("gold", 0)
  requireKnownStatus("campaign", "active", ["setup", "active", "paused"])
```

- [ ] **Step 2: Run verification and confirm failure**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL with an import/module error for `./plugins/dnd-game/db/access/types`.

- [ ] **Step 3: Implement shared helpers**

Create `code/.opencode/plugins/dnd-game/db/access/types.ts`:

```ts
import type { JsonValue } from "../schema"

export type JsonObject = Record<string, JsonValue>

export type JsonRow<T extends JsonObject = JsonObject> = {
  id: string
  data: T
}

export type AccessResult<T> = {
  ok: true
  value: T
}

export function assertNonNegative(field: string, value: number): void {
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`${field} must be a non-negative number`)
  }
}

export function requireKnownStatus(domain: string, status: string, allowed: readonly string[]): void {
  if (!allowed.includes(status)) {
    throw new Error(`${domain} status '${status}' is not supported`)
  }
}

export function requireFound<T>(domain: string, id: string, value: T | null | undefined): T {
  if (!value) throw new Error(`${domain} '${id}' not found`)
  return value
}

export function stripHiddenFields<T extends Record<string, unknown>>(data: T): Record<string, unknown> {
  const hiddenKeys = new Set([
    "secret",
    "secrets",
    "hidden",
    "hiddenExits",
    "hiddenConsequences",
    "dc",
    "dcs",
    "futureHooks",
    "runtimeDiscoveries",
    "unrevealedNpcMotives",
  ])
  return Object.fromEntries(Object.entries(data).filter(([key]) => !hiddenKeys.has(key)))
}
```

- [ ] **Step 4: Export shared helpers**

Modify `code/.opencode/plugins/dnd-game/db/access/index.ts`:

```ts
export * from "./types"
export * from "./reference"
export * from "./scenes"
export * from "./events"
export * from "./consequences"
export { withTransaction } from "./transactions"
```

- [ ] **Step 5: Run verification and confirm pass**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS with `Database auto-create and access layer check passed with 9 tables`.

- [ ] **Step 6: Commit**

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access/types.ts code/.opencode/plugins/dnd-game/db/access/index.ts
git commit -m "feat(db): add shared access layer helpers"
```

## Task 2: Campaigns, Characters, And Rules

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/access/campaigns.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/characters.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/rules.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Modify: `code/.opencode/check-database.ts`

- [ ] **Step 1: Add failing verification for campaign, character, and rules APIs**

Add imports to `code/.opencode/check-database.ts`:

```ts
import {
  createCampaign,
  getCampaign,
  updateCampaignSettings,
  getCampaignSettings,
} from "./plugins/dnd-game/db/access/campaigns"
import {
  createCharacter,
  getCharacter,
  updateCharacterResource,
  adjustCharacterResource,
  getCharacterResource,
} from "./plugins/dnd-game/db/access/characters"
import {
  setRulesConfig,
  getRulesConfig,
  updateRulesMode,
} from "./plugins/dnd-game/db/access/rules"
```

Add this verification block after the shared helper checks:

```ts
  const campaign = createCampaign(firstRun.db, {
    id: "camp-001",
    title: "Greenvale Trouble",
    status: "active",
  })
  if (campaign.title !== "Greenvale Trouble" || getCampaign(firstRun.db, "camp-001")?.status !== "active") {
    throw new Error("campaign create/read failed")
  }

  updateCampaignSettings(firstRun.db, "camp-001", { tone: "heroic", difficulty: "standard" })
  const campaignSettings = getCampaignSettings(firstRun.db, "camp-001")
  if (!campaignSettings || campaignSettings.tone !== "heroic") throw new Error("campaign settings update/read failed")

  const character = createCharacter(firstRun.db, {
    id: "char-001",
    campaignId: "camp-001",
    name: "Mira",
    kind: "player",
    status: "active",
  })
  if (character.name !== "Mira" || getCharacter(firstRun.db, "char-001")?.kind !== "player") {
    throw new Error("character create/read failed")
  }

  updateCharacterResource(firstRun.db, "char-001", "hp", 10, 12)
  adjustCharacterResource(firstRun.db, "char-001", "hp", -3)
  const hp = getCharacterResource(firstRun.db, "char-001", "hp")
  if (!hp || hp.currentValue !== 7 || hp.maxValue !== 12) throw new Error("character resource update failed")

  setRulesConfig(firstRun.db, "camp-001", { rulesMode: "strict", variantEncumbrance: false })
  updateRulesMode(firstRun.db, "camp-001", "loose")
  const rules = getRulesConfig(firstRun.db, "camp-001")
  if (!rules || rules.rulesMode !== "loose") throw new Error("rules config update/read failed")
```

- [ ] **Step 2: Run verification and confirm failure**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL with missing module errors for `campaigns`, `characters`, or `rules`.

- [ ] **Step 3: Implement `campaigns.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/campaigns.ts` with these exports:

```ts
import { eq } from "drizzle-orm"

import type { GameDatabase } from "../connection"
import { events } from "../schema"
import type { JsonValue } from "../schema"
import { requireFound, requireKnownStatus } from "./types"

const CAMPAIGN_STATUSES = ["setup", "active", "paused", "completed", "abandoned"] as const

export type CampaignRecord = {
  id: string
  title: string
  status: string
  settings?: Record<string, unknown>
}

export function createCampaign(db: GameDatabase, input: { id: string; title: string; status: string }): CampaignRecord {
  requireKnownStatus("campaign", input.status, CAMPAIGN_STATUSES)
  db.insert(events).values({
    id: input.id,
    data: { domain: "campaign", kind: "campaign", title: input.title, status: input.status } as unknown as JsonValue,
  }).run()
  return requireFound("campaign", input.id, getCampaign(db, input.id))
}

export function getCampaign(db: GameDatabase, id: string): CampaignRecord | null {
  const row = db.select().from(events).where(eq(events.id, id)).get() as { id: string; data: JsonValue } | undefined
  if (!row) return null
  const data = row.data as Record<string, unknown>
  if (data.domain !== "campaign" || data.kind !== "campaign") return null
  return { id: row.id, title: String(data.title), status: String(data.status), settings: data.settings as Record<string, unknown> | undefined }
}

export function updateCampaignSettings(db: GameDatabase, campaignId: string, settings: Record<string, unknown>): CampaignRecord {
  const campaign = requireFound("campaign", campaignId, getCampaign(db, campaignId))
  db.update(events).set({
    data: { domain: "campaign", kind: "campaign", title: campaign.title, status: campaign.status, settings } as unknown as JsonValue,
  }).where(eq(events.id, campaignId)).run()
  return requireFound("campaign", campaignId, getCampaign(db, campaignId))
}

export function getCampaignSettings(db: GameDatabase, campaignId: string): Record<string, unknown> | null {
  return getCampaign(db, campaignId)?.settings ?? null
}
```

- [ ] **Step 4: Implement `characters.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/characters.ts` with these exports:

```ts
import { eq } from "drizzle-orm"

import type { GameDatabase } from "../connection"
import { consequences, npcs } from "../schema"
import type { JsonValue } from "../schema"
import { assertNonNegative, requireFound, requireKnownStatus } from "./types"

const CHARACTER_KINDS = ["player", "companion", "npc"] as const
const CHARACTER_STATUSES = ["draft", "active", "inactive", "dead", "retired"] as const

export type CharacterRecord = { id: string; campaignId: string; name: string; kind: string; status: string }
export type CharacterResourceRecord = { id: string; characterId: string; resourceType: string; currentValue: number; maxValue: number }

export function createCharacter(db: GameDatabase, input: CharacterRecord): CharacterRecord {
  requireKnownStatus("character kind", input.kind, CHARACTER_KINDS)
  requireKnownStatus("character", input.status, CHARACTER_STATUSES)
  db.insert(npcs).values({ id: input.id, data: { domain: "character", ...input } as unknown as JsonValue }).run()
  return requireFound("character", input.id, getCharacter(db, input.id))
}

export function getCharacter(db: GameDatabase, id: string): CharacterRecord | null {
  const row = db.select().from(npcs).where(eq(npcs.id, id)).get() as { id: string; data: JsonValue } | undefined
  if (!row) return null
  const data = row.data as Record<string, unknown>
  if (data.domain !== "character") return null
  return { id: row.id, campaignId: String(data.campaignId), name: String(data.name), kind: String(data.kind), status: String(data.status) }
}

export function updateCharacterResource(db: GameDatabase, characterId: string, resourceType: string, currentValue: number, maxValue: number): CharacterResourceRecord {
  requireFound("character", characterId, getCharacter(db, characterId))
  assertNonNegative("currentValue", currentValue)
  assertNonNegative("maxValue", maxValue)
  const id = `resource-${characterId}-${resourceType}`
  db.insert(consequences).values({
    id,
    type: "character-resource",
    status: "active",
    trigger: characterId,
    target: characterId,
    data: { resourceType, currentValue, maxValue } as unknown as JsonValue,
  }).onConflictDoUpdate({ target: consequences.id, set: { data: { resourceType, currentValue, maxValue } as unknown as JsonValue } }).run()
  return requireFound("character resource", id, getCharacterResource(db, characterId, resourceType))
}

export function adjustCharacterResource(db: GameDatabase, characterId: string, resourceType: string, delta: number): CharacterResourceRecord {
  const current = requireFound("character resource", `${characterId}:${resourceType}`, getCharacterResource(db, characterId, resourceType))
  return updateCharacterResource(db, characterId, resourceType, current.currentValue + delta, current.maxValue)
}

export function getCharacterResource(db: GameDatabase, characterId: string, resourceType: string): CharacterResourceRecord | null {
  const id = `resource-${characterId}-${resourceType}`
  const row = db.select().from(consequences).where(eq(consequences.id, id)).get() as { id: string; target: string; data: JsonValue } | undefined
  if (!row) return null
  const data = row.data as Record<string, unknown>
  return { id: row.id, characterId: row.target, resourceType: String(data.resourceType), currentValue: Number(data.currentValue), maxValue: Number(data.maxValue) }
}
```

- [ ] **Step 5: Implement `rules.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/rules.ts` with these exports:

```ts
import { eq } from "drizzle-orm"

import type { GameDatabase } from "../connection"
import { events } from "../schema"
import type { JsonValue } from "../schema"
import { requireFound, requireKnownStatus } from "./types"

const RULES_MODES = ["strict", "loose"] as const

export type RulesConfig = { campaignId: string; rulesMode: string; variantEncumbrance?: boolean }

export function setRulesConfig(db: GameDatabase, campaignId: string, input: { rulesMode: string; variantEncumbrance?: boolean }): RulesConfig {
  requireKnownStatus("rules mode", input.rulesMode, RULES_MODES)
  const id = `rules-${campaignId}`
  db.insert(events).values({
    id,
    data: { domain: "rules", kind: "config", campaignId, ...input } as unknown as JsonValue,
  }).onConflictDoUpdate({ target: events.id, set: { data: { domain: "rules", kind: "config", campaignId, ...input } as unknown as JsonValue } }).run()
  return requireFound("rules config", id, getRulesConfig(db, campaignId))
}

export function getRulesConfig(db: GameDatabase, campaignId: string): RulesConfig | null {
  const row = db.select().from(events).where(eq(events.id, `rules-${campaignId}`)).get() as { data: JsonValue } | undefined
  if (!row) return null
  const data = row.data as Record<string, unknown>
  if (data.domain !== "rules" || data.kind !== "config") return null
  return { campaignId: String(data.campaignId), rulesMode: String(data.rulesMode), variantEncumbrance: Boolean(data.variantEncumbrance) }
}

export function updateRulesMode(db: GameDatabase, campaignId: string, rulesMode: string): RulesConfig {
  const current = requireFound("rules config", campaignId, getRulesConfig(db, campaignId))
  return setRulesConfig(db, campaignId, { ...current, rulesMode })
}
```

- [ ] **Step 6: Export modules**

Append to `code/.opencode/plugins/dnd-game/db/access/index.ts`:

```ts
export * from "./campaigns"
export * from "./characters"
export * from "./rules"
```

- [ ] **Step 7: Run verification and confirm pass**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access/campaigns.ts code/.opencode/plugins/dnd-game/db/access/characters.ts code/.opencode/plugins/dnd-game/db/access/rules.ts code/.opencode/plugins/dnd-game/db/access/index.ts
git commit -m "feat(db): add campaign character and rules access"
```

## Task 3: World And Dungeon APIs With Hidden/Player-Safe Separation

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/access/world.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/dungeons.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Modify: `code/.opencode/check-database.ts`

- [ ] **Step 1: Add failing verification for hidden world and dungeon APIs**

Add imports to `code/.opencode/check-database.ts`:

```ts
import {
  createHiddenWorldRecord,
  getHiddenWorldRecord,
  createLocation,
  getPlayerSafeLocation,
} from "./plugins/dnd-game/db/access/world"
import {
  createDungeon,
  createDungeonRoom,
  connectDungeonRooms,
  getDungeonRooms,
  getPlayerSafeDungeonRoom,
} from "./plugins/dnd-game/db/access/dungeons"
```

Add this verification block after the campaign/character/rules checks:

```ts
  createHiddenWorldRecord(firstRun.db, "hidden-001", "camp-001", "npc-motives", { secret: "Greta is scared of the mayor" })
  const hiddenWorld = getHiddenWorldRecord(firstRun.db, "hidden-001")
  if (!hiddenWorld || hiddenWorld.scope !== "npc-motives") throw new Error("hidden world create/read failed")

  createLocation(firstRun.db, "loc-001", "camp-001", "Greenvale Inn", "heartland", {
    description: "A warm inn.",
    secret: "A smuggler tunnel is below the cellar.",
    hiddenExits: ["cellar"],
  })
  const safeLocation = getPlayerSafeLocation(firstRun.db, "loc-001")
  if (!safeLocation || "secret" in safeLocation.data || "hiddenExits" in safeLocation.data) {
    throw new Error("player-safe location leaked hidden fields")
  }

  createDungeon(firstRun.db, "dun-001", "camp-001", "Old Barrow", "active")
  createDungeonRoom(firstRun.db, "room-001", "dun-001", "entry", "Entry Hall", { description: "Dusty steps.", hiddenExits: ["crypt"] })
  createDungeonRoom(firstRun.db, "room-002", "dun-001", "crypt", "Crypt", { description: "Cold stone." })
  connectDungeonRooms(firstRun.db, "conn-001", "dun-001", "room-001", "room-002", "door", "known")
  if (getDungeonRooms(firstRun.db, "dun-001").length !== 2) throw new Error("dungeon room query failed")
  const safeRoom = getPlayerSafeDungeonRoom(firstRun.db, "room-001")
  if (!safeRoom || "hiddenExits" in safeRoom.data) throw new Error("player-safe dungeon room leaked hidden fields")
```

- [ ] **Step 2: Run verification and confirm failure**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL with missing module errors for `world` or `dungeons`.

- [ ] **Step 3: Implement `world.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/world.ts` with domain-specific functions for hidden state and locations. Use `scenes` rows and `stripHiddenFields` from `types.ts`. Functions to export:

```ts
export type HiddenWorldRecord = { id: string; campaignId: string; scope: string; data: Record<string, unknown> }
export type LocationRecord = { id: string; campaignId: string; name: string; region: string; data: Record<string, unknown> }
export function createHiddenWorldRecord(db: GameDatabase, id: string, campaignId: string, scope: string, data: Record<string, unknown>): HiddenWorldRecord
export function getHiddenWorldRecord(db: GameDatabase, id: string): HiddenWorldRecord | null
export function createLocation(db: GameDatabase, id: string, campaignId: string, name: string, region: string, data: Record<string, unknown>): LocationRecord
export function getPlayerSafeLocation(db: GameDatabase, id: string): LocationRecord | null
```

Implementation requirements:

- `createHiddenWorldRecord` inserts into `scenes` with `domain: "hidden-world"`, `visibility: "hidden"`, `campaignId`, `scope`, and `data`.
- `getHiddenWorldRecord` returns hidden records only when the row has `domain: "hidden-world"`.
- `createLocation` inserts into `scenes` with `domain: "location"`, `visibility: "hidden"`, `campaignId`, `name`, `region`, and `data`.
- `getPlayerSafeLocation` returns location data with `stripHiddenFields` applied.

- [ ] **Step 4: Implement `dungeons.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/dungeons.ts` with dungeon, room, and connection functions. Functions to export:

```ts
export type DungeonRecord = { id: string; campaignId: string; name: string; status: string }
export type DungeonRoomRecord = { id: string; dungeonId: string; roomKey: string; name: string; data: Record<string, unknown> }
export function createDungeon(db: GameDatabase, id: string, campaignId: string, name: string, status: string): DungeonRecord
export function createDungeonRoom(db: GameDatabase, id: string, dungeonId: string, roomKey: string, name: string, data: Record<string, unknown>): DungeonRoomRecord
export function connectDungeonRooms(db: GameDatabase, id: string, dungeonId: string, fromRoomId: string, toRoomId: string, connectionType: string, status: string): void
export function getDungeonRooms(db: GameDatabase, dungeonId: string): DungeonRoomRecord[]
export function getPlayerSafeDungeonRoom(db: GameDatabase, roomId: string): DungeonRoomRecord | null
```

Implementation requirements:

- `createDungeon` uses `scenes` with `domain: "dungeon"`.
- `createDungeonRoom` requires the dungeon to exist and uses `scenes` with `domain: "dungeon-room"`.
- `connectDungeonRooms` requires both rooms to exist and have the same `dungeonId`, then inserts a `consequences` row with `type: "room-connection"`.
- `getPlayerSafeDungeonRoom` applies `stripHiddenFields` to room data.

- [ ] **Step 5: Export modules**

Append to `code/.opencode/plugins/dnd-game/db/access/index.ts`:

```ts
export * from "./world"
export * from "./dungeons"
```

- [ ] **Step 6: Run verification and confirm pass**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access/world.ts code/.opencode/plugins/dnd-game/db/access/dungeons.ts code/.opencode/plugins/dnd-game/db/access/index.ts
git commit -m "feat(db): add world and dungeon access"
```

## Task 4: Dice, Inventory, Currency, And Reputation

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/access/dice-rolls.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/inventory.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/reputation.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Modify: `code/.opencode/check-database.ts`

- [ ] **Step 1: Add failing verification for dice, inventory, currency, and reputation APIs**

Add imports to `code/.opencode/check-database.ts`:

```ts
import { recordDiceRoll, getDiceRoll, getDiceRollsForAction } from "./plugins/dnd-game/db/access/dice-rolls"
import { addInventoryItem, getInventory, setCurrency, adjustCurrency, getCurrency } from "./plugins/dnd-game/db/access/inventory"
import { setReputation, adjustReputation, getReputation } from "./plugins/dnd-game/db/access/reputation"
```

Add this verification block after the world/dungeon checks:

```ts
  recordDiceRoll(firstRun.db, {
    id: "roll-001",
    campaignId: "camp-001",
    eventId: "ev-001",
    actionId: "act-001",
    notation: "1d20+3",
    rolls: [12],
    modifier: 3,
    total: 15,
    purpose: "persuasion",
  })
  if (getDiceRoll(firstRun.db, "roll-001")?.total !== 15 || getDiceRollsForAction(firstRun.db, "act-001").length !== 1) {
    throw new Error("dice roll record/read failed")
  }

  addInventoryItem(firstRun.db, "inv-001", "camp-001", "character", "char-001", "it-potion", 2)
  if (getInventory(firstRun.db, "character", "char-001").length !== 1) throw new Error("inventory add/query failed")

  setCurrency(firstRun.db, "camp-001", "character", "char-001", { copper: 0, silver: 5, gold: 10, platinum: 0 })
  adjustCurrency(firstRun.db, "camp-001", "character", "char-001", { gold: -3, silver: 2 })
  const currency = getCurrency(firstRun.db, "camp-001", "character", "char-001")
  if (!currency || currency.gold !== 7 || currency.silver !== 7) throw new Error("currency set/adjust failed")

  setReputation(firstRun.db, "rep-001", "camp-001", "character", "char-001", "npc", "npc-greta", 5, "known")
  adjustReputation(firstRun.db, "rep-001", 2)
  if (getReputation(firstRun.db, "rep-001")?.score !== 7) throw new Error("reputation set/adjust failed")
```

- [ ] **Step 2: Run verification and confirm failure**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL with missing module errors for `dice-rolls`, `inventory`, or `reputation`.

- [ ] **Step 3: Implement `dice-rolls.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/dice-rolls.ts`. Store dice rolls in `events` rows with `domain: "dice-roll"`. Export:

```ts
export type DiceRollRecord = { id: string; campaignId: string; eventId?: string; actionId?: string; notation: string; rolls: number[]; modifier: number; total: number; purpose: string }
export function recordDiceRoll(db: GameDatabase, input: DiceRollRecord): DiceRollRecord
export function getDiceRoll(db: GameDatabase, id: string): DiceRollRecord | null
export function getDiceRollsForAction(db: GameDatabase, actionId: string): DiceRollRecord[]
```

Implementation requirements:

- Use `events` for inserts and reads.
- `getDiceRollsForAction` can scan `events` and filter `data.domain === "dice-roll" && data.actionId === actionId`, matching existing code style.
- Validate `total` and each roll are finite numbers.

- [ ] **Step 4: Implement `inventory.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/inventory.ts`. Store inventory item records in `items`; store currency balances in `consequences`. Export:

```ts
export type InventoryItemRecord = { id: string; campaignId: string; ownerType: string; ownerId: string; itemId: string; quantity: number }
export type CurrencyBalance = { id: string; campaignId: string; ownerType: string; ownerId: string; copper: number; silver: number; gold: number; platinum: number }
export function addInventoryItem(db: GameDatabase, id: string, campaignId: string, ownerType: string, ownerId: string, itemId: string, quantity: number): InventoryItemRecord
export function getInventory(db: GameDatabase, ownerType: string, ownerId: string): InventoryItemRecord[]
export function setCurrency(db: GameDatabase, campaignId: string, ownerType: string, ownerId: string, balance: { copper?: number; silver?: number; gold?: number; platinum?: number }): CurrencyBalance
export function adjustCurrency(db: GameDatabase, campaignId: string, ownerType: string, ownerId: string, delta: { copper?: number; silver?: number; gold?: number; platinum?: number }): CurrencyBalance
export function getCurrency(db: GameDatabase, campaignId: string, ownerType: string, ownerId: string): CurrencyBalance | null
```

Implementation requirements:

- `addInventoryItem` rejects quantities below `1`.
- `setCurrency` and `adjustCurrency` reject negative final balances.
- Currency row ID must be deterministic: `currency-${campaignId}-${ownerType}-${ownerId}`.

- [ ] **Step 5: Implement `reputation.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/reputation.ts`. Store records in `consequences` with `type: "reputation"`. Export:

```ts
export type ReputationRecord = { id: string; campaignId: string; subjectType: string; subjectId: string; targetType: string; targetId: string; score: number; status: string }
export function setReputation(db: GameDatabase, id: string, campaignId: string, subjectType: string, subjectId: string, targetType: string, targetId: string, score: number, status: string): ReputationRecord
export function adjustReputation(db: GameDatabase, id: string, delta: number): ReputationRecord
export function getReputation(db: GameDatabase, id: string): ReputationRecord | null
```

Implementation requirements:

- `setReputation` uses `trigger` for `subjectId` and `target` for `targetId`.
- `adjustReputation` must throw if the reputation record does not exist.

- [ ] **Step 6: Export modules**

Append to `code/.opencode/plugins/dnd-game/db/access/index.ts`:

```ts
export * from "./dice-rolls"
export * from "./inventory"
export * from "./reputation"
```

- [ ] **Step 7: Run verification and confirm pass**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access/dice-rolls.ts code/.opencode/plugins/dnd-game/db/access/inventory.ts code/.opencode/plugins/dnd-game/db/access/reputation.ts code/.opencode/plugins/dnd-game/db/access/index.ts
git commit -m "feat(db): add dice inventory and reputation access"
```

## Task 5: Combat, Quests, Session Logs, And Grouped Transactions

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/access/combat.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/quests.ts`
- Create: `code/.opencode/plugins/dnd-game/db/access/session-logs.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/transactions.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Modify: `code/.opencode/check-database.ts`

- [ ] **Step 1: Add failing verification for combat, quests, session logs, and grouped transactions**

Add imports to `code/.opencode/check-database.ts`:

```ts
import { createCombatEncounter, addInitiativeEntry, getInitiativeOrder, advanceCombatRound } from "./plugins/dnd-game/db/access/combat"
import { createQuest, addQuestObjective, completeQuestObjective, getQuest } from "./plugins/dnd-game/db/access/quests"
import { appendSessionLog, getSessionLogs, saveSessionRecap, getLatestSessionRecap } from "./plugins/dnd-game/db/access/session-logs"
import { recordActionEventAndStateChange } from "./plugins/dnd-game/db/access/transactions"
```

Add this verification block after the dice/inventory/reputation checks and before the existing generic rollback check:

```ts
  createCombatEncounter(firstRun.db, "combat-001", "camp-001", "ev-001", "active")
  addInitiativeEntry(firstRun.db, "init-001", "combat-001", "char-001", 18, 1, "active")
  addInitiativeEntry(firstRun.db, "init-002", "combat-001", "goblin-001", 12, 2, "active")
  if (getInitiativeOrder(firstRun.db, "combat-001")[0]?.combatantId !== "char-001") throw new Error("initiative order failed")
  if (advanceCombatRound(firstRun.db, "combat-001").roundNumber !== 2) throw new Error("combat round advance failed")

  createQuest(firstRun.db, "quest-001", "camp-001", "Find the Shipment", "in_progress")
  addQuestObjective(firstRun.db, "quest-001", "obj-001", "Ask Greta about the shipment")
  completeQuestObjective(firstRun.db, "quest-001", "obj-001")
  const quest = getQuest(firstRun.db, "quest-001")
  if (!quest || quest.objectives[0]?.status !== "completed") throw new Error("quest objective completion failed")

  appendSessionLog(firstRun.db, "session-001", "camp-001", "active", { summary: "Started in Greenvale." })
  if (getSessionLogs(firstRun.db, "camp-001").length !== 1) throw new Error("session log append/query failed")
  saveSessionRecap(firstRun.db, "recap-001", "camp-001", "session-001", "Greta mentioned a missing shipment.")
  if (getLatestSessionRecap(firstRun.db, "camp-001")?.body !== "Greta mentioned a missing shipment.") throw new Error("session recap save/read failed")

  try {
    recordActionEventAndStateChange(firstRun.db, {
      eventId: "ev-rollback",
      eventType: "test",
      actionId: "act-rollback",
      input: "force rollback",
      output: "rollback",
      consequenceId: "con-rollback",
      consequenceType: "test",
      consequenceTarget: "target-rollback",
      failAfterAction: true,
    })
  } catch {
    // expected
  }
  if (getEvent(firstRun.db, "ev-rollback") || getAction(firstRun.db, "act-rollback") || getConsequence(firstRun.db, "con-rollback")) {
    throw new Error("grouped transaction rollback leaked writes")
  }
```

- [ ] **Step 2: Run verification and confirm failure**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL with missing module/function errors.

- [ ] **Step 3: Implement `combat.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/combat.ts`. Store encounters in `events`; initiative entries in `consequences`. Export:

```ts
export type CombatEncounterRecord = { id: string; campaignId: string; eventId: string; status: string; roundNumber: number }
export type InitiativeEntryRecord = { id: string; encounterId: string; combatantId: string; initiative: number; turnOrder: number; status: string }
export function createCombatEncounter(db: GameDatabase, id: string, campaignId: string, eventId: string, status: string): CombatEncounterRecord
export function addInitiativeEntry(db: GameDatabase, id: string, encounterId: string, combatantId: string, initiative: number, turnOrder: number, status: string): InitiativeEntryRecord
export function getInitiativeOrder(db: GameDatabase, encounterId: string): InitiativeEntryRecord[]
export function advanceCombatRound(db: GameDatabase, encounterId: string): CombatEncounterRecord
```

Implementation requirements:

- Combat statuses are `setup`, `active`, `resolved`, `escaped`, `abandoned`.
- Initiative statuses are `active`, `defeated`, `fled`, `removed`.
- `getInitiativeOrder` returns entries sorted by `turnOrder` ascending.
- `advanceCombatRound` increments `roundNumber` by `1`.

- [ ] **Step 4: Implement `quests.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/quests.ts`. Store quest and objectives in `events`. Export:

```ts
export type QuestObjective = { id: string; description: string; status: string }
export type QuestRecord = { id: string; campaignId: string; title: string; status: string; objectives: QuestObjective[] }
export function createQuest(db: GameDatabase, id: string, campaignId: string, title: string, status: string): QuestRecord
export function addQuestObjective(db: GameDatabase, questId: string, objectiveId: string, description: string): QuestRecord
export function completeQuestObjective(db: GameDatabase, questId: string, objectiveId: string): QuestRecord
export function getQuest(db: GameDatabase, id: string): QuestRecord | null
```

Implementation requirements:

- Quest statuses are `open`, `in_progress`, `completed`, `failed`, `abandoned`.
- Objective statuses are `open`, `completed`.
- Completing a missing objective throws `quest objective '<id>' not found`.

- [ ] **Step 5: Implement `session-logs.ts`**

Create `code/.opencode/plugins/dnd-game/db/access/session-logs.ts`. Store logs and recaps in `events`. Export:

```ts
export type SessionLogRecord = { id: string; campaignId: string; status: string; data: Record<string, unknown> }
export type SessionRecapRecord = { id: string; campaignId: string; sessionLogId: string; body: string }
export function appendSessionLog(db: GameDatabase, id: string, campaignId: string, status: string, data: Record<string, unknown>): SessionLogRecord
export function getSessionLogs(db: GameDatabase, campaignId: string): SessionLogRecord[]
export function saveSessionRecap(db: GameDatabase, id: string, campaignId: string, sessionLogId: string, body: string): SessionRecapRecord
export function getLatestSessionRecap(db: GameDatabase, campaignId: string): SessionRecapRecord | null
```

Implementation requirements:

- Session statuses are `active`, `closed`, `abandoned`.
- `saveSessionRecap` requires the session log to exist.
- `getLatestSessionRecap` may scan rows and return the last matching recap by insertion order in this v0 implementation.

- [ ] **Step 6: Extend `transactions.ts`**

Modify `code/.opencode/plugins/dnd-game/db/access/transactions.ts` to keep `withTransaction` and add:

```ts
import { createEvent, logAction } from "./events"
import { addConsequence } from "./consequences"

export type RecordActionEventAndStateChangeInput = {
  eventId: string
  eventType: string
  actionId: string
  input: string
  output: string
  consequenceId: string
  consequenceType: string
  consequenceTarget: string
  failAfterAction?: boolean
}

export function recordActionEventAndStateChange(db: GameDatabase, input: RecordActionEventAndStateChangeInput): void {
  withTransaction(db, (tx) => {
    createEvent(tx, input.eventId, input.eventType)
    logAction(tx, input.actionId, input.input, input.output, { eventId: input.eventId })
    if (input.failAfterAction) throw new Error("forced grouped transaction failure")
    addConsequence(tx, input.consequenceId, input.consequenceType, "pending", input.actionId, input.consequenceTarget)
  })
}
```

- [ ] **Step 7: Export modules and grouped transaction helper**

Append to `code/.opencode/plugins/dnd-game/db/access/index.ts`:

```ts
export * from "./combat"
export * from "./quests"
export * from "./session-logs"
export { withTransaction, recordActionEventAndStateChange } from "./transactions"
```

If `index.ts` already has `export { withTransaction } from "./transactions"`, replace it with the combined export above.

- [ ] **Step 8: Run verification and confirm pass**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access/combat.ts code/.opencode/plugins/dnd-game/db/access/quests.ts code/.opencode/plugins/dnd-game/db/access/session-logs.ts code/.opencode/plugins/dnd-game/db/access/transactions.ts code/.opencode/plugins/dnd-game/db/access/index.ts
git commit -m "feat(db): add combat quest session and grouped transaction access"
```

## Task 6: Final Requirements Review And Cleanup

**Files:**
- Modify: `code/.opencode/check-database.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/access/index.ts`
- Review: all files under `code/.opencode/plugins/dnd-game/db/access/`

- [ ] **Step 1: Run full verification**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS.

- [ ] **Step 2: Confirm all HAT-21 domains are represented**

Run from repository root:

```bash
git grep -n "createCampaign\|createCharacter\|setRulesConfig\|createHiddenWorldRecord\|createDungeon\|recordDiceRoll\|addInventoryItem\|setReputation\|createCombatEncounter\|createQuest\|appendSessionLog" -- code/.opencode/plugins/dnd-game/db/access code/.opencode/check-database.ts
```

Expected: output includes definitions in access modules and verification usage in `check-database.ts`.

- [ ] **Step 3: Confirm no schema expansion occurred**

Run from repository root:

```bash
git diff master...HEAD -- code/.opencode/plugins/dnd-game/db/schema.ts code/.opencode/plugins/dnd-game/db/connection.ts
```

Expected: no new table definitions beyond the existing 9-table schema. Existing branch changes from HAT-20/HAT-21 may still be visible; do not remove them.

- [ ] **Step 4: Confirm no direct file writes from access modules**

Run from repository root:

```bash
git grep -n "writeFile\|appendFile\|mkdir\|rmSync\|createWriteStream" -- code/.opencode/plugins/dnd-game/db/access
```

Expected: no matches.

- [ ] **Step 5: Inspect final diff**

Run from repository root:

```bash
git diff master...HEAD --stat
git diff master...HEAD -- code/.opencode/plugins/dnd-game/db/access code/.opencode/check-database.ts
```

Expected: changes are limited to access modules and verification script, with no unrelated rewrites.

- [ ] **Step 6: Commit final cleanup if needed**

If Task 6 required any code or verification cleanup, commit it:

```bash
git add code/.opencode/check-database.ts code/.opencode/plugins/dnd-game/db/access
git commit -m "test(db): verify HAT-21 access layer coverage"
```

If Task 6 made no changes, do not create an empty commit.

## Self-Review

- Spec coverage: the plan covers every HAT-21 domain listed in the approved nine-table correction design: campaigns/settings, characters/resources, rules, hidden world/locations, dungeons/rooms/connections, events/actions, dice rolls, inventory/currency, reputation, combat/initiative, quests, session logs/recaps, and transactions.
- Placeholder scan: the plan contains no `TBD`, unfinished sections, or deferred requirements.
- Type consistency: function names used in verification steps match the function names assigned to module exports in the implementation steps.
- Scope check: the plan preserves the 9-table schema and does not add migrations or new database tables.
