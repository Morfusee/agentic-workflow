# Networking Fundamentals Resources

## Knowledge

- [OVH Docs: Proxmox VE Networking on HG/Scale Dedicated Servers](https://docs.ovh.com/us/en/dedicated/proxmox-network-hg-scale/)
  Step-by-step guide for bridge + routed mode on OVH. Use for: Proxmox-specific networking config.
- [OVH Docs: Configuring Additional IPs in bridge mode](https://docs.ovh.com/us/en/dedicated/network-bridging/)
  General bridge setup for virtual machines on OVH. Use for: understanding bridge vs routed mode.
- [OVH Docs: Getting started with Kimsufi dedicated server](https://docs.ovh.com/us/en/dedicated/getting-started-with-dedicated-server-eco/)
  First steps for Kimsufi/So You Start servers. Use for: initial server setup, rescue mode, etc.
- [OVH Docs: Configuring IPv6 on dedicated servers](https://docs.ovh.com/us/en/dedicated/network-ipv6/)
  IPv6 configuration for OVH dedicated servers. Use for: when you need IPv6 on VMs.
- [DigitalOcean: An Introduction to Networking Terminology, Interfaces, and Protocols](https://www.digitalocean.com/community/tutorials/an-introduction-to-networking-terminology-interfaces-and-protocols)
  Clear primer on IP addresses, ports, protocols, NAT, etc. Use for: core conceptual knowledge.
- [DigitalOcean: Understanding IP Addresses, Subnets, and CIDR Notation](https://www.digitalocean.com/community/tutorials/understanding-ip-addresses-subnets-and-cidr-notation-for-networking)
  The best concise explanation of subnetting and CIDR. Use for: understanding /32, /28, /24 notation.
- [Computer Networking: A Top-Down Approach — Kurose & Ross](https://www.amazon.com/Computer-Networking-Top-Down-Approach-7th/dp/0133594149)
  Standard academic textbook. Use for: deep knowledge when you want it. Not for quick learning.
- [Proxmox Wiki: Network Model](https://pve.proxmox.com/wiki/Network_Model)
  Official Proxmox networking docs explaining bridges, bonds, VLANs. Use for: understanding vmbr0, vmbr1 in your config.
- [IBM: What is a subnet?](https://www.ibm.com/topics/subnet)
  Enterprise-level explanation of subnetting. Use for: supplementing DigitalOcean article.
- [Subnet Calculator (calculator.net)](https://www.calculator.net/ip-subnet-calculator.html)
  Practical tool for calculating network/broadcast/gateway from CIDR. Use for: checking your IP math.

## Wisdom (Communities)

- [r/Proxmox](https://reddit.com/r/Proxmox)
  Active community for Proxmox-specific questions. Search before posting.
- [r/OVH](https://reddit.com/r/OVH)
  OVHCloud user community. Use for: provider-specific troubleshooting.
- [Proxmox Forum](https://forum.proxmox.com/)
  Official Proxmox forum. High-quality answers from devs and power users.
- [OVH Community](https://community.ovhcloud.com/)
  OVH's official community. Use for: Kimsufi-specific networking help.

## Gaps

- No single beginner-friendly resource found that explains OVH-specific networking concepts (Additional IPs, gateway 100.64.0.1, /32 on public interface) from the ground up. Lessons will need to bridge this gap.
