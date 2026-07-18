# Proxmox Duplicate OpenSSH UFW Cleanup Design

## Problem

The firewall role invokes `community.general.ufw` once to delete the unrestricted `OpenSSH` application rule. UFW can contain duplicate copies of that rule. One invocation removes one matching copy, so the subsequent check-mode verification still predicts another deletion and stops the play.

## Design

Keep the existing declarative module call and retry it until the module reports `changed: false`, which means no matching unrestricted `OpenSSH` rule remains. Cap retries so a module or host that cannot converge fails instead of looping indefinitely. Do not parse `ufw status` output or delete numbered rules.

The Tailscale-scoped numeric SSH rule is unaffected because the cleanup targets only the `OpenSSH` application profile. Existing post-mutation verification remains the final safety check.

## Testing

Add a policy test that requires the OpenSSH cleanup task to register its result, retry until it is unchanged, and use a finite retry count. Run the complete Proxmox policy test suite and parse all YAML files.
