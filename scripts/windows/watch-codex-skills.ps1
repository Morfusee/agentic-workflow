param(
  [string]$RepoSkills = "$PSScriptRoot\..\..\skills",
  [string]$CodexSkills = "$HOME\.codex\skills",
  [int]$IntervalSeconds = 5
)

$RepoSkills = (Resolve-Path $RepoSkills).Path

if (-not (Test-Path $CodexSkills -PathType Container)) {
  Write-Error "Codex skills directory not found: $CodexSkills"
  exit 1
}

function Link-SkillFolder {
  param([string]$SkillFolder)

  if (-not (Test-Path $SkillFolder -PathType Container)) { return }

  $name = Split-Path $SkillFolder -Leaf
  $linkPath = Join-Path $CodexSkills $name

  if (Test-Path $linkPath) { return }

  $mk = "mklink /J `"$linkPath`" `"$SkillFolder`""
  cmd /c $mk | Out-Null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[LINKED] $name"
  } else {
    Write-Host "[ERROR] Failed to link $name"
  }
}

Write-Host "Watching for skills in $RepoSkills"
Write-Host "Sync target is $CodexSkills"
Write-Host "Press Ctrl+C to stop."

while ($true) {
  Get-ChildItem -Path $RepoSkills -Directory | ForEach-Object {
    Link-SkillFolder -SkillFolder $_.FullName
  }
  Start-Sleep -Seconds $IntervalSeconds
}
