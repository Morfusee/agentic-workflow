# Recommended design

With only **one public IPv4**, I would **not** give the public IP directly to the OPNsense VM. Keep the primary IPv4 on Proxmox and place OPNsense behind a small private transit network.

```text
                              Internet
                                  │
                         Your single public IPv4
                                  │
                    ┌─────────────▼─────────────┐
                    │       Proxmox host        │
                    │                           │
                    │ vmbr0: existing public IP │
                    │ UFW: outer NAT / DNAT     │
                    └─────────────┬─────────────┘
                                  │
                     vmbr1: WAN transit network
                        10.255.255.0/30
                                  │
                       10.255.255.2/30 WAN
                    ┌─────────────▼─────────────┐
                    │         OPNsense          │
                    │                           │
                    │ WAN: 10.255.255.2         │
                    │ LAN: 10.77.0.1            │
                    │ DHCP, DNS, firewall, NAT  │
                    └─────────────┬─────────────┘
                                  │
                       vmbr2: private network
                           10.77.0.0/24
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
       Dokploy VM             Database VM         Other VMs
       10.77.0.10             10.77.0.20          DHCP/static
```

The traffic paths will be:

```text
Outbound:
Private VM → OPNsense → Proxmox NAT → Internet

Inbound HTTP:
Internet → Proxmox DNAT → OPNsense port forward
         → Dokploy/Traefik → application

Management:
Your device → Tailscale → Proxmox
```

Proxmox bridges behave like software network switches, and masquerading lets private guests share the host’s public IP. OVH’s documented transparent-VM approach relies on assigning a virtual MAC to an **Additional IP**; since you only have the primary IP, moving that IP into OPNsense would be substantially riskier. ([Proxmox VE][1])

## Why this is the right design for your situation

This design gives you:

* Continued access to Proxmox even if OPNsense is broken or powered off.
* A GUI firewall and router for all private VMs.
* DHCP for automatically assigning addresses to new VMs.
* Outbound Internet access for all private VMs.
* Port forwarding from your public IP.
* A clean place to add VLANs and isolated networks later.
* No dependence on an additional IPv4 or OVH virtual MAC.

The disadvantage is **double NAT**:

```text
VM private IP
    ↓ OPNsense NAT
OPNsense private WAN IP
    ↓ Proxmox NAT
Public IPv4
```

For normal web hosting, databases, package installation, Git, Docker image pulls, API calls, and similar workloads, this is generally fine. The main inconvenience is that every publicly exposed non-HTTP port needs one rule on Proxmox and one rule in OPNsense.

---

# Address plan

Use this exact plan unless one of these networks overlaps with something you already route through Tailscale.

| Component                       | Interface    |                       Address |              Gateway |
| ------------------------------- | ------------ | ----------------------------: | -------------------: |
| Proxmox                         | `vmbr0`      | Existing public configuration | Existing OVH gateway |
| Proxmox transit side            | `vmbr1`      |             `10.255.255.1/30` |                 None |
| OPNsense WAN                    | `vtnet0`     |             `10.255.255.2/30` |       `10.255.255.1` |
| OPNsense LAN                    | `vtnet1`     |                `10.77.0.1/24` |                 None |
| Proxmox private-side management | `vmbr2`      |                `10.77.0.2/24` |                 None |
| DHCP pool                       | OPNsense LAN |     `10.77.0.100–10.77.0.199` |          `10.77.0.1` |
| Dokploy                         | Private VM   |                  `10.77.0.10` |          `10.77.0.1` |
| Database server                 | Private VM   |                  `10.77.0.20` |          `10.77.0.1` |

A `/30` gives exactly two usable transit addresses:

```text
10.255.255.0    Network
10.255.255.1    Proxmox
10.255.255.2    OPNsense WAN
10.255.255.3    Broadcast
```

---

# Phase 0: Protect yourself from lockout

Before changing networking, verify that Tailscale access to Proxmox works.

Run these from your computer:

```bash
tailscale ping <proxmox-tailscale-name-or-ip>
ssh root@<proxmox-tailscale-ip>
```

Keep two SSH sessions open while applying firewall changes.

On Proxmox, back up the relevant files:

```bash
cp -a /etc/network/interfaces \
  /etc/network/interfaces.pre-opnsense

cp -a /etc/ufw/before.rules \
  /etc/ufw/before.rules.pre-opnsense

cp -a /etc/ufw/sysctl.conf \
  /etc/ufw/sysctl.conf.pre-opnsense

ufw status numbered > /root/ufw-status-pre-opnsense.txt
ip addr > /root/ip-addresses-pre-opnsense.txt
ip route > /root/ip-routes-pre-opnsense.txt
```

Also determine the actual public egress interface:

```bash
ip route get 1.1.1.1
```

You should see something resembling:

```text
1.1.1.1 via <gateway> dev vmbr0 src <public-ip>
```

The interface after `dev` is the interface that should replace `vmbr0` in later commands if yours differs.

