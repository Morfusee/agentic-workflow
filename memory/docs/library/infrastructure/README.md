---
date: 2026-07-17
type: index
tags: [infrastructure, networking, deployment, documentation]
related:
  - memory/docs/library/infrastructure/current-services.md
  - memory/docs/library/infrastructure/server-provisioning.md
  - memory/docs/library/infrastructure/dokploy-service-deployment.md
  - memory/docs/library/infrastructure/proxmox-opnsense-network-design.md
  - memory/docs/library/infrastructure/revised-proxmox-opnsense-network-design.md
  - memory/docs/library/infrastructure/opnsense-hardening-and-network-segmentation.md
  - memory/docs/library/infrastructure/opnsense-crowdsec-caddy.md
  - memory/docs/library/infrastructure/proxmox-ubuntu-cloud-init-template.md
  - memory/docs/library/infrastructure/github-vps-limited-access.md
---

# Infrastructure

Documentation for servers, networking, deployments, and currently running services.

## Choose a document

- [Current services](current-services.md) — inventory the services and containers that exist before migration or maintenance work.
- [Server provisioning](server-provisioning.md) — follow the standard flow for preparing a new server.
- [Dokploy service deployment](dokploy-service-deployment.md) — deploy and expose an application through Dokploy, Traefik, and Cloudflare.
- [Proxmox and OPNsense network design](proxmox-opnsense-network-design.md) — build the private VM network, firewall, NAT, DHCP, DNS, and public forwarding architecture.
- [Protect OPNsense and Caddy with CrowdSec](opnsense-crowdsec-caddy.md) — install CrowdSec, analyze Caddy access logs, and apply firewall-level bans.
- [Proxmox Ubuntu cloud-init template](proxmox-ubuntu-cloud-init-template.md) — create a reusable Ubuntu 24.04 template and provision cloned VMs through the Proxmox interface.
- [Limited GitHub access for a coding VPS](github-vps-limited-access.md) — grant selected repositories narrowly scoped HTTPS access while protecting administrative operations and important branches.

## Quick routing

- Need to understand what is already running? Open **Current services**.
- Preparing a new machine? Open **Server provisioning**.
- Shipping an application? Open **Dokploy service deployment**.
- Configuring Proxmox networking or OPNsense? Open **Proxmox and OPNsense network design**.
- Adding attack detection and automated bans to OPNsense-hosted sites? Open **Protect OPNsense and Caddy with CrowdSec**.
- Creating reusable Ubuntu VMs in Proxmox? Open **Proxmox Ubuntu cloud-init template**.
- Connecting a coding VPS to selected GitHub repositories? Open **Limited GitHub access for a coding VPS**.
