# Namespaced Command Hub Design

## Context

The repository currently exposes automation through one root `Justfile` and two files directly under `scripts/`. The command catalog, platform checks, and script paths all live in the root file. This is manageable today but will become difficult to navigate as the repository grows into a central automation hub.

Moving the scripts without coordinated changes would break callers and documentation. In particular, `scripts/sync_environment.py` assumes it is exactly one directory below the repository root.

## Goals

- Keep the root `Justfile` thin as the command catalog grows.
- Replace flat recipes with discoverable, domain-based namespaces.
- Organize executable automation under `scripts/<domain>/`.
- Separate user-facing recipe definitions from script implementations.
- Preserve existing automation behavior while changing its organization and command names.
- Make script and recipe path resolution independent of the caller's current repository subdirectory.
- Correct the mismatch between the README and the recipes exposed by the current `Justfile`.

## Non-goals

- Do not install a global launcher or modify shell profiles.
- Do not make commands available outside this repository.
- Do not retain compatibility aliases for the old flat recipe names.
- Do not create a custom command-line framework.
- Do not refactor the internal sync or authentication behavior beyond what the move requires.

## Architecture

Use three layers:

```text
agentic-workflow/
|-- Justfile
|-- commands/
|   |-- auth.just
|   |-- config.just
|   |-- dev.just
|   |-- repo.just
|   `-- sync.just
`-- scripts/
    |-- auth/
    |   `-- switch-accounts.ps1
    `-- sync/
        `-- environment.py
```

### Root Justfile

The root `Justfile` registers the five modules and provides the top-level listing. It contains no platform-specific automation or substantive command bodies. Its expected size is approximately 10–20 lines even as scripts are added within existing domains.

### Command modules

Files under `commands/` define the public recipe names, arguments, help text, platform checks, and script invocation. Each module anchors repository paths with `justfile_directory()` so that recipes work when invoked from the repository root or any descendant directory.

A bare module invocation, such as `just auth`, lists that module's recipes. It must not run the first operational recipe by default.

### Automation scripts

Files under `scripts/<domain>/` contain substantial automation logic. They do not own the public command catalog. New scripts should be grouped by a clear operational domain instead of being added directly to `scripts/`.

## Public Command Interface

Make a clean break from the flat names. Do not add compatibility aliases.

| Existing command | Namespaced command |
|---|---|
| `just sync-environment` | `just sync environment` |
| `just sync-skills` | `just sync skills` |
| `just sync-opencode` | `just sync opencode` |
| `just sync-codex` | `just sync codex` |
| Documented but missing | `just sync memory` |
| Documented but missing | `just sync nvim` |
| `just auth-save <name>` | `just auth save <name>` |
| `just auth-switch <name>` | `just auth switch <name>` |
| `just auth-list` | `just auth list` |
| `just skills-open` | `just config open-skills` |
| `just opencode-config` | `just config open-opencode` |
| `just serve` | `just dev serve-opencode` |
| `just install-path-privacy-hook` | `just repo install-hooks` |

Discovery commands are:

```text
just
just auth
just config
just dev
just repo
just sync
```

Each public operation has one canonical spelling and no short alias initially.

## Execution Flow

1. The user invokes a namespaced command from this repository or one of its descendants.
2. The root `Justfile` resolves the requested module under `commands/`.
3. The module performs any existing platform guard and invokes the appropriate script using a path anchored to `justfile_directory()`.
4. The script performs the existing operation and returns its exit status.
5. `just` propagates a non-zero script exit status to the caller.

`just sync environment` preserves the current all-target behavior, including Git-hook installation.

## Repository-root Resolution

After moving to `scripts/sync/environment.py`, the sync script must no longer calculate the repository root as its immediate parent directory. It should walk upward from its resolved file location and select the nearest ancestor containing stable repository markers required by the script, including the root `Justfile` and the `configs/`, `skills/`, and `memory/` directories.

If no valid root is found, the script should stop with a concise error rather than constructing paths relative to the wrong directory.

The authentication script does not depend on its current repository location. Its usage messages and all external callers must be updated to the new path.

## Platform and Error Behavior

- Synchronization remains cross-platform.
- Authentication remains Windows-only at the recipe layer.
- Unsupported platforms retain an explanatory message and do not attempt to run PowerShell automation.
- Existing sync error handling, backup behavior, dry-run behavior, and summary output remain unchanged.
- Missing repository markers fail before any sync operation begins.
- Bare namespace commands only display help and cannot trigger a state-changing operation.

## Reference Migration

Update every repository reference to the moved scripts and renamed commands, including:

- `README.md`
- `configs/codex/rules/default.rules`
- `skills/INDEX.md`
- `skills/tools/config-symlink-maintainer/SKILL.md`
- `Justfile` and the new command modules

Search the full tracked working tree for both old script filenames and old flat recipe names after the migration. Historical artifacts under `memory/` should only be changed when they describe the live repository interface rather than recording a past project state.

## Verification

Verify the migration with these checks:

1. Parse and format-check the root Justfile and all command modules.
2. Confirm `just` lists only the top-level namespaces.
3. Confirm each bare namespace lists its own recipes without running an operation.
4. Confirm every command in the public-interface table appears in the appropriate module listing.
5. Run each sync target through the moved script in dry-run mode.
6. Confirm authentication help and safe listing behavior still resolve through the moved PowerShell script on Windows.
7. Search for stale live references to the old script paths and flat recipe names.
8. Review the final diff and confirm unrelated user-owned changes remain untouched.

## Success Criteria

- The root `Justfile` acts only as a module index and top-level help entry point.
- All existing operations are available through the approved namespaced interface.
- `sync memory` and `sync nvim` match the capabilities already described in the README.
- Both scripts live under domain-specific subdirectories.
- Commands work from the repository root and descendant directories.
- No old flat aliases or global launcher are introduced.
- No unrelated repository files or automation behavior are changed.
