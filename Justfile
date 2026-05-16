set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

alias s := skills
alias ss := skills-sync
alias so := skills-open
alias sw := skills-watch
alias wo := weekly-open

default:
  @just --list

# Sync existing repo skills into ~/.codex/skills using mklink /J
skills-sync:
  @cmd /c scripts\windows\sync-codex-skills.cmd

# Open ~/.codex/skills in File Explorer
skills-open:
  @explorer "$env:USERPROFILE\.codex\skills"

# Keep auto-linking newly created repo skills
skills-watch:
  @powershell -ExecutionPolicy Bypass -File .\scripts\windows\watch-codex-skills.ps1

# One command for daily use: sync existing + watch future
skills: skills-sync
  @powershell -ExecutionPolicy Bypass -File .\scripts\windows\watch-codex-skills.ps1

# List latest 5 weeks, select one, and open its weekly slideshow HTML
weekly-open:
  @$weeks = Get-ChildItem -Path "memory\tickets" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d{4}-W\d{2}$' } | Sort-Object Name -Descending | Select-Object -First 5; if (-not $weeks) { Write-Error "No week folders found under memory\tickets."; exit 1 }; Write-Host "Select a week to open:`n"; for ($i = 0; $i -lt $weeks.Count; $i++) { Write-Host ("[{0}] {1}" -f ($i + 1), $weeks[$i].Name) }; $choice = Read-Host "`nEnter number (1-$($weeks.Count))"; if ($choice -notmatch '^\d+$') { Write-Error "Invalid input. Please enter a number."; exit 1 }; $index = [int]$choice - 1; if ($index -lt 0 -or $index -ge $weeks.Count) { Write-Error "Selection out of range."; exit 1 }; $selected = $weeks[$index]; $html = Join-Path $selected.FullName ("{0}-weekly-ticket-slideshow.html" -f $selected.Name); if (-not (Test-Path -LiteralPath $html)) { Write-Error ("Expected slideshow file not found: {0}" -f $html); exit 1 }; Write-Host ("Opening {0}" -f $html); Start-Process $html
