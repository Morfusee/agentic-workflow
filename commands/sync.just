[private]
default:
    @just --list sync

# Sync the complete environment
environment:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" all

# Sync memory links
memory:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" memory

# Sync OpenCode configuration
opencode:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" opencode

# Sync Codex configuration
codex:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" codex

# Sync skill links
skills:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" skills

# Sync Neovim configuration
nvim:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" nvim
