---
date: 2026-07-19
type: howto
tags: [opnsense, hardening, network-segmentation, firewall, infrastructure]
related:
  - memory/docs/library/infrastructure/proxmox-opnsense-network-design.md
  - memory/docs/library/infrastructure/revised-proxmox-opnsense-network-design.md
---

Below is the safest implementation for your current layout:

```text
Proxmox vmbr2:  10.77.0.2
OPNsense LAN:   10.77.0.1
Dokploy:        10.77.0.10
Management:     PC → Tailscale → Proxmox → SSH tunnel → OPNsense
```

## Before making changes

Open the OPNsense VM console in Proxmox:

```text
Proxmox
→ OPNsense VM
→ Console
```

Keep that tab open throughout the process.

From your computer, start your existing management tunnel:

```powershell
ssh -N -L 8443:10.77.0.1:443 morfuse@px
```

Then access:

```text
https://localhost:8443
```

Your OPNsense GUI remains on port `443`. Port `8443` exists only on your computer as the entrance to the SSH tunnel.

---

# 6. Make a backup first

We are doing this before items 1–5 because some of those changes can lock you out.

Navigate to:

```text
System
→ Configuration
→ Backups
```

Under **Download**, configure:

```text
Encrypt this configuration file: Enabled
Password: A strong password from your password manager
Save RRD data: Disabled
```

Download the configuration and name it something recognizable:

```text
opnsense-before-hardening-2026-07-19.xml
```

OPNsense configuration exports can be downloaded and password-protected from this screen. ([OPNsense Documentation][1])

Also create a temporary Proxmox snapshot:

```text
Proxmox
→ OPNsense VM
→ Snapshots
→ Take Snapshot
```

Name it:

```text
before-opnsense-hardening
```

Do not leave VM snapshots forever, but they are useful while making these changes.

If you completely lose access, the OPNsense console has:

```text
13) Restore a configuration
```

which can restore one of OPNsense’s locally retained configurations. ([OPNsense Documentation][2])

---

# 1. Ensure the GUI and SSH are not exposed on WAN

## 1A. Bind the GUI to LAN only

Navigate to:

```text
System
→ Settings
→ Administration
```

Under **Web GUI**, use:

```text
Protocol: HTTPS
TCP port: 443
Listen interfaces: LAN
HTTP Redirect: Disabled
Session timeout: 15 or 30 minutes
```

Do not select WAN.

Because your LAN address `10.77.0.1` is static, binding the GUI to LAN is appropriate. OPNsense warns that manually selecting listen interfaces can cause lockouts, which is why your Proxmox console must remain open. ([OPNsense Documentation][3])

Click:

```text
Save
→ Apply
```

Your current tunnel should continue working:

```text
localhost:8443 → Proxmox → 10.77.0.1:443
```

## 1B. Review WAN port forwards

Navigate to:

```text
Firewall
→ NAT
→ Destination NAT (Port Forward)
```

For your current Dokploy server, the public application rules should resemble:

### HTTP

```text
Interface: WAN
Protocol: TCP
Source: any
Destination: WAN address
Destination port: 80
Redirect target IP: 10.77.0.10
Redirect target port: 80
Description: Forward HTTP to Dokploy
```

### HTTPS

```text
Interface: WAN
Protocol: TCP
Source: any
Destination: WAN address
Destination port: 443
Redirect target IP: 10.77.0.10
Redirect target port: 443
Description: Forward HTTPS to Dokploy
```

Port forwarding should target Dokploy, not `This Firewall`. OPNsense describes the redirect target as the internal server receiving the forwarded traffic. ([OPNsense Documentation][4])

You should not have public port forwards for:

```text
22
8443
8006
OPNsense GUI
OPNsense SSH
```

## 1C. Review WAN firewall rules

Navigate to either:

```text
Firewall
→ Rules
→ WAN
```

or, in the newer interface:

```text
Firewall
→ Rules [new]
```

Filter by:

```text
Interface: WAN
```

Look for rules permitting traffic to:

```text
Destination: This Firewall
Ports: 22, 443 or 8443
```

Disable or delete those rules unless they are explicitly required for something else.

