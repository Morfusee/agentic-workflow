# HAT-20 SQLite Auto-Create Design

## Source

- Linear issue: `HAT-20` — Implement SQLite auto-create and database initialization
- Repository: `DnDGame`
- Scope: `code/.opencode/plugins/dnd-game/db/`

## Goal

Implement a repeatable local SQLite database setup for the DnDGame OpenCode plugin. A clean checkout should create the database and required tables automatically on first plugin startup. The schema is owned by Drizzle ORM table definitions, not versioned SQL migration files.

## Non-Goals

- Do not preserve or extend the old SQL migration runner.
- Do not create versioned SQL migration files.
- Do not implement domain state services beyond generic database helpers.
- Do not expand the schema beyond the 9 HAT-20 tables.

## Architecture

The database layer has one source of truth under `code/.opencode/plugins/dnd-game/db/`.

- `schema.ts` defines the 9 required Drizzle SQLite tables.
- `connection.ts` opens Bun SQLite, creates the `.data` directory, enables SQLite pragmas, initializes Drizzle, and runs idempotent table creation on startup.
- `helpers.ts` provides JSON-backed CRUD and JSON path helper functions.
- `query.ts` provides generic typed wrappers for system code.

The plugin entrypoint continues to call `initializeDatabase()` during startup. That call creates `code/.data/game.db` and all missing tables if they do not already exist. Runtime creation is programmatic rather than shelling out to `drizzle-kit push`, so plugin loading does not depend on a CLI subprocess.

The manual `setup:db` script calls the same initializer. This keeps startup behavior and explicit setup behavior aligned.

## Schema

Static reference tables:

- `weapons`
- `enemies`
- `items`
- `spells`
- `npcs`

Each static reference table has:

- `id TEXT PRIMARY KEY`
- `data TEXT NOT NULL`

Session-scoped tables:

- `scenes`
- `events`
- `actions`
- `consequences`

`scenes` and `events` have:

- `id TEXT PRIMARY KEY`
- `data TEXT NOT NULL`

`actions` has:

- `id TEXT PRIMARY KEY`
- `input TEXT NOT NULL`
- `output TEXT NOT NULL`
- `data TEXT NOT NULL`

`consequences` has:

- `id TEXT PRIMARY KEY`
- `type TEXT NOT NULL`
- `status TEXT NOT NULL`
- `trigger TEXT NOT NULL`
- `target TEXT NOT NULL`
- `data TEXT NOT NULL`

`consequences` includes indexes for `type`, `status`, and `target` so filtering does not require scanning JSON blobs.

## Helper Behavior

`helpers.ts` supports JSON-backed rows across all 9 tables:

- Insert or upsert a row by `id`.
- `findById` returns one typed row or `null`.
- `updatePath` updates a nested JSON path inside the `data` object.
- `queryByPath` returns rows where a nested JSON path equals the requested value.

JSON path helpers use simple dot paths such as `stats.damage` or `meta.rarity`. Normal misses return `null` or an empty array. Invalid writes or invalid path usage throw clear errors.

`query.ts` exposes generic typed table access for future `system/` code. It keeps raw SQL details inside the DB layer while preserving type information for callers.

## Startup And Failure Behavior

`initializeDatabase()` is responsible for:

1. Resolving the database path, defaulting to `code/.data/game.db`.
2. Creating the parent directory if needed.
3. Opening SQLite through Bun.
4. Enabling `PRAGMA foreign_keys = ON` and WAL mode.
5. Creating the required tables and indexes if they do not exist.
6. Returning the SQLite and Drizzle handles for callers that need direct access.

Initialization failures throw with the database path and failing step. Startup should not silently continue with a partially initialized database.

## Testing

`check-database.ts` verifies the required HAT-20 behavior against temporary SQLite files:

- A fresh database file is created from nothing.
- All 9 required tables exist.
- A second initialization run is idempotent.
- JSON insert/read round-trips preserve object data.
- `updatePath` updates nested JSON data.
- `queryByPath` finds rows by nested JSON path.
- `actions` includes `input` and `output` columns.
- `consequences` can filter by `type`, `status`, and `target`.

`check:plugin` remains responsible for proving that the OpenCode plugin loads and registers `dnd_game_health`.

## Cleanup

The old migration implementation should be removed:

- `db/migrations/`
- SQL migration runner files
- migration-specific docs and environment variables

This prevents two competing database initialization contracts from remaining in the repo.
