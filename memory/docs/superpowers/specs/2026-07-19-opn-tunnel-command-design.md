# OPN Tunnel Command Design

## Goal

Provide a memorable repository command that opens the existing SSH local-forward tunnel without requiring the user to recall its arguments.

## Design

Add an `opn` recipe to `commands/dev.just`. Running `just dev opn` will execute:

```sh
ssh -N -L 8443:10.77.0.1:8443 morfuse@px
```

The recipe will remain attached to the terminal so SSH connection errors are visible and the tunnel can be stopped with `Ctrl+C`. No background-process management, configuration options, or wrapper script will be added.

## Verification

- Confirm `just --list dev` includes `opn`.
- Use a dry run to confirm `just --dry-run dev opn` expands to the exact SSH command.
- Do not establish a live SSH session during automated verification.
