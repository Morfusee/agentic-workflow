# Handoff: Storybook PR Preview Tickets

## Next Session Focus

Create tickets for changing the ephemeral PR preview containers to serve Storybook instead of the full Next.js + Payload CMS app.

The feasibility was assessed: yes, it's doable. The next agent should create tickets to break this work down and implement (or delegate implementation).

## Context

The website repo (`C:\Users\mrqvp\Documents\Programming\website`, branch `feat/v3-redesign`) has a PR preview workflow at `.github/workflows/cms-dev.yml` that:

1. Builds Next.js (`pnpm build`)
2. Builds Storybook (`pnpm build:storybook`)
3. Pushes a Docker image containing both to `mmdctech/website:pr-<number>`
4. Deploys as a Coolify app that runs `node server.js` with Infisical secrets + MongoDB Atlas access

The proposal is to change the preview to serve only Storybook, which would eliminate the Infisical/Next.js/MongoDB dependency chain and speed up builds significantly.

## Key Files

- **CI workflow:** `.github/workflows/cms-dev.yml` — PR preview build/deploy/cleanup
- **Dockerfile:** `Dockerfile` — builds the image (copies `build/standalone` + `build/static` + `public/storybook`)
- **Entrypoint:** `scripts/start.sh` — logs into Infisical, runs `node server.js`
- **Docker compose:** `docker-compose.yml` — local dev only, not related to previews
- **Storybook config:** `.storybook/main.ts`, `.storybook/preview.ts` — standard Storybook for Next.js + Vite
- **Prod workflow:** `.github/workflows/cms-prod.yml` — deploys via Coolify webhook (not affected by this change)

## Feasibility Summary

**What would change for the preview flow:**

| Aspect | Current | Storybook-only |
|---|---|---|
| Build steps | `pnpm build` + `pnpm build:storybook` | `pnpm build:storybook` only |
| Build time | ~2-3 min | ~30-60s |
| Image content | Next.js server + Storybook static | Storybook static only |
| Container CMD | `start.sh` → `node server.js` | Static file server (e.g. `npx serve` or nginx) |
| Infisical needed | Yes (secrets for Next.js) | No |
| MongoDB needed | Yes (Atlas access list) | No |

**Two approaches:**

1. **New Dockerfile** (`Dockerfile.storybook`): Simple nginx-based image, only needs `public/storybook`. Cleanest separation. The CI workflow would use `docker/build-push-action` with `file: Dockerfile.storybook`.

2. **Reuse existing Dockerfile** with a different entrypoint: More complex, requires conditional build artifacts or workarounds.

## What Next Agent Should Do

### 1. Load Skills
- `$ticket-drafter` / `$ticket-prd-planner`: for creating the tickets
- Optionally `$workflow-orchestrator` if tickets should be pushed to Linear

### 2. Create Tickets

Suggested breakdown (agent should use judgment):

**Ticket A: "Add Storybook-only Dockerfile for PR previews"**
- Create `Dockerfile.storybook` using nginx:alpine or node-slim + `npx serve`
- Single COPY of `public/storybook` into the image
- Expose port 80 (or 3000 to match existing Coolify config)

**Ticket B: "Update PR preview CI to use Storybook-only image"**
- In `cms-dev.yml`, add conditional logic or a separate workflow variant
- Skip `pnpm build`, `.next` copy, and AtlasCLI steps
- Use `Dockerfile.storybook` for the image build
- No Infisical env vars needed on the Coolify app
- Update the Coolify app ports_exposes from 3000 to match the new image (80 if nginx)
- Update PR comment to say "Storybook preview deployed at: URL"

**Ticket C: "Clean up PR preview Coolify env vars and config"**
- For new PR previews, skip setting INFISICAL_CLIENT_ID/INFISICAL_CLIENT_SECRET/INFISICAL_PROJECT_ID
- No changes needed to existing previews (they already have these; harmless)
- Ensure cleanup job still works

### 3. Sensitive Info to Redact
- `COOLIFY_API_TOKEN`, `INFISICAL_CLIENT_SECRET`, `DOCKER_HUB_PAT` — credentials referenced in CI
- `mmdctech` Docker Hub credentials
- `configs.mmdc.com.ph` / `cms.mmdc.com.ph` — internal infrastructure domains
- MongoDB Atlas project details

## Suggested Skills

- `$ticket-drafter`: Draft profile-aware technical tickets for the three work items listed above. Covers classification, acceptance criteria, and provider-agnostic handoff metadata.
- `$ticket-prd-planner`: Use if the agent prefers a phased PRD approach before ticket creation, though this work is small enough for direct ticket drafting.
- `$workflow-orchestrator`: Use if tickets should be published to Linear (depends on whether the user requests provider publishing).
- `$writing-plans`: Use before implementing any of the tickets, to structure the implementation order.
- `$skill-orchestrator-go`: Use if delegating multiple ticket drafts or parallel implementation work to subagents.

## Safety Notes

- No secrets or credentials are included in this handoff.
- The production workflow (`cms-prod.yml`) must NOT be altered — this is preview-only.
- Existing PR previews for open PRs should continue to work; the change only affects newly created previews (or redeploys of existing ones).
- Before editing, run `git status` and `git diff` from `C:\Users\mrqvp\Documents\Programming\website` to confirm the working tree is clean and no user-owned changes are present.
- Preserve the existing `feat/v3-redesign` branch — do not switch branches unless the user requests it.
