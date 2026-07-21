[private]
default:
    @just --list repo

python := if os() == "windows" { "python" } else { "python3" }

# Install the repository's path-privacy Git hook
install-hooks:
    @{{ python }} "{{ justfile_directory() }}/scripts/sync/environment.py" hooks
