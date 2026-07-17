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
ip -br addr show vmbr0 vmbr1 vmbr2
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

### Network device 0

```text
Bridge: vmbr1
Model: VirtIO
Purpose: WAN
```

### Network device 1

```text
Bridge: vmbr2
Model: VirtIO
Purpose: LAN
```

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

1. Shut down or reboot OPNsense.
2. Remove or detach the ISO.
3. Boot from the virtual disk.

---

# Phase 4: Assign the interfaces

At the OPNsense console, assign:

```text
WAN: vtnet0
LAN: vtnet1
```

Verify the MAC addresses against those shown in Proxmox.

Do not configure VLANs yet.

Use console option:

```text
2) Set interface(s) IP address
```

Configure the LAN first:

```text
Interface: LAN
IPv4 address: 10.77.0.1
Subnet bits: 24
Upstream gateway: none
IPv6: none
Enable DHCP now: no
Revert WebGUI to HTTP: no
```

You will configure DHCP through the WebGUI later.

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

Set:

```text
Enable interface: Yes
Description: WAN
IPv4 Configuration Type: Static IPv4
IPv6 Configuration Type: None

IPv4 address: 10.255.255.2
Prefix: 30
Gateway: 10.255.255.1
```

When creating the gateway, mark it as an upstream gateway.

Because this WAN uses an RFC1918 address rather than a public address:

```text
Block private networks: unchecked
Block bogon networks: unchecked
```

OPNsense specifically documents that the private-network block must be disabled when its WAN uses a private address. ([OPNsense Documentation][4])

Initially, disable gateway monitoring or leave its monitor address blank. After outbound connectivity works, you can set the monitor address to something such as `1.1.1.1`.

## LAN configuration

Navigate to:

```text
Interfaces → LAN
```

Confirm:

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

For a small private network, use the DHCP service provided by your OPNsense installation—typically Dnsmasq or Kea. Do not enable two DHCP servers on the same interface.

Configure:

```text
Interface: LAN
Subnet: 10.77.0.0/24
Pool: 10.77.0.100 - 10.77.0.199
Router/Gateway: 10.77.0.1
DNS server: 10.77.0.1
Domain: lab.internal
```

Avoid using `.local`, because it is commonly used by multicast DNS.

OPNsense currently documents Kea and Dnsmasq as supported DHCP options; ISC DHCP is end-of-life. Kea is primarily positioned for larger or high-availability deployments, so a small environment does not require its more complex HA features. ([OPNsense Documentation][6])

## Reserve stable addresses for servers

Use static DHCP mappings based on the VM NIC’s MAC address:

```text
Dokploy:       10.77.0.10
Database:      10.77.0.20
Monitoring:    10.77.0.30
Other servers: 10.77.0.31 onward
```

Keep the DHCP pool beginning at `.100`, leaving `.2–.99` available for infrastructure.

For a new cloud-init VM in Proxmox:

```text
Network bridge: vmbr2
Model: VirtIO
IPv4 configuration: DHCP
IPv6 configuration: disabled
```

That VM will automatically receive:

```text
Address: 10.77.0.100–199
Gateway: 10.77.0.1
DNS: 10.77.0.1
```

This is the “automatic discovery” portion: OPNsense automatically leases an address and becomes the VM’s gateway. It does **not** automatically expose the VM to the Internet, which is intentional.

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


