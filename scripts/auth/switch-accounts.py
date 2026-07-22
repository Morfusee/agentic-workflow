#!/usr/bin/env python3
"""Switch Codex/OpenCode auth profiles.

Saves and restores ~/.codex/auth.json and ~/.local/share/opencode/auth.json in lockstep.
Profiles live under ~/.local/share/auth-profiles/<name>/

Commands:
    save    <profile>   Save current auth from both tools into a named profile.
    switch  <profile>   Restore a saved profile to both Codex and OpenCode.
    list                List saved profiles with timestamps.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


CODEX_AUTH = Path.home() / ".codex" / "auth.json"
OPENCODE_AUTH = Path.home() / ".local" / "share" / "opencode" / "auth.json"
PROFILES_ROOT = Path.home() / ".local" / "share" / "auth-profiles"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _log(tag: str, msg: str) -> None:
    print(f"[{tag:<6}] {msg}")


def _test_auth_files() -> bool:
    ok = True
    if not CODEX_AUTH.is_file():
        _log("ERROR", f"Codex auth not found: {CODEX_AUTH}")
        ok = False
    if not OPENCODE_AUTH.is_file():
        _log("ERROR", f"OpenCode auth not found: {OPENCODE_AUTH}")
        ok = False
    return ok


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


def cmd_save(name: str) -> None:
    if not name:
        _log("USAGE", "save <profile-name>")
        sys.exit(1)
    if not _test_auth_files():
        sys.exit(1)

    target = PROFILES_ROOT / name
    target.mkdir(parents=True, exist_ok=True)

    shutil.copy2(CODEX_AUTH, target / "codex-auth.json")
    shutil.copy2(OPENCODE_AUTH, target / "opencode-auth.json")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    (target / ".meta.json").write_text(json.dumps({"saved": now}))

    _log("SAVED", f"Profile '{name}' — Codex + OpenCode auth saved at {now}")


def cmd_switch(name: str) -> None:
    if not name:
        _log("USAGE", "switch <profile-name>")
        sys.exit(1)

    source = PROFILES_ROOT / name
    if not source.is_dir():
        _log("ERROR", f"Profile '{name}' not found at: {source}")
        available = [p.name for p in PROFILES_ROOT.iterdir() if p.is_dir()] if PROFILES_ROOT.is_dir() else []
        if available:
            print(f"Available profiles: {', '.join(available)}")
        else:
            print("No profiles saved yet. Use 'just auth save <name>' first.")
        sys.exit(1)

    codex_src = source / "codex-auth.json"
    opencode_src = source / "opencode-auth.json"

    if not codex_src.is_file():
        _log("ERROR", f"Missing codex-auth.json in profile '{name}'")
        sys.exit(1)
    if not opencode_src.is_file():
        _log("ERROR", f"Missing opencode-auth.json in profile '{name}'")
        sys.exit(1)

    CODEX_AUTH.parent.mkdir(parents=True, exist_ok=True)
    OPENCODE_AUTH.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(codex_src, CODEX_AUTH)
    shutil.copy2(opencode_src, OPENCODE_AUTH)

    _log("SWITCH", f"Activated profile '{name}' — Codex + OpenCode auth swapped")

    meta = source / ".meta.json"
    if meta.is_file():
        data = json.loads(meta.read_text())
        _log("INFO", f"Profile saved at: {data['saved']}")


def cmd_list() -> None:
    if not PROFILES_ROOT.is_dir():
        print("No profiles saved yet.")
        return

    profiles = sorted(p for p in PROFILES_ROOT.iterdir() if p.is_dir())
    if not profiles:
        print("No profiles saved yet.")
        return

    print()
    print("Saved auth profiles:")
    print("-------------------")
    for p in profiles:
        meta = p / ".meta.json"
        saved = ""
        if meta.is_file():
            try:
                data = json.loads(meta.read_text())
                saved = f" — saved {data['saved']}"
            except (json.JSONDecodeError, KeyError):
                pass
        print(f"  {p.name}{saved}")
    print()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Switch Codex + OpenCode auth profiles.",
        usage="%(prog)s {save,switch,list} [profile-name]",
    )
    parser.add_argument("command", choices=["save", "switch", "list"])
    parser.add_argument("profile", nargs="?", default="")
    args = parser.parse_args()

    cmds = {"save": cmd_save, "switch": cmd_switch, "list": cmd_list}
    if args.command == "list":
        cmds[args.command]()
    else:
        cmds[args.command](args.profile)


if __name__ == "__main__":
    main()