You do not need a separate block rule on WAN. OPNsense already applies default-deny behavior when no pass rule matches. Rules are processed by priority and sequence, with normal quick rules using first-match behavior. ([OPNsense Documentation][5])

## 1D. Test from outside

Do this from another Internet connection, such as mobile data—not from the private network.

In PowerShell:

```powershell
Test-NetConnection YOUR_PUBLIC_IP -Port 22
Test-NetConnection YOUR_PUBLIC_IP -Port 8443
```

Both should show:

```text
TcpTestSucceeded : False
```

These will probably show `True`, because they intentionally lead to Dokploy:

```powershell
Test-NetConnection YOUR_PUBLIC_IP -Port 80
Test-NetConnection YOUR_PUBLIC_IP -Port 443
```

Opening your public HTTPS address must show Dokploy, Traefik, or an application—not the OPNsense login page.

---

# 2. Create a named administrator with TOTP

Do not enable TOTP globally until you have tested it.

## 2A. Create the TOTP authentication server

Navigate to:

```text
System
→ Access
→ Servers
→ Add
```

Configure:

```text
Descriptive name: Local-TOTP
Type: Local + Timebased One Time Password
Token length: 6
Time window: Leave blank
Grace period: Leave blank
Reverse token order: Disabled
```

Save it.

These are the documented standard settings for a six-digit authenticator application. ([OPNsense Documentation][6])

## 2B. Create your named administrator

Navigate to:

```text
System
→ Access
→ Users
→ Add
```

Configure:

```text
Username: morfuse-admin
Password: A unique random password
Full name: Mark OPNsense Administrator
Group membership: admins
Login shell: /sbin/nologin
OTP seed: Generate new 160-bit secret
```

The important settings are:

```text
Group membership: admins
Login shell: /sbin/nologin
```

The `admins` membership gives the account administrative permissions. The no-login shell prevents the account from becoming an SSH or console shell account. OPNsense supports group-based privileges, OTP seeds, login shells and authorized SSH keys through its local user manager. ([OPNsense Documentation][7])

Save the user.

Edit `morfuse-admin` again. A QR code should now appear.

Scan it using your authenticator application. Save the seed or QR code securely because possession of that seed allows generation of valid tokens. ([OPNsense Documentation][6])

## 2C. Test TOTP

Navigate to:

```text
System
→ Access
→ Tester
```

Enter:

```text
Authentication server: Local-TOTP
Username: morfuse-admin
Password: SIX_DIGIT_TOKEN followed immediately by YOUR_PASSWORD
```

Example:

```text
123456MyVeryLongPassword
```

There is no space or colon between them.

The default OPNsense TOTP order is:

```text
token + password
```

OPNsense provides the authentication tester specifically so this can be verified before changing the WebGUI authentication server. ([OPNsense Documentation][6])

You must receive:

```text
Authentication successful
```

## 2D. Enable TOTP for the WebGUI

Keep your current browser session open.

Navigate to:

```text
System
→ Settings
→ Administration
→ Authentication
```

Change:

```text
Server: Local-TOTP
```

Save and apply.

Open an incognito/private browser window and go through the tunnel again:

```text
https://localhost:8443
```

Log in with:

```text
Username: morfuse-admin
Password: SIX_DIGIT_TOKEN + PASSWORD
```

Do not close your original browser session until the incognito login succeeds.

The selected authentication server controls WebGUI authentication. ([OPNsense Documentation][7])

---

# 3. Disable OPNsense SSH

Your SSH tunnel terminates on the **Proxmox host**, not OPNsense. Therefore, disabling SSH on OPNsense will not break your current management tunnel.

Navigate to:

```text
System
→ Settings
→ Administration
→ Secure Shell
```

Configure:

```text
Secure Shell Server: Disabled
Permit Root Login: Disabled
Permit Password Login: Disabled
```

Save and apply.

That is the recommended configuration for you because you already have:

```text
Tailscale access to Proxmox
Proxmox VM console access
SSH tunnel through Proxmox
```

If you later enable OPNsense SSH, use:

```text
Secure Shell Server: Enabled
Permit Root Login: Disabled
Permit Password Login: Disabled
Listen Interfaces: LAN
```

