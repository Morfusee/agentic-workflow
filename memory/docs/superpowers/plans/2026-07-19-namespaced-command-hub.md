# Namespaced Command Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the growing flat Justfile with repository-local namespaced command modules and move automation scripts into domain folders without changing their operational behavior.

**Architecture:** Keep the root `Justfile` as a module index, define the public interface in `commands/*.just`, and store implementations under `scripts/<domain>/`. Anchor recipe paths to `justfile_directory()` and make the sync script discover the repository root from stable markers.

**Tech Stack:** just 1.51.0 modules, Python 3.8+ standard library, PowerShell 7, Python `unittest`, Markdown documentation

---

## File Map

- Modify `Justfile`: replace flat recipes and aliases with module declarations and top-level discovery.
- Create `commands/auth.just`: expose authentication save, switch, and list recipes.
- Create `commands/config.just`: expose skills-folder and OpenCode-config opening recipes.
- Create `commands/dev.just`: expose the OpenCode server recipe.
- Create `commands/repo.just`: expose Git-hook installation.
- Create `commands/sync.just`: expose all supported sync targets.
- Move `scripts/sync_environment.py` to `scripts/sync/environment.py`: preserve sync behavior and add robust repository-root discovery.
- Move `scripts/switch-accounts.ps1` to `scripts/auth/switch-accounts.ps1`: preserve auth behavior and update usage text.
- Create `tests/scripts/test_sync_environment.py`: test repository-root discovery with the Python standard library.
- Modify `README.md`: document moved scripts and namespaced commands.
- Modify `configs/codex/rules/default.rules`: update the live sync-script path and allowed command prefix.
- Modify `skills/INDEX.md`: update the sync-script path.
- Modify `skills/tools/config-symlink-maintainer/SKILL.md`: teach the skill the new command-module layout and script path.
- Modify `skills/tools/config-symlink-maintainer/references/windows-symlink-checks.md`: update command examples.

### Task 1: Make repository-root discovery location-independent

**Files:**
- Modify: `scripts/sync_environment.py:20-33`
- Create: `tests/scripts/test_sync_environment.py`

- [ ] **Step 1: Write failing unit tests for root discovery**

Create `tests/scripts/test_sync_environment.py`:

```python
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "sync_environment.py"
)
SPEC = importlib.util.spec_from_file_location("sync_environment", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
SYNC_ENVIRONMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC_ENVIRONMENT)


class FindRepoRootTests(unittest.TestCase):
    def test_finds_nearest_ancestor_with_repository_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "Justfile").touch()
            for directory in ("configs", "skills", "memory"):
                (root / directory).mkdir()
            nested = root / "scripts" / "sync"
            nested.mkdir(parents=True)

            self.assertEqual(SYNC_ENVIRONMENT.find_repo_root(nested), root)

    def test_rejects_directory_without_repository_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(RuntimeError, "Repository root not found"):
                SYNC_ENVIRONMENT.find_repo_root(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify they fail for the missing function**

Run:

```powershell
python -m unittest tests/scripts/test_sync_environment.py -v
```

Expected: both tests fail during setup because `sync_environment` has no `find_repo_root` attribute.

- [ ] **Step 3: Add the minimal root-discovery implementation**

Replace the current path-resolution block in `scripts/sync_environment.py` with:

```python
# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

REPO_DIRECTORY_MARKERS = ("configs", "skills", "memory")


def find_repo_root(start: Path) -> Path:
    """Return the nearest ancestor containing the repository's stable markers."""
    resolved_start = start.resolve()
    for candidate in (resolved_start, *resolved_start.parents):
        if not (candidate / "Justfile").is_file():
            continue
        if all((candidate / marker).is_dir() for marker in REPO_DIRECTORY_MARKERS):
            return candidate
    raise RuntimeError(f"Repository root not found from: {resolved_start}")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root(SCRIPT_DIR)
```

Leave all source and target constants below `REPO_ROOT` unchanged.

- [ ] **Step 4: Run the unit tests and sync dry run**

Run:

```powershell
python -m unittest tests/scripts/test_sync_environment.py -v
python scripts/sync_environment.py memory --dry-run
```

Expected: two tests pass; the dry run exits 0 and reports planned memory links without changing them.

- [ ] **Step 5: Commit the independently working root-discovery change**

```powershell
git add scripts/sync_environment.py tests/scripts/test_sync_environment.py
git commit -m "refactor(scripts): discover repository root from markers"
```

### Task 2: Add namespaced command modules and move scripts

**Files:**
- Modify: `Justfile`
- Create: `commands/auth.just`
- Create: `commands/config.just`
- Create: `commands/dev.just`
- Create: `commands/repo.just`
- Create: `commands/sync.just`
- Move: `scripts/sync_environment.py` to `scripts/sync/environment.py`
- Move: `scripts/switch-accounts.ps1` to `scripts/auth/switch-accounts.ps1`
- Modify: `tests/scripts/test_sync_environment.py`

- [ ] **Step 1: Move both scripts into domain folders**

Move the files without altering their implementation:

```text
scripts/sync_environment.py       -> scripts/sync/environment.py
scripts/switch-accounts.ps1       -> scripts/auth/switch-accounts.ps1
```

Update `SCRIPT_PATH` in `tests/scripts/test_sync_environment.py` to:

```python
SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "sync" / "environment.py"
)
```

- [ ] **Step 2: Run tests directly against the moved sync script**

Run:

```powershell
python -m unittest tests/scripts/test_sync_environment.py -v
python scripts/sync/environment.py memory --dry-run
```

Expected: two tests pass and the moved script finds the repository root successfully.

- [ ] **Step 3: Replace the root Justfile with a module index**

Replace `Justfile` with:

```just
# Authentication profile commands
mod auth 'commands/auth.just'

