# Proxmox Duplicate OpenSSH UFW Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make one firewall-role run remove every duplicate unrestricted OpenSSH UFW application rule before verification.

**Architecture:** Retain `community.general.ufw` as the source of truth and apply Ansible's bounded `until` retry behavior to the existing deletion task. A source-level regression test locks in convergence without depending on UFW's human-readable status output.

**Tech Stack:** Ansible YAML, `community.general.ufw`, Python `unittest`, PyYAML

---

### Task 1: Specify duplicate-rule convergence

**Files:**
- Test: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Write the failing test**

Add a test that loads `roles/firewall/tasks/main.yml`, finds `Remove all unrestricted OpenSSH application rules`, and asserts that the task registers `proxmox_ufw_openssh_removal`, uses `until: not proxmox_ufw_openssh_removal.changed`, and has `retries: 10`.

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python -m unittest proxmox.tests.test_playbook_policies.VerificationOwnershipTests.test_firewall_removes_all_openssh_application_rules -v`

Expected: FAIL because the current task performs only one deletion.

### Task 2: Implement bounded declarative cleanup

**Files:**
- Modify: `proxmox/roles/firewall/tasks/main.yml`

- [ ] **Step 1: Add convergence behavior**

Change the existing task to:

```yaml
- name: Remove all unrestricted OpenSSH application rules
  community.general.ufw:
    rule: allow
    name: OpenSSH
    delete: true
  register: proxmox_ufw_openssh_removal
  until: not proxmox_ufw_openssh_removal.changed
  retries: 10
  when: proxmox_enable_firewall | bool
```

- [ ] **Step 2: Run the focused test**

Run: `python -m unittest proxmox.tests.test_playbook_policies.VerificationOwnershipTests.test_firewall_removes_all_openssh_application_rules -v`

Expected: PASS.

### Task 3: Verify the complete Proxmox policy surface

**Files:**
- Verify: `proxmox/roles/firewall/tasks/main.yml`
- Verify: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Run all policy tests**

Run: `python -m unittest discover -s proxmox/tests -v`

Expected: all tests pass.

- [ ] **Step 2: Parse every Proxmox YAML file**

Run a read-only Python/PyYAML check over every `*.yml` and `*.yaml` file under `proxmox`.

Expected: every file parses successfully.

- [ ] **Step 3: Review the final diff**

Confirm the only server-playbooks changes are the OpenSSH convergence behavior and its regression test, and that `repomix-output.xml` remains untouched.