and add an authorized public key to a named user. OPNsense explicitly discourages root SSH login and supports key-only authentication and interface-specific listening. ([OPNsense Documentation][3])

---

# 4. Restrict GUI access to Proxmox only

Your SSH tunnel causes Proxmox to make the connection to OPNsense. OPNsense therefore sees the management connection coming from:

```text
10.77.0.2
```

That is the Proxmox address on `vmbr2`.

## 4A. Create an administrator alias

Navigate to:

```text
Firewall
→ Aliases
→ Add
```

Configure:

```text
Enabled: Yes
Name: OPNSENSE_ADMINS
Type: Host(s)
Content: 10.77.0.2
Description: Proxmox management tunnel source
```

Save and apply.

Aliases can be used as reusable source or destination lists in firewall rules. ([OPNsense Documentation][8])

## 4B. Add the allow rule

Navigate to:

```text
Firewall
→ Rules
→ LAN
```

Or use:

```text
Firewall
→ Rules [new]
```

Create this rule:

```text
Action: Pass
Quick: Enabled
Interface: LAN
Direction: In
TCP/IP Version: IPv4
Protocol: TCP

Source: OPNSENSE_ADMINS
Source port: any

Destination: This Firewall
Destination port: HTTPS / 443

Log: Enabled temporarily
Description: Allow OPNsense GUI from Proxmox tunnel
```

Save and apply.

## 4C. Add a block rule immediately below it

Create another rule:

```text
Action: Block
Quick: Enabled
Interface: LAN
Direction: In
TCP/IP Version: IPv4
Protocol: TCP

Source: LAN net
Source port: any

Destination: This Firewall
Destination port: HTTPS / 443

Log: Enabled
Description: Block OPNsense GUI from other private VMs
```

Your LAN rule order should look like:

```text
1. PASS  OPNSENSE_ADMINS → This Firewall port 443
2. BLOCK LAN net         → This Firewall port 443
3. Existing broader LAN rules
```

The block rule is essential. Merely adding the first allow rule is insufficient if a later or existing broad LAN rule permits `LAN net → any`. With quick rules, the first matching rule wins. ([OPNsense Documentation][5])

Do not block all traffic to `This Firewall`, because your VMs may use OPNsense for DNS, DHCP, NTP or gateway services. Block only the management port.

---

# 5. Disable the automatic anti-lockout rule

Before doing this, confirm all of the following:

```text
The Proxmox OPNsense console is open.
The SSH tunnel is running.
The OPNSENSE_ADMINS alias contains 10.77.0.2.
The allow rule is above the block rule.
Your TOTP administrator login works.
Your original browser session is still open.
```

Navigate to:

```text
Firewall
→ Settings
→ Advanced
```

Find:

```text
Disable anti-lockout
```

Check the box.

Then:

```text
Save
→ Apply
```

The confusing wording means:

```text
Unchecked:
OPNsense automatically allows GUI/SSH from LAN.

Checked:
Only your own firewall rules determine GUI/SSH access.
```

OPNsense warns that checking this without a valid replacement rule can lock you out. ([OPNsense Documentation][9])

## Test the allowed path

Close the incognito window, reopen it and visit:

```text
https://localhost:8443
```

Log in using:

```text
morfuse-admin
TOKEN + PASSWORD
```

It should succeed.

## Test from Dokploy

SSH into Dokploy and run:

```bash
curl -kI --connect-timeout 5 https://10.77.0.1
```

It should time out or fail to connect.

That confirms Dokploy cannot reach your firewall administration page.

If you lose access, use:

```text
Proxmox
→ OPNsense VM
→ Console
→ 13) Restore a configuration
```

and select the configuration from immediately before the anti-lockout change.

---

# 6. Final backup and update routine

Now export another encrypted configuration:

```text
System
→ Configuration
→ Backups
```

Name it:

```text
opnsense-hardened-2026-07-19.xml
```

Keep both:

```text
opnsense-before-hardening-2026-07-19.xml
opnsense-hardened-2026-07-19.xml
```

## Check updates

Navigate to:

```text
System
→ Firmware
→ Status
```

or:

```text
System
→ Firmware
→ Updates
```