**Do not alter the current address, subnet, gateway, bridge port, or other configuration of your public bridge.**

---

# Phase 1: Create the two private bridges

In Proxmox:

```text
Node
└── System
    └── Network
```

## Create `vmbr1`: OPNsense WAN transit bridge

Click **Create → Linux Bridge**.

Use:

```text
Name: vmbr1
IPv4/CIDR: 10.255.255.1/30
Gateway: blank
Bridge ports: blank
Autostart: enabled
VLAN aware: disabled for now
Comment: OPNsense WAN transit
```

This bridge must have **no physical bridge port**. It exists only between Proxmox and OPNsense.

## Create `vmbr2`: private VM network

Create another Linux bridge:

```text
Name: vmbr2
IPv4/CIDR: 10.77.0.2/24
Gateway: blank
Bridge ports: blank
Autostart: enabled
VLAN aware: disabled for now
Comment: OPNsense private LAN
```

There must be only one default gateway on the Proxmox host: the existing gateway associated with the public network. Do not add gateways to `vmbr1` or `vmbr2`.

The resulting relevant configuration will conceptually resemble:

```text
vmbr0
  Existing OVH public configuration
  Physical network interface attached

vmbr1
  10.255.255.1/30
  No bridge port
  No gateway

vmbr2
  10.77.0.2/24
  No bridge port
  No gateway
```

Apply the configuration. Then verify:

```bash
ip -br addr | grep -E '^(vmbr0|vmbr1|vmbr2)\b'
```

Expected:

```text
vmbr0  UP  <your-public-address>
vmbr1  UP  10.255.255.1/30
vmbr2  UP  10.77.0.2/24
```

Confirm that both public SSH and Tailscale SSH still work before proceeding.

---

# Phase 2: Create the OPNsense VM

Download the AMD64 DVD ISO from OPNsense, upload it to your Proxmox ISO storage, and create a VM.

Use approximately:

| Setting             | Value              |
| ------------------- | ------------------ |
| Name                | `opnsense-router`  |
| Start at boot       | Yes                |
| CPU type            | `host`             |
| CPU cores           | 2                  |
| Memory              | 4096 MB            |
| Ballooning          | Disabled           |
| Disk                | 32 GB              |
| Disk controller     | VirtIO SCSI        |
| Network model       | VirtIO             |
| Proxmox VM firewall | Disabled initially |

OPNsense’s documentation requires at least 3 GB of RAM for installation, recommends at least an 8 GB virtual disk, supports KVM, and recommends disabling hardware offloading when virtualized. ([OPNsense Documentation][2])

## Add the interfaces in this order

### Configure network device 0 in the creation wizard

On the wizard’s network page, configure the adapter shown there as:

```text
Bridge: vmbr1
Model: VirtIO
Firewall: unchecked
Purpose: OPNsense WAN
```

Finish creating the VM, but do not start it yet.

### Add network device 1 after creating the VM

Open:

```text
OPNsense VM
→ Hardware
→ Add
→ Network Device
```

Configure the second adapter as:

```text
Bridge: vmbr2
Model: VirtIO
Firewall: unchecked
Purpose: OPNsense LAN
```

The final summary should contain something similar to:

```text
Network Device (net0): VirtIO, bridge=vmbr1
Network Device (net1): VirtIO, bridge=vmbr2
```

Do **not** attach this OPNsense VM to `vmbr0` under the current double-NAT design.

Write down their MAC addresses. That will help identify them if the interface order is unclear during installation.

Set the startup order so OPNsense starts before private VMs:

```text
Start order: 1
Startup delay: 10 seconds
Shutdown timeout: 60 seconds
```

Your Dokploy and other private VMs can use start order 2 or later.

---

# Phase 3: Install OPNsense

Start the VM and open its Proxmox console.

At the live environment login, use:

```text
Username: installer
Password: opnsense
```

Those are the documented installer credentials. The installer will prompt you to choose a filesystem, disk, and new root password. ([OPNsense Documentation][3])

For this VM, I would use:

```text
Filesystem: UFS
Partitioning: guided/default
Target: the 32 GB VM disk
Root password: a new strong password
```

ZFS also works, but UFS is simpler for a small single-disk firewall VM.

When installation finishes:

In the Proxmox web UI:

```text
VM 100 (opnsense-router)
→ Hardware
→ CD/DVD Drive (ide2)
→ Edit
→ Do not use any media
→ OK
```

That **ejects the OPNsense ISO but keeps the virtual CD/DVD drive**, which is usually preferable to removing the whole device. Proxmox presents ISO files to guests as virtual CD-ROM media. ([Proxmox VE][11])

Then check:

```text
VM 100
→ Options
→ Boot Order
```

Make sure the 32 GB disk, usually `scsi0`, is enabled and placed before the CD/DVD drive.

If the installer is still running, finish the installation first. When it asks to reboot:

1. Choose reboot.
2. Detach the ISO immediately.
3. Let the VM boot from `scsi0`.

CLI equivalent:

```bash
sudo qm set 100 --ide2 none,media=cdrom
```

