# Mission: Networking Fundamentals

## Why

You're setting up Proxmox on a KimSufi dedicated server at OVHCloud to self-host apps (Nextcloud, VPN, password manager, etc.). Right now you don't know the networking terms or concepts needed to configure the server properly, assign IPs to VMs, or troubleshoot connectivity.

## Success looks like

- You can explain what an IP address, subnet mask, gateway, and DNS are
- You can set up Proxmox networking on your KimSufi server with a bridge for VMs
- Your VMs have internet access (outbound) through the server's single public IP via NAT
- Your self-hosted apps are accessible from outside via port forwarding (no Additional IPs needed)
- You can read and understand OVH's network configuration guides without confusion

## Constraints

- ~1 month to get it running
- KimSufi is OVH's budget line — no vRack, limited IP options
- Comfortable with Linux CLI, just not networking
- No Additional IPs — all VMs share the server's single public IP via NAT + port forwarding

## Out of scope

- Advanced routing protocols (BGP, OSPF)
- OVH vRack configuration (not available on KimSufi)
- Additional / Failover IPs (not buying any)
- Complex firewall rule writing — only the NAT rules needed
- DNS configuration beyond understanding what it is
- Network security hardening in depth
