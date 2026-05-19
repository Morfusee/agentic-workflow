#Requires -Version 5.1
<#
.SYNOPSIS
  Creates junctions from the repo memory folder into OpenCode and Codex.
.DESCRIPTION
  - Treats agentic-workflow\memory as the source of truth.
  - Creates one directory junction for each tool memory folder.
  - Preserves existing real directories by backing them up before replacement.
  - Leaves already-correct links untouched.
#>

$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$repoMemoryDir = Join-Path $repoRoot "memory"
$targetPaths = @(
  (Join-Path $env:USERPROFILE ".config\opencode\memory"),
  (Join-Path $env:USERPROFILE ".codex\memory")
)

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Test-ReparsePoint {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return $false
  }

  $item = Get-Item -LiteralPath $Path -Force
  return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
}

function Test-LinkPointsToTarget {
  param(
    [string]$Path,
    [string]$Target
  )

  if (-not (Test-ReparsePoint -Path $Path)) {
    return $false
  }

  try {
    $item = Get-Item -LiteralPath $Path -Force
    $existingTarget = $item.Target
    if ($existingTarget -is [array]) {
      $existingTarget = $existingTarget[0]
    }

    if (-not $existingTarget) {
      return $false
    }

    $existingResolved = [System.IO.Path]::GetFullPath($existingTarget)
    $targetResolved = [System.IO.Path]::GetFullPath($Target)
    return [System.StringComparer]::OrdinalIgnoreCase.Equals($existingResolved, $targetResolved)
  } catch {
    return $false
  }
}

function Backup-ExistingDirectory {
  param([string]$Path)

  $backup = "$Path.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
  Move-Item -LiteralPath $Path -Destination $backup -Force
  Write-Host "[BACKUP] $Path -> $backup"
}

function New-Junction {
  param(
    [string]$Path,
    [string]$Target
  )

  cmd /c "mklink /J `"$Path`" `"$Target`"" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to create junction: $Path -> $Target"
  }
}

if (-not (Test-Path -LiteralPath $repoMemoryDir)) {
  throw "Repo memory folder not found: $repoMemoryDir"
}

foreach ($targetPath in $targetPaths) {
  $parentDir = Split-Path -Path $targetPath -Parent
  Ensure-Directory -Path $parentDir

  if (Test-LinkPointsToTarget -Path $targetPath -Target $repoMemoryDir) {
    Write-Host "[SKIP] Already linked: $targetPath"
    continue
  }

  if (Test-ReparsePoint -Path $targetPath) {
    Write-Host "[REMOVE] Existing link: $targetPath"
    Remove-Item -LiteralPath $targetPath -Force
  } elseif (Test-Path -LiteralPath $targetPath) {
    Backup-ExistingDirectory -Path $targetPath
  }

  try {
    New-Junction -Path $targetPath -Target $repoMemoryDir
    Write-Host "[LINKED] $targetPath -> $repoMemoryDir"
  } catch {
    throw "Failed to create directory junction: $targetPath -> $repoMemoryDir. $($_.Exception.Message)"
  }
}
