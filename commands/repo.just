[private]
default:
    @just --list repo
# Install the repository's path-privacy Git hook
install-hooks:
    @python "{{ justfile_directory() }}/scripts/sync/environment.py" hooks
