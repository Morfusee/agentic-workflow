# Notes

- User is comfortable with Linux CLI but has no networking knowledge
- Goal is self-hosting apps on Proxmox at OVH KimSufi
- Target: within a month
- First lesson should be about IP addressing, subnetting, and how it connects to OVH's Proxmox config
- **NO Additional IPs** — single public IP shared via NAT + port forwarding
- This means the network topology is: host public IP -> NAT -> VMs on private bridge. Inbound via port forwarding (DNAT).
