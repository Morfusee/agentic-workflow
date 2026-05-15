set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

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
