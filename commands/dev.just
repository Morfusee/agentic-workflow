[private]
default:
    @just --list dev
# Serve OpenCode on the current machine's Tailscale IPv4
serve-opencode:
    opencode serve --port 6767 --hostname $(tailscale ip -4)
