alias se := sync-environment
alias ss := sync-skills
alias so := sync-opencode
alias sc := sync-codex
alias sp := skills-open
alias oc := opencode-config
alias as := auth-save
alias aw := auth-switch
alias al := auth-list

default:
  @just --list

# Canonical all-in-one environment sync command
sync-environment:
  @python scripts/sync_environment.py all

# Sync skills symlinks into tool config paths
sync-skills:
  @python scripts/sync_environment.py skills

# Sync repo configs/opencode/* into ~/.config/opencode/
sync-opencode:
  @python scripts/sync_environment.py opencode

# Sync repo configs/codex/* into ~/.codex/
sync-codex:
  @python scripts/sync_environment.py codex

# Save current Codex + OpenCode auth into a named profile
auth-save +name:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File scripts/switch-accounts.ps1 save {{ name }}; \
  else \
    echo "auth-save: Windows-only for now. Run scripts/switch-accounts.ps1 manually."; \
  fi

# Switch Codex + OpenCode auth to a saved profile
auth-switch +name:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File scripts/switch-accounts.ps1 switch {{ name }}; \
  else \
    echo "auth-switch: Windows-only for now. Run scripts/switch-accounts.ps1 manually."; \
  fi

# List saved auth profiles
auth-list:
  @if [ "{{ os() }}" == "windows" ]; then \
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File scripts/switch-accounts.ps1 list; \
  else \
    echo "auth-list: Windows-only for now. Run scripts/switch-accounts.ps1 manually."; \
  fi

# Serve OpenCode bound to the current machine's Tailscale IPv4
serve:
  opencode serve --port 6767 --hostname $(tailscale ip -4)

# -----------------------------------------------------------------------
# Windows-only recipes
# -----------------------------------------------------------------------

# Open mirrored skills folders in default file manager
skills-open:
  @if [ "{{ os() }}" == "windows" ]; then \
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$codex = Join-Path $env:USERPROFILE ".codex\\skills"; explorer $codex; if ((Test-Path ".\\.skills.env") -and ((Get-Content ".\\.skills.env" | Where-Object { $_ -match "^\\s*SYNC_OPENCODE\\s*=\\s*true\\s*$" }).Count -gt 0)) { $open = Join-Path $env:USERPROFILE ".config\\opencode\\skills"; explorer $open }'; \
  else \
    xdg-open ~/.codex/skills 2>/dev/null; \
    if [ -f .skills.env ] && grep -qi '^\s*SYNC_OPENCODE\s*=\s*true\s*$' .skills.env 2>/dev/null; then \
      xdg-open ~/.config/opencode/skills 2>/dev/null; \
    fi; \
  fi

# Open opencode's config file in the default editor
opencode-config:
  @if [ "{{ os() }}" == "windows" ]; then \
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command '$$code = Join-Path $$env:LOCALAPPDATA "Programs\Microsoft VS Code\bin\code.cmd"; $$target = Join-Path $$env:USERPROFILE ".config\opencode\opencode.jsonc"; & $$code $$target'; \
  else \
    ${EDITOR:-nano} ~/.config/opencode/opencode.jsonc; \
  fi
