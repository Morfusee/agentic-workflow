# Segregate Ubuntu and Proxmox Ansible Automation

## Context

`server-playbooks` currently contains one working Ubuntu Ansible project at the
repository root. The requested change adds a separate Proxmox VE project while
preserving the Ubuntu project byte-for-byte. The repository also contains a
root-level Docker SSH test harness that must remain in place and an Ubuntu VPS
verification checklist that will move to `docs/`.

The original access design specified normal OpenSSH through Tailscale. The
approved revision changes Proxmox to use the same Tailscale SSH model as the
Ubuntu automation: Tailscale manages SSH authentication and authorization,
tailnet ACLs control access, and the controller's local ED25519 public key is
not required for Proxmox connections.

## Goals

- Move the existing Ubuntu project under `ubuntu/` without changing the
  contents of any moved Ubuntu file.
- Move `VPS_VERIFICATION_CHECKLIST.md` to
  `docs/VPS_VERIFICATION_CHECKLIST.md` without changing its contents.
- Leave the root `docker/` directory untouched.
- Create a fully independent `proxmox/` Ansible project with its own
  configuration, inventory, variables, playbooks, and roles.
- Provision Proxmox repositories, upgrades, optional subscription-warning
  removal, Tailscale SSH, UFW, unattended security updates, and validation.
- Configure QEMU Guest Agent support on Proxmox VMs without treating LXC
  containers as QEMU VMs.
- Stage access hardening so the current SSH path remains available until a
  separate Tailscale SSH session is manually verified.
- Preserve the requested focused Git history and perform local validation only.

## Non-Goals

- Do not run any playbook against a live Proxmox host.
- Do not modify, refactor, or repair unrelated Ubuntu automation.
- Do not install Fail2Ban, Docker, or developer tooling on Proxmox.
- Do not share live role paths or variable paths between the projects; copied
  role directories remain independent project-owned files.
- Do not commit passwords, private keys, Tailscale auth keys, or other secrets.
- Do not enable the Proxmox-native firewall in this task.
- Do not automatically enable UFW on the first run.

## Approved Repository Boundaries

The existing Ubuntu project moves with `git mv`:

```text
ansible.cfg       -> ubuntu/ansible.cfg
hosts             -> ubuntu/hosts
requirements.yml -> ubuntu/requirements.yml
group_vars/       -> ubuntu/group_vars/
playbooks/        -> ubuntu/playbooks/
roles/            -> ubuntu/roles/
vagrant/          -> ubuntu/vagrant/
README.md         -> ubuntu/README.md
```

The moved Ubuntu files retain their exact contents and their existing relative
role references. The Ubuntu project is run from inside `ubuntu/`.

The checklist moves separately:

```text
VPS_VERIFICATION_CHECKLIST.md -> docs/VPS_VERIFICATION_CHECKLIST.md
```

Its contents remain unchanged. Repository-wide search found no existing
references that require rewriting; the new root README links to the new path.
The root `docker/` directory and its contents remain untouched. Existing
untracked user-owned files, including `repomix-output.xml`, remain untouched.

The new root README describes the two independent projects, their commands,
the checklist location, and the fact that no role or variable paths are
shared.

## Proxmox Project Structure

```text
proxmox/
├── README.md
├── ansible.cfg
├── requirements.yml
├── inventory/
│   ├── hosts.yml
│   ├── group_vars/
│   │   ├── proxmox_hosts.yml
│   │   └── proxmox_guests.yml
│   └── host_vars/
│       └── pve1.yml.example
├── playbooks/
│   ├── site.yml
│   ├── host.yml
│   └── guests.yml
└── roles/
    ├── preflight/
    ├── repositories/
    ├── upgrade/
    ├── subscription_nag/
    ├── common/
    ├── users/
    ├── ssh/
    ├── tailscale/
    ├── firewall/
    ├── unattended_upgrades/
    ├── validation/
    └── qemu_guest_agent/
```

`proxmox/ansible.cfg` uses the Proxmox inventory and role path only:

```ini
[defaults]
inventory = ./inventory/hosts.yml
roles_path = ./roles
host_key_checking = True
retry_files_enabled = False
interpreter_python = auto_silent
```

The Proxmox requirements include only the collections used by this project:
`community.general` and `ansible.posix`.

The example inventory defines `pve1` with a placeholder address, root
connection, and Python 3. The guest group is valid while empty. The example
host variables contain no credentials or keys.

## Independent Reusable Roles

The Ubuntu `common`, `users`, and `ssh` roles are copied into
`proxmox/roles/`. Their task contents are not modified. The copies are
Proxmox-owned and may diverge in future work. No other Ubuntu role is copied.

The Proxmox variables override the copied common package defaults with a
hypervisor-safe list containing ACL support, certificates, curl, Git, OpenSSH,
sudo, UFW, and unattended-upgrades. Because Fail2Ban is absent from that
override and no Proxmox Fail2Ban role exists, Proxmox does not install it.

