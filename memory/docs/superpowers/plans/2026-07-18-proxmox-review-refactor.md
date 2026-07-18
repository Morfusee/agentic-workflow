# Proxmox Review Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address all twelve findings from the Proxmox review while preserving the project's fail-closed infrastructure safeguards.

**Architecture:** Each configuration role owns a reusable `tasks/verify.yml`; the validation role becomes a thin orchestrator plus cross-role health checks. Supporting cleanup remains local to the role that owns the behavior, and policy tests lock in the new boundaries.

**Tech Stack:** Ansible Core 2.20+, YAML, Python 3.12+, `community.general` 13.x, `ansible.posix`, Python `unittest` and PyYAML.

---

### Task 1: Add policy tests for the target architecture

**Files:**
- Modify: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Add structural policy tests**

Add test classes that read the role task files and assert:

```python
class VerificationOwnershipTests(unittest.TestCase):
    def test_validation_reuses_role_owned_verification(self):
        validation = (ROOT / "roles/validation/tasks/main.yml").read_text()
        for role in [
            "firewall",
            "repositories",
            "subscription_nag",
            "tailscale",
            "unattended_upgrades",
        ]:
            self.assertIn(f"name: {role}", validation)
            self.assertIn("tasks_from: verify", validation)

    def test_ufw_human_output_is_not_parsed(self):
        firewall = (ROOT / "roles/firewall/tasks/main.yml").read_text()
        validation = (ROOT / "roles/validation/tasks/main.yml").read_text()
        self.assertNotIn("ufw status verbose", firewall)
        self.assertNotIn("ufw status verbose", validation)
        self.assertNotIn("regex_search", (ROOT / "roles/firewall/tasks/verify.yml").read_text())

    def test_repository_inspector_is_role_owned(self):
        validation = (ROOT / "roles/validation/tasks/main.yml").read_text()
        inspector = ROOT / "roles/repositories/files/inspect_pve_sources.py"
        self.assertTrue(inspector.is_file())
        self.assertNotIn("import apt_pkg", validation)


class RuntimePolicyTests(unittest.TestCase):
    def test_proxmox_runtime_versions_are_bounded(self):
        requirements = yaml.safe_load((ROOT / "requirements.yml").read_text())
        versions = {
            item["name"]: item["version"] for item in requirements["collections"]
        }
        self.assertEqual(versions["community.general"], ">=13.0.0,<14.0.0")
        self.assertIn("ansible.posix", versions)
        for role in ["common", "ssh"]:
            metadata = yaml.safe_load((ROOT / f"roles/{role}/meta/main.yml").read_text())
            self.assertEqual(metadata["galaxy_info"]["min_ansible_version"], "2.20")

    def test_ssh_uses_one_owned_drop_in(self):
        ssh_tasks = (ROOT / "roles/ssh/tasks/main.yml").read_text()
        self.assertIn("99-server-playbooks.conf", ssh_tasks)
        self.assertNotIn("lineinfile", ssh_tasks)
        self.assertNotIn("lookup('env', 'HOME')", ssh_tasks)
```

- [ ] **Step 2: Run the new tests and confirm they fail**

Run from `proxmox/`:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: existing repository/subscription tests pass and the new architecture tests fail because the verification files, version pins, inspector, and SSH drop-in do not exist yet.

### Task 2: Correct runtime constraints, package composition, facts, and upgrade state

**Files:**
- Modify: `proxmox/requirements.yml`
- Modify: `proxmox/README.md`
- Modify: `proxmox/roles/common/meta/main.yml`
- Modify: `proxmox/roles/ssh/meta/main.yml`
- Modify: `proxmox/roles/common/defaults/main.yml`
- Modify: `proxmox/roles/common/tasks/main.yml`
- Modify: `proxmox/inventory/group_vars/proxmox_hosts.yml`
- Modify: `proxmox/roles/preflight/defaults/main.yml`
- Modify: `proxmox/roles/preflight/tasks/main.yml`
- Modify: `proxmox/roles/upgrade/defaults/main.yml`
- Modify: `proxmox/roles/upgrade/tasks/main.yml`
- Modify: `proxmox/roles/qemu_guest_agent/tasks/main.yml`

- [ ] **Step 1: Pin collection majors and document the controller baseline**

Use these requirements:

```yaml
---
collections:
  - name: community.general
    version: ">=13.0.0,<14.0.0"
  - name: ansible.posix
    version: ">=2.0.0,<3.0.0"
```

Set both role metadata files to `min_ansible_version: "2.20"`. Add a README requirement stating that the controller needs `ansible-core 2.20+` and Python 3.12+.

