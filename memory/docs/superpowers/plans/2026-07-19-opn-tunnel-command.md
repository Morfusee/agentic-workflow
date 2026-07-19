# OPN Tunnel Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `just dev opn` as a memorable shortcut for the OPN SSH local-forward tunnel.

**Architecture:** Extend the existing development command module with one foreground recipe. Keep the SSH invocation literal so the Just recipe remains transparent and requires no wrapper or configuration layer.

**Tech Stack:** Just, OpenSSH

---

### Task 1: Add and verify the tunnel recipe

**Files:**
- Modify: `commands/dev.just`

- [ ] **Step 1: Confirm the recipe is initially absent**

Run: `just --list dev`

Expected: the output lists `serve-opencode` and does not list `opn`.

- [ ] **Step 2: Add the minimal recipe**

Append this recipe to `commands/dev.just`:

```just
# Forward local port 8443 to the OPN service through px
opn:
    ssh -N -L 8443:10.77.0.1:8443 morfuse@px
```

- [ ] **Step 3: Verify command discovery**

Run: `just --list dev`

Expected: the output lists both `opn` and `serve-opencode`.

- [ ] **Step 4: Verify exact command expansion without connecting**

Run: `just --dry-run dev opn`

Expected output:

```text
ssh -N -L 8443:10.77.0.1:8443 morfuse@px
```

- [ ] **Step 5: Review the final diff**

Run: `git diff -- commands/dev.just`

Expected: only the `opn` comment, recipe name, and SSH command are added.