---

# Phase 4: Assign the interfaces

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
Subnet bits: 24
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
Subnet bits: 30
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

---

# Phase 5: Access the OPNsense WebGUI safely

Do **not** expose the OPNsense WebGUI through the public IP.

Because Proxmox has `10.77.0.2` on `vmbr2`, you can tunnel through the Proxmox host.

From your computer:

```bash
ssh -L 8443:10.77.0.1:443 root@<proxmox-tailscale-ip>
```

Leave that SSH session running and open:

```text
https://localhost:8443
```

A certificate warning is expected because OPNsense initially uses a self-signed certificate.

Log in using:

```text
Username: root
Password: the password you set during installation
```

---

# Phase 6: Configure OPNsense WAN and LAN

## WAN configuration

Navigate to:

```text
Interfaces → WAN
```

The static WAN address should already be present from Phase 4. Verify:

```text
Enable interface: Yes
Description: WAN
IPv4 Configuration Type: Static IPv4
IPv6 Configuration Type: None
Static IPv4 address: 10.255.255.2/30
Block private networks: unchecked
Block bogon networks: unchecked
```

Save and apply the interface changes.

OPNsense specifically documents that the private-network block must be disabled when its WAN uses a private address. ([OPNsense Documentation][4])

## Configure the WAN gateway

The gateway is configured separately from `Interfaces → WAN`. Navigate to:

```text
System → Gateways → Configuration
```

Check whether a gateway for WAN already exists. If you configured the WAN gateway from the console in Phase 4, OPNsense may already have created it.

If no correct entry exists, click **Add** and configure:

```text
Name: WAN_GW
Interface: WAN
Address Family: IPv4
IP Address: 10.255.255.1
Upstream Gateway: checked
Far Gateway: unchecked
Disable Gateway Monitoring: checked initially
Description: Proxmox transit gateway
```

Save and apply the gateway changes.

`Far Gateway` remains unchecked because `10.255.255.1` and `10.255.255.2/30` are directly connected on the same subnet. OPNsense manages gateways under **System → Gateways → Configuration**, and the active default route can be checked under **System → Routes → Status**. ([OPNsense Documentation][12])

After saving, navigate to:

```text
System → Routes → Status
```

Verify that the default IPv4 route resembles:

```text
default → 10.255.255.1 → WAN/vtnet0
```

Do not configure a gateway on LAN. The final interface addressing is:

```text
WAN/vtnet0: 10.255.255.2/30
WAN gateway: 10.255.255.1

LAN/vtnet1: 10.77.0.1/24
LAN gateway: none
```

After outbound connectivity works, you can enable gateway monitoring and set the monitor address to something such as `1.1.1.1`.

## LAN configuration

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

## Disable hardware offloading

Navigate to:

```text
Interfaces → Settings
```

Enable the options that disable:

```text
Hardware checksum offloading
Hardware TCP segmentation offloading
Hardware large receive offloading
```

The wording is counterintuitive: you normally **check** the boxes saying “Disable.”

OPNsense recommends disabling all hardware-offloading settings for virtual installations. ([OPNsense Documentation][2])

## Update OPNsense

Once Internet access works, use:

```text
System → Firmware → Status → Check for updates
```

OPNsense documents firmware updates through that page. ([OPNsense Documentation][5])

---

# Phase 7: Configure DHCP for automatic VM addressing

For your OPNsense 26.7 setup, use **Dnsmasq as the DHCP server**. It is the current default and is the simplest choice for a small Proxmox network. Keep **Unbound** handling DNS and configure Dnsmasq for DHCP only. ([OPNsense Documentation][13])

Your target is:

```text
OPNsense LAN: 10.77.0.1/24
DHCP pool:    10.77.0.100 – 10.77.0.199
Gateway:      10.77.0.1
DNS server:   10.77.0.1
```

## 1. Confirm Unbound DNS is enabled

In OPNsense, open:

```text
Services
→ Unbound DNS
→ General
```

Confirm:

```text
Enable Unbound: checked
Listen Port: blank
Network Interfaces: All
Outgoing Network Interfaces: All
```

Do not change its port. Blank means the normal DNS port `53`. OPNsense recommends leaving Unbound’s listening and outgoing interface selections at `All` unless you have a specific reason to restrict them. ([OPNsense Documentation][14])

Click **Apply** only if you changed something.

---

## 2. Enable Dnsmasq for DHCP

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ General
```

Configure:

```text
Enable: checked

Interface:
  LAN

Listen Port:
  0

DHCP register firewall rules:
  checked
```

Important details:

* Select **LAN only**, not WAN.
* Setting **Listen Port to `0`** disables Dnsmasq’s DNS function while leaving its DHCP function available.
* Unbound remains your DNS server on port 53.
* Selecting LAN allows OPNsense to register the necessary DHCP firewall handling for that interface. ([OPNsense Documentation][15])

Leave these disabled for now:

```text
Router Advertisements
DHCPv6
DHCP FQDN
DHCP reply delay
```

You are currently building an IPv4-only setup, so you do not need DHCPv6 or Router Advertisements.

Click:

```text
Save
→ Apply
```

---

## 3. Create the DHCP address range

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ DHCP ranges
```