- [ ] **Step 2: Compose common packages instead of replacing defaults**

Change common defaults to:

```yaml
---
proxmox_common_packages:
  - acl
  - ca-certificates
  - curl
  - fail2ban
  - git
  - openssh-server
  - sudo
  - ufw

proxmox_extra_common_packages: []
```

Install `{{ proxmox_common_packages + proxmox_extra_common_packages }}`. Replace the inventory's `common_packages` block with:

```yaml
proxmox_extra_common_packages:
  - unattended-upgrades
```

- [ ] **Step 3: Remove redundant fact gathering**

Delete the `ansible.builtin.setup` task from preflight and from the QEMU Guest Agent role because both corresponding plays gather facts by default. Keep the host-side guest inspection play at `gather_facts: false` because it does not use target facts.

- [ ] **Step 4: Keep upgrade state in the upgrade role**

Remove `proxmox_upgrade_changed` and `proxmox_reboot_performed` from preflight defaults. Add to upgrade defaults:

```yaml
proxmox_upgrade_changed: false
proxmox_reboot_performed: false
```

Register the optional upgrade as before, then derive the boolean without creating a fake result:

```yaml
- name: Store upgrade and reboot state
  ansible.builtin.set_fact:
    proxmox_upgrade_changed: >-
      {{ (proxmox_dist_upgrade.changed | default(false)) | bool }}
    proxmox_reboot_required: >-
      {{ proxmox_reboot_required_marker.stat.exists | bool }}
```

Delete the task that assigns `proxmox_dist_upgrade: {changed: false}`.

- [ ] **Step 5: Run policy tests**

Run the unittest command from Task 1. Expected: runtime/package-related assertions pass; verification and SSH tests still fail.

### Task 3: Replace UFW text parsing with declarative verification

**Files:**
- Create: `proxmox/roles/firewall/tasks/verify.yml`
- Modify: `proxmox/roles/firewall/tasks/main.yml`
- Modify: `proxmox/roles/firewall/defaults/main.yml`
- Delete: `proxmox/roles/firewall/handlers/main.yml`
- Modify: `proxmox/inventory/group_vars/proxmox_hosts.yml`
- Modify: `proxmox/roles/tailscale/tasks/main.yml`

- [ ] **Step 1: Centralize firewall defaults and rename the interface variable**

Set firewall defaults to:

```yaml
---
proxmox_enable_firewall: false
proxmox_firewall_confirm_tailscale_access: false
proxmox_allow_tailscale_direct_udp: true
proxmox_tailscale_interface: tailscale0
proxmox_management_ports:
  - port: "22"
    protocol: tcp
  - port: "8006"
    protocol: tcp
proxmox_ufw_default_incoming: deny
proxmox_ufw_default_outgoing: allow
proxmox_ufw_default_routed: allow
```

Remove matching copies from inventory. Replace every use of `proxmox_firewall_tailscale_interface` and literal managed `tailscale0` interface checks with `proxmox_tailscale_interface`.

- [ ] **Step 2: Create check-mode UFW verification**

Create `verify.yml` with the enabled-state, policy, scoped-rule, unrestricted-rule deletion, and OpenSSH deletion probes from the approved design. Register each probe and assert that no probe predicts a change. Do not add `changed_when: false`.

- [ ] **Step 3: Simplify firewall mutation tasks**

Remove both `failed_when: false` declarations from UFW deletion tasks. Enable UFW with:

```yaml
- name: Enable UFW after all allow rules exist
  community.general.ufw:
    state: enabled
  when: proxmox_enable_firewall | bool
```

Delete the reload notification, handler flush, status command, regex assertion, and firewall status fact. Include `verify.yml` after enabling UFW when the feature flag is true.

- [ ] **Step 4: Run policy tests**

Expected: UFW parsing tests pass and no test finds the removed handler or old interface variable.

### Task 4: Make Tailscale parsing and verification explicit

**Files:**
- Create: `proxmox/roles/tailscale/tasks/verify.yml`
- Modify: `proxmox/roles/tailscale/tasks/main.yml`

- [ ] **Step 1: Fail before parsing invalid JSON**

For both status reads, use `failed_when: proxmox_tailscale_status_<before|after>.rc != 0`. Parse each result inside a block and rescue JSON errors with `ansible.builtin.fail` containing an actionable message. Access backend state through a guarded parent:

```yaml
{{ (proxmox_tailscale_status_json | default({})).BackendState | default('Unknown') }}
```

- [ ] **Step 2: Standardize service management**

Replace the legacy service task with `ansible.builtin.systemd_service`. Continue to use `service_facts` for explicit verification.

