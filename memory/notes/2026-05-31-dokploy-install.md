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

1. Add a subdomain in Cloudflare and turn on **Proxied**.
2. Go to **SSL/TLS > Overview > Configure**.
3. Set Custom SSL/TLS to **Full** or **Full (Strict)** — avoids the "Redirect too many times" error for proxied traffic in browsers.

## 3. Configure Web Server

- Go to **Web Server** in Dokploy.
- Add the domain.
- Enable HTTPS.

## 4. Remove Exposed Port 3000

Run this to disable port 3000 while keeping the domain accessible:

```bash
docker service update --publish-rm "published=3000,target=3000,mode=host" dokploy
```
