param(
    [string] $ConfigPath
)

$ErrorActionPreference = "Stop"

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $PSScriptRoot "..\..\..\memory\skill-configs\opencode-models.json"
}

if (-not (Get-Command opencode -ErrorAction SilentlyContinue)) {
    throw "opencode CLI was not found on PATH."
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Model config not found: $ConfigPath"
}

$config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
$providers = @($config.providers)
$available = @{}
$providerErrors = @{}

foreach ($provider in $providers) {
    $models = & opencode models $provider 2>&1
    if ($LASTEXITCODE -eq 0) {
        $available[$provider] = @($models | Where-Object { $_ })
    }
    else {
        $available[$provider] = @()
        $providerErrors[$provider] = (($models | Out-String).Trim())
    }
}

$preferredAvailable = @()
foreach ($candidate in @($config.selection_order)) {
    $provider = ($candidate.model -split "/", 2)[0]
    if ($available.ContainsKey($provider) -and $available[$provider] -contains $candidate.model) {
        $preferredAvailable += [pscustomobject]@{
            model = $candidate.model
            variant = $candidate.variant
            cost_tier = $candidate.cost_tier
            requires_billing = $candidate.requires_billing
        }
    }
}

[pscustomobject]@{
    config_path = (Resolve-Path -LiteralPath $ConfigPath).Path
    providers = $providers
    available = $available
    provider_errors = $providerErrors
    preferred_available = $preferredAvailable
} | ConvertTo-Json -Depth 8
