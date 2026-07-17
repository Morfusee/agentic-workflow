# OPNsense Console Interface Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the abbreviated OPNsense interface-assignment instructions with the complete working console flow and align the later WebGUI verification section.

**Architecture:** Keep all setup actions in chronological order. Phase 4 owns Proxmox NIC preflight, OPNsense interface assignment, and static LAN/WAN console configuration; Phase 6 verifies those values and applies WebGUI-only options.

**Tech Stack:** Markdown documentation, PowerShell and ripgrep verification

---

## File Map

- Modify: `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md` — replace Phase 4 and refine the Phase 6 WAN/LAN wording.
- Preserve: all existing Phase 1, Phase 2, Phase 3, citation, and unrelated content.
- Protect: `memory/docs/superpowers/**` — no changes.

### Task 1: Replace Phase 4 with the complete console flow

**Files:**

- Modify: `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md`

- [ ] **Step 1: Replace the existing Phase 4 body**

Keep the `# Phase 4: Assign the interfaces` heading and replace everything below it through the separator before Phase 5 with:

````markdown
Before assigning interfaces, confirm the Proxmox VM still has the correct bridge mapping:

```text
OPNsense VM
→ Hardware

net0 → bridge=vmbr1
net1 → bridge=vmbr2
```

The current double-NAT design depends on this order:

```text
vtnet0 → WAN transit network on vmbr1
vtnet1 → private LAN on vmbr2
```

## Assign WAN and LAN

At the OPNsense console, choose:

```text
1) Assign interfaces
```

When prompted to configure link aggregation, enter:

```text
Configure LAGGs now? n
```

LAGG combines multiple NICs into one logical interface for bonding, redundancy, or additional throughput. This VM uses one WAN NIC and one LAN NIC, so link aggregation is not part of this setup.

When prompted to configure VLANs, enter:

```text
Configure VLANs now? n
```

Assign the interfaces:

```text
WAN interface: vtnet0
LAN interface: vtnet1
Optional interface: press Enter without typing anything
```

Review the assignment summary:

```text
WAN  -> vtnet0
LAN  -> vtnet1
```

When asked whether to proceed, enter:

```text
y
```

After assignment, the top of the console should show:

```text
WAN (vtnet0)
LAN (vtnet1)
```

## Configure the LAN address

Choose:

```text
2) Set interface(s) IP address
```

Select the LAN interface and answer the prompts as follows:

```text
Configure IPv4 address LAN interface via DHCP? n
LAN IPv4 address: 10.77.0.1
Subnet bit count: 24
Upstream gateway: press Enter
Configure IPv6 via WAN tracking or DHCP6? n
LAN IPv6 address: press Enter
Enable DHCP server on LAN? n
Revert WebGUI protocol to HTTP? n
Generate a new self-signed WebGUI certificate? n
Restore WebGUI access defaults? n
```

Keep DHCP disabled for now. It will be enabled and configured later through the OPNsense WebGUI.

The final LAN configuration is:

```text
LAN interface: vtnet1
LAN address: 10.77.0.1/24
Gateway: none
IPv6: disabled
DHCP server: disabled for now
WebGUI: keep HTTPS
```

Do not enter `10.77.0.2` as the LAN gateway. That address belongs to the Proxmox host on `vmbr2`; it is not an upstream router.

After the configuration finishes, the console should show:

```text
LAN (vtnet1) → 10.77.0.1/24
```

## Configure the WAN address

Choose option 2 again:

```text
2) Set interface(s) IP address
```

Select the WAN interface and enter:

```text
Configure IPv4 address WAN interface via DHCP? n
WAN IPv4 address: 10.255.255.2
Subnet bit count: 30
Upstream gateway: 10.255.255.1
Configure IPv6 address via DHCP6? n
WAN IPv6 address: press Enter
```

The final WAN configuration is:

```text
WAN interface: vtnet0
WAN address: 10.255.255.2/30
Gateway: 10.255.255.1
IPv6: disabled
```

The console should now show both configured interfaces:

```text
WAN (vtnet0) → 10.255.255.2/30
LAN (vtnet1) → 10.77.0.1/24
```
````

- [ ] **Step 2: Confirm every troubleshooting decision is represented**

Run:

```powershell
rg -n "bridge=vmbr1|bridge=vmbr2|Configure LAGGs|Configure VLANs|Optional interface|10\.77\.0\.1/24|10\.255\.255\.2/30|10\.77\.0\.2" 'memory\docs\library\infrastructure\proxmox-opnsense-network-design.md'
```

Expected: each required assignment, prompt, address, and warning appears in Phase 4.

### Task 2: Align Phase 6 with the console configuration

**Files:**

- Modify: `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md`

- [ ] **Step 1: Change WAN configuration from first-time setup to verification**

Immediately after the `## WAN configuration` heading, retain the existing navigation path and replace `Set:` with:

```markdown
The static WAN address should already be present from Phase 4. Verify:
```

Keep the existing WAN values and the instructions to mark the gateway as upstream, uncheck private-network and bogon blocking, and defer gateway monitoring.

- [ ] **Step 2: Change LAN configuration from first-time setup to verification**

Keep the existing `## LAN configuration` section and ensure it says:

````markdown
Navigate to:

```text
Interfaces → LAN
```

Confirm the console configuration is present:

```text
IPv4 Configuration Type: Static IPv4
IPv4 address: 10.77.0.1/24
IPv6 Configuration Type: None
```
````

Keep the hardware-offloading and update instructions unchanged.

- [ ] **Step 3: Check Phase 4 and Phase 6 for contradictions**

Run:

```powershell
rg -n -C 4 "^# Phase 4|^# Phase 6|static WAN address should already|Confirm the console configuration" 'memory\docs\library\infrastructure\proxmox-opnsense-network-design.md'
```

Expected: Phase 4 performs static address configuration and Phase 6 only verifies it before applying WebGUI-specific settings.

### Task 3: Verify the complete documentation change

**Files:**

- Verify: `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md`
- Protect: `memory/docs/superpowers/**`

- [ ] **Step 1: Confirm prior corrections remain present**

Run:

```powershell
rg -n "ip -br addr \| grep|Add network device 1|Do not use any media|qm set 100" 'memory\docs\library\infrastructure\proxmox-opnsense-network-design.md'
```

Expected: the Phase 1 bridge command, Phase 2 second-NIC workflow, and Phase 3 ISO-ejection instructions all remain.

- [ ] **Step 2: Confirm `superpowers/` is untouched**

Run:

```powershell
git status --short -- 'memory/docs/superpowers'
git diff --exit-code -- 'memory/docs/superpowers'
```

Expected: no output and exit code `0`.

- [ ] **Step 3: Review the final diff**

Run:

```powershell
git diff --check
git diff -- 'memory/docs/library/infrastructure/proxmox-opnsense-network-design.md'
git status --short --untracked-files=all
```

Expected: the guide contains only the accumulated requested corrections plus the new Phase 4 and Phase 6 rewrite. The implementation plan remains under `memory/plans/`, and no unrelated files change.
