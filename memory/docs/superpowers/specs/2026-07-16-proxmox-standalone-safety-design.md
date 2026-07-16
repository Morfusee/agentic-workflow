# Proxmox Standalone Safety Fixes Design

## Goal

Make the Proxmox automation fail safely outside its intended standalone,
non-Ceph environment while keeping upgrades, reboots, and Tailscale enrollment
explicit and predictable.

## Agreed Scope

The project targets one standalone Proxmox VE host. It does not support a
Proxmox cluster or Ceph. The existing subscription-warning patch remains
enabled and is not part of this change. Repository channel reversibility,
effective OpenSSH policy validation, collection pinning, CI, and Molecule are
also outside this focused change.

## Approaches Considered

### Ceph

1. Add complete release-aware Ceph no-subscription repository management.
2. Leave Ceph repositories untouched and fail when Ceph is detected.
3. Silently ignore Ceph.

Choose option 2. The user does not use Ceph, and incomplete Ceph management is
more dangerous than refusing an unsupported host. Detection happens before any
repository mutation. The role fails when it finds a Ceph repository, a
Proxmox-managed Ceph configuration, or installed Ceph server daemons. It never
edits a Ceph source. Remove the misleading `proxmox_manage_ceph_repository`
setting.

### Firewall

1. Build cluster-aware UFW rules.
2. Rely on the earlier preflight play.
3. Put an unconditional standalone-host guard inside the firewall role.

Choose option 3. Whenever UFW activation is requested, the firewall role checks
for `/etc/pve/corosync.conf` before any firewall mutation. If the file exists,
the role fails and leaves UFW unchanged. No cluster ports or network model are
added.

### Tailscale

1. Model every possible Tailscale preference and recovery state.
2. Keep requiring an auth key for every run.
3. Support the two expected states and fail on everything else.

Choose option 3. A `Running` backend needs no auth key; the role applies only
its owned preferences with `tailscale set` (`ssh` and `accept-dns`). A
`NeedsLogin` backend requires the environment auth key and uses `tailscale up`
with those same owned preferences. Missing, malformed, stopped, or otherwise
unexpected states fail with a recovery message rather than attempting
enrollment. The final status and Tailscale IPv4 checks remain authoritative.

## Component Changes

### Repository role

- Continue detecting PVE and Ceph source files read-only.
- Detect unsupported Ceph before disabling any enterprise PVE entry.
- Treat any Ceph APT source, `/etc/pve/ceph.conf`, or installed Ceph server
  daemon package (`ceph-mon`, `ceph-osd`, `ceph-mgr`, or `ceph-mds`) as
  unsupported.
- Fail with a clear standalone/non-Ceph scope message.
- Never add, disable, rewrite, or remove a Ceph repository.
- Remove `proxmox_manage_ceph_repository` from role and inventory defaults.

### Firewall role

- When `proxmox_enable_firewall` is false, preserve the current no-op behavior.
- When it is true, stat `/etc/pve/corosync.conf` before any UFW mutation.
- Assert that no Corosync configuration exists.
- Preserve the existing Tailscale interface, service, explicit-confirmation,
  management-port, and UFW validation gates.

### Upgrade role

- Set `proxmox_run_dist_upgrade` to false in role and inventory defaults.
- Set `proxmox_reboot_after_upgrade` to false in role and inventory defaults.
- Preserve existing upgrade and reboot behavior when an operator explicitly
  enables either variable.
- Remove the upgrade role from the default Phase 1 tagged command.
- Document a separate optional maintenance command that includes preflight,
  repositories, upgrade, and validation and requires the operator to set the
  desired variables deliberately.

### Tailscale role

- Install and start Tailscale before checking backend state.
- Parse `tailscale status --json` and fail if it cannot be read.
- Store the exact backend state.
- For `Running`, run one `tailscale set` command covering SSH and DNS
  preferences without requiring an auth key.
- For `NeedsLogin`, require `TAILSCALE_AUTHKEY` and run `tailscale up` with the
  SSH and DNS preferences.
- For every other backend state, fail without running `tailscale up`.
- Preserve secret redaction and final service, status, interface, and IPv4
  validation.

### QEMU Guest Agent role

- Keep the non-fatal service start so the result can be classified.
- Build a combined diagnostic string from the module result.
- Continue warning for the known missing virtio-channel condition.
- Fail when service startup fails for any other reason.
- Verify that the service is active when startup succeeds; retain the enabled
  check in all supported QEMU guests.

### Documentation

- State that this automation supports standalone, non-Ceph Proxmox only.
- Explain the firewall refusal on clustered hosts.
- Document that upgrades and reboots default off.
- Move upgrade execution into an explicit optional maintenance step.
- Explain that enrolled/running Tailscale hosts do not need the auth key on
  reruns and that unexpected backend states stop safely.

## Error Handling

All new safety checks fail before the related destructive action. Ceph
detection fails before repository edits, cluster detection fails before UFW
edits, unexpected Tailscale states fail before enrollment, and unknown guest
agent failures fail instead of being converted to success. Error messages name
the detected condition and the manual action required.

## Validation

- Parse all Ubuntu and Proxmox YAML files locally.
- Run `git diff --check`.
- Confirm no Ceph mutation task remains.
- Confirm upgrade and reboot defaults are false in both locations.
- Confirm the firewall Corosync check precedes all UFW mutation tasks.
- Confirm the Tailscale auth-key assertion is reachable only for `NeedsLogin`.
- Confirm unknown guest-agent startup failures are fatal.
- Run Ansible syntax checks only if Ansible is already available.
- Do not execute any playbook against a live host.

## Success Criteria

The default host workflow performs no distribution upgrade, no reboot, no SSH
hardening, and no firewall activation. A running Tailscale node can be rerun
without an auth key. Ceph, clustered firewall activation, unexpected Tailscale
states, and unknown guest-agent startup failures stop with clear errors before
unsafe mutation.
