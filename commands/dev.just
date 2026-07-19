[private]
default:
    @just --list dev
# Serve OpenCode on the current machine's Tailscale IPv4
serve-opencode:
    opencode serve --port 6767 --hostname $(tailscale ip -4)

# Forward local port 8443 to the OPN service through px
opn:
    ssh -N -L 8443:10.77.0.1:8443 morfuse@px
