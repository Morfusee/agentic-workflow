#Requires -Version 7
<#
.SYNOPSIS
Switch OpenAI/Codex accounts by swapping both Codex and OpenCode auth files in lockstep.
Stores saved profiles under ~/.local/share/auth-profiles/<name>/

.DESCRIPTION
Commands:
  save    <profile>   Save current auth state from both tools into a named profile.
  switch  <profile>   Restore a saved profile to both Codex and OpenCode.
  list                List saved profiles with timestamps.
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("save", "switch", "list")]
    [string]$Command,

    [Parameter(Position = 1)]
    [string]$ProfileName
)

$ErrorActionPreference = "Stop"

$userProfile = $env:USERPROFILE

$codexAuth      = Join-Path $userProfile ".codex\auth.json"
$opencodeAuth   = Join-Path $userProfile ".local\share\opencode\auth.json"
$profilesRoot   = Join-Path $userProfile ".local\share\auth-profiles"

function Write-Log {
    param([string]$Label, [string]$Message)
    Write-Host "[$($Label.PadRight(7))] $Message"
}

function Test-AuthFiles {
    $ok = $true
    if (-not (Test-Path -LiteralPath $codexAuth)) {
        Write-Host "[ERROR]   Codex auth not found: $codexAuth" -ForegroundColor Red
        $ok = $false
    }
    if (-not (Test-Path -LiteralPath $opencodeAuth)) {
        Write-Host "[ERROR]   OpenCode auth not found: $opencodeAuth" -ForegroundColor Red
        $ok = $false
    }
    return $ok
}

function Invoke-Save {
    param([string]$Name)

    if (-not $Name) {
        Write-Host "Usage: just auth save <profile-name>" -ForegroundColor Yellow
        exit 1
    }

    if (-not (Test-AuthFiles)) { exit 1 }

    $targetDir = Join-Path $profilesRoot $Name
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    Copy-Item -LiteralPath $codexAuth    -Destination (Join-Path $targetDir "codex-auth.json") -Force
    Copy-Item -LiteralPath $opencodeAuth -Destination (Join-Path $targetDir "opencode-auth.json") -Force

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    @{ saved = $timestamp } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $targetDir ".meta.json") -Encoding UTF8

    Write-Log "SAVED" "Profile '$Name' — Codex + OpenCode auth saved at $timestamp"
}

function Invoke-Switch {
    param([string]$Name)

    if (-not $Name) {
        Write-Host "Usage: just auth switch <profile-name>" -ForegroundColor Yellow
        exit 1
    }

    $sourceDir = Join-Path $profilesRoot $Name
    if (-not (Test-Path -LiteralPath $sourceDir)) {
        Write-Host "[ERROR]   Profile '$Name' not found at: $sourceDir" -ForegroundColor Red
        $available = Get-ChildItem -LiteralPath $profilesRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object { $_.Name }
        if ($available) {
            Write-Host "Available profiles: $($available -join ', ')"
        } else {
            Write-Host "No profiles saved yet. Use 'just auth save <name>' first."
        }
        exit 1
    }

    $codexSrc    = Join-Path $sourceDir "codex-auth.json"
    $opencodeSrc = Join-Path $sourceDir "opencode-auth.json"

    if (-not (Test-Path -LiteralPath $codexSrc)) {
        Write-Host "[ERROR]   Missing codex-auth.json in profile '$Name'" -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path -LiteralPath $opencodeSrc)) {
        Write-Host "[ERROR]   Missing opencode-auth.json in profile '$Name'" -ForegroundColor Red
        exit 1
    }

    $parent = Split-Path $codexAuth -Parent
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $parent = Split-Path $opencodeAuth -Parent
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    Copy-Item -LiteralPath $codexSrc    -Destination $codexAuth    -Force
    Copy-Item -LiteralPath $opencodeSrc -Destination $opencodeAuth -Force

    Write-Log "SWITCH" "Activated profile '$Name' — Codex + OpenCode auth swapped"

    if (Test-Path -LiteralPath (Join-Path $sourceDir ".meta.json")) {
        $meta = Get-Content -LiteralPath (Join-Path $sourceDir ".meta.json") -Raw | ConvertFrom-Json
        Write-Log "INFO"   "Profile saved at: $($meta.saved)"
    }
}

function Invoke-List {
    if (-not (Test-Path -LiteralPath $profilesRoot)) {
        Write-Host "No profiles saved yet."
        return
    }

    $profiles = Get-ChildItem -LiteralPath $profilesRoot -Directory -ErrorAction SilentlyContinue
    if (-not $profiles) {
        Write-Host "No profiles saved yet."
        return
    }

    Write-Host ""
    Write-Host "Saved auth profiles:" -ForegroundColor Cyan
    Write-Host "-------------------"
    foreach ($p in $profiles) {
        $metaPath = Join-Path $p.FullName ".meta.json"
        $saved = ""
        if (Test-Path -LiteralPath $metaPath) {
            try {
                $meta = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
                $saved = " — saved $($meta.saved)"
            } catch { }
        }
        Write-Host "  $($p.Name)$saved"
    }
    Write-Host ""
}

switch ($Command) {
    "save"   { Invoke-Save   -Name $ProfileName }
    "switch" { Invoke-Switch -Name $ProfileName }
    "list"   { Invoke-List }
    default  {
        Write-Host "Usage: scripts/auth/switch-accounts.ps1 [save|switch|list] [profile-name]" -ForegroundColor Yellow
        Write-Host "  save    <name>   Save current Codex + OpenCode auth to a profile"
        Write-Host "  switch  <name>   Restore a profile to Codex + OpenCode"
        Write-Host "  list             List saved profiles"
    }
}
