param(
  [string]$RepoRoot = "$PSScriptRoot\..\..",
  [string]$RepoNvimRelativePath = "configs\nvim",
  [string]$LocalNvim = "$env:LOCALAPPDATA\nvim"
)

$ErrorActionPreference = "Stop"

$RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$RepoNvim = Join-Path $RepoRoot $RepoNvimRelativePath
$RepoConfigs = Split-Path $RepoNvim -Parent
$LocalNvim = [System.IO.Path]::GetFullPath($LocalNvim)

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Test-JunctionToTarget {
  param(
    [string]$Path,
    [string]$Target
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $false
  }

  $item = Get-Item -LiteralPath $Path -Force
  if (-not $item.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) {
    return $false
  }

  $resolvedTarget = $item.Target
  if ($resolvedTarget -is [System.Array]) {
    $resolvedTarget = $resolvedTarget[0]
  }

  if (-not $resolvedTarget) {
    return $false
  }

  return [System.StringComparer]::OrdinalIgnoreCase.Equals(
    [System.IO.Path]::GetFullPath($resolvedTarget),
    [System.IO.Path]::GetFullPath($Target)
  )
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

Ensure-Directory -Path $RepoConfigs

if (-not (Test-Path -LiteralPath $LocalNvim)) {
  throw "Local nvim config not found: $LocalNvim"
}

if (Test-JunctionToTarget -Path $RepoNvim -Target $LocalNvim) {
  Write-Host "[OK] Junction already exists: $RepoNvim -> $LocalNvim"
  exit 0
}

$repoExists = Test-Path -LiteralPath $RepoNvim

if ($repoExists) {
  throw "Repo path already exists and is not the expected junction.`nRepo: $RepoNvim"
}

New-Junction -Path $RepoNvim -Target $LocalNvim
Write-Host "[LINKED] $RepoNvim -> $LocalNvim"