The copied SSH role's authorized-key task is conditional on
`ssh_via == "openssh"`. With the approved Proxmox value of
`ssh_via: tailscale`, it does not read the controller's local ED25519 key.
Its hardening tasks remain available for the second phase.

## Access Model and Phased Workflow

Proxmox uses:

```yaml
ssh_via: tailscale
proxmox_tailscale_enable_ssh: true
proxmox_harden_sshd: false
proxmox_enable_firewall: false
proxmox_firewall_confirm_tailscale_access: false
```

The Tailscale role reads `TAILSCALE_AUTHKEY` from the controller environment,
installs the official Debian repository and `tailscale`, enables `tailscaled`,
and brings the node up with Tailscale SSH enabled. Auth-key tasks use
`no_log: true`. Reruns inspect the existing connection and do not re-authenticate
an already connected node.

Tailscale ACL/SSH policy is external to this repository. Documentation tells
the operator to grant the source identity access to the Proxmox node on port 22
and to the configured Unix management user. The controller's local SSH key is
not a Proxmox prerequisite.

### Phase 1: Bootstrap

The safe first run configures everything that does not require disabling the
current SSH path:

```bash
ansible-playbook playbooks/host.yml \
  --tags preflight,repositories,upgrade,subscription_nag,common,users,tailscale,unattended_upgrades,validation
```

This phase validates Tailscale, leaves `sshd` hardening disabled, and leaves
UFW disabled. The existing SSH session remains available while the operator
opens a second terminal and verifies Tailscale SSH and the Proxmox GUI.

### Phase 2: SSH hardening

After manual verification succeeds, set `proxmox_harden_sshd: true` and run:

```bash
ansible-playbook playbooks/host.yml --tags ssh,validation
```

The playbook-level gate skips the copied SSH role until this variable is true.
When enabled, the unchanged copied role disables password authentication, sets
`PermitRootLogin prohibit-password`, validates `sshd`, and restarts SSH only
when necessary.

### Phase 3: UFW activation

Only after verifying a fresh Tailscale SSH session and GUI session, set both
firewall confirmation variables to true and run:

```bash
ansible-playbook playbooks/host.yml --tags firewall,validation
```

The firewall permits TCP 22 and 8006 only on `tailscale0`, optionally permits
UDP 41641 for direct Tailscale connectivity, removes unrestricted host rules
for SSH and the Proxmox GUI, and applies incoming-deny, outgoing-allow, and
routed-allow defaults. It prints a warning to test new sessions before closing
the original one.

## Host Playbook and Roles

`host.yml` targets `proxmox_hosts`, uses `become`, `serial: 1`, and
`any_errors_fatal: true`. The approved order is:

```text
preflight
→ repositories
→ upgrade
→ subscription_nag
→ common
→ users
→ tailscale
→ ssh (gated by proxmox_harden_sshd)
→ firewall
→ unattended_upgrades
→ validation
```

Moving Tailscale before SSH ensures a full run does not attempt SSH hardening
before Tailscale has been configured. The explicit hardening gate still
protects a fresh bootstrap from closing its current access path.

### Preflight

The read-only preflight role gathers normal facts, asserts Debian-based
operation and an installed `pve-manager`, runs `pveversion`, captures the
Proxmox version and Debian codename from `/etc/os-release`, checks `/etc/pve`,
detects cluster membership, and verifies `pveproxy` or its service exists. When
`proxmox_expect_single_node` is true, a detected multi-node cluster fails
before any mutation. It ends with a concise summary.

### Repositories

The repository role detects the Debian codename and whether the host uses
legacy `.list` files or deb822 `.sources` files. It disables the PVE enterprise
source without deleting unmanaged files, adds a managed no-subscription source
in the matching format, and runs `apt update`.

Ceph is inspected before any Ceph change. When Ceph is absent and no Ceph source
is configured, no Ceph repository is added. When an enterprise Ceph source
exists, only that source is disabled or replaced safely. No release codename or
Ceph release is hardcoded. Authentication errors remaining after `apt update`
fail the role. Repeated runs make no duplicate changes.

### Upgrade

When `proxmox_run_dist_upgrade` is true, the upgrade role runs an intentional
APT `dist-upgrade`, records whether packages changed, checks for a reboot
requirement, and reboots only when a change or reboot marker exists and
`proxmox_reboot_after_upgrade` is true. It uses `ansible.builtin.reboot`, waits
up to `proxmox_reboot_timeout`, confirms reachability, and runs `pveversion`
after the reboot. It does not implement unattended Proxmox upgrades.

### Subscription warning

The optional subscription-nag role inspects
`/usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js`. When enabled, it
backs up the file, detects an already patched state, and applies a guarded
replacement only for recognized Proxmox 8 subscription-check patterns. An
absent expected pattern produces a warning and leaves the file untouched. The
role restarts and validates `pveproxy` only after a successful file change.