- [ ] **Step 3: Extract role-local verification**

Move the post-enrollment JSON status, service fact assertion, interface check, IPv4 read, and IPv4 assertion into `tasks/verify.yml`. Include it at the end of the Tailscale role when enabled. Use `proxmox_tailscale_interface` for the interface command and labels.

- [ ] **Step 4: Run policy tests and YAML parsing**

Expected: policy tests still pass except for components not yet implemented; all edited YAML loads successfully with PyYAML.

### Task 5: Move repository inspection into the repository role

**Files:**
- Create: `proxmox/roles/repositories/files/inspect_pve_sources.py`
- Create: `proxmox/roles/repositories/tasks/verify.yml`
- Modify: `proxmox/roles/repositories/tasks/main.yml`
- Modify: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Add the standalone inspector**

Move the existing APT-source Python program unchanged in behavior into `files/inspect_pve_sources.py`. Give it a `#!/usr/bin/python3` header, split parsing into named functions, and emit the same sorted JSON list containing `uri`, `host`, `suite`, `components`, and `file`.

- [ ] **Step 2: Unit-test the inspector's pure parsing helpers**

Load the file with `importlib.util` and test parsing of the existing multi-stanza and canonical fixtures without requiring `apt_pkg`. Keep live `apt_pkg.SourceList` integration behind `main()` so importing the module remains testable.

- [ ] **Step 3: Add repository verification tasks**

Copy the inspector to a temporary remote path with mode `0755`, execute it, always remove it in an `always` block, parse the JSON, and assert the same community/enterprise source invariants currently enforced by validation. Include the verification file at the end of repository configuration.

- [ ] **Step 4: Run repository and full policy tests**

Expected: fixture tests and repository safety-order tests pass; validation contains no embedded Python.

### Task 6: Extract subscription and unattended-upgrade verification

**Files:**
- Create: `proxmox/roles/subscription_nag/tasks/verify.yml`
- Modify: `proxmox/roles/subscription_nag/tasks/main.yml`
- Create: `proxmox/roles/unattended_upgrades/tasks/verify.yml`
- Modify: `proxmox/roles/unattended_upgrades/tasks/main.yml`
- Delete: `proxmox/roles/unattended_upgrades/handlers/main.yml`

- [ ] **Step 1: Move subscription verification without weakening it**

Move the post-patch slurp, exact checked-command count, one managed marker, zero vendor predicates, service facts, and running `pveproxy` assertion into `subscription_nag/tasks/verify.yml`. Include it after handler flushing when popup removal is enabled and the widget is a regular file.

- [ ] **Step 2: Replace the unattended-upgrades handler**

Remove template notifications and the handler. Add:

```yaml
- name: Ensure the unattended-upgrade timer is enabled
  ansible.builtin.systemd_service:
    name: apt-daily-upgrade.timer
    enabled: true
    state: started
  when: proxmox_enable_unattended_upgrades | bool
```

- [ ] **Step 3: Add unattended-upgrade verification**

Move managed-file existence, policy-content, reboot-disabled, blacklist-entry, and timer-running checks into `tasks/verify.yml`. Keep the dry-run command in the configuration role, then include verification when enabled.

- [ ] **Step 4: Run subscription fixtures and full policy tests**

Expected: all subscription fixture protections remain green and no deleted handler is referenced.

### Task 7: Reduce validation to orchestration and cross-role health

**Files:**
- Modify: `proxmox/roles/validation/tasks/main.yml`
- Modify: `proxmox/roles/validation/defaults/main.yml`

- [ ] **Step 1: Keep only cross-role checks**

Retain Proxmox version/codename summary facts, one `service_facts` call, `sshd -t`, local `pvesh` JSON API validation, HTTPS API listener validation, and final summary. Assert service facts directly:

```yaml
- name: Require core Proxmox services
  ansible.builtin.assert:
    that:
      - ansible_facts.services['pveproxy.service'].state == 'running'
      - ansible_facts.services['pvedaemon.service'].state == 'running'
      - ansible_facts.services['ssh.service'].state == 'running'
      - proxmox_validation_sshd.rc == 0
```

Use guarded `.get()`-style Jinja defaults if service aliases without `.service` must remain supported.

- [ ] **Step 2: Include role-owned verification**

Add one `ansible.builtin.include_role` per verification owner with `tasks_from: verify`, guarded by the same feature flags used by configuration roles.

- [ ] **Step 3: Remove shadow defaults**

Delete repository paths, subscription patterns, unattended paths/policy, firewall state/interface, and repeated feature defaults from validation defaults. Keep only summary fallbacks that validation itself owns, if any are still required.

