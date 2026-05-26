param(
    [Parameter(Mandatory = $true)]
    [string] $Prompt,

    [ValidateSet("SEARCH", "INSPECT", "SUMMARIZE", "VALIDATE", "COMPARE", "DRAFT_FRAGMENT", "SMALL_PATCH", "OTHER")]
    [string] $TaskType = "OTHER",

    [ValidateSet("READ_ONLY", "PATCH_ALLOWED")]
    [string] $PermissionMode = "READ_ONLY",

    [string[]] $ScopeIn = @(),

    [string] $Model,

    [string] $Variant,

    [string] $ConfigPath,

    [ValidateSet("default", "json")]
    [string] $Format = "default"
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

function Test-ModelAvailable {
    param([string] $CandidateModel)

    $provider = ($CandidateModel -split "/", 2)[0]
    $models = & opencode models $provider 2>&1
    if ($LASTEXITCODE -eq 0) {
        return @($models) -contains $CandidateModel
    }

    Write-Warning "Could not list OpenCode models for provider '$provider': $(($models | Out-String).Trim())"
    return $false
}

if (-not $Model) {
    foreach ($candidate in @($config.selection_order)) {
        if (Test-ModelAvailable -CandidateModel $candidate.model) {
            $Model = $candidate.model
            if (-not $Variant) {
                $Variant = $candidate.variant
            }
            break
        }
    }
}

if (-not $Model) {
    throw "No configured OpenCode model is currently available. Run list-models.ps1 and update memory/skill-configs/opencode-models.json."
}

if (-not $Variant) {
    $Variant = "high"
}

$scopeText = if ($ScopeIn.Count -gt 0) {
    ($ScopeIn | ForEach-Object { "- $_" }) -join "`n"
}
else {
    "- No explicit file scope provided."
}

$modeRules = if ($PermissionMode -eq "READ_ONLY") {
    "Do not modify files. Return findings, evidence, assumptions, unknowns, and recommended next step only."
}
else {
    "Modify only files listed in Scope in. Keep the patch minimal. Report every changed file and why it changed."
}

$subagentPrompt = @"
You are an OpenCode subagent working under Codex as the supervising main agent.

Task type: $TaskType
Permission mode: $PermissionMode

Objective:
$Prompt

Scope in:
$scopeText

Constraints:
- Codex is the main agent and owns final decisions.
- Do not make broad architecture or product decisions.
- Stay inside the objective and scope.
- $modeRules
- Be concise and evidence-based.
- State uncertainty explicitly.

Return this exact report format:

SUBAGENT_REPORT
task_type: $TaskType
permission_mode: $PermissionMode
status: completed|blocked|failed
model: $Model
summary:
- ...
evidence:
- ...
assumptions:
- ...
unknowns:
- ...
risks_or_conflicts:
- ...
confidence: high|medium|low
recommended_next_step_for_main_agent: ...
changed_files: none
END_SUBAGENT_REPORT
"@

& opencode run --model $Model --variant $Variant --format $Format $subagentPrompt