Click the **plus/Add** button.

Enter:

```text
Interface: LAN

Start address:
10.77.0.100

End address:
10.77.0.199

Subnet Mask:
leave blank

Mode:
leave blank/default

Lease time:
86400

Domain:
lab.internal

Description:
Private LAN DHCP pool
```

`86400` means a one-day DHCP lease. Leaving the subnet mask blank lets Dnsmasq derive `/24` from the LAN interface. The range screen supports selecting the interface, start and end addresses, lease time, and domain. ([OPNsense Documentation][15])

Click:

```text
Save
→ Apply
```

You do **not** need to manually add DHCP options for the gateway and DNS server. When a range is created, Dnsmasq automatically advertises the receiving interface’s IP as both the default router and DNS server. In your case, that will be `10.77.0.1`. ([OPNsense Documentation][15])

Your clients should receive:

```text
IP address:  10.77.0.100–10.77.0.199
Subnet:      255.255.255.0
Gateway:     10.77.0.1
DNS:         10.77.0.1
Domain:      lab.internal
```

---

## 4. Confirm Dnsmasq actually started

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ Log
```

You should not see errors about port 67 already being occupied.

Also check the OPNsense dashboard under **Services**. Dnsmasq should show as running.

If it refuses to start, make sure neither of these is enabled:

```text
Services → Kea DHCP
Services → ISC DHCP
```

Only one DHCP server can listen on the DHCP port for the LAN interface. The OPNsense documentation specifically warns that Kea or ISC DHCP can block Dnsmasq from starting. ([OPNsense Documentation][15])

---

## 5. Create a test VM in Proxmox

Create a small Debian or Ubuntu VM, or use an existing private VM.

Its network device must be:

```text
Model: VirtIO
Bridge: vmbr2
VLAN Tag: blank
Firewall: unchecked initially
```

Do **not** attach this test VM to:

```text
vmbr0
vmbr1
```

The topology should be:

```text
Test VM
  │
  └── vmbr2
          │
          └── OPNsense LAN: 10.77.0.1
```

## For a cloud-init VM

In Proxmox:

```text
VM
→ Cloud-Init
→ IP Config
→ Edit
```

Choose:

```text
IPv4: DHCP
IPv6: DHCP or SLAAC disabled
```

Then regenerate the cloud-init image if Proxmox presents that option.

## For a normally installed Linux VM

During OS installation, choose automatic networking or DHCP.

For Ubuntu/Debian using Netplan, a simple DHCP configuration looks like:

```yaml
network:
  version: 2
  ethernets:
    ens18:
      dhcp4: true
      dhcp6: false
```

The interface is commonly `ens18`, but verify it inside the VM with:

```bash
ip -br link
```

Apply Netplan with:

```bash
sudo netplan apply
```

---

## 6. Verify that the VM received a lease

Inside the test VM, run:

```bash
ip -br addr
ip route
cat /etc/resolv.conf
```

Expected output should resemble:

```text
ens18    UP    10.77.0.100/24
```

The route should include:

```text
default via 10.77.0.1 dev ens18
```

DNS should ultimately point to:

```text
10.77.0.1
```

On systems using `systemd-resolved`, `/etc/resolv.conf` may show `127.0.0.53`. In that case, inspect the actual upstream DNS with:

```bash
resolvectl status
```

You should find:

```text
DNS Servers: 10.77.0.1
DNS Domain: lab.internal
```

---

## 7. View the lease inside OPNsense

Open:

```text
Services
→ Dnsmasq DNS & DHCP
→ Leases
```

You should see the test VM with information resembling:

```text
IP address: 10.77.0.100
MAC address: bc:24:11:...
Hostname: test-vm
Interface: LAN
```

This confirms that:

```text
VM DHCP broadcast
→ reaches vmbr2
→ reaches OPNsense LAN
→ receives a lease
```

---

## 8. Test LAN connectivity

Inside the VM:

```bash
ping -c 3 10.77.0.1
```

This must work before testing anything else.

Then test outbound IP connectivity:

```bash
ping -c 3 1.1.1.1
```

Then DNS:

```bash
getent hosts example.com
```

Then HTTPS:

```bash
curl -I https://example.com
```

Expected progression:

```text
10.77.0.1 works
    ↓
1.1.1.1 works
    ↓
example.com resolves
    ↓
HTTPS works
```

If the VM gets an address but cannot reach `1.1.1.1`, DHCP is working; the remaining problem is OPNsense outbound NAT/firewalling.

---

## Stable addresses for server VMs

For a new general-purpose VM, let DHCP assign an address automatically.

For important servers such as Dokploy or PostgreSQL, you need a stable address. With Dnsmasq, the cleanest reservation method is under:

```text
Services
→ Dnsmasq DNS & DHCP
→ Hosts
→ Add
```

You need the VM’s MAC address from:

```text
Proxmox VM
→ Hardware
→ Network Device
```

A reservation could be:

```text
Host:
dokploy