# Configuration access commands
mod config 'commands/config.just'

# Local development commands
mod dev 'commands/dev.just'

# Repository maintenance commands
mod repo 'commands/repo.just'

# Environment synchronization commands
mod sync 'commands/sync.just'

default:
  @just --list
```

- [ ] **Step 4: Create the authentication module**

Create `commands/auth.just`:

```just
default:
  @just --list auth

# Save current Codex + OpenCode auth into a named profile
save +name:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" save "{{ name }}"; \
  else \
    echo "auth save: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
  fi

# Switch Codex + OpenCode auth to a saved profile
switch +name:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" switch "{{ name }}"; \
  else \
    echo "auth switch: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
  fi

# List saved auth profiles
list:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" list; \
  else \
    echo "auth list: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
  fi
```

- [ ] **Step 5: Create the synchronization module**

Create `commands/sync.just`:

```just
default:
  @just --list sync

# Sync the complete environment
environment:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" all

# Sync memory links
memory:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" memory

# Sync OpenCode configuration
opencode:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" opencode

# Sync Codex configuration
codex:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" codex

# Sync skill links
skills:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" skills

# Sync Neovim configuration
nvim:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" nvim
```

- [ ] **Step 6: Create the repository and development modules**

Create `commands/repo.just`:

```just
default:
  @just --list repo

# Install the repository's path-privacy Git hook
install-hooks:
  @python "{{ justfile_directory() }}/scripts/sync/environment.py" hooks
```

Create `commands/dev.just`:

```just
default:
  @just --list dev

# Serve OpenCode on the current machine's Tailscale IPv4
serve-opencode:
  opencode serve --port 6767 --hostname $(tailscale ip -4)
```

- [ ] **Step 7: Create the configuration module**

Create `commands/config.just`:

```just
default:
  @just --list config

# Open mirrored skills folders in the default file manager
open-skills:
  @if [ "{{ os() }}" == "windows" ]; then \
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$$repo = "{{ justfile_directory() }}"; $$codex = Join-Path $$env:USERPROFILE ".codex\skills"; explorer $$codex; $$envFile = Join-Path $$repo ".skills.env"; if ((Test-Path $$envFile) -and ((Get-Content $$envFile | Where-Object { $$_ -match "^\s*SYNC_OPENCODE\s*=\s*true\s*$$" }).Count -gt 0)) { $$open = Join-Path $$env:USERPROFILE ".config\opencode\skills"; explorer $$open }'; \
  else \
    xdg-open ~/.codex/skills 2>/dev/null; \
    if [ -f "{{ justfile_directory() }}/.skills.env" ] && grep -qi '^\s*SYNC_OPENCODE\s*=\s*true\s*$' "{{ justfile_directory() }}/.skills.env" 2>/dev/null; then \
      xdg-open ~/.config/opencode/skills 2>/dev/null; \
    fi; \
  fi

# Open OpenCode's configuration file in the default editor
open-opencode:
  @if [ "{{ os() }}" == "windows" ]; then \
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$$code = Join-Path $$env:LOCALAPPDATA "Programs\Microsoft VS Code\bin\code.cmd"; $$target = Join-Path $$env:USERPROFILE ".config\opencode\opencode.jsonc"; & $$code $$target'; \
  else \
    $${EDITOR:-nano} ~/.config/opencode/opencode.jsonc; \
  fi
