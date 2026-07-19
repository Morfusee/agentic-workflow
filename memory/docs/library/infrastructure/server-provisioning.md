---
date: 2026-06-06
type: howto
tags: [vps, provisioning, ansible, tailscale, infrastructure]
related:
  - memory/docs/library/infrastructure/dokploy-service-deployment.md
  - memory/docs/library/infrastructure/current-services.md
---

# Server Provisioning

Use this guide when provisioning a fresh VPS before installing Dokploy or deploying services.

## Requirements

- Windows Subsystem for Linux (WSL).
- Access to the `server-playbook` repository.
- A non-ephemeral Tailscale auth key.
- Temporary VPS password from the hosting provider.

## Provisioning Flow

1. Clone or open the `server-playbook` repository from WSL.
2. Generate a non-ephemeral Tailscale auth key.
3. Add the Tailscale token to the appropriate `server-playbook` variables file.
   - For the agent/operator reading this later: inspect the playbook inventory, variable files, and README before editing. Do not guess the token location.
   - Treat the token as secret material. Do not commit it.
4. Toggle the global playbook variable that enables Tailscale provisioning.
5. Before running Ansible, SSH into the VPS manually.
6. Log in with the temporary VPS password.
7. Complete the initial password change prompt.
8. Use the new password for the Ansible provisioning run.
9. Run the provisioning command documented in `server-playbook/README.md`.
   - If multiple commands are listed, start with the command that matches the target inventory/environment.
   - If the first command fails because of inventory, SSH, or variable selection, inspect the README and playbook layout before retrying.
10. When provisioning completes, continue with `memory/docs/infrastructure/dokploy-service-deployment.md`.

## Notes

- The exact Ansible command is intentionally not duplicated here because `server-playbook` is the source of truth for its own command syntax.
- Do not store the Tailscale token in this repository.
- Do not skip the first manual VPS login. The initial password change must happen before Ansible can use the password reliably.
