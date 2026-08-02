# Stand-up Script

Yesterday, I split the deploy Compose into independent per-service stacks for inngest, nextjs, pgdog-postgres, and playwright, and ordered the stack lifecycle so services start and stop in the right sequence. I added rollback and reset commands for operators and slimmed the deployment docs down to minimal per-service guides, routing the main guide to them. I also fixed the PgDog port so it stays internal to the Docker network. No ClickUp task completion is recorded for this day; this work continues the deployment rollout from last week.

Today, I plan to validate the independent stacks on my personal VPS behind a reverse proxy using Dockploy, and confirm how the MMDC deployment path—which I believe uses Codify—should be represented in the instructions.

No major blockers right now.

---

# Ticket Dump

Generated: 2026-08-01
Requested range: 2026-08-01 (Ulaanbaatar local date, UTC+08:00)
Dump file date: 2026-08-01

No ClickUp task completions are known for this date. This dump is built from git commit evidence only.

---

# Grouped Summary

2026-08-01

## Independent service stacks
- Split the deploy Compose into independent per-service stacks (inngest, nextjs, pgdog-postgres, playwright) and documented them. (32daef2, f38614c)

## Stack lifecycle / just commands
- Ordered the independent stack lifecycle and added rollback and reset commands. (283abe3, b2e09e1)

## Deployment docs simplification
- Simplified the individual service guide and routed the main guide to the minimal per-service guides. (b53590b, f8c3c54)

## PgDog port fix
- Kept the PgDog port internal instead of publishing it to the host. (ad50a9f)

---

# Commit Evidence

Source: git log on `main`, commits authored by markvalenzuela-mmdc on 2026-08-01, chronological order.
Repository: `$HOME/Documents/Programming/mihc` (read-only reference)

## Independent service stacks

- `32daef2` feat(deploy): add independent service stacks — Adds separate Compose stacks per service so each can be deployed and rolled back on its own.
- `f38614c` docs(deploy): document independent production stacks — Documents the independent production stacks for operators.

## Stack lifecycle / just commands

- `283abe3` build(deploy): order independent stack lifecycle — Orders the stack lifecycle so services start and stop in the correct sequence.
- `b2e09e1` docs(deploy): add rollback and reset commands — Documents rollback and reset commands per stack.

## Deployment docs simplification

- `b53590b` docs(deploy): simplify individual service guide — Slims each per-service guide to the minimal steps needed to deploy.
- `f8c3c54` docs(deploy): route to minimal service guide — Routes the main deployment doc to the per-service minimal guides.

## PgDog port fix

- `ad50a9f` fix(deploy): keep pgdog port internal — Keeps the PgDog port internal to the Docker network instead of exposing it on the host.
