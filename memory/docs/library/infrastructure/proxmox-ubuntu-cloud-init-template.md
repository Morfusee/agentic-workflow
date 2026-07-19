---
date: 2026-07-17
type: howto
tags: [proxmox, ubuntu, cloud-init, vm-template, infrastructure]
related:
  - memory/docs/library/infrastructure/proxmox-opnsense-network-design.md
  - memory/docs/library/infrastructure/server-provisioning.md
---

You can do **nearly everything through the Proxmox web interface**. The only exception is importing the initial Ubuntu cloud-image disk: Proxmox still lists direct disk-image import as unavailable in the GUI, so you paste one command into **Node → Shell**, which is itself inside the web interface. After that, creating new VMs is entirely point-and-click. ([Proxmox VE][1])

# Part 1: Create the Ubuntu template once

## 1. Create an empty VM

In Proxmox:

1. Select your node, probably **`px`**.
2. Click **Create VM**.

Use these settings:

### General

```text
VM ID: 9000
Name: ubuntu-2404-template
Start at boot: No
```

### OS

Choose:

```text
Do not use any media
Guest OS Type: Linux
Version: 6.x - 2.6 Kernel
```

### System

```text
Machine: Default
BIOS: SeaBIOS
SCSI Controller: VirtIO SCSI single
QEMU Guest Agent: Leave unchecked for now
```

### Disks

The wizard may force you to create a disk.

Create the smallest temporary disk it permits:

```text
Bus/Device: SCSI
Storage: local-lvm
Disk size: 4 GiB
```

We will delete this disk shortly.

### CPU

```text
Type: host
Sockets: 1
Cores: 2
```

### Memory

```text
Memory: 2048 MiB
Ballooning: optional
```

### Network

Connect it to the bridge attached to the **LAN side of OPNsense**:

```text
Bridge: vmbr1
Model: VirtIO
```

Do **not** select the public OPNsense WAN bridge.

Click **Finish**, but do not start the VM.

---

## 2. Delete the temporary disk

Open:

```text
9000 (ubuntu-2404-template)
→ Hardware
```

Select the temporary hard disk:

1. Click **Detach**.
2. It will become **Unused Disk 0**.
3. Select **Unused Disk 0**.
4. Click **Remove**.
5. Confirm permanent removal.

You can also remove the empty CD/DVD drive:

```text
Hardware
→ CD/DVD Drive
→ Remove
```

---

## 3. Download and import Ubuntu

Canonical publishes a ready-to-boot Ubuntu 24.04 LTS cloud image suitable for this setup. ([Ubuntu Cloud Images][2])

In the left sidebar:

```text
px
→ Shell
```

Paste:

```bash
cd /root

wget -O ubuntu-24.04-cloudimg-amd64.img \
  https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
```

Import it into VM `9000`:

```bash
qm disk import \
  9000 \
  /root/ubuntu-24.04-cloudimg-amd64.img \
  local-lvm
```

You should see a successful import message.

Return to:

```text
9000
→ Hardware
```

Refresh the page if necessary. You should now see something like:

```text
Unused Disk 0
```

---

## 4. Attach the imported Ubuntu disk

Select **Unused Disk 0**, then click **Edit** or double-click it.

Configure:

```text
Bus/Device: SCSI 0
Discard: Enabled
SSD emulation: Enabled
IO thread: Enabled, if available
```

Click **Add**.

Your Ubuntu disk should now appear as:

```text
Hard Disk (scsi0)
```

---

## 5. Increase the disk size

The downloaded cloud image has a relatively small base disk.

Go to:

```text
Hardware
→ Hard Disk (scsi0)
→ Disk Action
→ Resize
```

The resize field asks for the amount to **add**, not the desired final size.

For example:

```text
Size Increment: 28 GiB
```

This should give you approximately a 30–32 GB disk, depending on the original image size.

Ubuntu cloud-init will expand the filesystem when the cloned VM boots.

---

## 6. Add the cloud-init drive

Go to:

```text
Hardware
→ Add
→ CloudInit Drive
```

Use:

```text
Storage: local-lvm
Bus/Device: IDE 2
```

Click **Add**.

You should now see:

```text
CloudInit Drive (ide2)
```

Proxmox supports using this cloud-init drive to provide instance-specific configuration such as usernames, SSH keys, networking, and DNS to cloned VMs. ([Proxmox VE][3])

---

## 7. Set the boot order

Open:

```text
9000
→ Options
→ Boot Order
→ Edit
```

Enable `scsi0` and move it to the top:

```text
1. scsi0
2. ide2
3. net0
```

You can disable the other boot devices if you prefer. The important part is that `scsi0` is first.

---

## 8. Configure cloud-init defaults

Open the new:

```text
9000
→ Cloud-Init
```

Configure the user:

```text
User: morfuse
Password: Leave empty
```

Using only an SSH key is safer than enabling a reusable password.

### Add your SSH key

On your Windows computer, run PowerShell:

```powershell
Get-Content $HOME\.ssh\id_ed25519.pub
```

Copy the entire output. It should start with:

```text
ssh-ed25519
```

In Proxmox:

```text
Cloud-Init
→ SSH public key
→ Edit
```

Paste the key.

### Configure networking

For automatic addressing from OPNsense:

```text
IP Config (net0)
IPv4: DHCP
IPv6: None
```

This is the easiest initial setup.

Each clone gets a new virtual MAC address, and OPNsense will assign it an available private IP.

For DNS, either leave the default or use your OPNsense LAN address. For example, assuming OPNsense LAN is `10.10.10.1`:

```text
DNS server: 10.10.10.1
```

After making the changes, click:

```text
Regenerate Image
```

---

## 9. Optional serial console

This can make troubleshooting cloud images easier.

Go to:

```text
Hardware
→ Add
→ Serial Port
```

Use:

```text
Socket
```

Then edit the display:

```text
Hardware
→ Display
→ Edit
→ Serial terminal 0
```

This is optional. The VM should still function without it.

---

## 10. Convert the VM to a template

**Do not start VM 9000.**

Right-click:

```text
ubuntu-2404-template
```

Select:

```text
Convert to template
```

Confirm the conversion.

You now have your reusable Ubuntu equivalent of an AMI:

```text
Template 9000: ubuntu-2404-template
```

Proxmox templates are designed to be cloned into new independent or linked VMs. ([Proxmox VE][4])

# Part 2: Provision a new VM through the GUI

Once the template exists, this is the process you repeat.

## 1. Clone the template

Right-click:

```text
ubuntu-2404-template
→ Clone
```

For a test VM:

```text
Target node: px
VM ID: 101
Name: test-vm-01
Mode: Full Clone
Target storage: local-lvm
```

Click **Clone**.

Use **Full Clone** for permanent servers. It produces an independent VM that no longer depends on the template.

Linked clones are faster and initially use less space, but remain dependent on the template.

---

## 2. Configure CPU and memory

Select the new VM:

```text
101 (test-vm-01)
```

Change the CPU:

```text
Hardware
→ Processors
→ Edit
```

For example:

```text
Sockets: 1
Cores: 2
Type: host
```

Change memory:

```text
Hardware
→ Memory
→ Edit
```

For example:

```text
Memory: 4096 MiB
```

---

## 3. Check its network

Open:

```text
Hardware
→ Network Device
```

Confirm:

```text
Bridge: vmbr1
Model: VirtIO
```

This places the VM behind OPNsense on your private LAN.

---

## 4. Configure cloud-init for the clone

Open:

```text
101
→ Cloud-Init
```

The clone inherits:

```text
User: morfuse
SSH public key: Your key
IPv4: DHCP
```

You usually do not need to change anything for a temporary VM.

Click:

```text
Regenerate Image
```

before the VM’s first boot.

For a server that needs a fixed address, edit **IP Config**. Assuming your private network is `10.10.10.0/24` and OPNsense is `10.10.10.1`:

```text
IPv4: Static
IPv4/CIDR: 10.10.10.20/24
Gateway: 10.10.10.1
```

Make sure the address is outside your OPNsense DHCP pool or reserved in OPNsense.

---

## 5. Start the VM

Click:

```text
Start
```

Ubuntu should:

1. Boot from the cloned cloud image.
2. Set its hostname from the Proxmox VM name.
3. Create the `morfuse` user.
4. Install your SSH public key.
5. Request an address from OPNsense.
6. Expand the filesystem.

You do not need to run an Ubuntu installer.

---

## 6. Find the VM’s IP address

Because the QEMU guest agent may not yet be installed, Proxmox might not immediately show the IP.

Check OPNsense:

```text
Services
→ Dnsmasq DNS & DHCP
→ Leases
```

The exact menu depends on which DHCP service you enabled.

You should find a lease for:

```text
test-vm-01
```

Then connect:

```bash
ssh morfuse@10.10.10.x
```

# Your normal provisioning workflow

After the template is ready, every new VM becomes:

```text
Right-click template
→ Clone
→ Enter VM name
→ Full Clone
→ Adjust CPU and RAM
→ Check Cloud-Init
→ Regenerate Image
→ Start
```

For DHCP-based VMs, this should require only a few clicks. The template is created once; you should not repeat the Ubuntu image import for every VM.

[1]: https://pve.proxmox.com/wiki/Roadmap?utm_source=chatgpt.com "Roadmap"
[2]: https://cloud-images.ubuntu.com/noble/current/?utm_source=chatgpt.com "Ubuntu 24.04 LTS (Noble Numbat) daily [20260705]"
[3]: https://pve.proxmox.com/wiki/Cloud-Init_Support?utm_source=chatgpt.com "Cloud-Init Support"
[4]: https://pve.proxmox.com/wiki/VM_Templates_and_Clones?utm_source=chatgpt.com "VM Templates and Clones"

