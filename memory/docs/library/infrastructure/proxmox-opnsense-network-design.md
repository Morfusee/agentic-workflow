---
date: 2026-07-19
type: howto
tags: [proxmox, opnsense, caddy, dokploy, networking, infrastructure]
related:
  - memory/docs/library/infrastructure/proxmox-opnsense-network-design.md
  - memory/docs/library/infrastructure/opnsense-hardening-and-network-segmentation.md
  - memory/docs/library/infrastructure/dokploy-service-deployment.md
---

# Unified Proxmox → OPNsense → Caddy → Dokploy Guide

This combines the original OPNsense routing setup, the Caddy edge-proxy setup, two Dokploy servers, wildcard DNS, internal DNS, and the migration away from double NAT.

There is one important architecture correction before beginning:

> With only one public IPv4 assigned to the Proxmox host, Proxmox normally has to perform masquerading and port forwarding for private guests. To remove double NAT, OPNsense must receive a public IPv4 directly. Proxmox’s own documentation describes masquerading as the normal approach when a hosted server has only one public IP. ([Proxmox VE][1])

The recommended supported design is therefore:

- Keep the main IP address assigned to you on your Proxmox host.
- Obtain an **Additional IPv4** for OPNsense.
- Give that Additional IPv4 an OVH virtual MAC.
- Attach OPNsense WAN directly to `vmbr0`.
- Let OPNsense perform the only NAT for private VMs.
- Remove all Proxmox NAT and port-forwarding rules.

This makes OPNsense the main router and firewall for your virtual infrastructure, while Proxmox retains its own management IP.

OVH’s documented bridged-router design requires an Additional IP, a provider-generated virtual MAC, a `/32` WAN address, and the provider gateway. Availability of virtual MACs may be limited on Eco/Kimsufi plans, so verify the option exists in your OVH control panel before starting. ([OVHcloud Help Centre][2])

---

# Final architecture

```text
Internet
   │
   ├── <PROXMOX_PUBLIC_IP>
   │      Proxmox management IP
   │      SSH/8006 restricted to Tailscale
   │
   └── <OPNSENSE_PUBLIC_IP>
          OPNsense WAN
          Caddy listens on TCP 80/443
                    │
                    ├── *.prod.mcube.uk
                    │       → 10.77.0.10:80
                    │       → Dokploy Production Traefik
                    │
                    └── *.stage.mcube.uk
                            → 10.77.0.11:80
                            → Dokploy Staging Traefik
```

Private network:

```text
10.77.0.0/24
Gateway: 10.77.0.1
DNS:     10.77.0.1
```

Address plan:

| Device                    |           Address |
| ------------------------- | ----------------: |
| OPNsense LAN              |       `10.77.0.1` |
| Proxmox private interface |       `10.77.0.2` |
| Dokploy production        |      `10.77.0.10` |
| Dokploy staging           |      `10.77.0.11` |
| Static server range       |   `10.77.0.10–99` |
| DHCP range                | `10.77.0.100–199` |

Outbound traffic now follows:

```text
10.77.0.x
   ↓
OPNsense 10.77.0.1
   ↓ one source-NAT operation
<OPNSENSE_PUBLIC_IP>
   ↓
Internet
```

There is no Proxmox NAT in that path.

---

# Phase 0 — Verify prerequisites

Do not perform this until all of these are available:

1. An OVH Additional IPv4 attached to the dedicated server.
2. The option to create an OVH virtual MAC for that Additional IP.
3. The dedicated server’s gateway address.
4. OVH rescue mode or IPMI access.
5. Proxmox console access to the OPNsense VM.

OVH commonly uses the first three octets of the server’s main IPv4 followed by `.254` as the gateway, but use the value displayed in your OVH control panel rather than assuming it. OVH’s router tutorial also specifies a `/32` mask for the Additional IP because the gateway is outside the assigned subnet. ([OVHcloud Help Centre][2])

```text
Internet
├── Proxmox management IPv4
│   └── Proxmox host only
│
└── OPNsense Additional IPv4
    ├── OPNsense WAN
    ├── Caddy on ports 80/443
    └── NAT/router for 10.77.0.0/24
         ├── Proxmox private address: 10.77.0.2
         ├── Dokploy production:      10.77.0.10
         ├── Dokploy staging:         10.77.0.11
         └── Other private VMs
```

That gives private VMs exactly one NAT layer:

```text
Private VM
→ OPNsense
→ Internet
```

Proxmox performs no NAT and no application port forwarding.

A second public IPv4 is required for this particular design. One public IPv4 cannot remain assigned to Proxmox and also be assigned directly to the OPNsense WAN interface. OVH’s documented VM-router configuration likewise requires an Additional IP and a virtual MAC. Virtual-MAC availability may be limited on Kimsufi/Eco servers, so verify that the **Add a virtual MAC** option exists before proceeding. ([OVHcloud Help Centre][1])

# Greenfield unified installation guide

## Phase 1 — Gather the required information

Before installing anything, record:

```text
Proxmox public IPv4:       <PROXMOX_PUBLIC_IP>
Proxmox public gateway:    <from OVH control panel>
Proxmox public prefix:     <from OVH control panel>

OPNsense Additional IPv4:  <additional IPv4>
OPNsense virtual MAC:      <generated by OVH>
OPNsense gateway:          <from OVH control panel>

Private network:           10.77.0.0/24
OPNsense LAN:              10.77.0.1
Proxmox private address:   10.77.0.2
Dokploy production:        10.77.0.10
Dokploy staging:           10.77.0.11
DHCP range:                10.77.0.100–10.77.0.199
```

In OVH:

```text
Network
→ Public IP Addresses
→ Additional IP
→ Add a virtual MAC
```

Use:

```text
Type: ovh
Name: opnsense
```

Avoid manually inventing a MAC address. Use the exact virtual MAC generated by OVH.

---

## Phase 2 — Create the Proxmox bridges

This phase can be completed entirely in the Proxmox GUI.

A normal Proxmox installation already creates `vmbr0`, so usually you only need to verify `vmbr0` and create the private bridge `vmbr1`. Proxmox describes a Linux bridge as a virtual network switch that connects physical interfaces and VM adapters.

Phase 2 has four steps. Complete them in order.

---

### Step 1 of 4 — Open the node network page

In Proxmox, open:

```text
Datacenter
→ your node, such as px
→ System
→ Network
```

You should see entries similar to:

| Entry | Purpose |
| --- | --- |
| `eno1` / `enpXsY` / `eth0` | Physical network interface |
| `vmbr0` | Existing public Linux bridge |

The physical-interface name varies by server. Do not assume it is `eno1`; use the interface already listed as a bridge port under `vmbr0`.

---

### Step 2 of 4 — Verify the public bridge `vmbr0`

Select:

```text
vmbr0
→ Edit
```

It should contain the currently working Proxmox public-network configuration.

Use:

| Proxmox field | Value |
| --- | --- |
| Name | `vmbr0` |
| IPv4/CIDR | Your Proxmox public IP and actual prefix |
| Gateway (IPv4) | Your Proxmox public gateway |
| Bridge ports | Your physical interface |
| Autostart | Enabled |
| VLAN aware | Disabled unless deliberately needed |
| Comment | Public bridge |

For example:

```text
Name: vmbr0
IPv4/CIDR: 139.99.9.206/<actual-prefix>
Gateway (IPv4): <actual-OVH-gateway>
Bridge ports: eno1
Autostart: checked
```

