---
date: 2026-05-31
type: howto
tags: [dokploy, deployment, self-hosted, infrastructure]
related: []
---

# Dokploy Installation Steps

## 1. Run the Install Script

```bash
curl -sSL https://dokploy.com/install.sh | sudo sh
```

## 2. Configure Cloudflare Subdomain

> **Caveat — DNS only first, then proxy.** When proxying apps with Cloudflare behind Dokploy or Traefik, the subdomain **must** start as **DNS only**. That is when Traefik issues the Let's Encrypt cert on the VPS. If the record is Proxied during instantiation, cert issuance fails.
>
> Workflow:
> 1. Add the subdomain in Cloudflare and leave it on **DNS only**.
> 2. Wait for Traefik to issue the Let's Encrypt cert and confirm HTTPS works.
> 3. Go to **SSL/TLS > Overview > Configure** and set Custom SSL/TLS to **Full (strict)** — required so the Let's Encrypt cert issued by Traefik is trusted when the record is later proxied.
> 4. Switch the record from **DNS only** to **Proxied**. Cloudflare will then proxy the app using the TLS cert issued by Traefik.
>
> Subdomains that do not satisfy Universal TLS (e.g. `api.ferd.mcube.uk`) must stay on **DNS only** permanently — they cannot be proxied.

## 3. Configure Web Server

- Go to **Web Server** in Dokploy.
- Add the domain.
- Enable HTTPS.

## 4. Remove Exposed Port 3000

Run this to disable port 3000 while keeping the domain accessible:

```bash
docker service update --publish-rm "published=3000,target=3000,mode=host" dokploy
```
