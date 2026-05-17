#Requires -Version 5.1
<#
.SYNOPSIS
  Symlinks the repo's .opencode/opencode.jsonc into ~/.config/opencode/opencode.jsonc
  so the single source-of-truth lives in agentic-workflow.
.DESCRIPTION
  - Backs up an existing real file (not symlink) before replacing it.
  - Removes an existing symlink/junction before creating a new one.
  - Prefers a SymbolicLink; falls back to a HardLink on Windows if symlinks
    are blocked by permissions/Developer Mode.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$repoConfig = Join-Path -Path (Join-Path -Path $repoRoot -ChildPath ".opencode") -ChildPath "opencode.jsonc"
$globalDir = Join-Path -Path (Join-Path -Path $env:USERPROFILE -ChildPath ".config") -ChildPath "opencode"
$globalConfig = Join-Path -Path $globalDir -ChildPath "opencode.jsonc"

function Test-ReparsePoint {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  $item = Get-Item -LiteralPath $Path -Force
  return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
}

function Test-HardLinkedToTarget {
  param(
    [string]$Path,
    [string]$Target
  )

  if (-not (Test-Path -LiteralPath $Path)) { return $false }

  try {
    $resolvedTarget = (Resolve-Path -LiteralPath $Target).ProviderPath
    $hardLinks = & fsutil hardlink list $Path 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $hardLinks) { return $false }

    foreach ($linkPath in $hardLinks) {
      $trimmed = $linkPath.Trim()
      if (-not $trimmed) { continue }
      try {
        $resolvedLink = (Resolve-Path -LiteralPath $trimmed).ProviderPath
        if ([string]::Equals($resolvedLink, $resolvedTarget, [System.StringComparison]::OrdinalIgnoreCase)) {
          return $true
        }
      } catch {
        continue
      }
    }
    return $false
  } catch {
    return $false
  }
}

if (-not (Test-Path -LiteralPath $repoConfig)) {
  Write-Error "Repo config not found: $repoConfig"
  exit 1
}

$resolvedRepoConfig = (Resolve-Path -LiteralPath $repoConfig).ProviderPath

if (-not (Test-Path -LiteralPath $globalDir)) {
  New-Item -ItemType Directory -Path $globalDir -Force | Out-Null
  Write-Host "Created global config directory: $globalDir"
}

# If target exists and is a reparse point, remove it so we can recreate cleanly
if (Test-ReparsePoint -Path $globalConfig) {
  try {
    $existing = Get-Item -LiteralPath $globalConfig -Force
    if ($existing.Target) {
      $existingTarget = $existing.Target
      if ($existingTarget -is [array]) { $existingTarget = $existingTarget[0] }
      $existingTargetResolved = (Resolve-Path -LiteralPath $existingTarget -ErrorAction Stop).ProviderPath
      if ([string]::Equals($existingTargetResolved, $resolvedRepoConfig, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Host "Config link already points to repo config. Nothing to do."
        exit 0
      }
    }
  } catch {
    # If we cannot resolve target, fall through and recreate the link.
  }

  Write-Host "Removing existing symlink/junction at $globalConfig"
  Remove-Item -LiteralPath $globalConfig -Force
}

if (Test-HardLinkedToTarget -Path $globalConfig -Target $repoConfig) {
  Write-Host "Config hard link already points to repo config. Nothing to do."
  exit 0
}

# If target is a real file, back it up before overwriting
if (Test-Path -LiteralPath $globalConfig) {
  $backup = "$globalConfig.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
  Write-Host "Backing up existing global config -> $backup"
  Move-Item -LiteralPath $globalConfig -Destination $backup -Force
}

# Attempt SymbolicLink first (requires Developer Mode or admin on Windows)
try {
  New-Item -ItemType SymbolicLink -Path $globalConfig -Target $repoConfig -Force | Out-Null
  Write-Host "Created SymbolicLink: $globalConfig -> $repoConfig"
  exit 0
} catch {
  Write-Host "SymbolicLink failed ($($_.Exception.Message)). Trying HardLink..."
}

# Fallback to HardLink (no elevation required, but must be on same volume)
try {
  New-Item -ItemType HardLink -Path $globalConfig -Target $repoConfig -Force | Out-Null
  Write-Host "Created HardLink: $globalConfig -> $repoConfig"
  Write-Warning "HardLink is sync-on-write, not a true symlink. If you move the repo, the global config will break. Consider enabling Windows Developer Mode for symlinks."
  exit 0
} catch {
  Write-Error "Failed to create link: $($_.Exception.Message)"
  exit 1
}