IP addresses:
10.77.0.10

Hardware addresses:
bc:24:11:xx:xx:xx

Description:
Dokploy reverse proxy
```

Click:

```text
Save
→ Apply
```

Use the Dnsmasq Hosts entry to associate the server’s MAC address with its stable IP. Keep infrastructure reservations outside the dynamic pool of `10.77.0.100–10.77.0.199`. ([OPNsense Documentation][15])

I recommend these assignments:

```text
10.77.0.10  Dokploy
10.77.0.20  PostgreSQL
10.77.0.30  Monitoring
10.77.0.31 onward  Other infrastructure
```

After adding a reservation, restart the VM’s network or reboot it. On Linux, you can also request a fresh lease:

```bash
sudo dhclient -r
sudo dhclient
```

The immediate goal is to get **one test VM on `vmbr2` showing in Dnsmasq Leases with an address between `10.77.0.100` and `10.77.0.199`**.

---

# Phase 8: Verify OPNsense’s internal firewall and outbound NAT

Navigate to:

```text
Firewall → Rules → LAN
```

You should have a rule equivalent to:

```text
Action: Pass
Interface: LAN
Protocol: IPv4 any
Source: LAN net
Destination: any
```

For the initial setup, this lets private VMs initiate outbound connections.

Navigate to:

```text
Firewall → NAT → Outbound
```

Use:

```text
Mode: Automatic outbound NAT
```

OPNsense uses source NAT to let multiple internal clients share its WAN address. In this architecture, that WAN address is `10.255.255.2`; Proxmox will then translate it again to your public address. ([OPNsense Documentation][7])

At this point OPNsense can reach Proxmox at `10.255.255.1`, but it cannot yet reach the Internet because the Proxmox host is not forwarding or masquerading traffic.

---

# Phase 9: Configure Proxmox forwarding through UFW

Because you already use UFW to restrict Proxmox management to Tailscale, keep UFW as the host-level firewall.

Its responsibility should remain small:

```text
1. Give OPNsense outbound Internet access.
2. Forward selected public ports to OPNsense.
3. Continue protecting the Proxmox host itself.
```

## Enable IPv4 forwarding

Edit:

```bash
nano /etc/ufw/sysctl.conf
```

Ensure this line exists and is uncommented:

```text
net.ipv4.ip_forward=1
```

Apply it:

```bash
sysctl --system
sysctl net.ipv4.ip_forward
```

Expected:

```text
net.ipv4.ip_forward = 1
```

## Add NAT rules

Back up the file again before editing:

```bash
cp -a /etc/ufw/before.rules \
  /etc/ufw/before.rules.before-opnsense-nat
```

Open:

```bash
nano /etc/ufw/before.rules
```

Check whether a `*nat` section already exists:

```bash
grep -n '^\*nat' /etc/ufw/before.rules
```

If there is already a NAT section, add the following rules inside that existing section before its `COMMIT`.

Otherwise, append this complete block after the existing `*filter ... COMMIT` section:

```text
# OPNsense outer NAT
*nat
:PREROUTING ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]

# Allow OPNsense WAN to share the Proxmox public IPv4
-A POSTROUTING -s 10.255.255.0/30 -o vmbr0 -j MASQUERADE

# Send public HTTP and HTTPS traffic to OPNsense
-A PREROUTING -i vmbr0 -p tcp --dport 80 \
  -j DNAT --to-destination 10.255.255.2:80

-A PREROUTING -i vmbr0 -p tcp --dport 443 \
  -j DNAT --to-destination 10.255.255.2:443

COMMIT
```

Replace `vmbr0` if `ip route get 1.1.1.1` showed a different public interface.

## Add UFW routed-traffic rules

Run:

```bash
ufw route allow \
  in on vmbr1 \
  out on vmbr0 \
  from 10.255.255.0/30 \
  comment 'OPNsense outbound Internet'

ufw route allow \
  in on vmbr0 \
  out on vmbr1 \
  to 10.255.255.2 \
  port 80 \
  proto tcp \
  comment 'Public HTTP to OPNsense'

ufw route allow \
  in on vmbr0 \
  out on vmbr1 \
  to 10.255.255.2 \
  port 443 \
  proto tcp \
  comment 'Public HTTPS to OPNsense'