```

- [ ] **Step 8: Update authentication usage text for the new interface**

In `scripts/auth/switch-accounts.ps1`, make these exact replacements:

```text
just auth-save <profile-name>    -> just auth save <profile-name>
just auth-switch <profile-name>  -> just auth switch <profile-name>
just auth-save <name>            -> just auth save <name>
scripts/switch-accounts.ps1      -> scripts/auth/switch-accounts.ps1
```

- [ ] **Step 9: Parse, format-check, and inspect command discovery**

Run:

```powershell
just --fmt --check
just --list
just --list auth
just --list config
just --list dev
just --list repo
just --list sync
```

Expected: formatting passes; the root lists five modules; each module lists only its approved recipes.

- [ ] **Step 10: Verify bare namespaces are non-mutating**

Run:

```powershell
just auth
just config
just dev
just repo
just sync
```

Expected: each command displays its module listing and exits 0 without running an operational recipe.

- [ ] **Step 11: Run the safe authentication listing path**

Run on Windows:

```powershell
just auth list
```

Expected: saved profiles are listed, or `No profiles saved yet.` is shown; no auth files are changed.

- [ ] **Step 12: Commit the breaking command-structure migration**

```powershell
git add Justfile commands scripts tests/scripts/test_sync_environment.py
git commit -m "feat(commands)!: add namespaced automation modules"
```

### Task 3: Update live documentation, rules, and skill guidance

**Files:**
- Modify: `README.md`
- Modify: `configs/codex/rules/default.rules`
- Modify: `skills/INDEX.md`
- Modify: `skills/tools/config-symlink-maintainer/SKILL.md`
- Modify: `skills/tools/config-symlink-maintainer/references/windows-symlink-checks.md`

- [ ] **Step 1: Update README script paths and command examples**

Make these path replacements throughout `README.md`:

```text
scripts/sync_environment.py  -> scripts/sync/environment.py
scripts/switch-accounts.ps1  -> scripts/auth/switch-accounts.ps1
```

Make these command replacements throughout `README.md`:

```text
just sync-environment  -> just sync environment
just sync-opencode     -> just sync opencode
just opencode-config   -> just config open-opencode
just sync-codex        -> just sync codex
just sync-memory       -> just sync memory
just sync-skills       -> just sync skills
just sync-nvim         -> just sync nvim
just auth-save         -> just auth save
just auth-switch       -> just auth switch
just auth-list         -> just auth list
```

Replace the obsolete aliases paragraph with:

```markdown
Commands are grouped by namespace. Run `just auth` to list authentication commands.
```

- [ ] **Step 2: Update rules and repository guidance**

In `configs/codex/rules/default.rules`, replace both instances of `scripts/sync_environment.py` with `scripts/sync/environment.py`.

In `skills/INDEX.md`, replace `scripts/sync_environment.py` with `scripts/sync/environment.py`.

In `skills/tools/config-symlink-maintainer/SKILL.md`:

- Replace `scripts/sync_environment.py` with `scripts/sync/environment.py`.
- Replace the instruction to update the sync script and Justfile aliases with: `Update the sync script and the relevant namespaced module under commands/ instead of adding one-off shell commands.`
- Replace `User-facing commands live in Justfile with short aliases when useful.` with `User-facing commands live in namespaced commands/*.just modules registered by the root Justfile.`

In `skills/tools/config-symlink-maintainer/references/windows-symlink-checks.md`, replace:

```text
just sync-codex     -> just sync codex
just sync-opencode  -> just sync opencode
just sync-nvim      -> just sync nvim
```

- [ ] **Step 3: Search for stale live references**

Run:

```powershell
rg -n --fixed-strings -- 'scripts/sync_environment.py' README.md Justfile commands configs skills scripts tests
rg -n --fixed-strings -- 'scripts/switch-accounts.ps1' README.md Justfile commands configs skills scripts tests
rg -n "just (sync-environment|sync-skills|sync-opencode|sync-codex|sync-memory|sync-nvim|auth-save|auth-switch|auth-list|skills-open|opencode-config|serve|install-path-privacy-hook)" README.md Justfile commands configs skills scripts tests
```

Expected: no matches. Do not rewrite the approved design specification, whose migration table intentionally records the old names.

- [ ] **Step 4: Re-run documentation-facing command checks**

Run:

```powershell
just --fmt --check
just --list
just --list sync
python scripts/sync/environment.py --help
pwsh -NoLogo -NoProfile -File scripts/auth/switch-accounts.ps1
```

Expected: all commands exit 0; help shows the sync targets; PowerShell usage displays the new script path and namespaced commands.

- [ ] **Step 5: Commit the reference migration**

```powershell
git add README.md configs/codex/rules/default.rules skills/INDEX.md skills/tools/config-symlink-maintainer/SKILL.md skills/tools/config-symlink-maintainer/references/windows-symlink-checks.md
git commit -m "docs(commands): document namespaced command interface"
```

### Task 4: Run final migration verification

**Files:**
- Verify only; modify implementation files only if a check exposes a defect within this plan's scope.

- [ ] **Step 1: Run the unit tests**

```powershell
python -m unittest tests/scripts/test_sync_environment.py -v
```

Expected: two tests pass.

- [ ] **Step 2: Run every sync target without mutation**

```powershell
python scripts/sync/environment.py memory --dry-run
python scripts/sync/environment.py opencode --dry-run
python scripts/sync/environment.py codex --dry-run
python scripts/sync/environment.py skills --dry-run
python scripts/sync/environment.py nvim --dry-run
python scripts/sync/environment.py hooks --dry-run
python scripts/sync/environment.py all --dry-run
```

Expected: every invocation exits 0 and prints an `OK` summary for each selected target.

- [ ] **Step 3: Confirm command discovery from a descendant directory**

Run from `scripts/sync/`:

```powershell
just --list
just --list sync
python environment.py memory --dry-run
```

Expected: `just` discovers the root Justfile, the sync module lists correctly, and the script finds the repository root.

- [ ] **Step 4: Confirm only intentional files changed**

Run:

```powershell
git status --short
git diff
git log -4 --oneline
```

Expected: the implementation and documentation commits are present; the pre-existing Proxmox document remains modified but uncommitted; no unrelated file is staged or committed.
