# Proxmox Standalone Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Proxmox project explicitly safe for one standalone, non-Ceph host while making upgrades, Tailscale enrollment, and guest-agent failures predictable.

**Architecture:** Add fail-closed checks at the role that owns each risky mutation. Remove incomplete Ceph management, make upgrades/reboots opt-in, model only the expected Tailscale states, classify guest-agent startup failures, and update the operator documentation.

**Tech Stack:** Ansible YAML, Proxmox VE APT/UFW, Tailscale CLI, systemd, Git, Ruby YAML parser for local static validation.

---

## Execution Rules

- Work on branch `codex/proxmox-standalone-safety` in an isolated worktree.
- Preserve the existing untracked `repomix-output.xml` in the main checkout.
- Do not edit `ubuntu/`, root `docker/`, or the subscription-warning role.
- Do not run a playbook against a live host.
- Use `apply_patch` for authored changes.
- Run `git diff --check` and static YAML parsing after each focused change.

## File Map

- Modify `proxmox/roles/repositories/defaults/main.yml` and `tasks/main.yml` for non-Ceph fail-closed behavior.
- Modify `proxmox/roles/firewall/tasks/main.yml` for an in-role standalone-host guard.
- Modify `proxmox/roles/upgrade/defaults/main.yml` and `proxmox/inventory/group_vars/proxmox_hosts.yml` for opt-in upgrades/reboots.
- Modify `proxmox/roles/tailscale/tasks/main.yml` for Running/NeedsLogin state handling.
- Modify `proxmox/roles/qemu_guest_agent/tasks/main.yml` for classified startup failures and active-state validation.
- Modify `proxmox/README.md` for the final operating contract.

## Task 1: Establish the isolated implementation workspace

- [ ] Verify `.worktrees/` is ignored with `git check-ignore .worktrees`.
- [ ] Create `.worktrees/proxmox-standalone-safety` on branch `codex/proxmox-standalone-safety`.
- [ ] Confirm the worktree has no tracked diff.
- [ ] Parse the current YAML baseline with Ruby and record that Ansible syntax checks are unavailable if `ansible-playbook` is not installed.

## Task 2: Remove incomplete Ceph management and fail closed

**Files:**

- Modify `proxmox/roles/repositories/defaults/main.yml`
- Modify `proxmox/roles/repositories/tasks/main.yml`
- Modify `proxmox/inventory/group_vars/proxmox_hosts.yml`

- [ ] Remove `proxmox_manage_ceph_repository` from both defaults files.
- [ ] Change the Ceph source scan to detect any Proxmox Ceph source, not only enterprise:

```yaml
- name: Detect Proxmox Ceph source files
  ansible.builtin.command:
    argv:
      - grep
      - -E
      - "proxmox[.]com/debian/ceph"
      - "{{ item.path }}"
```

- [ ] Stat `/etc/pve/ceph.conf` and derive installed server packages:

```yaml
- name: Inspect the Proxmox Ceph configuration
  ansible.builtin.stat:
    path: /etc/pve/ceph.conf
  register: proxmox_ceph_config

- name: Store detected Ceph server packages
  ansible.builtin.set_fact:
    proxmox_ceph_server_packages: >-
      {{ ['ceph-mon', 'ceph-osd', 'ceph-mgr', 'ceph-mds']
         | select('in', ansible_facts.packages.keys() | list) | list }}
```

- [ ] Before any repository mutation, assert that no Ceph source, config, or server package exists:

```yaml
- name: Require a standalone non-Ceph Proxmox host
  ansible.builtin.assert:
    that:
      - proxmox_ceph_source_paths | length == 0
      - not (proxmox_ceph_config.stat.exists | bool)
      - proxmox_ceph_server_packages | length == 0
    fail_msg: >-
      This project supports standalone non-Ceph Proxmox hosts only. Ceph was
      detected, so repository changes were stopped before mutation.
```

- [ ] Delete the `proxmox_manage_ceph` calculation and every task that adds Ceph paths to the enterprise paths-to-disable list. Keep PVE enterprise source handling unchanged.
- [ ] Verify no task mutates a Ceph source:

```powershell
rg -n "manage_ceph|enterprise_paths_to_disable.*ceph|debian/ceph" proxmox/roles/repositories proxmox/inventory/group_vars/proxmox_hosts.yml
```

Expected: only read-only Ceph detection remains.

## Task 3: Put the standalone guard inside the firewall role

**File:** `proxmox/roles/firewall/tasks/main.yml`

- [ ] Add these tasks immediately after the disabled-phase message and before any UFW task:

```yaml
- name: Check whether this host has Proxmox cluster configuration
  ansible.builtin.stat:
    path: /etc/pve/corosync.conf
  register: proxmox_firewall_corosync_config
  when: proxmox_enable_firewall | bool

- name: Refuse UFW activation on a clustered Proxmox host
  ansible.builtin.assert:
    that:
      - not (proxmox_firewall_corosync_config.stat.exists | bool)
    fail_msg: >-
      UFW activation stopped before mutation because /etc/pve/corosync.conf
      exists. This project supports one standalone Proxmox host only.
  when: proxmox_enable_firewall | bool
```

- [ ] Confirm the stat/assert tasks occur before every `community.general.ufw` task.

## Task 4: Make upgrades and reboots opt-in

**Files:**