```

Validate the UFW files before reloading:

```bash
iptables-restore --test < /etc/ufw/before.rules
```

If that command produces no error, reload:

```bash
ufw reload
```

Verify:

```bash
ufw status verbose
ufw status numbered
iptables -t nat -S
```

You should see rules resembling:

```text
-A POSTROUTING -s 10.255.255.0/30 -o vmbr0 -j MASQUERADE
-A PREROUTING -i vmbr0 -p tcp --dport 80 ...
-A PREROUTING -i vmbr0 -p tcp --dport 443 ...
```

UFW officially supports enabling forwarding in its sysctl file, adding masquerade and DNAT rules to `before.rules`, and using `ufw route allow` for forwarded traffic. NAT rules from `before.rules` do not appear in normal `ufw status`, which is why you verify them with `iptables -t nat -S`. ([Ubuntu Manpages][8])

---

# Phase 10: Test outbound Internet access

From the OPNsense WebGUI:

```text
Interfaces → Diagnostics → Ping
```

Test these in order:

```text
10.255.255.1
1.1.1.1
example.com
```

Interpretation:

| Result                         | Meaning                                                    |
| ------------------------------ | ---------------------------------------------------------- |
| Cannot ping `10.255.255.1`     | WAN addressing or interface assignment is wrong            |
| Can ping `.1`, not `1.1.1.1`   | Proxmox forwarding, UFW route rule, or masquerade is wrong |
| Can ping `1.1.1.1`, not domain | DNS configuration is wrong                                 |
| All three work                 | OPNsense outbound path works                               |

Now create or attach a test VM to `vmbr2`.

Inside the VM:

```bash
ip -br addr
ip route
cat /etc/resolv.conf
```

Expected route:

```text
default via 10.77.0.1
```

Then test:

```bash
ping -c 3 10.77.0.1
ping -c 3 1.1.1.1
getent hosts example.com
curl -I https://example.com
```

When these work, private VM outbound routing is complete.

---

# Phase 11: Configure inbound HTTP and HTTPS

Assume your Dokploy VM is:

```text
10.77.0.10
```

Make sure its NIC is attached only to:

```text
vmbr2
```

The Dokploy VM does not need a public interface.

## OPNsense HTTP forwarding rule

Navigate to:

```text
Firewall → NAT → Destination NAT (Port Forward)
```

Create:

```text
Interface: WAN
IP version: IPv4
Protocol: TCP
Source: any
Destination: WAN address
Destination port: HTTP / 80
Redirect target IP: 10.77.0.10
Redirect target port: 80
Filter rule association: Pass or Add associated filter rule
Description: HTTP to Dokploy
```

## OPNsense HTTPS forwarding rule

Create another:

```text
Interface: WAN
IP version: IPv4
Protocol: TCP
Source: any
Destination: WAN address
Destination port: HTTPS / 443
Redirect target IP: 10.77.0.10
Redirect target port: 443
Filter rule association: Pass or Add associated filter rule
Description: HTTPS to Dokploy
```

Apply the rules.

OPNsense’s documented destination NAT process uses WAN port forwards for this exact case: traffic to ports such as 80 and 443 is redirected to an internal web server, with an associated filter rule controlling whether the translated traffic is accepted. ([OPNsense Documentation][9])

The complete path is now:

```text
Internet client
  ↓
Public IPv4:443
  ↓ Proxmox DNAT
10.255.255.2:443
  ↓ OPNsense DNAT
10.77.0.10:443
  ↓
Dokploy / Traefik
```

---

# Phase 12: Configure public DNS

For every website served by Dokploy, create an `A` record pointing to the same public IPv4:

```text
app1.example.com → your public IPv4
app2.example.com → your public IPv4
api.example.com  → your public IPv4
```

You do not need one IP per domain.

Traefik receives all HTTP and HTTPS connections at `10.77.0.10` and selects the application based on the hostname in the request.

Conceptually:

```text
app1.example.com ─┐
app2.example.com ─┼─→ public IPv4 → Traefik → correct application
api.example.com  ─┘
```

Only one internal machine can directly receive public ports 80 and 443, which should be your reverse proxy.

---

# Phase 13: Configure internal DNS to avoid hairpin NAT

A private VM trying to open `app.example.com` will resolve it to your public IP. That creates an awkward path where traffic leaves OPNsense, reaches Proxmox’s public address, and tries to return through both NAT layers.

Avoid this with split DNS.

In OPNsense, add an Unbound or DNS host override:

```text
Host: app
Domain: example.com
IP: 10.77.0.10
```

Do the same for each hostname hosted by Dokploy:

```text
app1.example.com → 10.77.0.10
app2.example.com → 10.77.0.10
api.example.com  → 10.77.0.10
```

The result:

```text
External client:
app1.example.com → public IPv4

Private VM using OPNsense DNS:
app1.example.com → 10.77.0.10
```

This is simpler and more predictable than NAT reflection through two routers.

---

# Forwarding non-HTTP services

Suppose you intentionally want:

```text
Public TCP port 2222
        ↓
Private VM 10.77.0.30 port 22
```

You need an outer Proxmox rule and an inner OPNsense rule.

## Proxmox UFW NAT

Inside the existing `*nat` block:

```text
-A PREROUTING -i vmbr0 -p tcp --dport 2222 \
  -j DNAT --to-destination 10.255.255.2:2222
```

Then:

```bash
ufw route allow \
  in on vmbr0 \
  out on vmbr1 \
  to 10.255.255.2 \
  port 2222 \
  proto tcp \
  comment 'TCP 2222 to OPNsense'

