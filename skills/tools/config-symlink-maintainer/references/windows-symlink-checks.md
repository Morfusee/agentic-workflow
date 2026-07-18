# Windows Symlink Checks

Use PowerShell-native checks and keep filesystem changes in PowerShell when working on Windows.

## Inspect A Path

```powershell
$target = "$env:LOCALAPPDATA\nvim"
$item = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
$item | Format-List FullName,LinkType,Target,Attributes
```

## Resolve A Link

```powershell
(Get-Item -LiteralPath $target -Force).ResolvedTarget
```

## Check Before Removing Or Moving

```powershell
$resolved = (Resolve-Path -LiteralPath $target).Path
$allowed = "$env:USERPROFILE\AppData\Local\nvim"
if ($resolved -ne $allowed) {
  throw "Refusing to change unexpected path: $resolved"
}
```

## Validate Repo Commands

```powershell
just --list
just sync codex
just sync opencode
just sync nvim
```

After each sync, inspect both the repo source path and external target path.
