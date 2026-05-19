<!-- BEGIN AGENT NOTICE -->
<!-- Every agent reading this repository must honor the following rules. -->

# AGENT NOTICE — CRITICAL PATH RULES

## Rule 1: Canonical Memory Root

All memory-backed workflows in this repository resolve under this exact path:

```
${HOME}/Documents/Programming/agentic-workflow/memory
```

This is the **only** authoritative location for memory reads and writes.  
Do not create alternate memory roots. Do not write memory data elsewhere.

## Rule 2: Do Not Edit Mirrored / Junctioned Paths

This repository uses Windows junctions and symlinks for daily use:

| Source (edit here) | Mirrored to (do NOT edit here) |
|---|---|
| `memory/` | `%USERPROFILE%\.config\opencode\memory` |
| `memory/` | `%USERPROFILE%\.codex\memory` |
| `configs/opencode/` | `%USERPROFILE%\.config\opencode\` |
| `skills/` | `%USERPROFILE%\.codex\skills\` |
| `skills/` | `%USERPROFILE%\.config\opencode\skills\` (when `SYNC_OPENCODE=true`) |

**Always edit files in this repository's working tree.**  
Changes made in mirrored/junctioned target locations will be overwritten or lost.

<!-- END AGENT NOTICE -->

---

# agentic-workflow

## Windows setup

This repo is the source of truth for Neovim, OpenCode, memory, and skills.

### 1. Link Neovim

Run:

```powershell
just nvim-link
```

This creates `configs\nvim` as a junction to `%LOCALAPPDATA%\nvim`.

### 2. Link OpenCode config

Run:

```powershell
just opencode-link
```

This links `configs\opencode\opencode.jsonc` and `configs\opencode\AGENTS.md` into `%USERPROFILE%\.config\opencode\`.

If you want to open the config after linking, run:

```powershell
just opencode-config
```

### 3. Link memory

Run:

```powershell
just memory-sync
```

This junctions `memory\` into:

1. `%USERPROFILE%\.config\opencode\memory`
2. `%USERPROFILE%\.codex\memory`

### 4. Set up skills

If you want OpenCode skill mirroring, copy `.skills.env.example` to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Then run:

```powershell
just skills
```

`just skills` bootstraps `skills\` into `%USERPROFILE%\.codex\skills\`, then keeps watching for new skill folders. If `SYNC_OPENCODE=true`, it also mirrors into `%USERPROFILE%\.config\opencode\skills`.

Leave that terminal open while developing skills.

## Daily use

1. Put each new skill in `skills\<skill-name>\`.
2. Keep `just skills` running while you add or edit skills.
3. Rerun `just opencode-link` or `just memory-sync` if you change those sources.

## Troubleshooting

1. If `just nvim-link` says `%LOCALAPPDATA%\nvim` is missing, create that folder first.
2. If `just opencode-link` or `just memory-sync` hit an existing real file or directory, move it aside and rerun the command.
3. If Windows blocks OpenCode symlinks, the script will fall back to hard links when possible.
