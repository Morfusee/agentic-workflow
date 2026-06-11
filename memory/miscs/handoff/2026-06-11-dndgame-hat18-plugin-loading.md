# Handoff: DnDGame v0 — HAT-18 Plugin Loading Debug

**Date:** 2026-06-11
**Next session focus:** Debug and fix why the DnDGame OpenCode plugin is not loading after restart. The plugin shell (HAT-18) is implemented but not verified as functional in a live OpenCode session.

---

## Conversation Summary

The user continued from a previous planning session to implement HAT-18 ("Create minimal OpenCode plugin shell and registration path"). Using brainstorming, we designed the implementation approach: project-local plugin with shallow automated check plus manual restart verification. A formal plan was written, a subagent executed the implementation, and the main agent reviewed the diff.

All static verification passed — the dice tool was replaced with `dnd_game_health`, no excluded behavior remains, docs are updated. But when the user tried to verify the plugin loads in a live OpenCode session, it did not work. The user reports the plugin is not loading for unknown reasons.

## Current Project State

- **Repo:** `C:\Users\mrqvp\Documents\Programming\DnDGame`
- **Linear Team:** Hatudoggy (HAT)
- **User:** Mark (c684c9a8-fc1c-4356-886f-55084b6e7ec8)
- **Completed:** HAT-16 (scaffolding), HAT-18 (plugin shell — implemented but unverified)
- **Bun:** Available at `C:\Users\mrqvp\.bun\bin\bun.exe` (v1.3.14)
- **Unstaged changes:** Only HAT-18 implementation files and planning docs (not committed)

## Root Cause Hypothesis (Must Be Confirmed)

There are **two separate `.opencode/` directories** in this repo, and they serve different OpenCode projects:

### 1. Root-level `.opencode/` (current main session)

```
DnDGame/
  .opencode/
    opencode.json       ← has `"plugin": ["dnd"]` (npm package-style)
    package.json        ← has `@opencode-ai/plugin` dep
    node_modules/       ← installed
    plugins/            ← DOES NOT EXIST
  opencode.json         ← root project config
```

The main OpenCode session runs from `DnDGame/` and loads config from `DnDGame/.opencode/`. This directory has `"plugin": ["dnd"]` which tries to load an npm package called "dnd". There is **no `plugins/` directory here**, so no local file-based plugins are loaded.

### 2. Nested code project `.opencode/` (HAT-18 target)

```
DnDGame/
  code/
    .opencode/
      plugins/
        dnd-game/
          index.ts      ← the HAT-18 plugin lives here
      package.json
      node_modules/     ← has @opencode-ai/plugin installed
      check-plugin.ts
      README.md
    opencode.json
    AGENTS.md
```

This is the plugin HAT-18 created. But the root session doesn't look at `code/.opencode/`. For this plugin to load, OpenCode must be started from `code/`.

### Why the user sees "Drag n' Dev" but no plugin

When the user runs `opencode C:\Users\mrqvp\Documents\Programming\DnDGame\code`, OpenCode starts with `code/` as the project root. It shows "Drag n' Dev" (auto-generated project name). But the plugin may still not load because:

1. The `code/.opencode/package.json` uses `"@opencode-ai/plugin": "latest"` — may need `bun install` to resolve properly
2. OpenCode may expect the package.json in a specific format or location
3. The `tool` object return format may differ from what OpenCode expects
4. OpenCode may require the plugin export to be a default export, not a named export

**None of these hypotheses have been tested yet.** The next agent must determine the actual loading mechanism.

## Ticket of Focus

### HAT-18: Create minimal OpenCode plugin shell and registration path

- **URL:** https://linear.app/hatudoggy/issue/HAT-18
- **Status:** Implementation done, verification blocked
- **Linear status:** Still "Todo" (not moved to Done — plugin loading unverified)

## What the Next Agent Should Do

1. **Read the plugin brainstorm** at `docs/brainstorms/2026-06-09-opencode-plugins.md` to understand OpenCode plugin loading conventions.
2. **Fetch the actual OpenCode plugin docs** from https://opencode.ai/docs/plugins and verify the loading mechanism, export format, and dependency resolution.
3. **Debug the two-project structure:**
   - Determine whether the root `.opencode/` with `"plugin": ["dnd"]` is correct or leftover from HAT-16 scaffold.
   - Determine whether HAT-18's plugin should live under the root `.opencode/plugins/` instead of `code/.opencode/plugins/`.
   - Determine whether `code/` should be treated as a separate OpenCode project at all.
4. **Fix the plugin loading issue** so `dnd_game_health` appears in a live OpenCode session.
5. **Run the shallow check** (`bun run check:plugin` from `code/.opencode/`) if the module shape is still valid after any fixes.
6. **Update docs** if the project structure or loading approach changes.
7. **Commit HAT-18** once the plugin is verified as loading in a live session.

## Key Files

| File | Status | Notes |
|------|--------|-------|
| `code/.opencode/plugins/dnd-game/index.ts` | Modified | Replaced `dnd_dice` with `dnd_game_health` |
| `code/.opencode/check-plugin.ts` | New | Shallow registration check |
| `code/.opencode/package.json` | New | Local plugin deps, uses `"latest"` |
| `code/.opencode/README.md` | New | Restart and verification docs |
| `code/.opencode/node_modules/` | Exists | `@opencode-ai/plugin` installed |
| `docs/architecture/ARCHITECTURE.md` | Modified | Added HAT-18 health-only note |
| `docs/brainstorms/2026-06-10-hat18-plugin-shell.md` | New | Approved design decision |
| `docs/plans/hat18-plugin-shell.md` | New | Implementation plan |
| `.opencode/opencode.json` | Exists | Root session config, has `"plugin": ["dnd"]` |
| `.opencode/package.json` | Exists | Root session deps, `@opencode-ai/plugin` v1.17.3 |
| `.opencode/plugins/` | Does not exist | Root session has no local plugins dir |

## Dependency Graph (Relevant Subset)

```
HAT-16 [DONE]
  ├── HAT-15 (setup flow) [Todo]
  │     └── HAT-17 [Todo]
  └── HAT-18 (plugin shell) [Todo — BLOCKED on loading verification]
        ├── HAT-19 (SQLite schema) [Todo]
        ├── HAT-20 (migration runner) [Todo]
        ├── HAT-23 (tool contracts) [Todo]
        └── HAT-17 [Todo]
```

## Suggested Skills

| Order | Skill | Purpose |
|-------|-------|---------|
| 1 | `brainstorming` | If the plugin loading fix requires rethinking the project structure or export format |
| 2 | `capture-brainstorm` | Save any new decisions about plugin loading conventions |
| 3 | `writing-plans` | If a revised implementation plan is needed before fixing |

## Verification Checklist (for the next agent)

- [ ] `dnd_game_health` is visible/callable in a live OpenCode session
- [ ] `bun run check:plugin` passes from `code/.opencode/`
- [ ] No `dnd_dice`, `Math.random`, SQLite, or state mutation in HAT-18 files
- [ ] All HAT-18 files are committed
- [ ] Linear HAT-18 is moved to Done if verified