Perform:

```text
Check for updates
Run an Audit
```

The security audit checks installed package versions against a database of known vulnerabilities. ([OPNsense Documentation][10])

For updates:

1. Export the configuration.
2. Keep the Proxmox console available.
3. Read the changelog.
4. Install the update.
5. Reboot if requested.
6. Verify Internet routing, Dokploy and the management tunnel.
7. Remove the temporary Proxmox snapshot after everything is stable.

---

# 7. Segment Dokploy and database VMs

This is the larger architectural improvement. Do not perform it during the same session as the management-rule changes unless you are comfortable troubleshooting VM networking.

Your current network is:

```text
vmbr2 / 10.77.0.0/24

Proxmox: 10.77.0.2
OPNsense: 10.77.0.1
Dokploy:  10.77.0.10
Other VMs
```

Because these machines share the same virtual bridge and subnet, traffic between them does not need to pass through OPNsense.

Use separate Proxmox bridges:

```text
vmbr2 — Management — 10.77.0.0/24
vmbr3 — DMZ        — 10.77.20.0/24
vmbr4 — Databases  — 10.77.30.0/24
```

Proposed addresses:

```text
OPNsense Management: 10.77.0.1
Proxmox Management:  10.77.0.2

OPNsense DMZ:        10.77.20.1
Dokploy:             10.77.20.10

OPNsense Database:   10.77.30.1
Database VM:         10.77.30.20
```

## 7A. Create the Proxmox bridges

Navigate to:

```text
Proxmox
→ Node px
→ System
→ Network
→ Create
→ Linux Bridge
```

Create `vmbr3`:

```text
Name: vmbr3
IPv4/CIDR: Blank
Gateway: Blank
Bridge ports: Blank
Autostart: Enabled
Comment: OPNsense DMZ network
```

Create `vmbr4`:

```text
Name: vmbr4
IPv4/CIDR: Blank
Gateway: Blank
Bridge ports: Blank
Autostart: Enabled
Comment: OPNsense database network
```

Click:

```text
Apply Configuration
```

Do not modify:

```text
vmbr0
vmbr2
```

during this step.

## 7B. Add interfaces to OPNsense

Shut down the OPNsense VM during a maintenance window.

Navigate to:

```text
OPNsense VM
→ Hardware
→ Add
→ Network Device
```

Add:

```text
Model: VirtIO
Bridge: vmbr3
```

Add another:

```text
Model: VirtIO
Bridge: vmbr4
```

Start OPNsense.

## 7C. Assign the new OPNsense interfaces

Navigate to:

```text
Interfaces
→ Assignments
```

Add the interface connected to `vmbr3`, likely `vtnet2`.

Name it:

```text
DMZ
```

Add the interface connected to `vmbr4`, likely `vtnet3`.

Name it:

```text
DATABASE
```

Open the DMZ interface:

```text
Enable interface: Enabled
IPv4 Configuration Type: Static IPv4
IPv4 address: 10.77.20.1
Prefix: 24
Block private networks: Disabled
Block bogon networks: Disabled
```

Open the DATABASE interface:

```text
Enable interface: Enabled
IPv4 Configuration Type: Static IPv4
IPv4 address: 10.77.30.1
Prefix: 24
Block private networks: Disabled
Block bogon networks: Disabled
```

Save and apply each interface.

Separate interfaces and networks are the basis for applying different security policies to different zones. OPNsense supports assigning additional interfaces and VLAN-backed or separate network segments for this purpose. ([OPNsense Documentation][11])

## 7D. Move Dokploy to the DMZ

Stop the Dokploy VM.

Navigate to:

```text
Dokploy VM
→ Hardware
→ Network Device
→ Edit
```

Change:

```text
Bridge: vmbr2
```

to:

```text
Bridge: vmbr3
```

Under Cloud-Init, change:

```text
IPv4/CIDR: 10.77.20.10/24
Gateway: 10.77.20.1
```

Regenerate the cloud-init image, then start Dokploy.

Its new address will be:

```text
10.77.20.10
```

Update the OPNsense port forwards:

```text
Firewall
→ NAT
→ Destination NAT
```

