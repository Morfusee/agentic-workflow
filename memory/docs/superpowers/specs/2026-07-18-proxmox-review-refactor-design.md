# Proxmox Review Refactor Design

## Scope

Implement all actionable findings from the Proxmox review inside the independent
`proxmox/` Ansible project. Do not change `ubuntu/`, `docker/`, or repository-wide
tooling. Work on the existing `main` branch and preserve all existing work.

The controller baseline is `ansible-core 2.20+`. Proxmox role metadata and
documentation will state that minimum, and `community.general` will be pinned to
the compatible 13.x major range so future breaking releases are not selected
implicitly.

## Architecture

Use an incremental, role-owned verification design. The firewall, repositories,
subscription-nag, Tailscale, and unattended-upgrades roles will each own a
`tasks/verify.yml` file. A role will run its own verification after applying its
desired state. The validation role will reuse those same task files through
`include_role` and retain only cross-role checks: Proxmox API reachability, core
service health, SSH configuration syntax, and the final summary.

This removes the validation role's shadow implementations without weakening the
existing fail-closed safety model. Repository and subscription-patch safeguards
remain intact and move only as needed to establish clear ownership.

## Components and Data Flow

### Firewall

Replace parsing of `ufw status verbose` with `community.general.ufw` check-mode
probes for enabled state, default policies, Tailscale-scoped management rules,
and absence of unrestricted rules. Probe `changed` values remain intact because
they are the verification signal. Remove the redundant reload handler,
`flush_handlers`, status command, regex assertions, status fact, and broad
deletion error suppression.

Move management ports and UFW policy defaults into the firewall role. Rename
`proxmox_firewall_tailscale_interface` to `proxmox_tailscale_interface` and use
it consistently across Tailscale, firewall, and validation tasks.

### Role-local Verification

Create role-owned verification for repositories, subscription patching,
Tailscale, and unattended upgrades. The validation role includes those files
only when their corresponding features are enabled. Each verification file uses
variables and implementation details owned by its role.

Move the embedded APT-source inspection program from validation YAML to a
repository-owned executable file. The repository verification task executes it,
parses its JSON output, and preserves the existing checks for exactly one active
community source and no active enterprise source.

### QEMU Guest Agent

Check `/dev/virtio-ports/org.qemu.guest_agent.0` directly. When absent, install
and enable the package/service as appropriate but emit the specific device
guidance without inferring state from localized error text. Start and validate
the service through `ansible.builtin.systemd_service` when the channel exists,
using returned state instead of duplicate `systemctl` commands.

### Common Packages and Upgrade State

Rename the base package list to `proxmox_common_packages` and add
`proxmox_extra_common_packages`. Inventory supplies only additions, preventing
replacement of role defaults. Move upgrade/reboot result defaults from
preflight to upgrade. Represent the disabled distribution-upgrade result with a
direct boolean instead of a fabricated registered-result dictionary.

### Facts and Services

Rely on play-level fact gathering for the host and guest plays and remove
redundant `setup` tasks. Gather service facts where needed and check
`pveproxy`, `pvedaemon`, `ssh`, and other services directly from
`ansible_facts.services`. Keep `sshd -t` because it validates configuration
syntax rather than service state.

### Tailscale

Require successful `tailscale status --json` commands before parsing. Use a
guarded block/rescue only where a clearer parse failure is needed. Guard parent
objects before accessing `BackendState`, use the shared Tailscale interface
variable, and standardize service management on
`ansible.builtin.systemd_service`.

### Unattended Upgrades

Remove the misleading timer reload handler and its notifications. Ensure
`apt-daily-upgrade.timer` is enabled and started explicitly when unattended
upgrades are managed. Retain the dry-run validation and move policy verification
into the role-local verification file.

### SSH

Install one owned drop-in at
`/etc/ssh/sshd_config.d/99-server-playbooks.conf` containing the managed
password-authentication and root-login settings. Validate the complete SSH
configuration before reload. Accept the public-key value through a variable
instead of performing a controller-specific lookup inside the role. Remove the
empty/comment-only role files made obsolete by this design.

### Small Cleanup

Remove empty handlers/vars files, the unused enterprise pattern if confirmed
unused, redundant setup and direct service commands, and mixed legacy service
module usage touched by this refactor. Remove `ssh_port` only if repository-wide
search confirms it is unused; otherwise wire it consistently rather than
silently changing behavior.

## Safety and Error Handling

Declarative operations fail normally. Remove `failed_when: false` where it hides
real failures, especially UFW rule deletion and Tailscale JSON reads.
Intentionally tolerated failures must be followed by explicit, actionable
classification or assertions.

Firewall activation retains the standalone-host check, explicit confirmation,
active Tailscale interface, Tailscale IPv4, and running service gates.
Repository mutation remains after all Ceph and unexpected-source guards.
Subscription patching retains exact-match requirements, backup, scoped
replacement, post-patch validation, and refusal on unknown vendor structure.

No live Proxmox mutation is part of workstation verification.

## Testing

Extend `proxmox/tests/test_playbook_policies.py` to enforce:

- role-local verification and thin validation orchestration;
- absence of UFW human-output parsing and duplicated firewall verification;
- repository ownership of the source inspector;
- `ansible-core 2.20+` metadata and compatible collection major pins;
- SSH drop-in ownership;
- removal of redundant setup calls, handlers, and direct service-state commands;
- preservation of repository and subscription safety checks.

Run the Python policy tests and parse every Proxmox YAML file. Run Ansible syntax
checks for host, guest, and site playbooks when the local Ansible runtime and
required collections are available. Finally, inspect `git diff` and confirm all
changes are inside `proxmox/`, map directly to the review, and preserve the
pre-existing untracked `repomix-output.xml`.

## Success Criteria

All twelve review areas are addressed without weakening safety checks. The
validation role is a thin orchestrator, verification logic has one owner,
Proxmox tests pass, syntax checks pass where executable, and no non-Proxmox
project files are changed.
