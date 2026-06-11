# Handoff: DnDGame Plugin Health Check

**Date:** 2026-06-11 21:00
**Session focus:** Verifying /dnd_game_health plugin tool is working

## Summary

User wanted to check if the /dnd_game_health OpenCode plugin tool is working.

## What exists

- **Plugin file:** DnDGame/.opencode/plugins/dnd-game/index.ts — defines dnd_game_health tool returning { plugin, version, status, message }
- **Purpose:** HAT-18 minimal plugin shell. Single tool for verifying OpenCode loads the plugin after restart.
- **Scope:** Only dnd_game_health is registered. Dice, SQLite, validation, gameplay tools are deferred.

## Key constraint

dnd_game_health is a plugin tool registered via the OpenCode plugin API (@opencode-ai/plugin). It may not appear in the agent's tool list unless OpenCode has loaded the plugin. The plugin requires an OpenCode restart from the root DnDGame/ directory after changes to take effect.

## What to do next

1. Verify the plugin is loaded — check if dnd_game_health appears in the available tools list after an OpenCode restart from the DnDGame/ root.
2. If not visible, ensure the plugin file is correct and restart OpenCode from the correct directory.
3. If visible, invoke /dnd_game_health and confirm the JSON response matches expectations.

## Suggested skills

None required.
