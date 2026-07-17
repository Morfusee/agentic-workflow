# OPNsense Console Interface Configuration Design

## Goal

Rewrite Phase 4 of the Proxmox and OPNsense network guide as a complete chronological console walkthrough based on the setup flow that worked in practice.

## Scope

Update `memory/docs/library/infrastructure/proxmox-opnsense-network-design.md` only. Preserve all accumulated Phase 1, Phase 2, and Phase 3 corrections.

## Phase 4 Structure

### Proxmox preflight

Before changing OPNsense interface assignments, direct the reader to verify the VM Hardware page still maps:

```text
net0 → bridge=vmbr1
net1 → bridge=vmbr2
```

### Assign interfaces

Direct the reader to select console option `1) Assign interfaces`, then document the prompts in order:

- Answer `n` when asked to configure LAGGs.
- Explain briefly that LAGG bonding, redundancy, and combined throughput are outside this two-interface design.
- Answer `n` when asked to configure VLANs.
- Assign `vtnet0` as WAN.
- Assign `vtnet1` as LAN.
- Press Enter without typing anything for the optional interface.
- Review the WAN and LAN summary and confirm with `y`.

The expected assignment is:

```text
WAN (vtnet0)
LAN (vtnet1)
```

### Configure LAN

Direct the reader to select console option `2) Set interface(s) IP address`, choose LAN, and enter:

```text
IPv4 via DHCP: n
IPv4 address: 10.77.0.1
Subnet bits: 24
Upstream gateway: press Enter
IPv6 via WAN tracking or DHCP6: n
IPv6 address: press Enter
Enable DHCP server on LAN: n
Revert WebGUI protocol to HTTP: n
Generate a new self-signed WebGUI certificate: n
Restore WebGUI access defaults: n
```

Explain that DHCP will be configured later in the WebGUI and that `10.77.0.2` belongs to the Proxmox host, not the LAN gateway.

The expected LAN result is `LAN (vtnet1) → 10.77.0.1/24` with no gateway.

### Configure WAN

Direct the reader to select console option 2 again, choose WAN, and enter:

```text
IPv4 via DHCP: n
IPv4 address: 10.255.255.2
Subnet bits: 30
Upstream gateway: 10.255.255.1
IPv6: none
```

The expected WAN result is `WAN (vtnet0) → 10.255.255.2/30` with gateway `10.255.255.1`.

## Phase 6 Relationship

Revise Phase 6 so it verifies the LAN and WAN addresses already entered from the console. Keep the WebGUI-only requirements there:

- Mark the WAN gateway as upstream.
- Disable private-network and bogon blocking for the RFC1918 WAN.
- Disable or defer gateway monitoring until outbound connectivity works.
- Verify LAN addressing.
- Disable virtualized hardware offloading.
- Update OPNsense after connectivity works.

Do not describe Phase 6 as the first time the static interface addresses are configured.

## Verification

- Confirm Phase 4 follows the actual prompt order without conversational question-and-answer wording.
- Confirm every supplied answer and warning is represented once.
- Confirm Phase 6 does not contradict or unnecessarily repeat Phase 4.
- Confirm prior Phase 1 through Phase 3 edits remain present.
- Confirm no file under `memory/docs/superpowers/` changes.
