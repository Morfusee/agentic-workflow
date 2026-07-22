[private]
default:
    @just --list auth

save +name:
    python3 "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" save "{{ name }}"

switch +name:
    python3 "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" switch "{{ name }}"

list:
    python3 "{{ justfile_directory() }}/scripts/auth/switch-accounts.py" list
