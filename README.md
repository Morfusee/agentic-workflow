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

## Rule 2: Do Not Edit Mirrored / Linked Paths

This repository uses symlinks (or junctions on Windows) for daily use:

| Source (edit here) | Mirrored to (do NOT edit here) |
|---|---|
| `memory/` | `~/.config/opencode/memory` |
| `memory/` | `~/.codex/memory` |
| `configs/opencode/` | `~/.config/opencode/` |
| `skills/` | `~/.codex/skills/` |
| `skills/` | `~/.config/opencode/skills/` (when `SYNC_OPENCODE=true`) |

**Always edit files in this repository's working tree.**  
Changes made in mirrored/linked target locations will be overwritten or lost.

<!-- END AGENT NOTICE -->

---

# agentic-workflow

## Requirements

- **Python 3.8+** on all platforms (for `scripts/sync_environment.py`)
- **just** command runner (cross-platform)
- **Neovim** setup is Windows-specific (see below)

## Setup

### Windows

#### 1. Link Neovim

```powershell
just nvim-link
```

This creates `configs\nvim` as a junction to `%LOCALAPPDATA%\nvim`.

#### 2. Link OpenCode config

```powershell
just opencode-link
```

This links `configs\opencode\opencode.jsonc` and `configs\opencode\AGENTS.md` into `%USERPROFILE%\.config\opencode\`.

If you want to open the config after linking, run:

```powershell
just opencode-config
```

#### 3. Link memory

```powershell
just memory-sync
```

This symlinks `memory\` into:

1. `%USERPROFILE%\.config\opencode\memory`
2. `%USERPROFILE%\.codex\memory`

#### 4. Set up skills

If you want OpenCode skill mirroring, copy `.skills.env.example` to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Then run:

```powershell
just skills
```

`just skills` bootstraps `skills\` into `%USERPROFILE%\.codex\skills\`. If `SYNC_OPENCODE=true`, it also mirrors into `%USERPROFILE%\.config\opencode\skills`.

### macOS / Linux

#### 1. Link OpenCode config

```sh
just opencode-link
```

This symlinks `configs/opencode/opencode.jsonc` and `configs/opencode/AGENTS.md` into `~/.config/opencode/`.

#### 2. Link memory

```sh
just memory-sync
```

This symlinks `memory/` into:

1. `~/.config/opencode/memory`
2. `~/.codex/memory`

#### 3. Set up skills

```sh
just skills
```

This symlinks each `skills/<name>/` folder into `~/.codex/skills/` (skipping folders with `.codex-hidden`).

To also mirror into OpenCode, copy `.skills.env.example` to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Then run `just skills` again.

## Daily use

1. Put each new skill in `skills/<skill-name>/`.
2. Run `just skills` to sync new skill folders.
3. Run `just sync-environment` to sync everything at once.

## Troubleshooting

1. If a sync command says a path already exists as a real file or directory, the script backs it up with a timestamp and creates the symlink.
2. On Windows, if symlink creation fails, the script falls back to junctions (directories) or hard links (files). Enable Windows Developer Mode for true symlinks.
3. On macOS/Linux, symlinks are created directly.
4. If `python` is not on your PATH, install Python 3.8+ or use your package manager.
