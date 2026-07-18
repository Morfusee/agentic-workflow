[private]
default:
    @just --list config

# Open mirrored skills folders in the default file manager
open-skills:
    @if [ "{{ os() }}" == "windows" ]; then \
      powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$$repo = "{{ justfile_directory() }}"; $$codex = Join-Path $$env:USERPROFILE ".codex\skills"; explorer $$codex; $$envFile = Join-Path $$repo ".skills.env"; if ((Test-Path $$envFile) -and ((Get-Content $$envFile | Where-Object { $$_ -match "^\s*SYNC_OPENCODE\s*=\s*true\s*$$" }).Count -gt 0)) { $$open = Join-Path $$env:USERPROFILE ".config\opencode\skills"; explorer $$open }'; \
    else \
      xdg-open ~/.codex/skills 2>/dev/null; \
      if [ -f "{{ justfile_directory() }}/.skills.env" ] && grep -qi '^\s*SYNC_OPENCODE\s*=\s*true\s*$' "{{ justfile_directory() }}/.skills.env" 2>/dev/null; then \
        xdg-open ~/.config/opencode/skills 2>/dev/null; \
      fi; \
    fi

# Open OpenCode's configuration file in the default editor
open-opencode:
    @if [ "{{ os() }}" == "windows" ]; then \
      powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$$code = Join-Path $$env:LOCALAPPDATA "Programs\Microsoft VS Code\bin\code.cmd"; $$target = Join-Path $$env:USERPROFILE ".config\opencode\opencode.jsonc"; & $$code $$target'; \
    else \
      $${EDITOR:-nano} ~/.config/opencode/opencode.jsonc; \
    fi