Under advanced options, when shown, use:

```text
Bridge STP: disabled
Bridge FD: 0
```

> **Important:** Do not replace the public prefix or gateway with values from an example. Preserve the exact values already making Proxmox reachable.

Do not enter the OPNsense Additional IP on `vmbr0`. That IP will be configured inside OPNsense.

The public bridge holds:

```text
Physical NIC
├── Proxmox public address
└── OPNsense WAN virtual adapter
```

---

### Step 3 of 4 — Create the private bridge `vmbr1`

While still under:

```text
Node
→ System
→ Network
```

Click:

```text
Create
→ Linux Bridge
```

Enter:

| Proxmox field | Value |
| --- | --- |
| Name | `vmbr1` |
| IPv4/CIDR | `10.77.0.2/24` |
| Gateway (IPv4) | Leave empty |
| Bridge ports | Leave empty |
| Autostart | Enabled |
| VLAN aware | Disabled |
| Comment | OPNsense private LAN |

Under advanced options, if present, use:

```text
Bridge STP: disabled
Bridge FD: 0
```

The important settings are:

```text
Bridge ports: blank
Gateway: blank
```

Proxmox must have only one default gateway, through `vmbr0`.

In the configuration file, a blank **Bridge ports** field becomes effectively:

```ini
bridge-ports none
```

This makes `vmbr1` a private virtual switch with no physical network cable attached.

Click **Create**. You should now see:

```text
vmbr0    Public bridge
vmbr1    10.77.0.2/24
```

---

### Step 4 of 4 — Apply the network configuration

At the top of the **Network** page, click **Apply Configuration**.

Proxmox stages GUI network changes before applying them. With `ifupdown2`, which is standard on current Proxmox installations, **Apply Configuration** can reload the network without rebooting.

Because this is a remote OVH server:

- Keep the current SSH session open.
- Keep the Proxmox browser page open.
- Have OVH rescue access available.
- Do not alter the working `vmbr0` values unnecessarily.

Creating an isolated `vmbr1` normally should not interrupt `vmbr0`, but public-network changes always deserve caution.

Avoid attaching ordinary service VMs to `vmbr0`. Only OPNsense WAN should use the public bridge.

---

## Phase 3 — Create and install the OPNsense VM

Phase 3 has 15 steps. Complete them in order.

---

### Step 1 of 15 — Prepare the OPNsense ISO

The OPNsense download is often compressed as:

```text
OPNsense-xx.x-dvd-amd64.iso.bz2
```

Proxmox needs the extracted `.iso`, not the `.bz2` archive.

On Windows, right-click the file in 7-Zip and extract it. The result should be:

```text
OPNsense-xx.x-dvd-amd64.iso
```

OPNsense's documentation confirms that the downloaded image must be unpacked before use.

#### Upload the ISO to Proxmox

In the Proxmox GUI:

1. Select the node, probably `px`.
2. Select **local** storage.
3. Open **ISO Images**.
4. Click **Upload**.
5. Select the extracted OPNsense DVD ISO.
6. Wait until the upload finishes.

Use **local**, not **local-lvm**, because ISO images normally reside on directory storage.

---

### Step 2 of 15 — Start the VM creation wizard

Click **Create VM**.

On the **General** tab, use:

```text
Node:           px
VM ID:          any unused ID, for example 100
Name:           opnsense
Resource Pool:  leave empty
```

Start-at-boot behavior will be enabled later under the VM's **Options** page.

---

### Step 3 of 15 — Configure the OS tab

Use:

```text
Use CD/DVD disc image file: enabled
Storage:                     local
ISO image:                   your OPNsense DVD ISO
Guest OS Type:               Other
Version:                     default
```

OPNsense officially supports installation in a VM from its DVD ISO.

---

### Step 4 of 15 — Configure the System tab

Use:

```text
Machine:          q35
BIOS:             SeaBIOS
SCSI Controller:  VirtIO SCSI single
QEMU Guest Agent: disabled for now
TPM:              none
```

OPNsense supports the newer Q35 chipset under KVM.

#### Why SeaBIOS is recommended here

OPNsense works without UEFI. SeaBIOS is simpler because it does not require an EFI disk or Secure Boot settings.

OVMF may be used instead, but then configure:

```text
BIOS:             OVMF (UEFI)
EFI Storage:      local
Pre-Enroll Keys:  disabled
EFI Disk:         created
```

Do not enable Secure Boot. It provides no meaningful benefit for this appliance and can complicate booting.

---

### Step 5 of 15 — Configure the Disk tab

Use:

```text
Bus/Device:     SCSI 0
Storage:        local
Disk size:      32 GiB
Cache:          Default
Discard:        optional
SSD emulation:  optional, if the physical storage is SSD
```

A 32 GB disk is comfortably above OPNsense's documented minimum virtual-disk recommendation of 8 GB.

If the Proxmox installation only exposes **local**, using it here is acceptable. The virtual disk will generally be stored as a raw or QCOW2 file rather than an LVM volume.

---

### Step 6 of 15 — Configure the CPU tab

Use:

```text
Sockets:  1
Cores:    2
Type:     host
NUMA:     disabled
```

The `host` type exposes the physical CPU's supported instructions directly to OPNsense. On a single Proxmox node, losing cross-host live-migration compatibility is irrelevant.

Two cores are enough for routing, NAT, firewalling, and moderate VPN use. Additional services such as heavy IDS/IPS inspection may eventually justify more cores.

---

### Step 7 of 15 — Configure the Memory tab

Use:

```text
Memory:             4096 MiB
Ballooning Device:  unchecked
```

OPNsense recommends at least 3 GB for virtual installations, so 4 GB is appropriate. Low memory can cause installation-copy failures.

Disable ballooning because OPNsense is the router and its assigned memory should remain predictable.

---

### Step 8 of 15 — Add the WAN network device

The VM wizard adds the first network device. Configure it as the WAN interface:

```text
Bridge:       vmbr0
Model:        VirtIO (paravirtualized)
MAC address:  exact OVH-generated virtual MAC
VLAN Tag:     empty
Firewall:     unchecked
Rate limit:   empty/unlimited
Multiqueue:   default
```

Enter the OVH MAC exactly. Do not:

- Generate a random WAN MAC.
- Copy the physical server's MAC.
- Use the Proxmox host's MAC.
- Use the automatically generated Proxmox MAC.

OVH specifically requires the VM network interface to use the virtual MAC associated with the Additional IP.

#### Do not start the VM yet

On the final wizard page, leave **Start after created** unchecked.

Create the VM first, and then add the LAN adapter.

---

### Step 9 of 15 — Add the LAN network device

Select:

```text
opnsense VM
→ Hardware
→ Add
→ Network Device
```

Configure:

```text
Bridge:       vmbr1
Model:        VirtIO
MAC address:  automatically generated
VLAN Tag:     empty
Firewall:     unchecked
Rate limit:   unlimited
```

This should become the second device, `net1`.

The intended mapping is:

```text
Proxmox net0 → vmbr0 → OPNsense vtnet0 → WAN
Proxmox net1 → vmbr1 → OPNsense vtnet1 → LAN
```

#### Verify the device order

From the Proxmox host, run:

```shell
qm config <VMID>
```

For VM ID `100`:

```shell
qm config 100
```

The output should resemble:

```text
net0: virtio=02:00:00:AB:CD:EF,bridge=vmbr0
net1: virtio=BC:24:11:12:34:56,bridge=vmbr1
```

