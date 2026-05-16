# agentic-workflow

## Codex Skills (Windows Only)

Use this repo `skills/` folder as the single source of truth for custom skills. The workflow can read a local `.skills.env` file so you can keep your OpenCode mirroring preference in config instead of repeating flags.

### Local config

Copy [`.skills.env.example`](C:/Users/mrqvp/Documents/Programming/agentic-workflow/.skills.env.example) to `.skills.env` and set:

```dotenv
SYNC_OPENCODE=true
```

Use `false` if you only want Codex mirroring. The local `.skills.env` file is gitignored.

### One-command workflow with `just` (recommended)

Run:

```powershell
just skills
```

What it does:
1. Sync existing folders in `skills\` into `%USERPROFILE%\.codex\skills\` via `mklink /J`.
2. Start one watcher that keeps the selected target folders mirrored from the same repo source.

If `.skills.env` contains `SYNC_OPENCODE=true`, the same workflow also mirrors into `%USERPROFILE%\.config\opencode\skills`.

Leave that terminal open to keep continuous linking active.

### Optional `just` targets

```powershell
just skills-sync
just skills-watch
just skills-open
```

These map to:
- [sync-skills.cmd](C:/Users/mrqvp/Documents/Programming/agentic-workflow/scripts/windows/sync-skills.cmd)
- [watch-skills.ps1](C:/Users/mrqvp/Documents/Programming/agentic-workflow/scripts/windows/watch-skills.ps1)

### Required skill structure

Each skill folder must contain:

`<skill-name>\SKILL.md`