Change both HTTP and HTTPS redirect targets from:

```text
10.77.0.10
```

to:

```text
10.77.20.10
```

## 7E. Move a separate database VM

For a separate database VM:

```text
Bridge: vmbr4
IPv4/CIDR: 10.77.30.20/24
Gateway: 10.77.30.1
```

Your Docker databases that run inside Dokploy itself remain on the Dokploy VM. This database network applies when you provision a separate PostgreSQL, MongoDB or other database VM.

## 7F. Create aliases

Create:

```text
DOKPLOY_HOST
Type: Host
Content: 10.77.20.10
```

Create:

```text
DATABASE_HOSTS
Type: Host
Content: 10.77.30.20
```

Create:

```text
DATABASE_PORTS
Type: Port(s)
Content:
5432
27017
```

Only include ports for databases that genuinely exist.

## 7G. Add DMZ firewall rules

Under:

```text
Firewall
→ Rules
→ DMZ
```

Add these in order.

### Allow DNS to OPNsense

```text
Action: Pass
Protocol: TCP/UDP
Source: DMZ net
Destination: This Firewall
Destination port: 53
Description: Allow DMZ DNS
```

### Allow NTP to OPNsense

```text
Action: Pass
Protocol: UDP
Source: DMZ net
Destination: This Firewall
Destination port: 123
Description: Allow DMZ NTP
```

### Allow Dokploy to databases

```text
Action: Pass
Protocol: TCP
Source: DOKPLOY_HOST
Destination: DATABASE_HOSTS
Destination port: DATABASE_PORTS
Description: Allow Dokploy to required databases
```

### Allow web access for updates

```text
Action: Pass
Protocol: TCP
Source: DMZ net
Destination: any
Destination ports: 80 and 443
Description: Allow DMZ web access
```

Leave everything else blocked by default.

## 7H. Add database firewall rules

Under:

```text
Firewall
→ Rules
→ DATABASE
```

Add only what database servers need, such as:

```text
DATABASE net → This Firewall TCP/UDP 53
DATABASE net → This Firewall UDP 123
DATABASE net → Internet TCP 80/443
```

Do not add:

```text
DATABASE net → LAN net any
DATABASE net → DMZ net any
```

When Dokploy initiates an allowed database connection, return traffic is automatically permitted by the firewall’s state tracking.

## Final expected result

```text
Internet
   │
   ▼
OPNsense WAN
   │
   ├── TCP 80/443 ──► Dokploy 10.77.20.10
   │
   ├── Dokploy ─────► DB 10.77.30.20 on approved ports only
   │
   └── Management GUI accessible only through:
       Tailscale → Proxmox 10.77.0.2 → OPNsense 10.77.0.1
```

Your immediate hardening work is **steps 1–6**. Step 7 is a separate network migration and should be performed after the hardened management path has been tested and backed up.

[1]: https://docs.opnsense.org/manual/backups.html?utm_source=chatgpt.com "Configuration"
[2]: https://docs.opnsense.org/manual/install.html?utm_source=chatgpt.com "Initial Installation & Configuration"
[3]: https://docs.opnsense.org/manual/settingsmenu.html "Settings — OPNsense  documentation"
[4]: https://docs.opnsense.org/manual/nat.html "Network Address Translation — OPNsense  documentation"
[5]: https://docs.opnsense.org/manual/firewall.html "Rules — OPNsense  documentation"
[6]: https://docs.opnsense.org/manual/how-tos/two_factor.html "Configure 2FA TOTP & Google Authenticator — OPNsense  documentation"
[7]: https://docs.opnsense.org/manual/users.html "Access / User Management — OPNsense  documentation"
[8]: https://docs.opnsense.org/manual/aliases.html "Aliases — OPNsense  documentation"
[9]: https://docs.opnsense.org/manual/firewall_settings.html "(Advanced) Settings — OPNsense  documentation"
[10]: https://docs.opnsense.org/manual/firmware.html?utm_source=chatgpt.com "Firmware — OPNsense documentation"
[11]: https://docs.opnsense.org/manual/how-tos/vlan_and_lagg.html?utm_source=chatgpt.com "VLAN and LAGG Setup"
