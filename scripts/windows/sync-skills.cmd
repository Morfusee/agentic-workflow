@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\skills") do set "REPO_SKILLS=%%~fI"
for %%I in ("%SCRIPT_DIR%..\..\.skills.env") do set "CONFIG_FILE=%%~fI"
set "CODEX_SKILLS=%USERPROFILE%\.codex\skills"
set "OPENCODE_SKILLS=%USERPROFILE%\.config\opencode\skills"
set "INCLUDE_OPENCODE=%SYNC_OPENCODE%"

if exist "%CONFIG_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%CONFIG_FILE%") do (
    set "KEY=%%~A"
    set "VALUE=%%~B"
    if /I "!KEY!"=="SYNC_OPENCODE" if /I "%INCLUDE_OPENCODE%"=="" set "INCLUDE_OPENCODE=!VALUE!"
  )
)

if /I "%INCLUDE_OPENCODE%"=="" set "INCLUDE_OPENCODE=false"

if not exist "%REPO_SKILLS%" (
  echo [ERROR] Repo skills directory not found: "%REPO_SKILLS%"
  exit /b 1
)

if not exist "%CODEX_SKILLS%" (
  mkdir "%CODEX_SKILLS%" >nul 2>&1
)
if not exist "%CODEX_SKILLS%" (
  echo [ERROR] Unable to create target skills directory: "%CODEX_SKILLS%"
  exit /b 1
)

echo Syncing repo skills from:
echo   "%REPO_SKILLS%"
echo to:
echo   "%CODEX_SKILLS%"
if /I "%INCLUDE_OPENCODE%"=="true" (
  if not exist "%OPENCODE_SKILLS%" (
    mkdir "%OPENCODE_SKILLS%" >nul 2>&1
  )
  if not exist "%OPENCODE_SKILLS%" (
    echo [ERROR] Unable to create target skills directory: "%OPENCODE_SKILLS%"
    exit /b 1
  )
  echo   "%OPENCODE_SKILLS%"
)
echo.

for %%T in ("%CODEX_SKILLS%") do (
  echo [TARGET] %%~fT
  for /d %%D in ("%REPO_SKILLS%\*") do (
    set "NAME=%%~nxD"
    set "LINK_PATH=%%~fT\!NAME!"

    if exist "!LINK_PATH!" (
      echo [SKIP] !NAME! ^(already exists^)
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
)

if /I "%INCLUDE_OPENCODE%"=="true" (
  for %%T in ("%OPENCODE_SKILLS%") do (
    echo [TARGET] %%~fT
    for /d %%D in ("%REPO_SKILLS%\*") do (
      set "NAME=%%~nxD"
      set "LINK_PATH=%%~fT\!NAME!"

      if exist "!LINK_PATH!" (
        echo [SKIP] !NAME! ^(already exists^)
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
  )
)

echo Done.
exit /b 0
