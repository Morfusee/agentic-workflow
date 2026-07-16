# Proxmox Community Repository and Subscription Popup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Proxmox playbooks enforce one `pve-no-subscription` source and reliably suppress the Proxmox 9.2 subscription popup, then apply only those changes to the live host.

**Architecture:** Use Ansible's structured `deb822_repository` module to own the canonical PVE 9 repository files and remove only a byte-for-byte recognized legacy duplicate. Scope the UI patch to `Proxmox.Utils.checked_command`, require exactly one supported predicate, and verify the patched file and service state. Keep live application limited to preflight, repository, subscription, and validation tags.

**Tech Stack:** Ansible Core 2.18, YAML/Jinja, Python 3 standard-library `unittest`, Proxmox VE 9.2, Debian 13 deb822 APT sources, WSL Ubuntu.

---

## File Map

- Modify `proxmox/roles/repositories/defaults/main.yml`: declare canonical, deprecated, and enterprise deb822 source names/paths.
- Modify `proxmox/roles/repositories/tasks/main.yml`: replace file-wide deb822 regex editing with structured repository management and safe duplicate cleanup.
- Modify `proxmox/roles/repositories/templates/pve-no-subscription.sources.j2`: retain the recognized legacy duplicate content used by the cleanup guard.
- Modify `proxmox/roles/subscription_nag/defaults/main.yml`: define the scoped widget match, replacement marker, and postcondition patterns once.
- Modify `proxmox/roles/subscription_nag/tasks/main.yml`: count, patch, back up, and verify exactly one supported `checked_command` predicate.
- Modify `proxmox/roles/validation/defaults/main.yml`: use the canonical PVE source path and subscription widget defaults.
- Modify `proxmox/roles/validation/tasks/main.yml`: validate normalized active repositories and subscription patch state.
- Create `proxmox/tests/fixtures/proxmoxlib-old.js`: older supported widget fixture.
- Create `proxmox/tests/fixtures/proxmoxlib-9.2.js`: current Proxmox 9.2 widget fixture with an unrelated subscription expression.
- Create `proxmox/tests/fixtures/proxmox.sources`: canonical community source fixture.
- Create `proxmox/tests/fixtures/pve-no-subscription.sources`: recognized duplicate fixture.
- Create `proxmox/tests/fixtures/multi-stanza.sources`: regression fixture containing enterprise and unrelated stanzas.
- Create `proxmox/tests/test_playbook_policies.py`: standard-library regression tests for scoped popup matching and repository safety invariants.

### Task 1: Add failing policy fixtures and tests

**Files:**
- Create: `proxmox/tests/fixtures/proxmoxlib-old.js`
- Create: `proxmox/tests/fixtures/proxmoxlib-9.2.js`
- Create: `proxmox/tests/fixtures/proxmox.sources`
- Create: `proxmox/tests/fixtures/pve-no-subscription.sources`
- Create: `proxmox/tests/fixtures/multi-stanza.sources`
- Create: `proxmox/tests/test_playbook_policies.py`

- [ ] **Step 1: Create the widget fixtures**

Use a minimal old fixture containing:

```javascript
Proxmox.Utils = {
    checked_command: function (orig_cmd) {
        Proxmox.Utils.API2Request({
            success: function (response) {
                const data = response.result.data;
                if (data.status !== 'Active') {
                    Ext.Msg.show({ title: 'No valid subscription' });
                    return;
                }
                orig_cmd();
            },
        });
    },
};
```

Use a Proxmox 9.2 fixture containing the current compound condition plus a second, unrelated expression after `checked_command`:

```javascript
Proxmox.Utils = {
    checked_command: function (orig_cmd) {
        Proxmox.Utils.API2Request({
            success: function (response) {
                const res = response.result;
                if (
                    res === null ||
                    res === undefined ||
                    !res ||
                    res.data.status.toLowerCase() !== 'active'
                ) {
                    Ext.Msg.show({ title: 'No valid subscription' });
                    return;
                }
                orig_cmd();
            },
        });
    },
};

const subscription = !(res.data.status.toLowerCase() !== 'active');
```

- [ ] **Step 2: Create repository fixtures**

The canonical and duplicate fixtures must contain:

```text
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

The multi-stanza fixture must contain one enterprise PVE stanza and one unrelated Debian stanza, each with its own `Enabled:` field.

- [ ] **Step 3: Add regression tests**

Create `test_playbook_policies.py` with tests that:

```python
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class SubscriptionNagPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        defaults = yaml.safe_load(
            (ROOT / "roles/subscription_nag/defaults/main.yml").read_text()
        )
        cls.pattern = re.compile(defaults["proxmox_subscription_nag_supported_pattern"])
        cls.replacement = defaults["proxmox_subscription_nag_replacement"]

    def patch(self, text: str) -> str:
        matches = list(self.pattern.finditer(text))
        self.assertEqual(len(matches), 1)
        return self.pattern.sub(
            rf"\g<1>{self.replacement}\g<3>", text, count=1
        )

    def test_old_widget_signature_is_scoped_and_patchable(self):
        source = (FIXTURES / "proxmoxlib-old.js").read_text()
        patched = self.patch(source)
        self.assertIn(self.replacement, patched)
        self.assertNotIn("data.status !== 'Active'", patched)

    def test_proxmox_9_widget_leaves_unrelated_expression_unchanged(self):
        source = (FIXTURES / "proxmoxlib-9.2.js").read_text()
        patched = self.patch(source)
        self.assertIn(
            "const subscription = !(res.data.status.toLowerCase() !== 'active');",
            patched,
        )
        self.assertEqual(patched.count(self.replacement), 1)


class RepositoryPolicyTests(unittest.TestCase):
    def test_canonical_and_legacy_duplicate_are_identical(self):
        canonical = (FIXTURES / "proxmox.sources").read_text().strip()
        duplicate = (FIXTURES / "pve-no-subscription.sources").read_text().strip()
        self.assertEqual(canonical, duplicate)

    def test_repository_tasks_do_not_globally_replace_enabled_fields(self):
        tasks = (ROOT / "roles/repositories/tasks/main.yml").read_text()
        self.assertNotIn("regexp: '(?m)^(\\s*)Enabled:", tasks)
        self.assertIn("ansible.builtin.deb822_repository", tasks)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests and verify the new expectations fail**

Run:

```bash
cd proxmox
python3 -m unittest discover -s tests -v
```

Expected: errors or failures because the scoped pattern defaults and structured repository tasks do not exist yet.

### Task 2: Replace brittle repository mutation with canonical deb822 management

**Files:**
- Modify: `proxmox/roles/repositories/defaults/main.yml`
- Modify: `proxmox/roles/repositories/tasks/main.yml`
- Modify: `proxmox/roles/validation/defaults/main.yml`

- [ ] **Step 1: Define canonical repository paths**

Use these defaults:

```yaml
proxmox_repository_channel: no-subscription
proxmox_no_subscription_list_path: /etc/apt/sources.list.d/pve-no-subscription.list
proxmox_no_subscription_sources_path: /etc/apt/sources.list.d/proxmox.sources
proxmox_deprecated_no_subscription_sources_path: /etc/apt/sources.list.d/pve-no-subscription.sources
proxmox_enterprise_sources_path: /etc/apt/sources.list.d/pve-enterprise.sources
proxmox_proxmox_keyring: /usr/share/keyrings/proxmox-archive-keyring.gpg
proxmox_enterprise_pattern: enterprise.proxmox.com
proxmox_apt_update_error_pattern: '(?i)(enterprise.*(401|403|NO_PUBKEY|not authenticated)|NO_PUBKEY.*enterprise)'
```

Mirror only the path defaults consumed directly by the final validation role.

- [ ] **Step 2: Keep all existing discovery and Ceph checks before mutation**

Retain the source discovery, package facts, `/etc/pve/ceph.conf` check, Ceph server-package detection, and standalone assertion through the current `Require a standalone non-Ceph Proxmox host` task.

- [ ] **Step 3: Install the structured deb822 dependency after the Ceph gate**

Add:

```yaml
- name: Install deb822 repository support
  ansible.builtin.apt:
    name: python3-debian
    state: present
    update_cache: false
```

- [ ] **Step 4: Manage the selected repository channel structurally**

For `no-subscription`, use:

```yaml
- name: Manage the Proxmox community repository
  ansible.builtin.deb822_repository:
    name: proxmox
    types: [deb]
    uris: http://download.proxmox.com/debian/pve
    suites: ["{{ proxmox_debian_codename }}"]
    components: [pve-no-subscription]
    signed_by: "{{ proxmox_proxmox_keyring }}"
    enabled: true
    state: present
  when: proxmox_repository_channel == "no-subscription"

- name: Keep the Proxmox enterprise repository disabled
  ansible.builtin.deb822_repository:
    name: pve-enterprise
    types: [deb]
    uris: https://enterprise.proxmox.com/debian/pve
    suites: ["{{ proxmox_debian_codename }}"]
    components: [pve-enterprise]
    signed_by: "{{ proxmox_proxmox_keyring }}"
    enabled: false
    state: present
  when: proxmox_repository_channel == "no-subscription"
```

For `enterprise`, manage the same two named repositories with the community repository absent and enterprise enabled. This makes channel switching complete instead of printing a message only.

- [ ] **Step 5: Remove only recognized obsolete community files**

Stat and slurp the deprecated deb822 path and legacy `.list` path. Compare each existing file with its corresponding rendered template. Assert equality before `state: absent`; fail with the unexpected path when content differs. Do not delete arbitrary source files discovered elsewhere.

- [ ] **Step 6: Fix empty enterprise-error matching**

Set:

```yaml
proxmox_apt_enterprise_error: >-
  {{ ((proxmox_apt_update.stdout | default(''))
      ~ '\n' ~ (proxmox_apt_update.stderr | default('')))
     | regex_search(proxmox_apt_update_error_pattern)
     | default('', true) }}
```

Then retain the `length == 0` assertion.

- [ ] **Step 7: Run policy tests**

Run `python3 -m unittest discover -s tests -v` from `proxmox/`.

Expected: repository tests pass; subscription tests still fail because Task 3 is pending.

### Task 3: Implement the scoped Proxmox 9 subscription patch

**Files:**
- Modify: `proxmox/roles/subscription_nag/defaults/main.yml`
- Modify: `proxmox/roles/subscription_nag/tasks/main.yml`

- [ ] **Step 1: Define the canonical scoped patterns once**

Add defaults equivalent to:

```yaml
proxmox_subscription_nag_replacement: "false /* managed by server-playbooks subscription_nag */"
proxmox_subscription_nag_supported_pattern: >-
  (?s)(checked_command:\s*function\s*\(orig_cmd\)\s*\{.*?)
  (res\.data\.status\.toLowerCase\(\)\s*!==\s*['\"]active['\"]|(?:res\.data|data)\.status\s*!==\s*['\"]Active['\"])
  (.*?orig_cmd\(\);)
proxmox_subscription_nag_patched_pattern: >-
  (?s)checked_command:\s*function\s*\(orig_cmd\)\s*\{.*?false\s*/\*\s*managed by server-playbooks subscription_nag\s*\*/.*?orig_cmd\(\);
```

Ensure YAML folding does not insert literal spaces between the three regex groups; use a single quoted scalar if necessary and confirm through the Python regression test.

- [ ] **Step 2: Replace silent unsupported handling with exact-count assertions**

After slurping the file, calculate:

```yaml
proxmox_subscription_nag_already_patched: >-
  {{ proxmox_subscription_nag_text
     | regex_search(proxmox_subscription_nag_patched_pattern) is not none }}
proxmox_subscription_nag_supported_matches: >-
  {{ proxmox_subscription_nag_text
     | regex_findall(proxmox_subscription_nag_supported_pattern) }}
```

When removal is enabled and the file is not already patched, assert that the match list length is exactly one. The failure message must include the installed `proxmox-widget-toolkit` version and state that the vendor signature is unsupported or ambiguous.

- [ ] **Step 3: Back up and patch exactly one scoped predicate**

Keep the existing `copy` backup with `force: false`. Replace with:

```yaml
- name: Patch the recognized checked_command subscription predicate
  ansible.builtin.replace:
    path: "{{ proxmox_subscription_nag_path }}"
    regexp: "{{ proxmox_subscription_nag_supported_pattern }}"
    replace: "\\g<1>{{ proxmox_subscription_nag_replacement }}\\g<3>"
  register: proxmox_subscription_nag_patch
  when:
    - proxmox_remove_subscription_nag | bool
    - proxmox_subscription_nag_stat.stat.exists | bool
    - not (proxmox_subscription_nag_already_patched | bool)
    - proxmox_subscription_nag_supported_matches | length == 1
  notify: Restart pveproxy
```