The MAC on `net0` must match the OVH-generated virtual MAC.

Device order matters because the first VirtIO network interface normally becomes `vtnet0`, while the second becomes `vtnet1`. Nevertheless, verify them by their MAC addresses during interface assignment rather than trusting the names blindly.

If the actual private bridge is named `vmbr2`, use `vmbr2`. Do not blindly select `vmbr1` merely because this guide uses that name.

---

### Step 10 of 15 — Configure startup behavior

Open:

```text
opnsense VM
→ Options
```

Set:

```text
Start at boot:  yes
Start/Shutdown order:
    Order:             1
    Startup delay:     30
    Shutdown timeout:  120
```

The startup delay gives OPNsense time to initialize before Proxmox starts VMs that depend on it for DHCP, DNS, or Internet access.

Also open **Boot Order** and ensure that, during installation, the order is:

```text
1. CD/DVD drive
2. SCSI disk
```

---

### Step 11 of 15 — Start the installation

Select the VM and click **Start**, and then open **Console**.

OPNsense will boot into a live environment from the DVD ISO.

You may see:

```text
Press any key to start the configuration importer
```

Do not press anything. The importer is for restoring an existing configuration.

Wait for the login prompt.

---

### Step 12 of 15 — Start the OPNsense installer

At the login prompt, enter:

```text
login: installer
password: opnsense
```

The password will not visibly move the cursor while typing. That is normal.

OPNsense documents `installer` / `opnsense` as the default installer credentials. The live environment also allows `root` / `opnsense`.

If the installer account does not work:

1. Log in as `root`.
2. Enter `opnsense` as the password.
3. Select **8) Shell**.
4. Run:

```shell
opnsense-installer
```

---

### Step 13 of 15 — Complete the installer selections

Use approximately these selections.

For the keymap, select:

```text
Default keymap
```

For the filesystem, either UFS or ZFS can be used. For this VM, use:

```text
Install ZFS
```

Then select:

```text
ZFS configuration:  stripe
Disk:               the 32 GB virtual disk
```

A stripe is correct because there is only one virtual disk. It does not provide redundancy, but the Proxmox host handles the actual storage redundancy and backups.

OPNsense currently describes ZFS as the generally preferred and more reliable option.

The target disk will probably appear as something similar to:

```text
da0
```

Select the disk by its 32 GB size. Do not select the CD/DVD drive.

#### Confirm formatting

Choose **Yes**.

This only erases the VM's 32 GB virtual disk; it does not erase the Proxmox host.

#### Set the root password

Set a strong root password and save it in a password manager.

#### Complete the installation

When the installer reaches its completion screen, do not allow the VM to repeatedly boot from the ISO.

---

### Step 14 of 15 — Remove the installation ISO

Before selecting the final reboot option, return to the Proxmox GUI:

```text
opnsense VM
→ Hardware
→ CD/DVD Drive
→ Edit
```

Select **Do not use any media**. Then return to the console and select **Complete Install**.

Alternatively:

1. Shut down the VM after installation.
2. Remove the ISO.
3. Change **Boot Order** so the SCSI disk is first.
4. Start the VM again.

The final boot order should be:

```text
1. scsi0
```

The empty CD/DVD device may remain attached. Only the ISO needs to be ejected; deleting the virtual CD drive is unnecessary.

---

### Step 15 of 15 — Assign WAN and LAN correctly

After booting from the installed disk, OPNsense may ask whether to configure VLANs and assign interfaces.

For the VLAN prompt, enter:

```text
Do you want to configure VLANs now? n
```

#### Assign the interfaces

Be careful: OPNsense may ask for the LAN interface first, even though the WAN mapping is commonly described first.

Enter:

```text
LAN interface:       vtnet1
WAN interface:       vtnet0
Optional interface:  press Enter
```

Confirm with `y`.

The resulting assignment must be:

```text
WAN = vtnet0 = OVH virtual MAC = vmbr0
LAN = vtnet1 = automatic MAC = vmbr1
```

OPNsense's documentation notes that manual assignment asks for LAN first and WAN second.

#### Verify using the MAC addresses

During assignment, OPNsense normally displays the detected interfaces and their MAC addresses. Match them as follows:

```text
Interface carrying OVH virtual MAC → WAN
Other VirtIO interface             → LAN
```

This is safer than relying only on `vtnet0` and `vtnet1`.

If the assignments are wrong later, log in to the console and choose:

```text
1) Assign interfaces
```

---

## Phase 4 — Configure the OPNsense LAN first

This phase establishes the private network before configuring the OVH WAN.

At the end of this phase, the LAN should be:

```text
OPNsense LAN
vtnet1
   │
   ├── Address: 10.77.0.1/24
   ├── Gateway: none
   ├── IPv6: none
   └── Bridge: vmbr1
```

`10.77.0.1` becomes the default gateway for every private VM attached to this bridge.

OPNsense normally starts with `192.168.1.1/24` on LAN. Replace that default address with `10.77.0.1/24`.

Phase 4 has seven steps. Complete them in order.

---

### Step 1 of 7 — Confirm the LAN interface

Before changing its address, confirm:

```text
WAN = vtnet0 = vmbr0 = OVH virtual MAC
LAN = vtnet1 = vmbr1 = automatically generated MAC
```

From the Proxmox host, run:

```shell
qm config <OPNSENSE_VM_ID>
```

For example:

```shell
qm config 100
```

The output should resemble:

```text
net0: virtio=02:00:00:AB:CD:EF,bridge=vmbr0
net1: virtio=BC:24:11:12:34:56,bridge=vmbr1
```

Use the bridge actually attached to the OPNsense LAN device. If the private bridge is named `vmbr2`, replace `vmbr1` throughout this phase.

---

### Step 2 of 7 — Open the OPNsense console

In Proxmox, open:

```text
OPNsense VM
→ Console
```

Log in with:

```text
Username: root
Password: the root password created during installation
```

The console menu contains:

```text
1) Assign interfaces
2) Set interface(s) IP address
3) Reset the root password
...
```

OPNsense documents option `2` as the console command for setting interface addresses.

Select:

```text
2
```

---

### Step 3 of 7 — Configure the LAN address

The precise wording may vary slightly by OPNsense version, but answer approximately as follows.

#### Select the LAN interface

You may see:

```text
Available interfaces:

1 - WAN
2 - LAN
```

Enter:

```text
2
```

Make sure the selected interface is **LAN**, not **WAN**.

#### Configure IPv4

When asked:

```text
Configure IPv4 address LAN interface via DHCP?
```

Enter:

```text
n
```

For the new LAN IPv4 address, enter:

```text
10.77.0.1
```

For the subnet bit count, enter:

```text
24
```

A `/24` describes this network:

```text
Network:     10.77.0.0
Usable IPs:  10.77.0.1–10.77.0.254
Broadcast:   10.77.0.255
```

It does not automatically assign all those addresses to OPNsense. OPNsense itself receives only `10.77.0.1`.

#### Leave the upstream gateway empty

When asked for the upstream gateway, press **Enter** and leave it completely blank.

Do not enter:

- `10.77.0.1`
- The OVH gateway

The LAN interface has no upstream gateway because OPNsense is the gateway for the LAN. The system's default route will later point through the WAN interface.

#### Leave IPv6 unconfigured

When asked whether to configure IPv6 through DHCP6, enter:

```text
n
```

When asked for a LAN IPv6 address, press **Enter**. This leaves IPv6 unconfigured for now.

#### Leave the DHCP server disabled for now

