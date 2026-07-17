---
date: 2026-06-06
type: reference
tags: [vps, docker, dokploy, services, infrastructure]
related:
  - memory/docs/infrastructure/server-provisioning.md
  - memory/docs/infrastructure/dokploy-service-deployment.md
  - memory/notes/2026-05-30-vps-current-services.md
---

# Current Services

This is the canonical infrastructure inventory reference. The original dated snapshot remains at `memory/notes/2026-05-30-vps-current-services.md`.

## Pre-Migration Snapshot

Snapshot date: 2026-05-30

Context: Docker services running on the existing VPS ahead of migration to a fresh VPS with Dokploy.

## Running Docker Containers

| Container ID | Image | Name | Uptime | Ports |
|---|---|---|---|---|
| `e7cbc4a3e5c1` | `ghcr.io/morfusee/void-vendor:latest` | `void-vendor-void-vendor-1` | 3 months | - |
| `e4e021bac900` | `containrrr/watchtower` | `void-vendor-watchtower-1` | 3 months | 8080/tcp |
| `13cd3cff9021` | `ghcr.io/ykzsolutions/mmdc-student-portal:latest` | `mmdc-student-portal` | 6 months | 3001/tcp |
| `df3a42641776` | `traefik:latest` | `traefik` | 7 months | 80:80, 443:443 |
| `7db44d796a56` | `tecnativa/docker-socket-proxy` | `traefik-gateway-socket-proxy-1` | 8 months | 2375/tcp |
| `25ff22766d8d` | `ghcr.io/moghtech/komodo-periphery:latest` | `komodo-periphery-periphery-1` | 8 months | - |

## Docker Templates And Folders To Migrate

- [x] `komodo-periphery` - already present
- [x] `mmdc-student-portal-backend` - already present
- [x] `traefik-gateway` - already present
- [x] `void-vendor` - already present
- [ ] `firestore-erd` - needs to be added; currently on the down VPS

## Service Dependencies

- `traefik` - reverse proxy and SSL termination for all services; ports 80 and 443 exposed.
- `traefik-gateway-socket-proxy-1` - provides Docker socket access to Traefik for dynamic routing.
- `komodo-periphery` - Komodo monitoring/periphery agent.
- `void-vendor` - application container; no exposed host ports in the snapshot, likely routed through Traefik.
- `void-vendor-watchtower-1` - automatic container image updates for `void-vendor`.
- `mmdc-student-portal` - student portal application; port 3001 internal.

## Migration Notes

- Recover the `firestore-erd` template from the down VPS before adding it to the new host.
- Migrate Traefik configuration, labels, middlewares, and routers alongside the containers.
- Watchtower is scoped to the `void-vendor` Compose project only.

## Upkeep Checklist

Use this checklist when reviewing each hosted project:

1. Confirm the service is visible in Dokploy.
2. Confirm the Compose file uses internal `expose` ports rather than public host-port exposure unless explicitly required.
3. Confirm required environment variables are present in Dokploy.
4. Confirm the domain points to the expected service and port.
5. Confirm Cloudflare proxy state matches the domain constraints.
6. Confirm backups or recovery steps exist for stateful services such as databases.
7. Confirm restart procedure is known from Dokploy for the service.