- [ ] **Step 4: Verify the file after mutation**

After flushing the `pveproxy` handler, slurp the file again and assert that the scoped patched pattern exists exactly once and the original supported pattern no longer matches.

- [ ] **Step 5: Run all policy tests**

Run `python3 -m unittest discover -s tests -v`.

Expected: all widget and repository policy tests pass.

### Task 4: Strengthen final validation for the requested outcomes

**Files:**
- Modify: `proxmox/roles/validation/defaults/main.yml`
- Modify: `proxmox/roles/validation/tasks/main.yml`

- [ ] **Step 1: Replace presence-only repository validation with normalized active-entry validation**

Extend the existing `apt_pkg.SourceList` Python query to print normalized JSON objects for active PVE sources with `uri`, `suite`, `components`, and source file. Parse the JSON and assert:

```yaml
- proxmox_validation_community_sources | length == 1
- proxmox_validation_enterprise_sources | length == 0
- proxmox_validation_community_sources[0].suite == proxmox_validation_codename
- "pve-no-subscription" in proxmox_validation_community_sources[0].components
```

The failure message must list every normalized PVE source and its file so a duplicate is immediately actionable.

- [ ] **Step 2: Add the subscription-widget postcondition**

When popup removal is enabled, stat and slurp the widget and assert that `proxmox_subscription_nag_patched_pattern` matches. This prevents a successful final summary when the popup remains active.

- [ ] **Step 3: Run tests and syntax checking**

Run:

```bash
python3 -m unittest discover -s tests -v
ANSIBLE_CONFIG="$PWD/ansible.cfg" \
ANSIBLE_ROLES_PATH="$PWD/roles" \
ansible-playbook -i inventory/hosts.yml --syntax-check playbooks/site.yml
```

Expected: all tests pass and Ansible prints `playbook: playbooks/site.yml`.

### Task 5: Review and commit the local playbook implementation

**Files:**
- Review every file listed in the File Map.

- [ ] **Step 1: Inspect the scoped diff**

Run:

```bash
git status --short
git diff --check
git diff -- proxmox/roles/repositories proxmox/roles/subscription_nag proxmox/roles/validation proxmox/tests
```

Expected: only repository, popup, validation, and focused test files changed; no unrelated audit findings are implemented.

- [ ] **Step 2: Commit the verified playbook changes**

```bash
git add proxmox/roles/repositories proxmox/roles/subscription_nag proxmox/roles/validation proxmox/tests
git commit -m "fix(proxmox): normalize community repository and subscription popup"
```

Expected: one Conventional Commit containing only the approved implementation.

### Task 6: Apply the targeted playbook tags to Proxmox

**Files:**
- No additional source changes.

- [ ] **Step 1: Capture read-only pre-application evidence**

Through WSL SSH, record source filenames/content hashes, the widget hash, `pveproxy` state, host uptime, and running guest IDs. Do not mutate during this step.

- [ ] **Step 2: Run the targeted host playbook**

From `proxmox/` in WSL, use the configured inventory and run:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/host.yml \
  --tags preflight,repositories,subscription_nag,validation
```

Expected changes: install `python3-debian` if missing, normalize the two Proxmox repository files, refresh APT metadata, back up and patch `proxmoxlib.js`, and restart `pveproxy`. Expected unchanged: upgrades, reboot, SSH, UFW rules, Tailscale preferences, users, and guests.

- [ ] **Step 3: Verify live repository state**

Use `apt_pkg.SourceList` or an equivalent read-only query and require exactly one active `download.proxmox.com/debian/pve` entry with suite `trixie` and component `pve-no-subscription`. Require no active enterprise PVE entry and a successful `apt-cache policy` query.

- [ ] **Step 4: Verify live popup patch and service health**

Require:

- the backup file exists;
- the scoped managed marker occurs exactly once inside `checked_command`;
- the unpatched predicate does not remain inside `checked_command`;
- `pveproxy`, `pvedaemon`, SSH, and Tailscale are active;
- host uptime shows no reboot;
- the pre-application running guest IDs remain running.

- [ ] **Step 5: Report browser cache behavior**

If the popup remains in an already-open tab, instruct the user to hard-refresh or reopen the Proxmox UI. Do not make additional server changes unless the on-disk scoped verification fails.
