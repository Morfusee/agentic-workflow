[private]
default:
    @just --list auth

# Save current Codex + OpenCode auth into a named profile
save +name:
    @if [ "{{ os() }}" == "windows" ]; then \
      pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" save "{{ name }}"; \
    else \
      echo "auth save: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
    fi

# Switch Codex + OpenCode auth to a saved profile
switch +name:
    @if [ "{{ os() }}" == "windows" ]; then \
      pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" switch "{{ name }}"; \
    else \
      echo "auth switch: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
    fi

# List saved auth profiles
list:
    @if [ "{{ os() }}" == "windows" ]; then \
      pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{ justfile_directory() }}/scripts/auth/switch-accounts.ps1" list; \
    else \
      echo "auth list: Windows-only for now. Run scripts/auth/switch-accounts.ps1 manually."; \
    fi