You may be asked:

```text
Do you want to enable the DHCP server on LAN?
```

For this phase, enter:

```text
n
```

The final DHCP scope will be configured deliberately later. For initial access, use a temporary static address on Proxmox.

If DHCP is enabled accidentally, it is not disastrous, but verify its range before attaching other VMs.

#### Keep HTTPS enabled

You may be asked:

```text
Do you want to revert to HTTP as the webGUI protocol?
```

Enter:

```text
n
```

#### Do not restore WebGUI defaults

If asked whether to restore WebGUI access defaults, enter:

```text
n
```

Only use that recovery option if the WebGUI is inaccessible because of a previous configuration mistake.

When complete, the console should display:

```text
LAN (vtnet1) → v4: 10.77.0.1/24
```

---

### Step 4 of 7 — Establish temporary WebGUI access

Because `vmbr1` is an isolated virtual switch, the Windows computer cannot directly reach `10.77.0.1` yet.

The simplest temporary path is:

```text
Windows
   │
   │ Tailscale SSH
   ▼
Proxmox host: 10.77.0.2
   │
   │ vmbr1
   ▼
OPNsense LAN: 10.77.0.1
```

A Proxmox Linux bridge acts like a virtual network switch that connects the host and attached guests.

#### Add a temporary private IP to Proxmox if needed

On the Proxmox host, check the bridge first:

```shell
ip -br address show vmbr1
```

If it has no address in `10.77.0.0/24`, temporarily add:

```shell
sudo ip address add 10.77.0.2/24 dev vmbr1
```

If logged in as `root`, use:

```shell
ip address add 10.77.0.2/24 dev vmbr1
```

Do not add a gateway.

Verify:

```shell
ip -br address show vmbr1
```

Expected output:

```text
vmbr1    UP    10.77.0.2/24
```

Test OPNsense:

```shell
ping -c 3 10.77.0.1
```

Then test HTTPS:

```shell
curl -kI https://10.77.0.1
```

A response such as `HTTP/1.1 200 OK` or a redirect confirms that the WebGUI is reachable.

The `ip address add` command is temporary. It disappears after a Proxmox reboot or network reload, which is preferable during initial setup.

---

### Step 5 of 7 — Tunnel the WebGUI to Windows

From PowerShell, run:

```powershell
ssh -N -L 8443:10.77.0.1:443 morfuse@px
```

Here:

```text
8443        = temporary port on the Windows computer
10.77.0.1   = OPNsense LAN address
443         = OPNsense HTTPS WebGUI
morfuse@px  = normal Tailscale SSH connection to Proxmox
```

Leave that PowerShell window open.

Open:

```text
https://localhost:8443
```

The browser will probably display a certificate warning because OPNsense initially uses a self-signed certificate and the certificate name will not match `localhost`. That is expected during setup.

Proceed only because:

- You created the SSH tunnel yourself.
- It runs through the Tailscale connection.
- The destination is the OPNsense VM.

Log in using:

```text
Username: root
Password: the OPNsense root password
```

OPNsense exposes its initial WebGUI on HTTPS and uses the `root` account for the first login.

#### If a DNS-rebind warning appears

Try opening:

```text
https://10.77.0.1
```

This only works when the computer already has a route to the private subnet.

For the SSH-tunnel method, temporarily add this entry to the Windows hosts file:

```text
127.0.0.1 opnsense.px.mcube.uk
```

The hosts file is:

```text
C:\Windows\System32\drivers\etc\hosts
```

Then browse to:

```text
https://opnsense.px.mcube.uk:8443
```

Remove the hosts-file entry later, after internal DNS or Tailscale routing is configured.

---

### Step 6 of 7 — Complete the initial setup wizard

OPNsense usually offers to start the wizard after the first WebGUI login. If it does not, open:

```text
System
→ Wizard
```

The exact page order can vary slightly by release.

#### General information

Set:

```text
Hostname:  opnsense
Domain:    px.mcube.uk
```

Do not put the complete hostname in the **Hostname** field.

Correct:

```text
Hostname:  opnsense
Domain:    px.mcube.uk
```

This produces:

```text
opnsense.px.mcube.uk
```

Incorrect:

```text
Hostname:  opnsense.px.mcube.uk
Domain:    px.mcube.uk
```

OPNsense defines the hostname field as the host portion without the domain, while the domain is entered separately.

#### DNS servers

Enter:

```text
Primary DNS:    1.1.1.1
Secondary DNS:  9.9.9.9
```

If the wizard provides gateway selectors beside each DNS server, leave them set to **None**.

There is currently only one future WAN gateway, so explicit DNS-to-gateway binding is unnecessary.

#### DNS override

You may see:

```text
Allow DNS server list to be overridden by DHCP/PPP on WAN
```

Uncheck it.

The OVH WAN will eventually use a manually configured static Additional IP rather than ISP-provided DNS through DHCP. Disabling the override ensures that the explicit DNS servers remain configured. OPNsense states that enabling this option permits WAN DHCP or PPP to replace the DNS servers used by the system and its DNS services.

#### Local DNS service

You may see:

```text
Do not use the local DNS service as a nameserver for this system
```

Leave this unchecked.

This permits OPNsense itself to use its local DNS resolver. The setup wizard configures Unbound as the resolver and Dnsmasq for DHCP-related functionality in current OPNsense versions.

#### Time server

The NTP server can normally remain at its default, such as:

```text
0.opnsense.pool.ntp.org
```

Set:

```text
Timezone: Asia/Manila
```

OPNsense stores this under the general system settings and recommends selecting the timezone closest to the deployment.

Accurate time matters for:

- Firewall logs
- TLS certificates
- Authentication codes
- Update checks
- Scheduled tasks
- Troubleshooting event timelines

#### WAN interface

Do not enter the OVH Additional IP in this phase unless already following the dedicated OVH WAN procedure.

For now, leave IPv4 set to:

```text
IPv4 configuration type: DHCP
```

This is temporary. It probably will not obtain an address from OVH, which is expected.

Set:

```text
IPv6 configuration type: None
```

Leave these enabled for a public OVH WAN:

```text
Block private networks: enabled
Block bogon networks:   enabled
```

Do not configure these yet:

- OVH Additional IP
- `/32` prefix
- OVH gateway
- Gateway route
- Public DNS record
- Port forwarding

Those belong to the next phase.

#### LAN interface

Confirm:

```text
LAN IPv4 address: 10.77.0.1
Subnet mask:      24
```

There must be no LAN gateway.

If the wizard attempts to change the LAN address back to `192.168.1.1`, replace it with `10.77.0.1`.

Keep IPv6 disabled for now.

#### Administrator password

Set a strong, unique root password if this has not already been done.

Do not reuse:

- The Proxmox password
- An email password
- The OVH password
- A regular Linux-account password

Store it in a password manager.

A named administrator and TOTP-based two-factor authentication can be configured later.

#### Apply the wizard configuration

Complete the wizard and allow OPNsense to reload.

The browser connection may temporarily disappear while services restart.

Reconnect through the existing SSH tunnel using:

```text
https://localhost:8443
```

If necessary, stop the tunnel with `Ctrl+C` and recreate it:

```powershell
ssh -N -L 8443:10.77.0.1:443 morfuse@px
```

---

### Step 7 of 7 — Verify the resulting LAN configuration

In OPNsense, open:

```text
Interfaces
→ Overview
```

Confirm:

