# HAT-20 SQLite Auto-Create Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the HAT-20 Drizzle/SQLite database layer that auto-creates the 9 required tables on first plugin startup.

**Architecture:** `schema.ts` owns Drizzle table definitions, `connection.ts` owns SQLite/Drizzle initialization and idempotent table creation, `helpers.ts` owns JSON row helpers, and `query.ts` owns generic typed wrappers. The old SQL migration runner is removed so there is one database initialization contract.

**Tech Stack:** Bun, Bun SQLite, Drizzle ORM SQLite core, TypeScript, OpenCode local plugin scripts.

---

## File Structure

- Create: `code/.opencode/plugins/dnd-game/db/schema.ts` — Drizzle table definitions and table registry for all 9 HAT-20 tables.
- Create: `code/.opencode/plugins/dnd-game/db/helpers.ts` — JSON row insert/upsert/find/update/query helpers.
- Create: `code/.opencode/plugins/dnd-game/db/query.ts` — generic typed table query wrapper factory.
- Modify: `code/.opencode/plugins/dnd-game/db/connection.ts` — replace migration execution with SQLite opening, Drizzle handle creation, and programmatic auto-create.
- Modify: `code/.opencode/plugins/dnd-game/db/init.ts` — make the plugin startup import path delegate to the connection initializer.
- Modify: `code/.opencode/setup-database.ts` — call the new initializer and print schema setup results.
- Modify: `code/.opencode/check-database.ts` — replace migration checks with HAT-20 schema/helper checks.
- Modify: `code/.opencode/check-plugin.ts` — ensure the plugin check uses a temp DB path so it does not mutate the developer DB during verification.
- Modify: `code/.opencode/package.json` — add `drizzle-orm` dependency.
- Modify: `code/.opencode/tsconfig.json` — include DB check/setup TypeScript files in type checking if needed.
- Modify: `code/.opencode/README.md` — document auto-create setup and remove migration wording.
- Delete: `code/.opencode/plugins/dnd-game/db/migrate.ts` — obsolete migration runner.
- Delete: `code/.opencode/plugins/dnd-game/db/migration-runner.ts` — duplicate obsolete migration runner.
- Delete: `code/.opencode/plugins/dnd-game/db/migrations/0001_initial_schema.sql` — versioned SQL migration file forbidden by HAT-20.

## Task 1: Add Drizzle Dependency

**Files:**
- Modify: `code/.opencode/package.json`
- Modify: `code/.opencode/bun.lock`
- Modify: `code/.opencode/package-lock.json` if npm lock changes after install

- [ ] **Step 1: Add Drizzle ORM to the nested plugin project**

Run from `code/.opencode`:

```bash
bun add drizzle-orm
```

Expected: `package.json` contains `"drizzle-orm"` under `dependencies`, and `bun.lock` updates.

- [ ] **Step 2: Verify the dependency can be imported**

Run from `code/.opencode`:

```bash
bun -e "import { sqliteTable } from 'drizzle-orm/sqlite-core'; console.log(typeof sqliteTable)"
```

Expected output includes:

```text
function
```

## Task 2: Write Failing Database Verification Checks

**Files:**
- Modify: `code/.opencode/check-database.ts`

- [ ] **Step 1: Replace the migration-oriented check with HAT-20 assertions**

Write `code/.opencode/check-database.ts` with this content:

```ts
import { mkdtempSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { Database } from "bun:sqlite"

import { initializeDatabase } from "./plugins/dnd-game/db/connection"
import { findById, queryByPath, updatePath, upsertJsonRow } from "./plugins/dnd-game/db/helpers"
import { actions, consequences, weapons } from "./plugins/dnd-game/db/schema"

const expectedTables = [
  "weapons",
  "enemies",
  "items",
  "spells",
  "npcs",
  "scenes",
  "events",
  "actions",
  "consequences",
]

const tempDir = mkdtempSync(join(tmpdir(), "dndgame-db-check-"))

try {
  const databasePath = join(tempDir, "game.db")
  const firstRun = initializeDatabase({ databasePath })

  verifyTablesExist(databasePath)
  verifyActionsColumns(databasePath)

  const weaponData = {
    name: "Longsword",
    stats: { damage: "1d8", kind: "slashing" },
    meta: { rarity: "common" },
  }
  upsertJsonRow(firstRun.db, weapons, "weapon-longsword", weaponData)

  const weapon = await findById<typeof weaponData>(firstRun.db, weapons, "weapon-longsword")
  if (!weapon || weapon.data.stats.damage !== "1d8") {
    throw new Error("JSON round-trip failed for weapons")
  }

  updatePath(firstRun.db, weapons, "weapon-longsword", "stats.damage", "1d10")
  const updatedWeapons = await queryByPath<typeof weaponData>(firstRun.db, weapons, "stats.damage", "1d10")
  if (updatedWeapons.length !== 1 || updatedWeapons[0].id !== "weapon-longsword") {
    throw new Error("Nested JSON path query failed for weapons")
  }

  firstRun.db.insert(actions).values({
    id: "action-001",
    input: "I open the door.",
    output: "The door creaks open.",
    data: { sceneId: "scene-001", intent: "explore" },
  }).run()

  firstRun.db.insert(consequences).values({
    id: "consequence-001",
    type: "state-change",
    status: "pending",
    trigger: "action-001",
    target: "door-001",
    data: { description: "Door is now open." },
  }).run()

  const matchingConsequences = firstRun.db
    .select()
    .from(consequences)
    .where((table, { and, eq }) =>
      and(eq(table.type, "state-change"), eq(table.status, "pending"), eq(table.target, "door-001")),
    )
    .all()
  if (matchingConsequences.length !== 1) {
    throw new Error("Consequences filtering by type, status, and target failed")
  }

  firstRun.sqlite.close()

  const secondRun = initializeDatabase({ databasePath })
  secondRun.sqlite.close()

  verifyTablesExist(databasePath)

  console.log(`Database auto-create check passed with ${expectedTables.length} HAT-20 tables`)
} finally {
  rmSync(tempDir, { recursive: true, force: true })
}

function verifyTablesExist(databasePath: string): void {
  const database = new Database(databasePath, { readonly: true })
  const tables = database
    .query("SELECT name FROM sqlite_master WHERE type = 'table'")
    .all()
    .map((row) => (row as { name: string }).name)
  database.close()

  const missingTables = expectedTables.filter((table) => !tables.includes(table))
  if (missingTables.length > 0) {
    throw new Error(`Missing expected tables: ${missingTables.join(", ")}`)
  }
}

function verifyActionsColumns(databasePath: string): void {
  const database = new Database(databasePath, { readonly: true })
  const columns = database
    .query("PRAGMA table_info(actions)")
    .all()
    .map((row) => (row as { name: string }).name)
  database.close()

  for (const column of ["input", "output"]) {
    if (!columns.includes(column)) {
      throw new Error(`actions table is missing ${column} column`)
    }
  }
}
```

- [ ] **Step 2: Run the check to verify it fails before implementation**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL because `helpers.ts` and `schema.ts` do not exist yet.

## Task 3: Add Drizzle Schema

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/schema.ts`

- [ ] **Step 1: Create schema definitions and table registry**

Write `code/.opencode/plugins/dnd-game/db/schema.ts` with this content:

```ts
import { index, sqliteTable, text } from "drizzle-orm/sqlite-core"

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

const jsonText = <TData extends JsonValue>() => text("data", { mode: "json" }).$type<TData>().notNull()

