alias se := sync-environment
alias ss := sync-skills
alias sm := sync-memory
alias so := sync-opencode
alias sn := sync-nvim
alias sp := skills-open
alias oc := opencode-config

default:
  @just --list

# Canonical all-in-one environment sync command
sync-environment:
  @python scripts/sync_environment.py all

# Sync skills symlinks into tool config paths
sync-skills:
  @python scripts/sync_environment.py skills

# Sync repo memory into OpenCode and Codex memory directories
sync-memory:
  @python scripts/sync_environment.py memory

# Sync repo configs/opencode/* into ~/.config/opencode/
sync-opencode:
  @python scripts/sync_environment.py opencode

# Sync repo configs/nvim into OS-specific nvim config location
sync-nvim:
  @python scripts/sync_environment.py nvim

# -----------------------------------------------------------------------
# Windows-only recipes
# -----------------------------------------------------------------------

# Open mirrored skills folders in File Explorer
[windows]
skills-open:
  @powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$codex = Join-Path $env:USERPROFILE ".codex\skills"; explorer $codex; if ((Test-Path ".\.skills.env") -and ((Get-Content ".\.skills.env" | Where-Object { $_ -match "^\s*SYNC_OPENCODE\s*=\s*true\s*$" }).Count -gt 0)) { $open = Join-Path $env:USERPROFILE ".config\opencode\skills"; explorer $open }'

# Open opencode's config file in the default editor
[windows]
opencode-config:
  @powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$code = Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code\bin\code.cmd"; $target = Join-Path $env:USERPROFILE ".config\opencode\opencode.jsonc"; & $code $target'