```text
LAN device:  vtnet1
IPv4:        10.77.0.1/24
IPv6:        none
Gateway:     none
Status:      up
```

Also open:

```text
System
→ Settings
→ General
```

Confirm:

```text
Hostname:    opnsense
Domain:      px.mcube.uk
Timezone:    Asia/Manila
DNS server:  1.1.1.1
DNS server:  9.9.9.9
```

OPNsense places the hostname, domain, timezone, and system DNS configuration on this **General** settings page.

---

## Phase 5 — Configure the OPNsense WAN

This phase assigns the OVH Additional IP to OPNsense, creates the far gateway, installs the default route, and verifies Internet and repository access.

Phase 5 has nine steps. Complete them in order.

---

### Step 1 of 9 — Configure the static WAN address

Open:

```text
Interfaces
→ WAN
```

Configure:

```text
Enable interface:          enabled
IPv4 Configuration Type:  Static IPv4
IPv6 Configuration Type:  None
```

Under **Static IPv4 configuration**, enter:

```text
IPv4 Address:  <OPNSENSE_ADDITIONAL_IP>
Prefix:        32
```

Example only:

```text
IPv4 Address:  192.0.2.50
Prefix:        32
```

A `/32` means that OPNsense owns only that individual public IP. It does not imply that the OVH gateway belongs to the same directly connected subnet.

#### Leave the MAC address field blank

Leave the OPNsense WAN **MAC Address** field blank.

The correct virtual MAC is already assigned to the VM's network adapter in Proxmox. Entering another value inside OPNsense would override it.

#### Enable private and bogon filtering

Set:

```text
Block private networks:  enabled
Block bogon networks:    enabled
```

These settings are appropriate because `vtnet0` is a public Internet-facing interface.

#### Leave the gateway rule unset initially

At this point, leave:

```text
IPv4 gateway rules:  None
```

`OVH_WAN` has not been created yet.

Click:

```text
Save
→ Apply changes
```

OPNsense may temporarily show the WAN address without working Internet access. That is expected because the gateway and default route have not yet been configured.

---

### Step 2 of 9 — Create the OVH gateway

Open:

```text
System
→ Gateways
→ Configuration
```

Click **Add**.

Configure:

```text
Name:              OVH_WAN
Description:       OVH WAN gateway
Interface:         WAN
Address Family:    IPv4
IP Address:        <OVH_GATEWAY>
Upstream Gateway:  enabled
Far Gateway:       enabled
Monitor IP:        1.1.1.1
```

Also verify the advanced options:

```text
Disable Gateway Monitoring:  unchecked
Disable Host Route:          unchecked
Mark Gateway as Down:        unchecked
```

Leave priority and weight at their defaults.

#### Why Far Gateway is required

The WAN interface is configured as:

```text
<OPNSENSE_ADDITIONAL_IP>/32
```

From a normal subnetting perspective, no other address—including the OVH gateway—is inside that `/32`.

Enabling **Far Gateway** tells OPNsense that the gateway may legitimately exist outside the interface's directly connected subnet. OPNsense defines this option specifically for gateways outside the connected interface network.

Conceptually, OPNsense needs to install:

```text
<OVH_GATEWAY> reachable through vtnet0
0.0.0.0/0 routed through <OVH_GATEWAY>
```

#### Why Upstream Gateway is enabled

This identifies `OVH_WAN` as an Internet-facing gateway that can provide the system's default IPv4 route.

#### Why Monitor IP is `1.1.1.1`

The immediate OVH gateway being reachable only proves that the local link works. Monitoring `1.1.1.1` checks whether traffic can travel beyond the gateway.

OPNsense requires the monitor address to be reachable through the interface and gateway being monitored.

Click:

```text
Save
→ Apply changes
```

---

### Step 3 of 9 — Assign the gateway to the WAN interface

Return to:

```text
Interfaces
→ WAN
```

Under **Static IPv4 configuration**, select:

```text
IPv4 gateway rules:  OVH_WAN
```

Click:

```text
Save
→ Apply changes
```

Wait several seconds for the routes and gateway-monitoring service to reload.

Do not add a WAN firewall rule during this process. Traffic initiated by OPNsense itself does not require an inbound WAN allow rule.

---

### Step 4 of 9 — Verify the installed route and gateway

Open:

```text
System
→ Routes
→ Status
```

Look for a default IPv4 route resembling:

```text
Destination:  0.0.0.0/0
Gateway:      <OVH_GATEWAY>
Interface:    vtnet0
```

There should also be a route that makes the far gateway reachable through the WAN interface.

Then open:

```text
System
→ Gateways
→ Configuration
```

Find `OVH_WAN` and confirm:

```text
Gateway:  OVH_WAN
Status:   Online
```

It may initially display **Pending** or **Offline** for several seconds while monitoring starts.

If it remains offline, check whether the monitor address is reachable through the intended interface and whether the appropriate route exists under **System → Routes → Status**.

---

### Step 5 of 9 — Test the OVH gateway

Open:

```text
Interfaces
→ Diagnostics
→ Ping
```

Configure:

```text
Address Family:  IPv4
Source Address:  <OPNSENSE_ADDITIONAL_IP>
Host:            <OVH_GATEWAY>
Count:           3
```

Select the WAN Additional IP as the source. OPNsense's diagnostic ping supports choosing the source address so the correct interface and route can be verified.

Run the test.

Expected:

```text
0% packet loss
```

If the gateway test fails, check:

- [ ] The correct Additional IP is entered.
- [ ] The prefix is `/32`.
- [ ] The correct OVH gateway is entered.
- [ ] **Far Gateway** is enabled.
- [ ] WAN is `vtnet0`.
- [ ] `vtnet0` is connected to `vmbr0`.
- [ ] `vtnet0` uses the OVH virtual MAC.
- [ ] The Additional IP is attached to this OVH server.

Do not continue until the gateway is reachable.

---

### Step 6 of 9 — Test Internet routing

Still under:

```text
Interfaces
→ Diagnostics
→ Ping
```

Configure:

```text
Source Address:  <OPNSENSE_ADDITIONAL_IP>
Host:            1.1.1.1
```

Run the test.

If the OVH gateway responds but `1.1.1.1` does not, open:

```text
System
→ Routes
→ Status
```

Make sure the default route points to `OVH_WAN`.

Also verify:

```text
System
→ Gateways
→ Configuration
→ OVH_WAN
```

These settings must remain:

```text
Upstream Gateway:   enabled
Far Gateway:        enabled
Disable Host Route: unchecked
```

---

### Step 7 of 9 — Test DNS resolution

Pinging `pkg.opnsense.org` alone is not a reliable repository test. A hostname may resolve and serve HTTPS while refusing ICMP echo requests.

Instead, open:

```text
Interfaces
→ Diagnostics
→ DNS Lookup
```

Enter:

```text
pkg.opnsense.org
```

The lookup should return at least one IP address.

The hostname may also be tested with ping, but do not treat a failed ping as conclusive if DNS resolution works.

---

### Step 8 of 9 — Test the OPNsense repository

Open:

```text
System
→ Firmware
→ Status
```

Click **Check for updates**.

This confirms that:

- The WAN address works.
- The default route works.
- DNS resolution works.
- HTTPS works.
- The OPNsense repository is reachable.

Do not proceed if errors appear, such as:

```text
Transient resolver failure
Unable to update repository
Repository has no meta file
```

The completion criteria are:

- [x] The OVH gateway responds.
- [x] `1.1.1.1` responds.
- [x] `pkg.opnsense.org` resolves.
- [x] The firmware update check reaches the repository.