ufw reload
```

## OPNsense port forward

```text
Interface: WAN
Protocol: TCP
Destination: WAN address
Destination port: 2222
Redirect target: 10.77.0.30
Redirect target port: 22
Filter rule association: Pass
```

The path becomes:

```text
Public-IP:2222
   ↓
OPNsense-WAN:2222
   ↓
10.77.0.30:22
```

However, for SSH administration, continue using Tailscale instead of exposing public SSH.

For raw TCP services, your options are:

1. Give every service a different public port.
2. Use an L4 TCP proxy on the Dokploy VM.
3. Obtain additional public IPs later.
4. Access the service through Tailscale rather than exposing it.

---

# How private VMs should be configured

Each private VM should normally have:

```text
Bridge: vmbr2
NIC model: VirtIO
IPv4: DHCP or a DHCP reservation
Gateway: 10.77.0.1
DNS: 10.77.0.1
No NIC attached to vmbr0
```

For manually configured static addressing:

```text
Address: 10.77.0.X/24
Gateway: 10.77.0.1
DNS: 10.77.0.1
```

Do not choose an address inside the dynamic pool unless it is reserved.

For example:

```text
Dokploy:     10.77.0.10/24
PostgreSQL:  10.77.0.20/24
Monitoring:  10.77.0.30/24
```

Publishing a Docker port inside one of these VMs does **not** automatically expose it publicly.

For example:

```yaml
ports:
  - "8080:8080"
```

means:

```text
10.77.0.25:8080 is available on the private network
```

It does not bypass OPNsense or Proxmox. You still need a reverse-proxy route or NAT forwarding rule for public access.

---

# Testing inbound connectivity

Test from a genuinely external connection, such as your phone using mobile data. Do not initially test from a private VM because split DNS or hairpin behavior may obscure the result.

On Proxmox, observe the public interface:

```bash
tcpdump -ni vmbr0 'tcp port 80 or tcp port 443'
```

Observe the OPNsense transit interface:

```bash
tcpdump -ni vmbr1 \
  'host 10.255.255.2 and (tcp port 80 or tcp port 443)'
```

On the Dokploy VM:

```bash
sudo tcpdump -ni any 'tcp port 80 or tcp port 443'
```

Also confirm that the service is listening:

```bash
sudo ss -lntp | grep -E ':(80|443)\b'
```

## Diagnosing where traffic stops

| Observation                                      | Problem area                                          |
| ------------------------------------------------ | ----------------------------------------------------- |
| Nothing arrives on `vmbr0`                       | DNS, provider firewall, wrong public IP, or client    |
| Arrives on `vmbr0`, not `vmbr1`                  | Proxmox DNAT or UFW route rule                        |
| Arrives on OPNsense WAN, not LAN                 | OPNsense NAT or WAN firewall rule                     |
| Arrives at Dokploy but no response               | Traefik, Docker, guest firewall, or listening address |
| Private VM reaches OPNsense but not Internet     | OPNsense outbound NAT or WAN gateway                  |
| OPNsense reaches `10.255.255.1` but not Internet | Proxmox masquerade, UFW, or IP forwarding             |
| IP connectivity works but DNS fails              | OPNsense DNS or DHCP DNS setting                      |

OPNsense also provides:

```text
Firewall → Log Files → Live View
Interfaces → Diagnostics → Packet Capture
Interfaces → Diagnostics → Ping
```

Use the WAN packet capture first, then LAN. That immediately shows whether OPNsense received and translated the connection.

---

# Security rules I recommend

## Keep these private

Do not publicly forward:

```text
22      Proxmox SSH
8006    Proxmox WebGUI
443     OPNsense WebGUI itself
5432    PostgreSQL
3306    MySQL
27017   MongoDB
6379    Redis
```

Your public 443 forward should go through OPNsense to Dokploy, not to the OPNsense administrative interface.

Continue using Tailscale for:

```text
Proxmox WebGUI
Proxmox SSH
OPNsense WebGUI through an SSH tunnel
Direct private-VM SSH
Database administration
```

## Use stable IPs for publicly routed servers

Do not forward traffic to an unreserved DHCP address. Give Dokploy and any explicitly routed server a static DHCP mapping.

## Use OPNsense aliases

As the rules grow, create aliases such as:

```text
WEB_PROXY       10.77.0.10
DATABASES       10.77.0.20, 10.77.0.21
PRIVATE_NETS    10.77.0.0/24
WEB_PORTS       80, 443
```

Aliases let you refer to named groups of hosts, networks, and ports instead of repeating raw addresses throughout the firewall configuration. ([OPNsense Documentation][10])

## Do not add IDS/IPS immediately

First establish:

```text
Routing
DHCP
DNS
Outbound NAT
Inbound port forwarding
Backups
```

Add intrusion detection, traffic shaping, VLAN segmentation, and more restrictive east-west filtering afterward. Otherwise, troubleshooting becomes unnecessarily difficult.

---

# Backups

Back up three separate layers.

## Proxmox host configuration

```bash
cp -a /etc/network/interfaces /root/interfaces-working
cp -a /etc/ufw/before.rules /root/ufw-before-working.rules
cp -a /etc/ufw/sysctl.conf /root/ufw-sysctl-working.conf
ufw status numbered > /root/ufw-working.txt
```

## OPNsense configuration

Use:

```text
System → Configuration → Backups
```

Download the configuration XML after every meaningful networking change.

## OPNsense VM

Create a Proxmox backup after:

1. Installation.
2. WAN and LAN configuration.
3. DHCP and outbound routing.
4. Working public port forwarding.

A firewall configuration backup is more useful than relying only on a VM snapshot because it can be restored onto a fresh OPNsense installation.

---

# Rollback procedure

If reloading UFW breaks forwarding but Proxmox remains reachable:

```bash
cp -a /etc/ufw/before.rules.pre-opnsense \
  /etc/ufw/before.rules
