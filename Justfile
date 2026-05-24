alias s := skills-sync
alias ss := skills-sync
alias so := skills-open
alias nl := nvim-link
alias wo := weekly-open
alias oco := opencode-config
alias ol := opencode-link
alias ms := memory-sync
alias se := sync-environment

default:
  @just --list

# Sync all environment links (memory, opencode config, skills)
sync-environment:
  @python scripts/sync_environment.py all

# Bootstrap skills symlinks into tool config paths
skills-sync:
  @python scripts/sync_environment.py skills

# One command for daily use: sync skills
skills: skills-sync

# Link repo configs/opencode/* into ~/.config/opencode/
opencode-link:
  @python scripts/sync_environment.py opencode

# Link repo memory/ into OpenCode and Codex memory directories
memory-sync:
  @python scripts/sync_environment.py memory

# -----------------------------------------------------------------------
# Windows-only recipes
# -----------------------------------------------------------------------

[windows]
# Open mirrored skills folders in File Explorer
skills-open:
    #!powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command
    explorer "$env:USERPROFILE\.codex\skills"
    if ((Test-Path '.\.skills.env') -and ((Get-Content '.\.skills.env' | Where-Object { $_ -match '^\s*SYNC_OPENCODE\s*=\s*true\s*$' }).Count -gt 0)) { explorer "$env:USERPROFILE\.config\opencode\skills" }

[windows]
# Create a repo-side junction for LOCALAPPDATA nvim
nvim-link:
    #!powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command
    & .\scripts\windows\link-nvim.ps1

[windows]
# Open opencode's config file in the default editor
opencode-config:
    #!powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command
    & "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd" "$env:USERPROFILE\.config\opencode\opencode.jsonc"

[windows]
# List latest 5 weeks, select one, and open its weekly slideshow HTML
weekly-open:
    #!powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command
    $weeks = Get-ChildItem -Path "memory\tickets\linear" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d{4}-W\d{2}$' } | Sort-Object Name -Descending | Select-Object -First 5; if (-not $weeks) { Write-Error "No week folders found under memory\tickets\linear."; exit 1 }; Write-Host "Select a week to open:`n"; for ($i = 0; $i -lt $weeks.Count; $i++) { Write-Host ("[{0}] {1}" -f ($i + 1), $weeks[$i].Name) }; $choice = Read-Host "`nEnter number (1-$($weeks.Count))"; if ($choice -notmatch '^\d+$') { Write-Error "Invalid input. Please enter a number."; exit 1 }; $index = [int]$choice - 1; if ($index -lt 0 -or $index -ge $weeks.Count) { Write-Error "Selection out of range."; exit 1 }; $selected = $weeks[$index]; $candidates = @((Join-Path $selected.FullName 'weekly-slideshow.html'), (Join-Path $selected.FullName ("{0}-weekly-ticket-slideshow.html" -f $selected.Name)), (Join-Path $selected.FullName ("{0}-weekly-ticket-slideshow-presenter.html" -f $selected.Name))); $html = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1; if (-not $html) { Write-Error ("Expected slideshow file not found in: {0}" -f $selected.FullName); exit 1 }; Write-Host ("Opening {0}" -f $html); Start-Process $html