---

### Step 9 of 9 — Complete the final configuration check

The OPNsense WAN should now show:

```text
Interface:              vtnet0
Bridge:                 vmbr0
MAC:                    OVH-generated virtual MAC
IPv4 Configuration:     Static IPv4
IPv4 Address:           <OPNSENSE_ADDITIONAL_IP>/32
IPv6 Configuration:     None
IPv4 gateway rules:     OVH_WAN
Block private networks: enabled
Block bogon networks:   enabled
```

The gateway should show:

```text
Name:              OVH_WAN
Interface:         WAN
Address Family:    IPv4
IP Address:        <OVH_GATEWAY>
Upstream Gateway:  enabled
Far Gateway:       enabled
Monitor IP:        1.1.1.1
Status:            Online
```

Keep this management path unchanged:

```text
Proxmox vmbr1:  10.77.0.2/24
OPNsense LAN:   10.77.0.1/24
```

---

## Phase 6 — Configure virtualization networking settings

Open:

```text
Interfaces
→ Settings
```

Ensure these are disabled:

```text
Hardware checksum offloading
Hardware TCP segmentation offloading
Hardware large receive offloading
VLAN hardware filtering
```

OPNsense recommends disabling hardware offloading for virtual installations because some virtual drivers and packet-forwarding features behave incorrectly with it enabled. ([OPNsense Documentation][2])

Reboot OPNsense after applying these settings.

---

## Phase 7 — Configure LAN firewall access

Open:

```text
Firewall
→ Rules
→ LAN
```

Create:

```text
Action: Pass
Interface: LAN
Direction: In
IP version: IPv4
Protocol: Any
Source: LAN net
Destination: Any
Gateway: default
Description: Allow private network outbound
```

This allows private VMs to reach OPNsense and the Internet.

Avoid selecting the WAN gateway explicitly in this rule. Leave the gateway as the default unless policy routing is intentional.

---

## Phase 8 — Configure source NAT

Open:

```text
Firewall
→ NAT
→ Source NAT
```

Select:

```text
Automatic Source NAT rule generation
```

Apply the configuration.

OPNsense will automatically translate:

```text
10.77.0.0/24
→ OPNsense WAN IPv4
```

Automatic source NAT is the recommended mode when one WAN IPv4 is shared by an internal network. ([OPNsense Documentation][3])

Do not create source NAT on Proxmox.

---

## Phase 9 — Configure DHCP

Use Dnsmasq as the DHCP service and Unbound as the DNS resolver.

Phase 9 has 11 steps. Step 6 is optional, and Steps 9–11 may be deferred for now.

---

### Step 1 of 11 — Ensure no other DHCP server is active

Only one DHCP server should listen on the LAN.

Check that this service is not enabled for LAN:

```text
Services
→ KEA DHCP
```

Also check, if present:

```text
Services
→ ISC DHCPv4
```

If either service is enabled on LAN, disable it before enabling Dnsmasq.

OPNsense warns that Dnsmasq may fail to start when Kea or ISC DHCP already occupies the required DHCP ports.

This does not affect Unbound. Unbound provides DNS, while Dnsmasq will provide DHCP.

---

### Step 2 of 11 — Configure the Dnsmasq service

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ General
```

Set:

```text
Enable:                        enabled
Interface:                     LAN
Listen Port:                   0
DHCP authoritative:            enabled
DHCP register firewall rules:  enabled
Router Advertisements:         disabled
```

Then click **Apply**.

#### Interface

Select only:

```text
LAN
```

Do not select WAN.

Selecting LAN tells Dnsmasq where to accept DHCP requests and allows OPNsense to register the required DHCP firewall rules for that interface.

#### Listen Port

Set:

```text
0
```

This is an intentional special value. In OPNsense, setting the Dnsmasq listening port to `0` completely disables its DNS function while leaving DHCP available. This avoids a conflict with Unbound, which normally owns TCP and UDP port 53.

The service division becomes:

```text
Dnsmasq:
  DHCP only
  UDP 67

Unbound:
  DNS only
  TCP/UDP 53
```

Do not leave the Dnsmasq port blank in this design. A blank value means the normal DNS port 53, which would conflict with Unbound.

#### DHCP authoritative

Enable this because OPNsense is intended to be the only DHCP server on `10.77.0.0/24`.

Authoritative mode helps Dnsmasq respond cleanly to clients that previously received leases from another network or DHCP server.

#### DHCP register firewall rules

Enable this.

It creates the service-level firewall allowances required for LAN clients to send DHCP requests to OPNsense. It does not grant general Internet access; that still depends on the LAN firewall rules.

#### Router Advertisements

Leave this disabled because IPv6 is currently disabled in this design.

---

### Step 3 of 11 — Create the LAN DHCP range

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ DHCP ranges
```

Click **Add**.

Configure:

```text
Interface:      LAN
Start address:  10.77.0.100
End address:    10.77.0.199
```

For the domain field, either leave it blank or enter:

```text
px.mcube.uk
```

Leaving it blank allows the system domain configured earlier to be used.

Leave the remaining advanced fields at their defaults unless there is a specific reason to change them.

Click:

```text
Save
→ Apply
```

OPNsense's current Dnsmasq configuration uses this model: select an interface and provide the beginning and end of the address pool.

---

### Step 4 of 11 — Use the automatically derived DHCP options

The original phase listed:

```text
Subnet mask:  255.255.255.0
Router:       10.77.0.1
DNS server:   10.77.0.1
```

Those are the correct values for clients to receive, but the current Dnsmasq interface may not ask for them manually.

Dnsmasq automatically derives the common DHCP options from the interface receiving the request:

```text
Subnet:  10.77.0.0/24
Mask:    255.255.255.0

Router option:
10.77.0.1

DNS-server option:
10.77.0.1
```

The router and DNS values default to the IPv4 address of the OPNsense LAN interface. OPNsense documents that a DHCP range automatically sends these standard options without requiring separate manual entries.

Therefore, the configured range can be as simple as:

```text
Interface:  LAN
Start:      10.77.0.100
End:        10.77.0.199
```

Do not manually override the router or DNS options unless the defaults are wrong.

---

### Step 5 of 11 — Reserve addresses below `.100`

The addresses below `.100` are protected because they are outside the DHCP pool.

Dnsmasq will only allocate dynamically:

```text
10.77.0.100–10.77.0.199
```

It will not dynamically assign:

```text
10.77.0.2
10.77.0.10
10.77.0.11
10.77.0.50
```

There is no need to create 98 individual reservations.

The planned address allocation is:

```text
10.77.0.1       OPNsense
10.77.0.2       Proxmox
10.77.0.3–9     Network infrastructure
10.77.0.10      Dokploy production
10.77.0.11      Dokploy staging
10.77.0.12–99   Static servers
```

Configure these static addresses directly in the VM's operating system or through Proxmox cloud-init.

For example, Dokploy production should use:

```text
Address:  10.77.0.10/24
Gateway:  10.77.0.1
DNS:      10.77.0.1
```

Do not configure the same machine with both a manually assigned static address and a DHCP reservation. Choose one method per machine.

For infrastructure servers, direct static addressing through cloud-init is appropriate.

---

### Optional Step 6 of 11 — Create DHCP reservations

