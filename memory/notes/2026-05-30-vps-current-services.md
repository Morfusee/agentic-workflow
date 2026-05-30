---
date: 2026-05-30
type: infrastructure
tags: [vps, docker, migration, dokploy, infrastructure]
related: []
---

# Current VPS Services — Pre-Migration Snapshot

**Date:** 2026-05-30
**Context:** Documenting current Docker services running on the existing VPS ahead of migration to a fresh VPS with Dokploy.

## Running Docker Containers

| Container ID | Image | Name | Uptime | Ports |
|---|---|---|---|---|
| `e7cbc4a3e5c1` | `ghcr.io/morfusee/void-vendor:latest` | `void-vendor-void-vendor-1` | 3 months | — |
| `e4e021bac900` | `containrrr/watchtower` | `void-vendor-watchtower-1` | 3 months | 8080/tcp |
| `13cd3cff9021` | `ghcr.io/ykzsolutions/mmdc-student-portal:latest` | `mmdc-student-portal` | 6 months | 3001/tcp |
| `df3a42641776` | `traefik:latest` | `traefik` | 7 months | 80:80, 443:443 |
| `7db44d796a56` | `tecnativa/docker-socket-proxy` | `traefik-gateway-socket-proxy-1` | 8 months | 2375/tcp |
| `25ff22766d8d` | `ghcr.io/moghtech/komodo-periphery:latest` | `komodo-periphery-periphery-1` | 8 months | — |

## Docker Templates/Folders to Migrate

- [x] `komodo-periphery` — already present
- [x] `mmdc-student-portal-backend` — already present
- [x] `traefik-gateway` — already present
- [x] `void-vendor` — already present
- [ ] `firestore-erd` — needs to be added (currently on the down VPS)

## Service Dependencies

- **traefik** — reverse proxy and SSL termination for all services (ports 80/443 exposed)
- **traefik-gateway-socket-proxy-1** — provides Docker socket access to Traefik for dynamic routing
- **komodo-periphery** — Komodo monitoring/periphery agent
- **void-vendor** — application container (no exposed ports, likely routed through Traefik)
- **void-vendor-watchtower** — automatic container image updates for void-vendor
- **mmdc-student-portal** — student portal application (port 3001 internal)

## Migration Notes

- The `firestore-erd` template needs to be recovered from the down VPS before it can be added.
- Traefik handles all ingress — the Traefik configuration (labels, middlewares, routers) must be migrated alongside the containers.
- Watchtower is scoped to the void-vendor compose project only.