- [ ] **Step 4: Run policy tests and inspect validation length**

Expected: validation owns no UFW parsing, APT inspector, subscription regex implementation, or unattended policy parsing; structural tests pass.

### Task 8: Simplify QEMU Guest Agent state detection

**Files:**
- Modify: `proxmox/roles/qemu_guest_agent/tasks/main.yml`

- [ ] **Step 1: Probe the virtio channel directly**

After package installation, add:

```yaml
- name: Check for the QEMU Guest Agent virtio channel
  ansible.builtin.stat:
    path: /dev/virtio-ports/org.qemu.guest_agent.0
  register: qemu_guest_agent_channel
```

- [ ] **Step 2: Manage service state from the prerequisite**

Warn when the channel is absent. When present, use one `ansible.builtin.systemd_service` task with `enabled: true` and `state: started`, register its result, and assert `status.ActiveState == 'active'`. When absent, enable the service without forcing a start so it is ready after the device is added.

- [ ] **Step 3: Remove brittle classification and duplicate commands**

Delete message regex classification, `systemctl is-active`, `systemctl is-enabled`, and their assertions. Retain package facts only if they add evidence not already guaranteed by the successful package task; otherwise remove that redundant verification too.

- [ ] **Step 4: Parse YAML and run policy tests**

Expected: no English error fragments or direct `systemctl` calls remain in the role.

### Task 9: Install an owned SSH hardening drop-in

**Files:**
- Modify: `proxmox/roles/ssh/tasks/main.yml`
- Create: `proxmox/roles/ssh/defaults/main.yml`
- Modify: `proxmox/roles/ssh/handlers/main.yml`
- Delete: `proxmox/roles/ssh/vars/main.yml`
- Modify: `proxmox/inventory/group_vars/proxmox_hosts.yml`

- [ ] **Step 1: Define explicit SSH inputs**

Add defaults:

```yaml
---
proxmox_authorized_key: ""
proxmox_sshd_drop_in_path: /etc/ssh/sshd_config.d/99-server-playbooks.conf
```

Remove unused `ssh_port` from inventory after confirming no references. Require a non-empty `proxmox_authorized_key` only when `ssh_via == "openssh"`.

- [ ] **Step 2: Replace vendor-file edits with one copy task**

Write this owned content with mode `0644` and validate the staged file with
`/usr/sbin/sshd -t -f %s` before installation:

```text
PasswordAuthentication no
PermitRootLogin prohibit-password
```

- [ ] **Step 3: Validate before reloading**

Use a handler block that runs `/usr/sbin/sshd -t` and then reloads SSH with `ansible.builtin.systemd_service`. Do not restart SSH for a configuration-only change.

- [ ] **Step 4: Run policy tests**

Expected: the SSH drop-in test passes and no controller `HOME` lookup or `lineinfile` remains.

### Task 10: Complete cleanup, documentation, and full verification

**Files:**
- Delete: `proxmox/roles/common/handlers/main.yml`
- Delete: `proxmox/roles/common/vars/main.yml`
- Modify: any Proxmox file containing confirmed dead variables or legacy service-module calls touched by prior tasks
- Modify: `proxmox/README.md`
- Modify: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Remove confirmed dead files and variables**

Delete empty/comment-only common files. Remove `proxmox_enterprise_pattern` only if `rg` confirms it has no consumer. Standardize touched systemd operations on `ansible.builtin.systemd_service`.

- [ ] **Step 2: Update operator documentation**

Document the controller baseline, collection installation, role-owned validation behavior, explicit OpenSSH key variable when used, and unchanged staged firewall safety workflow.

- [ ] **Step 3: Run all local tests**

From `proxmox/` run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python -c "from pathlib import Path; import yaml; [yaml.safe_load(p.read_text()) for p in Path('.').rglob('*.yml')]; print('all Proxmox YAML parsed')"
ansible-playbook --syntax-check playbooks/host.yml
ansible-playbook --syntax-check playbooks/guests.yml
ansible-playbook --syntax-check playbooks/site.yml
```

Expected: unit tests pass, YAML parsing prints `all Proxmox YAML parsed`, and syntax checks pass. If Ansible or collections are unavailable locally, record that limitation and do not weaken tests to hide it.

- [ ] **Step 4: Run final preservation checks**

From the repository root run:

```powershell
git diff --check
git status --short
git diff -- proxmox
```

Expected: only intentional files under `proxmox/` are modified or added; `repomix-output.xml` remains untracked and unchanged; no `ubuntu/` or `docker/` path appears in the diff.
