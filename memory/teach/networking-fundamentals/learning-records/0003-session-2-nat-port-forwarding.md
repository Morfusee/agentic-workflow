# Session 2: NAT & Port Forwarding

Corrected the approach: no Additional IPs. Instead, the server's single public IP is shared via iptables MASQUERADE (outbound) and DNAT (inbound port forwarding).

Covered:
- SNAT/Masquerade vs DNAT/Port Forwarding
- Bridge configuration for single-NIC KimSufi on OVH
- iptables NAT rules: POSTROUTING MASQUERADE, PREROUTING DNAT, FORWARD rules
- Persisting iptables rules across reboots
- The tradeoff: one port one VM without a reverse proxy
- OVH quirks: /32 public IP, 100.64.0.1 gateway, proxy_arp

Updated: MISSION.md (success criteria now says NAT instead of Additional IPs), NOTES.md (constraint recorded), glossary (added NAT terms). Added learning record 0002 for the path correction.

Next (Lesson 3): hands-on Proxmox install on KimSufi — applying all of this on the real server.