### Tailscale

The dedicated Proxmox Tailscale role uses the detected Debian codename for the
official repository, installs and starts `tailscaled`, and configures Tailscale
SSH without exposing the auth key. It verifies the daemon, JSON status,
`tailscale0`, and a Tailscale IPv4 address, then exposes that address as a fact
for firewall and validation roles. It uses `--accept-dns=false` by default and
does not require a controller public key.

### Unattended upgrades

The role manages `20auto-upgrades` and `50unattended-upgrades` directly. It
enables daily package-list refreshes and checks, restricts upgrades to Debian
security updates, performs periodic cleanup, disables automatic reboot, and
blacklists Proxmox and virtualization packages. It runs a safe dry-run/debug
validation without failing when no packages are available.

### Validation

The validation role is read-only. It checks Proxmox version, `pveproxy`,
`pvedaemon`, SSH, `sshd -t`, Tailscale state when enabled, the local API at
`https://127.0.0.1:8006/api2/json/version` with certificate validation disabled
only for that self-signed local check, UFW state and interface rules when
managed, unattended-upgrade configuration, and repository state. Its summary
includes Proxmox version, Debian codename, Tailscale IP, firewall status,
upgrade status, reboot status, and unattended-upgrade status.

## Guest Agent Workflow

`guests.yml` contains two plays because the QEMU configuration change happens
on the Proxmox host while package installation happens inside the guest VM.

The first play targets `proxmox_hosts`, iterates over
`groups['proxmox_guests']`, and skips entries without `proxmox_vmid`. For each
VMID it checks `qm config` first. It runs `qm set <vmid> --agent enabled=1`
only when the ID is confirmed to be a QEMU VM and the agent is not already
enabled. It checks `pct config` to recognize LXC guests and never runs `qm set`
against them. Unknown or non-QEMU entries receive clear warnings.

The second play targets `proxmox_guests` and applies `qemu_guest_agent`. The
role asserts Debian or Ubuntu, installs `qemu-guest-agent`, enables the
service, starts it when supported, tolerates the valid pre-channel connection
condition, and verifies package installation plus service enablement. An empty
guest group skips cleanly.

Each guest inventory entry may define:

```yaml
proxmox_vmid: 100
proxmox_node: pve1
```

`site.yml` imports `host.yml` and `guests.yml` to provide the complete
orchestration entry point. The documentation recommends staged `host.yml`
execution for a fresh host and explains that `site.yml` may intentionally
upgrade and reboot an existing Proxmox host.

## Documentation and Ignore Rules

`proxmox/README.md` documents collection installation, the required
`TAILSCALE_AUTHKEY` environment variable without a real key, syntax checks,
the three-phase access workflow, Tailscale ACL prerequisites, guest-agent
execution, GUI/manual verification, and the full `site.yml` workflow.

The root `.gitignore` keeps existing behavior and adds retry files, vault
artifacts, the vault password file, and real Proxmox host variable files while
allowing `*.yml.example` inventory templates to remain tracked.

## Git Workflow

Implementation occurs on the explicitly requested branch
`feat/segregate-ubuntu-proxmox` with these focused commits:

1. `refactor: move existing ubuntu playbooks`
2. `feat: scaffold proxmox ansible project`
3. `feat: add proxmox host provisioning roles`
4. `feat: add proxmox guest agent automation`
5. `docs: document ubuntu and proxmox workflows`

The checklist move and root documentation updates belong in the documentation
commit. The migration commit must be inspectable as 100% renames for the
existing Ubuntu files.

## Verification

Run only local checks:

- `git diff --check` from the repository root.
- Ubuntu collection installation and playbook syntax check from `ubuntu/`.
- Proxmox collection installation and syntax checks for `host.yml`,
  `guests.yml`, and `site.yml` from `proxmox/`.
- `ansible-lint` for the three Proxmox playbooks when already installed.
- Rename summary and numstat checks using `--find-renames=100%`.
- Repository-wide searches for Ubuntu role references, symlinks, secrets,
  Docker/Fail2Ban installation in Proxmox, and references to the old checklist
  path.

If Ansible or ansible-lint is unavailable locally, report that limitation and
complete the static and Git checks without installing unrelated runtime
dependencies. No live host execution is part of this task.

## Risks and Mitigations

- The largest migration risk is accidental content modification; use `git mv`,
  inspect rename detection, and compare moved blobs.
- The largest access risk is losing the initial SSH path; keep SSH hardening
  gated, keep UFW disabled, and require a manual Tailscale SSH test.
- The largest repository risk is enabling enterprise or Ceph sources
  incorrectly; detect source format and existing Ceph configuration before
  managing anything.
- The subscription patch could be overwritten or become incompatible; backup,
  match known patterns only, warn on unknown versions, and validate `pveproxy`.
- Guest automation could mistake an LXC for a VM; check `qm` and `pct` before
  any `qm set` operation.
