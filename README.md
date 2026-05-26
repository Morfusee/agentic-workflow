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

## Setup

### Windows

#### 1. Sync everything (recommended)

```powershell
just sync-environment
```

This is the canonical command and syncs:

1. `memory/` -> `%USERPROFILE%\.config\opencode\memory` and `%USERPROFILE%\.codex\memory`
2. `configs/opencode/*` -> `%USERPROFILE%\.config\opencode/`
3. `configs/codex/*` -> `%USERPROFILE%\.codex/` (Codex permissions/config)
4. `skills/` -> `%USERPROFILE%\.codex\skills/` (and optionally OpenCode)
5. `configs/nvim/` -> `%LOCALAPPDATA%\nvim`

#### 2. Sync only OpenCode config

```powershell
just sync-opencode
```

This links `configs\opencode\opencode.jsonc` and `configs\opencode\AGENTS.md` into `%USERPROFILE%\.config\opencode\`.

If you want to open the config after linking, run:

```powershell
just opencode-config
```

#### 3. Sync only Codex config

```powershell
just sync-codex
```

This links:

1. `configs\\codex\\config.toml.template` -> `%USERPROFILE%\\.codex\\config.toml` (rendered)
2. `configs\\codex\\rules\\default.rules` -> `%USERPROFILE%\\.codex\\rules\\default.rules`

#### 4. Sync only memory

```powershell
just sync-memory
```

This symlinks `memory\` into:

1. `%USERPROFILE%\.config\opencode\memory`
2. `%USERPROFILE%\.codex\memory`

#### 5. Sync only skills

If you want OpenCode skill mirroring, copy `.skills.env.example` to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Then run:

```powershell
just sync-skills
```

`just sync-skills` bootstraps `skills\` into `%USERPROFILE%\.codex\skills\`. If `SYNC_OPENCODE=true`, it also mirrors into `%USERPROFILE%\.config\opencode\skills`. OpenCode skill sync skips folders with `.opencode-hidden`.

#### 6. Sync only Neovim config

```powershell
just sync-nvim
```

This links `%LOCALAPPDATA%\nvim` to `configs\nvim\` (repo is source of truth).

### macOS / Linux

#### 1. Sync everything (recommended)

```sh
just sync-environment
```

This is the canonical command and syncs memory, OpenCode config, skills, and Neovim.
It also syncs Codex config from `configs/codex/` into `~/.codex/`.

#### 2. Sync only OpenCode config

```sh
just sync-opencode
```

This symlinks `configs/opencode/opencode.jsonc` and `configs/opencode/AGENTS.md` into `~/.config/opencode/`.

#### 3. Sync only memory

```sh
just sync-memory
```

This symlinks `memory/` into:

1. `~/.config/opencode/memory`
2. `~/.codex/memory`

#### 4. Sync only skills

```sh
just sync-skills
```

This symlinks each `skills/<name>/` folder into `~/.codex/skills/` (skipping folders with `.codex-hidden`).

To also mirror into OpenCode, copy `.skills.env.example` to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Then run `just sync-skills` again. OpenCode skill sync skips folders with `.opencode-hidden`.

#### 5. Sync only Neovim config

```sh
just sync-nvim
```

This links `~/.config/nvim` to `configs/nvim/` (repo is source of truth).

## Daily use

1. Put each new skill in `skills/<skill-name>/`.
2. Run `just sync-skills` to sync new skill folders.
3. Run `just sync-environment` to sync everything at once.

## Troubleshooting

1. If a sync command says a path already exists as a real file or directory, the script backs it up with a timestamp and creates the symlink.
2. On Windows, if symlink creation fails, the script falls back to junctions (directories) or hard links (files). Enable Windows Developer Mode for true symlinks.
3. On macOS/Linux, symlinks are created directly.
4. If `python` is not on your PATH, install Python 3.8+ or use your package manager.
5. On Linux, Homebrew may install `python3` without a `python` symlink. Fix with:
   ```sh
   ln -s /home/linuxbrew/.linuxbrew/bin/python3 /home/linuxbrew/.linuxbrew/bin/python
   ```
