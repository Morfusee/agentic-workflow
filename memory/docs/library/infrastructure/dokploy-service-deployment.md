---
date: 2026-06-06
type: howto
tags: [dokploy, deployment, cloudflare, github, infrastructure]
related:
  - memory/docs/library/infrastructure/server-provisioning.md
  - memory/docs/library/infrastructure/current-services.md
---

# Dokploy Service Deployment

Use this guide after server provisioning is complete and Dokploy is installed.

## Install Dokploy

Run the official install script on the provisioned VPS:

```bash
curl -sSL https://dokploy.com/install.sh | sudo sh
```

## Configure GitHub Access

1. In Dokploy, go to **Git**.
2. Select **GitHub** as the provider.
3. Enable organization access.
   - This is required for Dokploy to see repositories under GitHub organizations.
4. If the GitHub app was renamed, find the equivalent URL for the renamed app and update the name in Dokploy's Git Providers list as well.

## Database Compatibility

- Use MongoDB 7 for services that are incompatible with MongoDB 8 or with the current VPS environment.
- Do not upgrade those services to MongoDB 8 unless the application compatibility issue has been verified as fixed.

## Compose File Requirements

1. Provide a valid Compose file for the service.
2. Use `expose` for ports that Traefik/Dokploy should discover internally.
3. Avoid publishing application ports directly to the internet unless the service explicitly requires public host-port exposure.

Example shape:

```yaml
services:
  app:
    image: example/app:latest
    expose:
      - "3000"
```

## Internal-Only External Port Workaround

When creating or editing a Dokploy service, set **External Port** to a single space character (` `), then save.

This keeps the service internally hosted and prevents it from being visible directly on the public internet while still allowing Traefik/Dokploy routing through the configured domain.

If an older Dokploy deployment has already exposed port `3000`, remove that published port with:

```bash
docker service update --publish-rm "published=3000,target=3000,mode=host" dokploy
```

## Environment Variables

1. Add the required environment variables in Dokploy before first deployment.
2. Do not commit secrets to this repository.
3. Keep per-service env var names and values in the secret manager or Dokploy configuration, not in docs.

## Domain Setup

1. In Cloudflare, create the DNS record for the service domain.
2. Leave the Cloudflare record as **DNS only** for the first deploy.
   - Do not enable proxy before Let's Encrypt has issued the certificate.
3. In Dokploy, add the domain to the service.
4. Set the domain port to the port listed in the Compose file's `expose` section.
5. Set **Let's Encrypt** as the certificate provider.
6. Deploy or save the service and wait for the Let's Encrypt certificate to generate.
7. Confirm HTTPS works directly.
8. In Cloudflare, set SSL/TLS mode to **Full (strict)**.
9. Switch the Cloudflare record from **DNS only** to **Proxied** when the domain supports proxying.

## Cloudflare Proxy With Traefik

If Dokploy-hosted subdomains stop working after switching Cloudflare from **DNS only** to **Proxied**, configure Traefik to trust Cloudflare's forwarded headers.

This fixed cases where proxied Dokploy services were inaccessible and where proxying the Dokploy dashboard caused logs to stop streaming.

Add Cloudflare's IP ranges to `forwardedHeaders.trustedIPs` for both `web` and `websecure` in `traefik.yml`:

```yaml
entryPoints:
  web:
    address: ":80"
    forwardedHeaders: &cloudflareForwardedHeaders
      trustedIPs:
        - "173.245.48.0/20"
        - "103.21.244.0/22"
        - "103.22.200.0/22"
        - "103.31.4.0/22"
        - "141.101.64.0/18"
        - "108.162.192.0/18"
        - "190.93.240.0/20"
        - "188.114.96.0/20"
        - "197.234.240.0/22"
        - "198.41.128.0/17"
        - "162.158.0.0/15"
        - "104.16.0.0/13"
        - "104.24.0.0/14"
        - "172.64.0.0/13"
        - "131.0.72.0/22"
        - "2400:cb00::/32"
        - "2606:4700::/32"
        - "2803:f800::/32"
        - "2405:b500::/32"
        - "2405:8100::/32"
        - "2a06:98c0::/29"
        - "2c0f:f248::/32"

  websecure:
    address: ":443"
    forwardedHeaders: *cloudflareForwardedHeaders
```

After changing `traefik.yml`, restart or redeploy Traefik so the static configuration is reloaded.

Also verify Cloudflare-side settings:

- WebSockets are enabled.
- SSL/TLS mode is **Full (strict)**.
- Security Rules, WAF rules, and Access/Zero Trust policies are not blocking the subdomain or WebSocket upgrades.
- The Cloudflare IP ranges are current at `https://www.cloudflare.com/ips/`.

## Cloudflare Caveats

- Cloudflare proxying before certificate issuance can cause Let's Encrypt failures.
- Subdomains that do not satisfy Cloudflare Universal TLS coverage must stay **DNS only** permanently.
- `api.ferd.mcube.uk` is an example of a subdomain that may need to remain **DNS only**.
- Do not set `forwardedHeaders.trustedIPs` to trust all traffic. Keep it scoped to Cloudflare's published IP ranges.

## Repeat Per Service

Repeat the Compose, env var, database, and domain setup steps for each service deployed in Dokploy.
