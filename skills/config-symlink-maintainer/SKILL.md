---
name: config-symlink-maintainer
description: Maintain repo-owned configuration as the source of truth and safely sync or symlink it into tool config locations. Use when working on Codex, OpenCode, Neovim, skills, memory, or other local developer-tool config mirroring, symlink setup, backup policy, or Justfile sync commands.
---

# Config Symlink Maintainer

Use this skill to keep local tool configuration reproducible from this repository without losing user data.

## Workflow

1. Identify the canonical repo path and the external tool config path.
2. Inspect the existing repo implementation first: `scripts/sync_environment.py`, `Justfile`, `.skills.env`, `configs/`, `skills/`, and `memory/`.
3. Check whether the external target exists, whether it is a symlink or junction, and where it resolves.
4. Preserve existing user data before changing links. Prefer the repo's existing backup policy and avoid creating repeated backups for unchanged files.
5. Update the sync script and Justfile aliases instead of adding one-off shell commands.
6. Validate by running the narrow sync command and checking the resolved target path.
7. Report what is linked, copied, backed up, skipped, and how to retry safely.

## Safety Rules

- Never delete a real config directory without proving it is inside the intended target and has been backed up or intentionally moved.
- On Windows, use PowerShell path inspection before any recursive remove or move.
- Treat `.env`, credentials, SSH, cloud, and local app secrets as non-copyable unless the user explicitly instructs otherwise.
- Prefer idempotent commands: rerunning a sync should not create unnecessary backups or duplicate links.
- Confirm before writing outside `C:\Users\mrqvp\Documents\Programming\agentic-workflow` unless the sync script already owns that target behavior.

## Repo Conventions

- Source-of-truth paths live under `configs/`, `skills/`, and `memory/`.
- User-facing commands live in `Justfile` with short aliases when useful.
- Environment toggles belong in `.skills.env` or another repo-tracked template plus a local ignored file.
- Keep generated external config out of skill folders.

## Validation Checklist

- `just --list` shows the intended command and aliases.
- The narrow sync command completes without syntax errors.
- The external path resolves to the expected repo path or contains the expected synced files.
- Re-running the sync does not create a new backup when nothing changed.
- Sensitive files were neither copied nor exposed.

Read `references/windows-symlink-checks.md` for Windows-specific inspection commands.