For ordinary devices that should use DHCP but always receive the same address, create a Dnsmasq host entry.

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ Hosts
```

Add:

```text
Host:                <hostname>
IP addresses:        <reserved-address>
Hardware addresses:  <device-MAC>
```

For example:

```text
Host:                monitoring
IP addresses:        10.77.0.20
Hardware addresses:  BC:24:11:12:34:56
```

Reservations may exist outside the dynamic DHCP pool. OPNsense treats each reservation as its own single-address allocation.

For cloud-init servers, static guest configuration remains simpler and more explicit.

---

### Step 7 of 11 — Confirm Unbound is running

Open:

```text
Services
→ Unbound DNS
→ General
```

Confirm:

```text
Enable Unbound:  enabled
Listen Port:     blank or 53
```

A blank Unbound listening port means the normal DNS port 53. Unbound is OPNsense's standard recursive DNS resolver and is enabled by default on new installations.

Do not set both services to port 53.

Correct:

```text
Unbound port:  53
Dnsmasq port:  0
```

Incorrect:

```text
Unbound port:  53
Dnsmasq port:  53
```

---

### Step 8 of 11 — Understand the limitation of Dnsmasq port `0`

With Dnsmasq's DNS feature disabled, it provides addresses but does not answer DNS queries for dynamically registered DHCP hostnames.

For example, a DHCP client named:

```text
test-vm
```

may receive an address successfully, but Unbound will not necessarily resolve:

```text
test-vm.px.mcube.uk
```

For important static servers, create records under:

```text
Services
→ Unbound DNS
→ Overrides
```

For example:

```text
dokploy-prod.px.mcube.uk  → 10.77.0.10
dokploy-stage.px.mcube.uk → 10.77.0.11
```

A more advanced alternative is to let Dnsmasq provide DHCP-hostname DNS on a nonstandard port such as `53053`, then configure Unbound to forward the relevant local zone to it. OPNsense documents that architecture, but it is not necessary for this initial deployment.

For now, port `0` is the simpler option.

> **Optional stopping point:** The initial DHCP configuration is complete. Steps 9–11 are validation and observation tasks that may be deferred for now.

---

### Optional Step 9 of 11 — Test DHCP from a private VM

Use a test VM attached to:

```text
Bridge: vmbr1
```

Configure its IPv4 networking to use DHCP.

On Ubuntu with Netplan, that normally resembles:

```yaml
network:
  version: 2
  ethernets:
    ens18:
      dhcp4: true
```

The interface name may differ.

Restart networking or reboot the VM, and then inspect its lease:

```shell
ip -4 address
ip route
cat /etc/resolv.conf
```

Expected results:

```text
Address:
10.77.0.100–10.77.0.199

Subnet:
10.77.0.0/24

Default gateway:
10.77.0.1

DNS:
10.77.0.1
```

The first client will not necessarily receive `.100`; Dnsmasq may choose any currently available address in the configured range.

---

### Optional Step 10 of 11 — Test connectivity in order

From the DHCP client, perform these tests in order.

Confirm its address:

```shell
ip -4 address
```

Confirm its route:

```shell
ip route
```

Expected:

```text
default via 10.77.0.1
```

Test the gateway:

```shell
ping -c 3 10.77.0.1
```

Test public routing:

```shell
ping -c 3 1.1.1.1
```

Test DNS through Unbound:

```shell
getent hosts example.com
```

Alternatively:

```shell
nslookup example.com 10.77.0.1
```

Test HTTPS:

```shell
curl -I https://example.com
```

If all these tests work, DHCP, LAN firewalling, source NAT, routing, and DNS are operating together.

---

### Optional Step 11 of 11 — Inspect active leases

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ Leases
```

The test VM should appear with information such as:

- IP address
- MAC address
- Hostname
- Lease start
- Lease expiry

If the lease does not appear, open:

```text
Services
→ Dnsmasq DNS & DHCP
→ Log
```

OPNsense recommends checking this log when Dnsmasq fails to start or issue leases.

---

### Troubleshooting reference

#### Dnsmasq will not start

Check:

- [ ] Dnsmasq is enabled.
- [ ] The LAN interface is selected.
- [ ] A DHCP range exists.
- [ ] Kea DHCP is disabled.
- [ ] ISC DHCP is disabled.
- [ ] **Listen Port** is `0`.

Then inspect:

```text
Services
→ Dnsmasq DNS & DHCP
→ Log
```

#### A client receives no IP address

Check that its NIC is attached to:

```text
vmbr1
```

Not:

```text
vmbr0
```

Then verify:

```text
DHCP range interface:          LAN
DHCP register firewall rules: enabled
Range:                         10.77.0.100–199
```

#### A client receives an IP but has no Internet access

Check:

```text
Default gateway:  10.77.0.1
LAN firewall pass rule
Automatic Source NAT
OVH_WAN gateway status
```

#### A client can reach `1.1.1.1` but not domain names

Check:

```text
DNS server received by client:  10.77.0.1
Unbound service:                 running
Unbound listen port:             53
Dnsmasq listen port:             0
```

#### Dnsmasq reports that port 53 is already in use

Confirm:

```text
Services
→ Dnsmasq DNS & DHCP
→ General
→ Listen Port
```

is exactly:

```text
0
```

Then apply the configuration again.

---

## Phase 10 — Configure Unbound DNS

Open:

```text
Services
→ Unbound DNS
→ General
```

Configure:

```text
Enabled: yes
Listen Port: 53
Network Interfaces: All
Outgoing Network Interfaces: All
DNSSEC: enabled
```

OPNsense recommends leaving listening and outgoing interface selections on `All` unless there is a specific reason to restrict them. Incorrect interface selection can prevent Unbound from starting or resolving correctly. ([OPNsense Documentation][4])

Private VMs will use:

```text
DNS: 10.77.0.1
```

At this point, do not add application-domain overrides. Wildcard internal overrides are handled later and remain optional.

---

## Phase 11 — Verify routing with a temporary VM

Create an Ubuntu VM connected only to:

```text
Bridge: vmbr1
```

Use DHCP initially, or assign:

```text
IP: 10.77.0.100/24
Gateway: 10.77.0.1
DNS: 10.77.0.1
```

Test:

```bash
ip route
ping -c 3 10.77.0.1
ping -c 3 1.1.1.1
getent hosts example.com
curl -4 https://ifconfig.me
```

The public address returned by the final command should be the OPNsense Additional IPv4.

Avoid progressing to Dokploy or Caddy until basic routing and DNS are working.

---

## Phase 12 — Move the OPNsense WebGUI

Caddy must listen on ports 80 and 443.

Open:

```text
System
→ Settings
→ Administration
```

Set:

```text
TCP Port: 8443
Disable web GUI redirect rule: enabled
```

Reconnect at:

```text
https://10.77.0.1:8443
```

Confirm that port 8443 works before installing or enabling Caddy.

Avoid exposing port 8443 publicly.

---

## Phase 13 — Install Caddy

Open:

```text
System
→ Firmware
→ Plugins
```

Install:

```text
os-caddy
```

Then open:

```text
Services
→ Caddy Web Server
→ General Settings
```

Configure:

```text
Enabled: yes
ACME email: your email address
Auto HTTPS: enabled
HTTP/3: disabled initially
```

Keeping HTTP/3 disabled means only TCP 80 and TCP 443 are needed.

---

## Phase 14 — Permit public web traffic

Open:

```text
Firewall
→ Rules
→ WAN
```

Create an HTTP rule:

```text
Action: Pass
Protocol: TCP
Source: Any
Destination: This Firewall
Destination port: 80
Description: Allow Caddy HTTP
```

