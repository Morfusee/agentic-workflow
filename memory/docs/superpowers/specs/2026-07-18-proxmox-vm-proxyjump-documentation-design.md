# Proxmox VM ProxyJump Documentation Design

## Goal

Document how to run the Ubuntu Ansible playbook against a private VM inside Proxmox when SSH access requires a jump through the Proxmox host. The guidance must preserve automatic loading of `ubuntu/group_vars/all.yml`, including existing Tailscale settings.

## Scope

Update only `ubuntu/README.md`. Do not change the inventory, playbook, roles, or variables.

## Documentation Structure

Add a `Proxmox VMs Through a Jump Host` section near the general playbook-running instructions. The section will:

1. Explain the connection path with the concrete example `morfuse@px` to `morfuse@10.77.0.10`.
2. Recommend a persistent named entry in `ubuntu/hosts` using `ansible_host`, `ansible_user`, and `ansible_ssh_common_args` with OpenSSH `ProxyJump`.
3. Show the normal `ansible-playbook` command using `-l` and the inventory alias.
4. Show the one-off alternative using both `-i hosts` and `-i '10.77.0.10,'`.
5. Warn that using only the inline inventory replaces the configured inventory source and can prevent `group_vars/all.yml` from loading, producing errors such as `'ssh_via' is undefined`.
6. Mention `-K` for a VM account that requires a sudo password.

## Example

The persistent inventory example will use a descriptive alias such as `proxmoxvm` and the user's real connection values. The text will tell readers to replace the user, jump-host alias, VM address, and inventory alias for other environments.

## Verification

Review the rendered Markdown structure and commands, then inspect the final Git diff. Confirm that only `ubuntu/README.md` changes in the server-playbooks repository and that all pre-existing user changes remain untouched.
