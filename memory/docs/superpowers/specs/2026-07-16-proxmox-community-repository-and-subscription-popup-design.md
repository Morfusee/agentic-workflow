# Proxmox Community Repository and Subscription Popup Design

## Objective

Configure the standalone Proxmox VE host to use exactly one community `pve-no-subscription` repository and suppress the no-subscription popup through a narrowly scoped, verified UI patch.

The implementation will be made in the WSL-mounted `server-playbooks` repository and then applied to the Proxmox host through the existing Ansible playbook. It must not reboot the host or its guests.

## Current State

- Proxmox VE 9.2.4 is installed on the host.
- The host has no subscription key, which is intentional.
- Two files currently declare the same active `pve-no-subscription` repository:
  - `/etc/apt/sources.list.d/proxmox.sources`
  - `/etc/apt/sources.list.d/pve-no-subscription.sources`
- The subscription role recognizes only the older `status !== 'Active'` widget signature.
- Proxmox 9.2.4 uses `res.data.status.toLowerCase() !== 'active'` inside `Proxmox.Utils.checked_command`.
- The active widget file is package-original and no Ansible backup currently exists.

## Repository Design

The existing `/etc/apt/sources.list.d/proxmox.sources` file will be the canonical Proxmox PVE repository file on this host. For the `no-subscription` channel, the playbook will manage one deb822 stanza containing:

```text
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

Before mutation, the role will continue to detect Ceph sources, Ceph configuration, and Ceph server packages and stop if any are present.

The role will inspect existing PVE source files before deciding what to change. It will preserve Debian, Debian security, Tailscale, and unrelated repository definitions. It will remove `/etc/apt/sources.list.d/pve-no-subscription.sources` only when that file matches the recognized role-owned no-subscription content. Unexpected content will cause a failure instead of deletion.

Deb822 changes must be stanza-scoped. The implementation must not globally replace every `Enabled:` line in a file merely because one stanza references the enterprise PVE repository.

After configuration, validation will normalize active APT entries and require:

- exactly one active `download.proxmox.com/debian/pve` entry for the detected Debian codename;
- component `pve-no-subscription`;
- no active `enterprise.proxmox.com/debian/pve` entry;
- no duplicate normalized PVE repository targets;
- a successful `apt-get update`.

The enterprise-error match will normalize a missing regex result to an empty string before applying `length`, avoiding a `NoneType` failure.

## Subscription Popup Design

The playbook will continue to modify `/usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js`, but only within the `Proxmox.Utils.checked_command` implementation.

Supported signatures will include:

- older Proxmox: `res.data.status !== 'Active'` or equivalent `data.status !== 'Active'`;
- Proxmox 9.2: `res.data.status.toLowerCase() !== 'active'`.

The role will:

1. Read the widget file and isolate the `checked_command` block.
2. Count supported subscription-status predicates inside that block.
3. Require exactly one supported predicate when popup removal is enabled.
4. Create the original-file backup before mutation.
5. Replace only the matched predicate, leaving other subscription-state calculations untouched.
6. Re-read the widget and assert that the `checked_command` popup predicate is disabled.
7. Restart `pveproxy` and require the service to return active.

An unsupported future widget signature will fail clearly rather than letting the playbook report success while leaving the popup active.

Package upgrades may restore the vendor JavaScript. The subscription role therefore remains after the upgrade role and must be rerun following toolkit updates performed outside this playbook.

## Verification

Local verification will include:

- clean, scoped diff review;
- syntax checking of `playbooks/site.yml` with the project config and roles path supplied explicitly in WSL;
- fixture-based checks for the older and Proxmox 9.2 widget signatures;
- fixture coverage proving unrelated subscription expressions are not modified;
- repository fixtures covering a canonical no-subscription source, the known duplicate, and a multi-stanza deb822 file.

The server application will use only the required tags:

```text
preflight,repositories,subscription_nag,validation
```

Post-application verification will require:

- exactly one active PVE no-subscription repository;
- no active enterprise PVE repository;
- successful APT metadata refresh;
- a patched and verified `checked_command` block;
- active `pveproxy`;
- no reboot and no guest state changes.

## Expected Operational Effects

- The recognized duplicate repository file will be removed.
- The canonical `proxmox.sources` file will represent the community channel.
- APT metadata will be refreshed.
- The Proxmox widget JavaScript will be backed up and patched.
- `pveproxy` will briefly restart, which may momentarily reconnect the browser UI.
- The Proxmox host and all guests will remain running.

## Exclusions

- No enterprise subscription will be configured.
- The `pvetest` repository will not be enabled.
- No distribution upgrade, reboot, SSH-hardening change, firewall change, or guest configuration change is part of this work.
- Unrelated audit findings will not be changed in this implementation.
