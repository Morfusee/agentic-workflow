[private]
default:
    @just --list auth

python := if os() == "windows" { "python" } else { "python3" }

save +name:
    @{{ python }} "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" save "{{ name }}"

switch +name:
    @{{ python }} "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" switch "{{ name }}"

list:
    @{{ python }} "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" list
