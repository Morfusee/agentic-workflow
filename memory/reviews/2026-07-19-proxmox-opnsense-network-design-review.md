# Proxmox and OPNsense network design review

**Date:** 2026-07-19
**Review scope:** Comparison of `revised-proxmox-opnsense-network-design.md` against `proxmox-opnsense-network-design.md`, with emphasis on security hardening and omitted controls
**Reviewer:** requirements-reviewer
**Overall status:** **PARTIAL**

## Summary

The revised architecture is cleaner and removes double NAT, but its threat model is more demanding because OPNsense now hosts the Internet-facing Caddy reverse proxy. Public web exposure and certificate automation are improved, but several important hardening and recovery controls are missing.

## Checks

### Backup and recovery guidance

**Status:** FAIL

The original document includes dedicated Proxmox configuration backups, OPNsense XML exports, VM backups, and rollback instructions. The revision mentions rescue/IPMI availability but provides no known-good snapshot, configuration export, or rollback sequence.

Add backups before material changes and checkpoints after working WAN, LAN, routing, DNS, Caddy, and firewall configuration.

### Proxmox management restrictions

**Status:** PARTIAL

The architecture says SSH and port 8006 are restricted to Tailscale, but it does not show or verify the UFW, nftables, Proxmox firewall, or provider-firewall rules that enforce this.

Add steps to:

- Verify Tailscale access before network changes.
- Restrict TCP 22 and 8006 to trusted Tailscale or management sources.
- Test from an external, non-Tailscale connection that both ports are closed.
- Preserve OVH rescue or IPMI access.

### OPNsense administrative access

**Status:** PARTIAL

Moving the WebGUI to port 8443 and stating that it must not be exposed publicly is useful, but the revision does not explicitly bind or firewall it to trusted management sources. It also does not cover MFA, a separate administrator account, or session hardening.

Add a management alias and explicit rule for port 8443, restrict its listening interfaces where practical, and test externally that WAN port 8443 is unreachable.

### OPNsense security updates

**Status:** FAIL

The firmware page is used only to confirm repository connectivity. The guide never instructs the operator to install available OPNsense updates, reboot when required, and verify the installed version afterward.

The same lifecycle guidance is missing for Proxmox, Caddy, Docker, Dokploy, and guest operating systems.

### Network and workload isolation

**Status:** FAIL

Proxmox management, OPNsense management, production, staging, and other VMs all share `10.77.0.0/24`. The LAN firewall rule permits `LAN net` to `Any` using any protocol.

OPNsense cannot filter direct traffic between machines on the same layer-2 subnet. A compromised Dokploy VM could therefore contact adjacent VMs and the Proxmox private address unless guest or Proxmox firewall rules stop it.

Use separate VLANs, bridges, or subnets for at least:

- Management
- Edge or reverse proxy
- Production
- Staging
- Databases, if introduced

Permit only required flows between those zones. If segmentation is deferred, document that risk and add restrictive guest or Proxmox firewall rules.

### DNS resolver exposure

**Status:** PARTIAL

Unbound is configured with network and outgoing interfaces set to `All`. Default WAN firewall blocking should prevent public recursion, but LAN-only binding offers better defense in depth.

Configure only the required internal listening interfaces where feasible and include a negative external test proving that WAN DNS recursion is unavailable.

### Cloudflare credential handling

**Status:** PARTIAL

Using a zone-scoped token with only Zone Read and DNS Edit is good. The revision does not address secure storage, rotation, revocation, or configuration backups that may contain the credential.

Document how the token is stored, who can retrieve exported OPNsense configurations, how backups are encrypted, and how to rotate or revoke the token.

### Caddy on the firewall appliance

**Status:** PARTIAL

The revision correctly limits public firewall rules to TCP 80 and 443, disables HTTP/3 initially, and separates the WebGUI port. However, running the public reverse proxy as an OPNsense plugin increases the firewall appliance's attack surface.

Document this tradeoff and add:

- Plugin patching procedures
- Access and error-log retention
- Monitoring and alerting
- Configuration backup and rollback
- Validation that only intended hostnames and routes are accepted

A dedicated edge-proxy VM would provide a stronger isolation boundary, although it is not mandatory if the plugin risk is explicitly accepted and managed.

### Dokploy and Docker host hardening

**Status:** FAIL

The revision assigns VM resources, installs Docker and Dokploy, and configures domains, but does not cover:

- Host firewall rules
- Tailscale-only or otherwise restricted SSH administration
- OS, Docker, and Dokploy patching
- Non-root administration
- Docker socket protection
- Secret handling
- Application and volume backups
- Database isolation

These controls should be added before treating the production environment as hardened.

### Public exposure

**Status:** PASS

Only OPNsense WAN is attached to the public bridge. WAN rules expose Caddy on TCP 80 and 443, while Dokploy remains private and does not receive direct public port forwarding.

### Certificate automation

**Status:** PASS

The design uses DNS-01 wildcard certificates and a zone-restricted Cloudflare token instead of the Global API Key.

### Functional validation

**Status:** PASS

The revision includes ordered checks for routing, DNS, source NAT, direct Dokploy routing, internal Caddy behavior, public DNS, TLS, and external reachability.

## Recommended negative tests

Add explicit tests proving that:

- Public TCP 22, 8006, and 8443 are unreachable.
- DNS recursion through the OPNsense WAN address fails.
- Staging cannot initiate connections to production except for approved flows.
- Application VMs cannot reach Proxmox management services.
- Databases are inaccessible outside their approved application sources.
- Only intended application hostnames are served by Caddy and Dokploy.

## Priority order

1. Add backup and rollback procedures.
2. Enforce and verify Proxmox and OPNsense management restrictions.
3. Install updates rather than merely checking repository connectivity.
4. Separate management, production, staging, proxy, and database trust zones.
5. Add Dokploy, Docker, credential, monitoring, and maintenance hardening.
