# agentic-workflow

## Codex Skills (Windows Only)

Use this repo as the source of truth for custom Codex skills, then mirror each repo skill into `~/.codex/skills` with junctions (`mklink /J`).

### One-command workflow with `just` (recommended)

Run:

```powershell
just skills
```

What it does:
1. Sync existing folders in `skills\` into `%USERPROFILE%\.codex\skills\` via `mklink /J`.
2. Start a watcher that auto-links new skill folders you create later.

Leave that terminal open to keep continuous linking active.

### Optional `just` targets

```powershell
just skills-sync
just skills-watch
```

These map to:
- [sync-codex-skills.cmd](C:/Users/mrqvp/Documents/Programming/agentic-workflow/scripts/windows/sync-codex-skills.cmd)
- [watch-codex-skills.ps1](C:/Users/mrqvp/Documents/Programming/agentic-workflow/scripts/windows/watch-codex-skills.ps1)

### Manual single skill link (optional)

```cmd
mklink /J "%USERPROFILE%\.codex\skills\linear-standup-prep" "C:\Users\mrqvp\Documents\Programming\agentic-workflow\skills\linear-standup-prep"
```

### Required skill structure

Each skill folder must contain:

`<skill-name>\SKILL.md`
