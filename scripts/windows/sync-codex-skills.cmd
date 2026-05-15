@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\skills") do set "REPO_SKILLS=%%~fI"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"

if not exist "%REPO_SKILLS%" (
  echo [ERROR] Repo skills directory not found: "%REPO_SKILLS%"
  exit /b 1
)

if not exist "%CODEX_SKILLS%" (
  echo [ERROR] Codex skills directory not found: "%CODEX_SKILLS%"
  exit /b 1
)

echo Syncing repo skills from:
echo   "%REPO_SKILLS%"
echo to:
echo   "%CODEX_SKILLS%"
echo.

for /d %%D in ("%REPO_SKILLS%\*") do (
  set "NAME=%%~nxD"
  set "LINK_PATH=%CODEX_SKILLS%\!NAME!"

  if exist "!LINK_PATH!" (
    echo [SKIP] !NAME! ^(already exists in codex skills^)
  ) else (
    cmd /c mklink /J "!LINK_PATH!" "%%~fD" >nul
    if !errorlevel! equ 0 (
      echo [LINKED] !NAME!
    ) else (
      echo [ERROR] Failed to link !NAME!
    )
  )
)

echo.
echo Done.
exit /b 0
