#!/usr/bin/env python3
"""Cross-platform environment sync script.

Symlinks repo files and directories (memory, configs/opencode, skills, nvim)
into tool config paths (~/.config/opencode/, ~/.codex/, nvim config home).

Works on Windows, macOS, and Linux without WSL.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

MEMORY_SOURCE = REPO_ROOT / "memory"
CONFIG_DIR = REPO_ROOT / "configs" / "opencode"
CODEX_CONFIG_DIR = REPO_ROOT / "configs" / "codex"
SKILLS_SOURCE = REPO_ROOT / "skills"
NVIM_SOURCE = REPO_ROOT / "configs" / "nvim"
ENV_FILE = REPO_ROOT / ".skills.env"

OPENCODE_DIR = Path.home() / ".config" / "opencode"
CODEX_DIR = Path.home() / ".codex"

MEMORY_TARGETS = [
    OPENCODE_DIR / "memory",
    CODEX_DIR / "memory",
]

OPENCODE_CONFIG_FILES = [
    "opencode.jsonc",
    "AGENTS.md",
]

CODEX_CONFIG_TEMPLATE = "config.toml.template"

CODEX_SKILLS_DIR = CODEX_DIR / "skills"
OPENCODE_SKILLS_DIR = OPENCODE_DIR / "skills"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(label: str, message: str) -> None:
    print(f"[{label:>7}] {message}")


def error(message: str) -> None:
    print(f"[  ERROR] {message}", file=sys.stderr)


def load_env_toggle(key: str = "SYNC_OPENCODE") -> Optional[str]:
    if not ENV_FILE.is_file():
        return None
    try:
        text = ENV_FILE.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        k, _, v = stripped.partition("=")
        if k.strip() == key:
            return v.strip()
    return None


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_nvim_target() -> Path:
    if platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "nvim"
        return Path.home() / "AppData" / "Local" / "nvim"
    return Path.home() / ".config" / "nvim"


def path_kind(path: Path) -> str:
    if not os.path.lexists(str(path)):
        return "missing"
    if path.is_symlink():
        return "link"
    try:
        st = os.lstat(str(path))
        if (
            platform.system() == "Windows"
            and hasattr(st, "st_reparse_tag")
            and st.st_reparse_tag != 0
        ):
            return "link"
    except OSError:
        pass
    if path.is_file():
        return "file"
    if path.is_dir():
        return "dir"
    return "dir"


def link_points_to(dest: Path, source: Path) -> bool:
    try:
        dest_real = os.path.realpath(str(dest))
        src_real = str(source.resolve())
        return os.path.normcase(dest_real) == os.path.normcase(src_real)
    except OSError:
        return False


def backup_existing(path: Path) -> None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.backup.{timestamp}")
    # On Windows, moving a symlink can require privileges (or fail depending on
    # symlink type). For file symlinks, preserve the *contents* as a regular
    # backup file and then remove the symlink.
    if path.is_symlink():
        if path.is_dir():
            shutil.move(str(path), str(backup_path))
            log("BACKUP", f"{path} -> {backup_path}")
            return

        ensure_parent_dir(backup_path)
        try:
            shutil.copyfile(str(path), str(backup_path), follow_symlinks=True)
        except FileNotFoundError:
            # Broken symlink: preserve the link target string for debugging.
            try:
                target = os.readlink(str(path))
            except OSError:
                target = "<unreadable>"
            backup_path.write_text(f"broken-symlink-target: {target}\n", encoding="utf-8", newline="\n")
        try:
            path.unlink()
        except OSError:
            os.remove(str(path))
        log("BACKUP", f"{path} -> {backup_path} (copied contents; removed symlink)")
        return

    shutil.move(str(path), str(backup_path))
    log("BACKUP", f"{path} -> {backup_path}")


# ---------------------------------------------------------------------------
# Link creation (platform-aware)
# ---------------------------------------------------------------------------

def _try_symlink(dest: Path, source: Path, is_dir: bool) -> bool:
    try:
        dest.symlink_to(source.resolve(), target_is_directory=is_dir)
        return True
    except (OSError, NotImplementedError):
        return False


def _try_junction(dest: Path, source: Path) -> bool:
    if platform.system() != "Windows":
        return False
    try:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dest), str(source.resolve())],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.SubprocessError, OSError):
        return False


def _try_hardlink(dest: Path, source: Path) -> bool:
    try:
        os.link(str(source.resolve()), str(dest))
        return True
    except OSError:
        return False


def create_link(dest: Path, source: Path, is_dir: bool) -> None:
    ensure_parent_dir(dest)

    if _try_symlink(dest, source, is_dir):
        return

    if platform.system() == "Windows":
        if is_dir and _try_junction(dest, source):
            log("WARN", "Junction created instead of symlink. Consider enabling Windows Developer Mode for true symlinks.")
            return
        if not is_dir and _try_hardlink(dest, source):
            log("WARN", "Hard link created instead of symlink. Consider enabling Windows Developer Mode for true symlinks.")
            return

    raise RuntimeError(
        f"Failed to create link: {dest} -> {source}. "
        f"On Windows, enable Developer Mode or run as administrator."
    )


# ---------------------------------------------------------------------------
# Link removal
# ---------------------------------------------------------------------------

def _remove_path(path: Path) -> bool:
    try:
        os.unlink(str(path))
        return True
    except OSError:
        pass
    try:
        os.rmdir(str(path))
        return True
    except OSError:
        pass
    if platform.system() == "Windows":
        try:
            subprocess.run(
                ["cmd", "/c", "rmdir", str(path)],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.SubprocessError:
            pass
    return False


# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------

def _sync_link(dest: Path, source: Path, is_dir: bool, dry_run: bool) -> bool:
    kind = path_kind(dest)

    if kind == "missing":
        if dry_run:
            log("DRY-RUN", f"Would create link: {dest}")
            return True
        try:
            create_link(dest, source, is_dir)
            log("LINKED", f"{dest} -> {source}")
            return True
        except RuntimeError as e:
            error(str(e))
            return False

    if kind == "link":
        if link_points_to(dest, source):
            log("SKIP", f"{dest}")
            return True
        if dry_run:
            log("DRY-RUN", f"Would replace link: {dest} -> {source}")
            return True
        if not _remove_path(dest):
            error(f"Cannot remove existing link at {dest}")
            return False
        log("REMOVE", f"Old link at {dest}")
        try:
            create_link(dest, source, is_dir)
            log("LINKED", f"{dest} -> {source}")
            return True
        except RuntimeError as e:
            error(str(e))
            return False

    if dry_run:
        log("DRY-RUN", f"Would backup and link: {dest} -> {source}")
        return True

    backup_existing(dest)
    try:
        create_link(dest, source, is_dir)
        log("LINKED", f"{dest} -> {source}")
        return True
    except RuntimeError as e:
        error(str(e))
        return False


# ---------------------------------------------------------------------------
# Sync operations
# ---------------------------------------------------------------------------

def sync_memory(dry_run: bool = False) -> bool:
    if not MEMORY_SOURCE.is_dir():
        error(f"Memory source not found: {MEMORY_SOURCE}")
        return False
    all_ok = True
    for target in MEMORY_TARGETS:
        if not _sync_link(target, MEMORY_SOURCE, is_dir=True, dry_run=dry_run):
            all_ok = False
    return all_ok


def sync_opencode_config(dry_run: bool = False) -> bool:
    if not CONFIG_DIR.is_dir():
        error(f"Config source directory not found: {CONFIG_DIR}")
        return False
    all_ok = True
    for filename in OPENCODE_CONFIG_FILES:
        source = CONFIG_DIR / filename
        if not source.is_file():
            error(f"Config file not found: {source}")
            all_ok = False
            continue
        dest = OPENCODE_DIR / filename
        if not _sync_link(dest, source, is_dir=False, dry_run=dry_run):
            all_ok = False
    return all_ok


def sync_codex_config(dry_run: bool = False) -> bool:
    if not CODEX_CONFIG_DIR.is_dir():
        error(f"Config source directory not found: {CODEX_CONFIG_DIR}")
        return False

    all_ok = True

    # Render config.toml from an in-repo template so paths are portable across machines/users.
    template_path = CODEX_CONFIG_DIR / CODEX_CONFIG_TEMPLATE
    if not template_path.is_file():
        error(f"Config template not found: {template_path}")
        all_ok = False
    else:
        try:
            template_text = template_path.read_text(encoding="utf-8")
        except OSError as e:
            error(f"Cannot read template: {e}")
            all_ok = False
        else:
            rendered = template_text
            userprofile = str(Path.home())
            localappdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))

            rendered = rendered.replace("{USERPROFILE}", userprofile)
            rendered = rendered.replace("{LOCALAPPDATA}", localappdata)

            dest = CODEX_DIR / "config.toml"
            if dry_run:
                log("DRY-RUN", f"Would write rendered config: {dest} (from {template_path})")
            else:
                ensure_parent_dir(dest)
                # Keep at most one backup for Codex config.toml to avoid backup spam.
                # If a backup already exists, overwrite in place without creating a new one.
                backup_once = dest.with_name("config.toml.backup")
                if os.path.lexists(str(dest)) and not backup_once.exists():
                    if dest.is_symlink() and not dest.exists():
                        # Broken symlink: just remove it and proceed (backup adds little value).
                        try:
                            dest.unlink()
                        except OSError:
                            os.remove(str(dest))
                        log("REMOVE", f"Broken symlink at {dest}")
                    else:
                        ensure_parent_dir(backup_once)
                        try:
                            shutil.copyfile(str(dest), str(backup_once), follow_symlinks=True)
                            log("BACKUP", f"{dest} -> {backup_once}")
                        except OSError as e:
                            error(f"Cannot create one-time backup: {e}")
                try:
                    dest.write_text(rendered, encoding="utf-8", newline="\n")
                    log("WROTE", f"{dest} (rendered from repo template)")
                except OSError as e:
                    error(f"Cannot write rendered config: {e}")
                    all_ok = False

    rules_source = CODEX_CONFIG_DIR / "rules" / "default.rules"
    if not rules_source.is_file():
        error(f"Rules file not found: {rules_source}")
        all_ok = False
    else:
        rules_dest = CODEX_DIR / "rules" / "default.rules"
        if not _sync_link(rules_dest, rules_source, is_dir=False, dry_run=dry_run):
            all_ok = False

    return all_ok


def sync_skills(dry_run: bool = False) -> bool:
    if not SKILLS_SOURCE.is_dir():
        error(f"Skills source not found: {SKILLS_SOURCE}")
        return False

    targets = [CODEX_SKILLS_DIR]
    env_val = load_env_toggle("SYNC_OPENCODE")
    if env_val is not None and env_val.lower() == "true":
        targets.append(OPENCODE_SKILLS_DIR)

    all_ok = True
    skill_folders = sorted([p for p in SKILLS_SOURCE.iterdir() if p.is_dir()])

    for target in targets:
        target.mkdir(parents=True, exist_ok=True)

        for skill_folder in skill_folders:
            name = skill_folder.name
            is_hidden = (skill_folder / ".codex-hidden").is_file()

            if is_hidden and target == CODEX_SKILLS_DIR:
                log("HIDDEN", f"{name} (skipped for Codex)")
                continue

            dest = target / name
            if not _sync_link(dest, skill_folder, is_dir=True, dry_run=dry_run):
                all_ok = False

    return all_ok


def sync_nvim(dry_run: bool = False) -> bool:
    if not NVIM_SOURCE.is_dir():
        error(f"Neovim source not found: {NVIM_SOURCE}")
        return False

    target = get_nvim_target()
    return _sync_link(target, NVIM_SOURCE, is_dir=True, dry_run=dry_run)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync repo environment files into tool config paths."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        choices=["memory", "opencode", "codex", "skills", "nvim", "all"],
        default=["all"],
        help="Which targets to sync (default: all).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without executing.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extra diagnostics.",
    )

    args = parser.parse_args()

    if "all" in args.targets:
        targets_to_run = ["memory", "opencode", "codex", "skills", "nvim"]
    else:
        targets_to_run = args.targets

    results = {}
    for target in targets_to_run:
        if target == "memory":
            results["memory"] = sync_memory(dry_run=args.dry_run)
        elif target == "opencode":
            results["opencode"] = sync_opencode_config(dry_run=args.dry_run)
        elif target == "codex":
            results["codex"] = sync_codex_config(dry_run=args.dry_run)
        elif target == "skills":
            results["skills"] = sync_skills(dry_run=args.dry_run)
        elif target == "nvim":
            results["nvim"] = sync_nvim(dry_run=args.dry_run)

    print()
    all_ok = all(results.values())
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"[SUMMARY] {name}: {status}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
