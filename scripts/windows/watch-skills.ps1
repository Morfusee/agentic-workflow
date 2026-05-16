param(
  [string]$RepoSkills = "$PSScriptRoot\..\..\skills",
  [string]$CodexSkills = "$HOME\.codex\skills",
  [string]$OpenCodeSkills = "$HOME\.config\opencode\skills",
  [string]$ConfigFile = "$PSScriptRoot\..\..\.skills.env",
  [int]$IntervalSeconds = 5
)

$RepoSkills = (Resolve-Path $RepoSkills).Path
$ConfigFile = [System.IO.Path]::GetFullPath($ConfigFile)
$includeOpenCodeFromConfig = $false

function Get-ConfigValue {
  param(
    [string]$Path,
    [string]$Key
  )

  if (-not (Test-Path $Path -PathType Leaf)) { return $null }

  foreach ($line in Get-Content $Path) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#")) { continue }

    $parts = $trimmed -split "=", 2
    if ($parts.Count -ne 2) { continue }

    if ($parts[0].Trim() -eq $Key) {
      return $parts[1].Trim()
    }
  }

  return $null
}

$configValue = Get-ConfigValue -Path $ConfigFile -Key "SYNC_OPENCODE"
if ($null -ne $configValue) {
  $includeOpenCodeFromConfig = $configValue.ToLowerInvariant() -eq "true"
}

$TargetSkills = @($CodexSkills)

if ($includeOpenCodeFromConfig) {
  $TargetSkills += $OpenCodeSkills
}

foreach ($target in $TargetSkills) {
  if (-not (Test-Path $target -PathType Container)) {
    try {
      New-Item -ItemType Directory -Path $target -Force -ErrorAction Stop | Out-Null
    } catch {
      Write-Error "Unable to create target skills directory: $target"
      exit 1
    }
  }
}

function Link-SkillFolder {
  param([string]$SkillFolder)

  if (-not (Test-Path $SkillFolder -PathType Container)) { return }

  $name = Split-Path $SkillFolder -Leaf
  $isHidden = Test-Path (Join-Path $SkillFolder ".codex-hidden")

  foreach ($target in $TargetSkills) {
    $linkPath = Join-Path $target $name

    if ($isHidden -and ($target -eq $CodexSkills)) { continue }
    if (Test-Path $linkPath) { continue }

    $mk = "mklink /J `"$linkPath`" `"$SkillFolder`""
    cmd /c $mk | Out-Null
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[LINKED] $name -> $target"
    } else {
      Write-Host "[ERROR] Failed to link $name -> $target"
    }
  }
}

Write-Host "Watching for skills in $RepoSkills"
Write-Host "Sync targets:"
foreach ($target in $TargetSkills) {
  Write-Host "  $target"
}
Write-Host "Press Ctrl+C to stop."

while ($true) {
  Get-ChildItem -Path $RepoSkills -Directory | ForEach-Object {
    Link-SkillFolder -SkillFolder $_.FullName
  }
  Start-Sleep -Seconds $IntervalSeconds
}
