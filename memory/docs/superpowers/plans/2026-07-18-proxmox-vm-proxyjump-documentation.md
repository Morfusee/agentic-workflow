# Proxmox VM ProxyJump Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document reliable Ubuntu playbook execution against private Proxmox VMs reached through an SSH jump host while preserving `group_vars/all.yml` loading.

**Architecture:** Add one self-contained section to the Ubuntu project's existing README. Prefer a named host in the configured inventory, with a two-inventory one-off command as the fallback.

**Tech Stack:** Markdown, Ansible inventory, OpenSSH `ProxyJump`

---

### Task 1: Document Proxmox VM jump-host access

**Files:**
- Modify: `ubuntu/README.md`

- [ ] **Step 1: Confirm the working tree state**

Run:

```bash
git status --short
git diff
```

Expected: identify and preserve every pre-existing modification before editing.

- [ ] **Step 2: Add the ProxyJump documentation**

Insert the following section after the general playbook-running examples and before `Vagrant Validation`:

````markdown
## Proxmox VMs Through a Jump Host

A VM on a private Proxmox network may only be reachable by jumping through the Proxmox host. For example, this SSH command connects to `10.77.0.10` through `px`:

```bash
ssh -J morfuse@px morfuse@10.77.0.10
```

For repeated Ansible runs, add a named VM entry under `[servers]` in `hosts`:

```ini
proxmoxvm ansible_host=10.77.0.10 ansible_user=morfuse ansible_ssh_common_args='-o ProxyJump=morfuse@px'
```

Run the playbook from `ubuntu/` with the inventory alias:

```bash
ansible-playbook playbooks/playbook.yml -l proxmoxvm
```

Replace `proxmoxvm`, `10.77.0.10`, `morfuse`, and `px` with the values for the target environment. Add `-K` when the VM account requires a sudo password.

For a one-off run without adding the VM to `hosts`, load both the repository inventory and the inline host:

```bash
ansible-playbook playbooks/playbook.yml \
  -i hosts \
  -i '10.77.0.10,' \
  -u morfuse \
  -e "ansible_ssh_common_args='-o ProxyJump=morfuse@px'"
```

The comma after `10.77.0.10` is required for Ansible's inline host-list inventory. Keep `-i hosts` as well: using only `-i '10.77.0.10,'` replaces the configured inventory source and can prevent `group_vars/all.yml` from loading. Missing shared variables can then cause errors such as `'ssh_via' is undefined`.

When `group_vars/all.yml` already sets `ssh_via: tailscale` and a valid `tailscale_authkey`, either command applies those settings during the playbook run. After Tailscale is connected, later runs can target the VM's Tailscale address instead of using the jump host.
````

- [ ] **Step 3: Verify the documentation diff**

Run:

```bash
git diff --check
git diff -- ubuntu/README.md
git status --short
```

Expected: no whitespace errors; only the intended README section is present in this repository's diff; all pre-existing changes remain intact.

- [ ] **Step 4: Commit the documentation**

Run:

```bash
git add -- ubuntu/README.md
git diff --cached --check
git diff --cached -- ubuntu/README.md
git commit -m "docs(ubuntu): explain Proxmox VM jump hosts"
```

Expected: one commit containing only `ubuntu/README.md`.