export const weapons = sqliteTable("weapons", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const enemies = sqliteTable("enemies", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const items = sqliteTable("items", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const spells = sqliteTable("spells", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const npcs = sqliteTable("npcs", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const scenes = sqliteTable("scenes", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const events = sqliteTable("events", {
  id: text("id").primaryKey(),
  data: jsonText(),
})

export const actions = sqliteTable("actions", {
  id: text("id").primaryKey(),
  input: text("input").notNull(),
  output: text("output").notNull(),
  data: jsonText(),
})

export const consequences = sqliteTable(
  "consequences",
  {
    id: text("id").primaryKey(),
    type: text("type").notNull(),
    status: text("status").notNull(),
    trigger: text("trigger").notNull(),
    target: text("target").notNull(),
    data: jsonText(),
  },
  (table) => [
    index("idx_consequences_type").on(table.type),
    index("idx_consequences_status").on(table.status),
    index("idx_consequences_target").on(table.target),
  ],
)

export const schema = {
  weapons,
  enemies,
  items,
  spells,
  npcs,
  scenes,
  events,
  actions,
  consequences,
}

export const tableNames = Object.keys(schema)
```

- [ ] **Step 2: Run the check again**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL because helper and connection APIs are not implemented yet.

## Task 4: Implement Connection And Auto-Create

**Files:**
- Modify: `code/.opencode/plugins/dnd-game/db/connection.ts`
- Modify: `code/.opencode/plugins/dnd-game/db/init.ts`
- Modify: `code/.opencode/setup-database.ts`

- [ ] **Step 1: Replace migration initialization with SQLite/Drizzle initialization**

Write `code/.opencode/plugins/dnd-game/db/connection.ts` with this content:

```ts
import { mkdirSync } from "node:fs"
import { dirname } from "node:path"
import { fileURLToPath } from "node:url"
import { Database } from "bun:sqlite"
import { drizzle, type BunSQLiteDatabase } from "drizzle-orm/bun-sqlite"

import { schema, tableNames } from "./schema"

export const DEFAULT_DATABASE_PATH = fileURLToPath(new URL("../../../../.data/game.db", import.meta.url))

export type InitializeDatabaseOptions = {
  databasePath?: string
}

export type InitializeDatabaseResult = {
  databasePath: string
  sqlite: Database
  db: BunSQLiteDatabase<typeof schema>
  tables: string[]
}

export function openGameDatabase(databasePath = DEFAULT_DATABASE_PATH): Database {
  try {
    mkdirSync(dirname(databasePath), { recursive: true })
    const sqlite = new Database(databasePath)
    sqlite.exec("PRAGMA foreign_keys = ON")
    sqlite.exec("PRAGMA journal_mode = WAL")
    return sqlite
  } catch (error) {
    throw new Error(`Failed to open SQLite database at ${databasePath}: ${formatError(error)}`)
  }
}

export function initializeDatabase(options: InitializeDatabaseOptions = {}): InitializeDatabaseResult {
  const databasePath = options.databasePath ?? process.env.DNDGAME_DATABASE_PATH ?? DEFAULT_DATABASE_PATH
  const sqlite = openGameDatabase(databasePath)

  try {
    ensureSchema(sqlite, databasePath)
    return {
      databasePath,
      sqlite,
      db: drizzle(sqlite, { schema }),
      tables: tableNames,
    }
  } catch (error) {
    sqlite.close()
    throw error
  }
}

function ensureSchema(sqlite: Database, databasePath: string): void {
  try {
    sqlite.exec(`
      CREATE TABLE IF NOT EXISTS weapons (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS enemies (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS spells (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS npcs (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS scenes (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS actions (
        id TEXT PRIMARY KEY,
        input TEXT NOT NULL,
        output TEXT NOT NULL,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE TABLE IF NOT EXISTS consequences (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        trigger TEXT NOT NULL,
        target TEXT NOT NULL,
        data TEXT NOT NULL CHECK (json_valid(data))
      );

      CREATE INDEX IF NOT EXISTS idx_consequences_type ON consequences(type);
      CREATE INDEX IF NOT EXISTS idx_consequences_status ON consequences(status);
      CREATE INDEX IF NOT EXISTS idx_consequences_target ON consequences(target);
    `)
  } catch (error) {
    throw new Error(`Failed to initialize SQLite schema at ${databasePath}: ${formatError(error)}`)
  }
}

function formatError(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
```

- [ ] **Step 2: Make the plugin startup initializer delegate to the connection initializer**

Write `code/.opencode/plugins/dnd-game/db/init.ts` with this content:

```ts
import { initializeDatabase as initializeConnection, type InitializeDatabaseOptions } from "./connection"

export type DatabaseInitConfig = InitializeDatabaseOptions

export function initializeDatabase(config?: DatabaseInitConfig): void {
  const { sqlite } = initializeConnection(config)
  sqlite.close()
}
```

- [ ] **Step 3: Update the manual setup script**

Write `code/.opencode/setup-database.ts` with this content:

```ts
import { initializeDatabase } from "./plugins/dnd-game/db/connection"

const databasePath = process.env.DNDGAME_DATABASE_PATH

const { sqlite, db, ...result } = initializeDatabase({ databasePath })
sqlite.close()

console.log(JSON.stringify(result, null, 2))
```

- [ ] **Step 4: Run the check again**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: FAIL because `helpers.ts` is still missing.

## Task 5: Implement JSON Helpers

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/helpers.ts`

- [ ] **Step 1: Create JSON row helper functions**

Write `code/.opencode/plugins/dnd-game/db/helpers.ts` with this content:

```ts
import { eq, sql } from "drizzle-orm"
import type { AnySQLiteTable } from "drizzle-orm/sqlite-core"
import type { BunSQLiteDatabase } from "drizzle-orm/bun-sqlite"

import type { JsonValue, schema } from "./schema"

type GameDb = BunSQLiteDatabase<typeof schema>
type JsonTable = AnySQLiteTable & { id: unknown; data: unknown }

export type JsonRow<TData extends JsonValue> = {
  id: string
  data: TData
}

export function insertJsonRow<TData extends JsonValue>(db: GameDb, table: JsonTable, id: string, data: TData): void {
  db.insert(table).values({ id, data }).run()
}

export function upsertJsonRow<TData extends JsonValue>(db: GameDb, table: JsonTable, id: string, data: TData): void {
  db.insert(table)
    .values({ id, data })
    .onConflictDoUpdate({ target: table.id, set: { data } })
    .run()
}

export async function findById<TData extends JsonValue>(
  db: GameDb,
  table: JsonTable,
  id: string,
): Promise<JsonRow<TData> | null> {
  const row = db.select().from(table).where(eq(table.id, id)).get() as JsonRow<TData> | undefined
  return row ?? null
}

export function updatePath<TValue extends JsonValue>(db: GameDb, table: JsonTable, id: string, path: string, value: TValue): void {
  const jsonPath = toSqliteJsonPath(path)
  const result = db
    .update(table)
    .set({ data: sql`json_set(${table.data}, ${jsonPath}, json(${JSON.stringify(value)}))` })
    .where(eq(table.id, id))
    .run()

  if (result.changes === 0) {
    throw new Error(`Cannot update ${table[Symbol.for("drizzle:Name") as never] ?? "row"} path ${path}: id '${id}' was not found`)
  }
}

export async function queryByPath<TData extends JsonValue>(
  db: GameDb,
  table: JsonTable,
  path: string,
  value: JsonValue,
): Promise<JsonRow<TData>[]> {
  const jsonPath = toSqliteJsonPath(path)
  return db
    .select()
    .from(table)
    .where(sql`json_extract(${table.data}, ${jsonPath}) = ${value}`)
    .all() as JsonRow<TData>[]
}

function toSqliteJsonPath(path: string): string {
  const parts = path.split(".").filter(Boolean)
  if (parts.length === 0 || parts.some((part) => !/^[A-Za-z_][A-Za-z0-9_]*$/.test(part))) {
    throw new Error(`Invalid JSON path '${path}'. Use dot paths like 'stats.damage'.`)
  }

  return `$.${parts.join(".")}`
}
```

- [ ] **Step 2: Run the check and fix type/runtime mismatches**

Run from `code/.opencode`:

```bash
bun run check:db
```

Expected: PASS or a targeted TypeScript/runtime error that identifies a mismatch in Drizzle's table typing. If a mismatch appears, keep the public helper signatures the same and adjust only the internal casts/imports needed to satisfy Drizzle.

## Task 6: Implement Generic Query Wrappers

**Files:**
- Create: `code/.opencode/plugins/dnd-game/db/query.ts`

- [ ] **Step 1: Add generic table query wrapper factory**

Write `code/.opencode/plugins/dnd-game/db/query.ts` with this content:

```ts
import { eq } from "drizzle-orm"
import type { AnySQLiteTable } from "drizzle-orm/sqlite-core"
import type { BunSQLiteDatabase } from "drizzle-orm/bun-sqlite"

import type { schema } from "./schema"

type GameDb = BunSQLiteDatabase<typeof schema>
type TableWithId = AnySQLiteTable & { id: unknown }

export function createTableQuery<TRow extends { id: string }, TInsert extends { id: string }>(db: GameDb, table: TableWithId) {
  return {
    all(): TRow[] {
      return db.select().from(table).all() as TRow[]
    },

    findById(id: string): TRow | null {
      return (db.select().from(table).where(eq(table.id, id)).get() as TRow | undefined) ?? null
    },

    insert(row: TInsert): void {
      db.insert(table).values(row).run()
    },

    deleteById(id: string): void {
      db.delete(table).where(eq(table.id, id)).run()
    },
  }
}
```

- [ ] **Step 2: Run TypeScript/plugin checks**

Run from `code/.opencode`:

```bash
bun run check:plugin
```

Expected: PASS after plugin check is updated in the next task if it currently writes to the default DB.

## Task 7: Update Plugin Check And Docs

**Files:**
- Modify: `code/.opencode/check-plugin.ts`
- Modify: `code/.opencode/README.md`
- Modify: `code/.opencode/tsconfig.json`

- [ ] **Step 1: Make plugin check use a temp database path**

Write `code/.opencode/check-plugin.ts` with this content:

```ts
import { mkdtempSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"

import { DnDGame } from "./plugins/dnd-game/index"

type PluginHooks = {
  tool?: Record<string, unknown>
}

const tempDir = mkdtempSync(join(tmpdir(), "dndgame-plugin-check-"))
const previousDatabasePath = process.env.DNDGAME_DATABASE_PATH

try {
  process.env.DNDGAME_DATABASE_PATH = join(tempDir, "game.db")
  const hooks = (await DnDGame({} as never)) as PluginHooks

  if (!hooks || typeof hooks !== "object") {
    throw new Error("DnDGame plugin did not return a hooks object")
  }

  if (!hooks.tool || typeof hooks.tool !== "object") {
    throw new Error("DnDGame plugin did not register a tool map")
  }

  if (!("dnd_game_health" in hooks.tool)) {
    throw new Error("DnDGame plugin did not register dnd_game_health")
  }

  if ("dnd_dice" in hooks.tool) {
    throw new Error("dnd_dice must not be registered by HAT-18")
  }

  console.log("DnDGame plugin registration check passed: dnd_game_health is registered")
} finally {
  if (previousDatabasePath === undefined) {
    delete process.env.DNDGAME_DATABASE_PATH
  } else {
    process.env.DNDGAME_DATABASE_PATH = previousDatabasePath
  }
  rmSync(tempDir, { recursive: true, force: true })
}
```

- [ ] **Step 2: Include scripts in TypeScript config**

Change `code/.opencode/tsconfig.json` to include all project-local TypeScript files:

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "types": ["@types/node"],
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ESNext",
    "allowJs": true,
    "checkJs": false,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": false
  },
  "include": ["**/*.ts"]
}
```

- [ ] **Step 3: Update README database setup section**

Replace the database setup section in `code/.opencode/README.md` with:

```md
## Database Setup

The plugin creates the local SQLite database automatically on startup. The schema is defined in `plugins/dnd-game/db/schema.ts`, and startup creates the required tables and indexes if they do not exist.

From `code/.opencode`, run the setup command when you want to initialize or verify the database manually:

```bash
bun run setup:db
```

By default this creates or updates `code/.data/game.db`. To use another database, set `DNDGAME_DATABASE_PATH` before running the command.

For a temporary verification database, run:

```bash
bun run check:db
```

The check verifies fresh database creation, all 9 HAT-20 tables, idempotent setup, JSON round-trips, nested JSON path helpers, `actions.input`, `actions.output`, and `consequences` filtering.
```

- [ ] **Step 4: Run plugin and database checks**

Run from `code/.opencode`:

```bash
bun run check:db
bun run check:plugin
```

Expected: both commands PASS.

## Task 8: Remove Old Migration Path

**Files:**
- Delete: `code/.opencode/plugins/dnd-game/db/migrate.ts`
- Delete: `code/.opencode/plugins/dnd-game/db/migration-runner.ts`
- Delete: `code/.opencode/plugins/dnd-game/db/migrations/0001_initial_schema.sql`

- [ ] **Step 1: Delete obsolete migration files**

Remove the files listed above. If the `migrations` directory becomes empty, remove it too.

- [ ] **Step 2: Search for migration references**

Run from repo root:

```bash
rg "migration|migrations|schema_migrations|DNDGAME_MIGRATIONS_DIR" code/.opencode
```

Expected: no references to active migration setup remain. Historical lockfile package names are acceptable only if they come from dependencies, not project code/docs.

- [ ] **Step 3: Run final checks**

Run from `code/.opencode`:

```bash
bun run check:db
bun run check:plugin
```

Expected: both commands PASS.

## Task 9: Final Review And Commit

**Files:**
- Review all modified files from Tasks 1-8

- [ ] **Step 1: Inspect working tree**

Run from repo root:

```bash
git status --short
git diff
```

Expected: only HAT-20 database implementation files changed. No unrelated docs/specs or generated SQLite files should be staged.

- [ ] **Step 2: Run verification commands**

Run from `code/.opencode`:

```bash
bun run check:db
bun run check:plugin
```

Expected: both commands PASS.

- [ ] **Step 3: Commit HAT-20 implementation**

Run from repo root:

```bash
git add code/.opencode/package.json code/.opencode/bun.lock code/.opencode/package-lock.json code/.opencode/tsconfig.json code/.opencode/README.md code/.opencode/check-database.ts code/.opencode/check-plugin.ts code/.opencode/setup-database.ts code/.opencode/plugins/dnd-game/index.ts code/.opencode/plugins/dnd-game/db
git commit -m "feat: add SQLite auto-create database layer"
```

Expected: commit succeeds with only intended HAT-20 changes.

## Self-Review

- Spec coverage: The plan covers the 9 tables, startup auto-create, `connection.ts`, `helpers.ts`, `query.ts`, no SQL migration files, schema existence checks, fresh DB creation, JSON round-trip, nested JSON helpers, `actions.input/output`, and `consequences` filtering.
- Placeholder scan: No TBD/TODO placeholders remain.
- Type consistency: The public initializer returns `{ databasePath, sqlite, db, tables }`; checks and setup use those names consistently. JSON helpers accept a Drizzle DB handle and a table with `id` and `data` columns.
