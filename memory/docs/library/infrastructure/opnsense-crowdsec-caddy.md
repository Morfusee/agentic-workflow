---
date: 2026-07-20
type: howto
tags: [opnsense, crowdsec, caddy, firewall, security]
related:
  - memory/docs/library/infrastructure/README.md
  - memory/docs/library/infrastructure/opnsense-hardening-and-network-segmentation.md
  - memory/docs/library/infrastructure/proxmox-opnsense-network-design.md
---

# Protect OPNsense and Caddy with CrowdSec

Configure CrowdSec in two layers:

1. Protect OPNsense itself and apply firewall-level bans.
2. Feed Caddy access logs into CrowdSec so attacks against `*.cloud.mcube.uk` can trigger bans.

## 1. Install the OPNsense CrowdSec plugin

In OPNsense, navigate to:

```text
System
→ Firmware
→ Plugins
```

Enable:

```text
Show community plugins
```

Find:

```text
os-crowdsec
```

Click the install `+` button.

The plugin installs three components:

```text
os-crowdsec
crowdsec
crowdsec-firewall-bouncer
```

The firewall bouncer turns CrowdSec decisions into packet blocks on OPNsense. Do not manually start the FreeBSD services from the terminal; the OPNsense plugin manages them. ([CrowdSec Documentation][1])

## 2. Verify the CrowdSec services

Refresh the OPNsense interface, then open:

```text
Services
→ CrowdSec
→ Overview
```

Confirm that the components are running.

Then open:

```text
Services
→ CrowdSec
→ Settings
```

Leave these enabled:

```text
Enable Log Processor
Enable LAPI
Enable Remediation Component
```

| Component | Purpose |
| --- | --- |
| Log Processor | Reads logs and detects attacks |
| LAPI | Stores alerts and ban decisions |
| Remediation Component | Blocks decided IPs through the firewall |

These components are normally enabled by default. The FreeBSD and OPNsense CrowdSec collections are also installed automatically. ([CrowdSec Documentation][2])

Press:

```text
Apply
```

You do not need to create a normal WAN firewall rule for CrowdSec bans. The remediation component and firewall bouncer manage their own blocking mechanism.

## 3. Enable Caddy JSON access logs

CrowdSec needs Caddy access logs to detect attacks against proxied websites.

Navigate to:

```text
Services
→ Caddy Web Server
→ General Settings
→ Log Settings
```

Enable:

```text
Log HTTP Access in JSON Format
```

Save and apply.

Then navigate to:

```text
Services
→ Caddy Web Server
→ Reverse Proxy
→ Domains
```

Edit every public domain that CrowdSec should monitor, such as:

```text
dokploy.mcube.uk
whoami.cloud.mcube.uk
*.cloud.mcube.uk
```

Inside each domain, open the **Access** section and enable:

```text
HTTP Access Log
```

Save and apply.

Caddy should now create one JSON log file per domain under:

```text
/var/log/caddy/access/
```

This is the log location documented by the OPNsense Caddy plugin. ([OPNsense Documentation][3])

## 4. Confirm that Caddy is producing logs

Open the OPNsense console or connect through SSH. From the OPNsense console menu, choose:

```text
8) Shell
```

Check the directory:

```sh
ls -lah /var/log/caddy/access/
```

You should see files after visiting one of your public domains.

Inspect recent entries:

```sh
tail -n 20 /var/log/caddy/access/*.log
```

For a live view:

```sh
tail -f /var/log/caddy/access/*.log
```

Visit one of your domains from a browser. A new JSON entry should appear.

Do not continue until this works. Without access-log entries, CrowdSec has nothing from Caddy to analyze.

## 5. Install the CrowdSec Caddy collection

In the OPNsense shell, run:

```sh
cscli collections install crowdsecurity/caddy
```

Verify it:

```sh
cscli collections list | grep caddy
```

The collection includes the parser and detection scenarios needed to understand Caddy's JSON access logs. OPNsense's official Caddy integration specifically instructs installing `crowdsecurity/caddy`. ([OPNsense Documentation][3])

## 6. Add the Caddy log acquisition configuration

Create the acquisition directory if it does not already exist:

```sh
mkdir -p /usr/local/etc/crowdsec/acquis.d
```

Create the Caddy configuration:

```sh
cat > /usr/local/etc/crowdsec/acquis.d/caddy.yaml <<'EOF'
filenames:
  - /var/log/caddy/access/*.log

force_inotify: true
poll_without_inotify: true

labels:
  type: caddy
EOF
```

Check it:

```sh
cat /usr/local/etc/crowdsec/acquis.d/caddy.yaml
```

The path, wildcard, and labels above are recommended by the OPNsense Caddy documentation. ([OPNsense Documentation][3])

## 7. Restart CrowdSec through the GUI

Do not restart the individual packages manually.

Return to:

```text
Services
→ CrowdSec
→ Settings
```

Press:

```text
Apply
```

Alternatively, use the restart control on the CrowdSec overview page.

Then check:

```text
Services
→ CrowdSec
→ Overview
```

Confirm that the Log Processor, LAPI, and Remediation Component are running.

## 8. Verify that CrowdSec reads the logs

From the OPNsense shell, run:

```sh
cscli metrics
```

Look for entries involving:

```text
/var/log/caddy/access/
caddy
```

Also check alerts:

```sh
cscli alerts list
```

Check current bans:

```sh
cscli decisions list -a
```

It is normal for the alerts and decisions lists to be empty at first. The important verification is that Caddy log lines appear in the acquisition and parser metrics.

You can also inspect the installed components:

```sh
cscli collections list
cscli parsers list
cscli scenarios list
```

## 9. Safely test firewall blocking

Only perform this test when you have OPNsense console access through Proxmox. Do not test against the only IP address from which you can administer the firewall.

Determine the public IP of a separate test device, such as a phone using mobile data, and temporarily ban it:

```sh
cscli decisions add -t ban -d 2m -i PUBLIC_TEST_IP
```

Example:

```sh
cscli decisions add -t ban -d 2m -i 203.0.113.50
```

List the decision:

```sh
cscli decisions list
```

From that device, try opening:

```text
https://dokploy.mcube.uk
```

The connection should be blocked. The decision expires automatically after two minutes.

To remove it immediately:

```sh
cscli decisions delete -i PUBLIC_TEST_IP
```

CrowdSec's OPNsense documentation recommends this manual two-minute decision as a safer test than deliberately brute-forcing a service. ([CrowdSec Documentation][2])

## 10. Protect trusted addresses

Current CrowdSec versions whitelist private networks by default for locally generated decisions. This generally protects LAN addresses such as `10.77.0.0/24` from automatic local bans. ([CrowdSec Documentation][2])

Keep the following administrative paths protected:

```text
10.77.0.0/24
Your Proxmox management path
Your Tailscale administration path
Your regular home public IP, if static
```

Do not remove CrowdSec's default whitelist parser unless you specifically want internal devices to be automatically banned.

## 11. Optional: connect the CrowdSec web console

The CrowdSec web console is not required for protection, but it provides centralized visibility into alerts and decisions.

Create an enrollment key in CrowdSec Console, then run:

```sh
cscli console enroll --name opnsense-mcube YOUR-ENROLLMENT-KEY
```

Approve the pending engine enrollment in the CrowdSec web console. ([CrowdSec Documentation][4])

Check its status:

```sh
cscli console status
```

## Traffic flow

Once configured, protection works as follows:

```text
Internet client
      ↓
OPNsense firewall
      ↓
CrowdSec firewall bouncer checks existing bans
      ↓
Caddy receives HTTPS request
      ↓
Caddy writes JSON access log
      ↓
CrowdSec analyzes the log
      ↓
Suspicious behavior triggers a decision
      ↓
Firewall bouncer blocks that source IP
```

This protects every internal application routed through the OPNsense Caddy instance without requiring CrowdSec on each VM.

## Cloudflare caveat

When using Cloudflare's proxied, orange-cloud mode, confirm that Caddy records the visitor's real IP rather than a Cloudflare edge IP before enabling automated bans. Otherwise, CrowdSec could detect or block the proxy address instead of the attacker.

## Final verification

Before relying on the setup, confirm:

- The Log Processor, LAPI, and Remediation Component are enabled and running.
- Caddy produces JSON access logs for every monitored public domain.
- `cscli metrics` shows the Caddy log files and parser activity.
- A temporary ban against a separate test device blocks traffic and then expires.
- Trusted management paths remain reachable.

[1]: https://docs.crowdsec.net/u/getting_started/installation/opnsense/ "OPNsense | CrowdSec"
[2]: https://docs.crowdsec.net/docs/next/getting_started/install_crowdsec_opnsense "OPNsense | CrowdSec"
[3]: https://docs.opnsense.org/manual/how-tos/caddy.html "Caddy: Reverse Proxy - OPNsense documentation"
[4]: https://docs.crowdsec.net/docs/cscli/cscli_console_enroll "cscli console enroll"
