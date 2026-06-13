# Path Correction: NAT Instead of Additional IPs

User clarified they do not want to buy Additional IPs from OVH. All VMs will share the server's single public IP through NAT (masquerade) for outbound traffic and port forwarding (DNAT) for inbound access.

This changes the network topology from the one outlined in Lesson 1's diagram. Lesson 2 must cover NAT, port forwarding, and iptables rules rather than Additional IP routing. Future sessions should skip Additional IP configuration entirely.

Evidence: user explicitly stated "set this up without adding or buying an additional IP" and wants "proper networking and routing without additional IPs."

Implications:
- No routed-mode /32 additional IP config needed per VM
- Instead: single bridge (vmbr0), VMs get private 192.168.0.x/24 addresses, host does NAT
- Port forwarding directs specific ports (e.g. 443, 80, 51820) to specific VMs
- This is simpler to manage but means all services share port space (can't have two VMs on port 443)