Create an HTTPS rule:

```text
Action: Pass
Protocol: TCP
Source: Any
Destination: This Firewall
Destination port: 443
Description: Allow Caddy HTTPS
```

There are no destination-NAT rules for these ports.

The traffic terminates on Caddy itself:

```text
Internet
→ OPNsense WAN
→ Caddy
```

Avoid forwarding 80 or 443 directly to either Dokploy VM.

---

## Phase 15 — Create Cloudflare wildcard DNS

Use separate namespaces:

```text
*.prod.mcube.uk
*.stage.mcube.uk
```

Create these DNS records:

```text
Type: A
Name: *.prod
Content: <OPNSENSE_ADDITIONAL_IP>
Proxy status: DNS only
```

```text
Type: A
Name: *.stage
Content: <OPNSENSE_ADDITIONAL_IP>
Proxy status: DNS only
```

Wildcard records cover hostnames such as:

```text
api.prod.mcube.uk
web.prod.mcube.uk
api.stage.mcube.uk
preview.stage.mcube.uk
```

An exact DNS record can still override a wildcard record. ([Cloudflare Docs][5])

Keep these records DNS-only while setting up TLS.

---

## Phase 16 — Create a Cloudflare API token

Caddy needs DNS access to obtain wildcard certificates.

Create a token restricted to the `mcube.uk` zone with:

```text
Zone → Zone → Read
Zone → DNS → Edit
```

In OPNsense Caddy settings, configure:

```text
DNS provider: Cloudflare
API token: <restricted token>
Resolver: 1.1.1.1
```

Avoid using the Cloudflare Global API Key.

---

## Phase 17 — Configure wildcard Caddy routing

### Production domain

Create a Caddy domain:

```text
Domain: *.prod.mcube.uk
Protocol: HTTPS
DNS-01 challenge: enabled
```

Create its handler:

```text
Frontend: *.prod.mcube.uk
Upstream protocol: HTTP
Upstream host: 10.77.0.10
Upstream port: 80
```

### Staging domain

Create:

```text
Domain: *.stage.mcube.uk
Protocol: HTTPS
DNS-01 challenge: enabled
```

Handler:

```text
Frontend: *.stage.mcube.uk
Upstream protocol: HTTP
Upstream host: 10.77.0.11
Upstream port: 80
```

The routing result is:

```text
*.prod.mcube.uk  → 10.77.0.10:80
*.stage.mcube.uk → 10.77.0.11:80
```

Caddy preserves the original hostname when proxying, allowing Dokploy’s Traefik to perform the second hostname match.

Avoid using multi-level application names such as:

```text
v2.api.prod.mcube.uk
```

A certificate for `*.prod.mcube.uk` covers `api.prod.mcube.uk`, but not another level below it.

---

## Phase 18 — Create the Dokploy VMs

### Production VM

```text
Name: dokploy-prod
Bridge: vmbr1
IP: 10.77.0.10/24
Gateway: 10.77.0.1
DNS: 10.77.0.1
CPU: 2–4 vCPU
RAM: 4 GB initially
Disk: based on workload
Start at boot: enabled
Startup order: 2
```

### Staging VM

```text
Name: dokploy-stage
Bridge: vmbr1
IP: 10.77.0.11/24
Gateway: 10.77.0.1
DNS: 10.77.0.1
CPU: 2–4 vCPU
RAM: 4 GB initially
Disk: based on workload
Start at boot: enabled
Startup order: 3
```

Install Docker and Dokploy independently on each VM.

The two installations do not synchronize projects, databases, secrets, or deployments.

---

## Phase 19 — Configure application domains in Dokploy

For a production application:

```text
Domain: api.prod.mcube.uk
Container port: application’s internal port
HTTPS: disabled
Certificate: none
```

For staging:

```text
Domain: api.stage.mcube.uk
Container port: application’s internal port
HTTPS: disabled
Certificate: none
```

Caddy owns the public TLS certificate. Dokploy receives plain HTTP over the private LAN.

Avoid enabling HTTPS for the same hostname in both Caddy and Dokploy.

The request path is:

```text
https://api.prod.mcube.uk
→ OPNsense Caddy
→ HTTP to 10.77.0.10:80
→ Dokploy Traefik
→ application container
```

---

## Phase 20 — Optional internal wildcard DNS

This phase is optional.

Without overrides, internal clients resolve application domains to the OPNsense public IP. Because that address belongs directly to OPNsense, Caddy can accept the connection.

To force private traffic directly to the LAN address instead, create these Unbound host overrides:

```text
Host: *
Domain: prod.mcube.uk
Type: A
IP: 10.77.0.1
```

```text
Host: *
Domain: stage.mcube.uk
Type: A
IP: 10.77.0.1
```

Unbound supports `*` as a wildcard host value. ([OPNsense Documentation][4])

Do not create one Unbound record for every application.

---

## Phase 21 — Validate the entire path

Test Dokploy production directly:

```bash
curl -v \
  -H 'Host: api.prod.mcube.uk' \
  http://10.77.0.10/
```

Test staging directly:

```bash
curl -v \
  -H 'Host: api.stage.mcube.uk' \
  http://10.77.0.11/
```

Test Caddy internally:

```bash
curl -vk \
  --resolve api.prod.mcube.uk:443:10.77.0.1 \
  https://api.prod.mcube.uk/
```

Test public DNS:

```bash
dig +short api.prod.mcube.uk @1.1.1.1
dig +short api.stage.mcube.uk @1.1.1.1
```

Both should return the OPNsense Additional IPv4.

Finally, test through mobile data:

```text
https://api.prod.mcube.uk
https://api.stage.mcube.uk
```

---

# Normal deployment workflow afterward

For each new production application:

```text
1. Deploy it on Dokploy production.
2. Add app-name.prod.mcube.uk.
3. Select the correct container port.
4. Leave Dokploy HTTPS disabled.
5. Redeploy.
```

For staging:

```text
1. Deploy it on Dokploy staging.
2. Add app-name.stage.mcube.uk.
3. Select the correct container port.
4. Leave Dokploy HTTPS disabled.
5. Redeploy.
```

Nothing else is configured per application:

| Component                 | Per application |
| ------------------------- | --------------: |
| Cloudflare wildcard DNS   |              No |
| OPNsense firewall         |              No |
| Caddy wildcard route      |              No |
| Unbound wildcard override |              No |
| Proxmox NAT               |              No |
| Dokploy domain            |         **Yes** |

That is the clean, from-scratch version: no migration phases, no cleanup instructions, and no assumptions about an earlier network configuration.

[1]: https://help.ovhcloud.com/csm/en-sg-dedicated-servers-pfsense-bridging?id=kb_article_view&sysparm_article=KB0043896&utm_source=chatgpt.com "Configure a pfSense Network Bridge on a Dedicated Server - OVHcloud"
[2]: https://docs.opnsense.org/manual/virtuals.html?utm_source=chatgpt.com "Virtual & Cloud-Based Installation — OPNsense documentation"
[3]: https://docs.opnsense.org/manual/nat.html?utm_source=chatgpt.com "Network Address Translation — OPNsense documentation"
[4]: https://docs.opnsense.org/manual/unbound.html?utm_source=chatgpt.com "Unbound DNS — OPNsense documentation"
[5]: https://developers.cloudflare.com/dns/manage-dns-records/reference/wildcard-dns-records/?utm_source=chatgpt.com "Wildcard DNS records · Cloudflare DNS docs"
