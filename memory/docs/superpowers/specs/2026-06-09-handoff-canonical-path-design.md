# Handoff Canonical Path Fix

## Summary

Redirect handoff skill output from OS temp directory to the canonical memory path `<canonical-memory-root>/memory/miscs/handoff/`, and remove the non-standard `argument-hint` frontmatter field.

## Changes

### SKILL.md

1. **Remove `argument-hint` frontmatter field** — AGENTS.md only permits `name` and `description` in frontmatter. The `argument-hint` field is non-conformant and removed.

2. **Change save path** — from "temporary directory of the user's OS" to `<canonical-memory-root>/memory/miscs/handoff/`. This aligns with the global AGENTS.md canonical memory root rule while keeping handoff files discoverable under a dedicated `miscs/handoff/` subdirectory.

### What stays the same

- Ambiguitous file naming — agent picks a sensible filename based on context
- "Suggested skills" section requirement
- Redaction of sensitive information
- Reference-by-path/URL instead of duplication
- Argument-driven tailoring for next-session focus

## Rationale

The OS temp directory is ephemeral and non-discoverable. The canonical memory root is the authoritative location for all memory-backed workflows per global AGENTS.md. Placing handoff files under `memory/miscs/handoff/` makes them persistent, browsable, and consistent with the rest of the repo's artifact conventions.