```

List UFW rules:

```bash
ufw status numbered
```

Delete the three OPNsense route rules by number, starting from the highest number:

```bash
ufw delete <rule-number>
```

Then:

```bash
ufw reload
```

If the private network configuration causes trouble, restore:

```bash
cp -a /etc/network/interfaces.pre-opnsense \
  /etc/network/interfaces
```

Do not restart networking blindly while connected only through the public interface. Use the OVH rescue system if the host itself becomes unreachable.

The benefit of the recommended architecture is that an OPNsense failure should affect only private-VM routing. The Proxmox host retains its public IPv4 and Tailscale management path.

---

# What a future cleaner design would look like

If you later obtain an **Additional IPv4**, you can give that address to OPNsense WAN using the OVH virtual MAC mechanism:

```text
Primary public IPv4
    → Proxmox management

Additional public IPv4
    → OPNsense WAN through vmbr0
```

That removes the outer Proxmox NAT:

```text
Internet → OPNsense → private VMs
```

Until then, the transit-network design is the safest compromise:

```text
Proxmox keeps the only public IP
OPNsense controls the private networks
UFW performs only the unavoidable outer NAT
Dokploy receives public web traffic
Tailscale handles administration
```

## Final target checklist

You are finished when all of these are true:

```text
[ ] Proxmox remains reachable over Tailscale
[ ] vmbr1 is 10.255.255.1/30
[ ] vmbr2 is 10.77.0.2/24
[ ] OPNsense WAN is 10.255.255.2/30
[ ] OPNsense WAN gateway is 10.255.255.1
[ ] OPNsense LAN is 10.77.0.1/24
[ ] DHCP gives VMs 10.77.0.100–199
[ ] A private VM can reach 1.1.1.1
[ ] A private VM can resolve DNS
[ ] Public TCP 80 and 443 reach OPNsense
[ ] OPNsense forwards 80 and 443 to 10.77.0.10
[ ] Dokploy/Traefik receives the request
[ ] Proxmox 22 and 8006 remain unavailable publicly
[ ] OPNsense WebGUI remains unavailable publicly
[ ] OPNsense configuration XML has been backed up
```

[1]: https://pve.proxmox.com/pve-docs/pve-admin-guide.html?utm_source=chatgpt.com "Proxmox VE Administration Guide"
[2]: https://docs.opnsense.org/manual/virtuals.html "Virtual & Cloud-Based Installation — OPNsense  documentation"
[3]: https://docs.opnsense.org/manual/install.html "Initial Installation & Configuration — OPNsense  documentation"
[4]: https://docs.opnsense.org/manual/how-tos/ipsec-s2s.html?utm_source=chatgpt.com "IPsec - Site to Site tunnel"
[5]: https://docs.opnsense.org/manual/updates.html?utm_source=chatgpt.com "Updates — OPNsense documentation"
[6]: https://docs.opnsense.org/manual/kea.html?utm_source=chatgpt.com "KEA DHCP"
[7]: https://docs.opnsense.org/manual/nat.html?utm_source=chatgpt.com "Firewall Network Address Translation"
[8]: https://manpages.ubuntu.com/manpages/focal/man8/ufw-framework.8.html?utm_source=chatgpt.com "using the ufw framework"
[9]: https://docs.opnsense.org/manual/nat.html "Network Address Translation — OPNsense  documentation"
[10]: https://docs.opnsense.org/manual/aliases.html?utm_source=chatgpt.com "Aliases"
[11]: https://pve.proxmox.com/pve-docs/qm.conf.5.html?utm_source=chatgpt.com "qm.conf(5)"
[12]: https://docs.opnsense.org/manual/gateways.html?utm_source=chatgpt.com "Gateways"
[13]: https://docs.opnsense.org/manual/dhcp.html "DHCP — OPNsense  documentation"
[14]: https://docs.opnsense.org/manual/unbound.html "Unbound DNS — OPNsense  documentation"
[15]: https://docs.opnsense.org/manual/dnsmasq.html "Dnsmasq DNS & DHCP — OPNsense  documentation"