- Modify `proxmox/roles/upgrade/defaults/main.yml`
- Modify `proxmox/inventory/group_vars/proxmox_hosts.yml`
- Modify `proxmox/README.md`

- [ ] Set both defaults to false in both YAML files:

```yaml
proxmox_run_dist_upgrade: false
proxmox_reboot_after_upgrade: false
```

- [ ] Remove `upgrade` from the Phase 1 tag list in the README.
- [ ] Add an optional maintenance section that instructs the operator to verify backups and maintenance timing, set the two variables deliberately, and run:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/host.yml --tags preflight,repositories,upgrade,validation
```

- [ ] State explicitly that package upgrades and reboots are disabled by default.

## Task 5: Simplify Tailscale state and auth-key handling

**File:** `proxmox/roles/tailscale/tasks/main.yml`

- [ ] Remove the auth-key assertion from the top of the role.
- [ ] Keep repository installation, package installation, and service startup unchanged.
- [ ] After `tailscale status --json`, assert that output is JSON before parsing:

```yaml
- name: Require a readable Tailscale backend status
  ansible.builtin.assert:
    that:
      - proxmox_tailscale_status_before.stdout | trim is match('^[{]')
    fail_msg: >-
      Tailscale backend status could not be read. No enrollment command was run.
```

- [ ] Parse the JSON and store the exact backend state:

```yaml
- name: Store the Tailscale backend state
  ansible.builtin.set_fact:
    proxmox_tailscale_backend_state: >-
      {{ proxmox_tailscale_status_json.BackendState | default('Unknown') }}
```

- [ ] Assert the state is either `Running` or `NeedsLogin`; every other state fails before `tailscale up`.
- [ ] Require `TAILSCALE_AUTHKEY` only when the state is `NeedsLogin`.
- [ ] For `NeedsLogin`, run the existing secret-redacted `tailscale up` command with both `--accept-dns` and the desired SSH flag.
- [ ] For `Running`, replace the two SSH-only commands with one no-auth command:

```yaml
- name: Apply owned Tailscale preferences on an enrolled node
  ansible.builtin.command:
    argv:
      - tailscale
      - set
      - "--accept-dns={{ 'true' if proxmox_tailscale_accept_dns | bool else 'false' }}"
      - "--ssh={{ 'true' if proxmox_tailscale_enable_ssh | bool else 'false' }}"
  changed_when: false
  when:
    - proxmox_enable_tailscale | bool
    - proxmox_tailscale_backend_state == "Running"
```

- [ ] Keep the final Running backend, interface, service, and IPv4 checks.
- [ ] Update the README to say a Running node needs no auth key on reruns and unexpected states stop safely.

## Task 6: Classify QEMU Guest Agent startup failures

**File:** `proxmox/roles/qemu_guest_agent/tasks/main.yml`

- [ ] Keep the service start registered with `failed_when: false`.
- [ ] Add two facts after the start task:

```yaml
- name: Collect QEMU Guest Agent startup diagnostics
  ansible.builtin.set_fact:
    qemu_guest_agent_start_details: >-
      {{ qemu_guest_agent_start.msg | default('') }}
      {{ qemu_guest_agent_start.stderr | default('') }}
      {{ qemu_guest_agent_start.stdout | default('') }}

- name: Classify a missing QEMU guest channel
  ansible.builtin.set_fact:
    qemu_guest_agent_missing_channel: >-
      {{ qemu_guest_agent_start_details
         | regex_search('(?i)(org[.]qemu[.]guest_agent[.]0|virtio-ports|no such file or directory)')
         is not none }}
```

- [ ] Warn only for the classified missing-channel condition.
- [ ] Fail when the start result reports failure and the condition is not missing-channel.
- [ ] Run `systemctl is-active qemu-guest-agent` and assert `active` whenever the missing-channel exception does not apply.
- [ ] Preserve package-installed and service-enabled assertions.

## Task 7: Document the standalone contract

**File:** `proxmox/README.md`

- [ ] State near the top that clustered and Ceph hosts are rejected before related mutations.
- [ ] Explain that UFW activation checks `/etc/pve/corosync.conf` itself.
- [ ] Include the optional maintenance procedure and false defaults.
- [ ] Explain Tailscale rerun behavior without exposing a real key.
- [ ] Preserve the existing three access-hardening phases and GUI/Tailscale verification warnings.

## Task 8: Final local validation and commit

- [ ] Parse all YAML:

```powershell
ruby -ryaml -e 'files = Dir["ubuntu/**/*.yml"] + Dir["proxmox/**/*.yml"]; files.each { |f| YAML.load_stream(File.read(f)) }; puts "YAML parsed: #{files.length} files"'
```

- [ ] Run `git diff --check` and inspect the complete diff.
- [ ] Confirm no changes under `ubuntu/`, `docker/`, or `proxmox/roles/subscription_nag/`.
- [ ] Confirm `repomix-output.xml` remains untouched in the main checkout.
- [ ] Run Ansible syntax checks only if `ansible-playbook` exists; otherwise report the limitation.
- [ ] Commit the implementation:

```powershell
git add proxmox
git commit -m "fix: harden standalone proxmox safety gates"
```

## Self-Review

- Every agreed safety change maps to a task.
- Ceph and cluster handling fail before mutation.
- No subscription-warning behavior changes.
- Tailscale owns only SSH and DNS preferences.
- Upgrade and reboot remain available but require explicit variables.
- No live-host command appears in validation.
