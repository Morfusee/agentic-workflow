# Ticket Dump

Generated: 2026-06-15 20:08 PHT
Requested range: 2026-06-15
Dump file date: 2026-06-15

---

# Stand-up Script

Yesterday, I worked on setting up the Storybook PR preview for the component showcase. I simplified the CI pipeline by creating a Dockerfile.storybook and updating the cms-dev.yml workflow to build and deploy only Storybook instead of the full Next.js + Payload CMS stack. I also cleaned up the Storybook sidebar to show only redesign components by hiding non-redesign story categories. The task is complete and sitting in a PR as a preview-only branch.

Today, I just plan on tackling any tickets that come my way.

No major blockers right now.

---

# Selected Tasks

- [86d3btbp4]: Set up Storybook PR preview for component showcase
  - Status: complete
  - Activity date: 2026-06-15
  - URL: https://app.clickup.com/t/86d3btbp4
  - Reference: `# All Scraped Tasks` -> `## 86d3btbp4: Set up Storybook PR preview for component showcase`
  - Stand-up relevance: Main work item completed today — built the CI pipeline for Storybook-only PR previews and cleaned up the Storybook sidebar.

---

# Unselected Tasks

Carry-over tasks not yet included in a stand-up. These reappear as selectable items in future stand-up prompts.

No unselected tasks.

---

# Manual Tasks

No manual tasks added.

---

# Grouped Summary

2026-06-15

## complete
- 86d3btbp4: Set up Storybook PR preview for component showcase

---

# All Scraped Tasks

## 86d3btbp4: Set up Storybook PR preview for component showcase

Status: complete
Activity date: 2026-06-15
URL: https://app.clickup.com/t/86d3btbp4
Initial dev assignee: Mark Rolis Valenzuela
Testing actors: None identified
My role for this task: dev-owner

### Why this task was included
Created by me, status changed by me, commented on by me

### Description
Replace the full Next.js + Payload CMS PR preview with a lightweight Storybook-only preview. Newly created atoms, molecules, and organisms will be viewable via Storybook without building a custom showcase page, and without needing Infisical secrets or MongoDB access.

**Scope**
* Create `Dockerfile.storybook` — nginx-based image, single COPY of `public/storybook`, expose port 80
* Update `.github/workflows/cms-dev.yml` to use the Storybook Dockerfile for PR preview builds
* Skip `pnpm build`, `.next` copy, and AtlasCLI steps — only run `pnpm build:storybook`
* Update PR comment to say "Storybook preview deployed at: URL"

**Deliverable**
- Dockerfile.storybook exists and builds a static Storybook image
- PR preview workflow builds and deploys Storybook-only (no Next.js, no Infisical, no MongoDB)
- Preview URL serves Storybook with all atoms, molecules, and organisms visible
- Existing prod workflow (cms-prod.yml) is untouched
- Existing open PR previews continue working

### Comments

#### Mark Rolis Valenzuela - 2026-06-15 06:54
All requirements for this ticket are already implemented and committed.

Branch: feat/preview-v3-redesign
What changed:

Added Dockerfile.storybook as an nginx-based static image that copies public/storybook and exposes port 80.
Updated .github/workflows/cms-dev.yml to build only Storybook, use Dockerfile.storybook, and remove the Next.js, .next, and AtlasCLI preview build steps.
Updated the preview deployment flow to set Coolify preview apps to port 80, stop injecting preview Infisical app env vars, and post Storybook preview deployed at: ... in the PR comment.

Notes:
Local verification completed with a Storybook build to a temporary output directory. Docker image build could not be verified in this environment because Docker Desktop is not available.

Required action/s:
Review the workflow and Docker changes on feat/preview-v3-redesign.
Trigger a preview deployment on an open PR and confirm the Storybook URL serves the component library, including existing PR previews redeployed through the updated port configuration.

#### Mark Rolis Valenzuela - 2026-06-15 08:28
Changes on feat/preview-v3-redesign branch
---
1. CI: Storybook-only PR preview deployment
Simplified cms-dev.yml workflow to build and deploy only Storybook (no Next.js build, no Infisical secrets, no MongoDB Atlas DB access)
Added Dockerfile.storybook — nginx:1.29-alpine serving static Storybook output on port 80
Coolify app port changed from 3000 to 80
PR comment now says "Storybook preview deployed at:" instead of generic deployment message

2. Storybook sidebar: show only redesign components
Hidden non-redesign story categories by adding tags: ['!dev'] to meta objects (Storybook excludes tagged stories from the sidebar)
Hidden categories: Component (4), Layout (8), Cards (5), Widgets (3), Custom (1), blocks (2) — 23 stories total
Visible categories: Atoms (11), Molecules (5), Organisms (2) — only those with Website Redesign tickets.

#### Mark Rolis Valenzuela - 2026-06-15 08:32
All Hero redesign tickets have been merged onto feat/v3-redesign:

86d36z2p0 — Implement Hero redesign variants as reusable components → moved to complete
86d36xrtt — Hero Section (Desktop and Mobile) → moved to complete

### Activity Timeline
- 2026-06-15 06:35 created: Task created by Mark Rolis Valenzuela
- 2026-06-15 06:54 commented: Implementation completed and documented on feat/preview-v3-redesign
- 2026-06-15 08:28 commented: Changes summary including Dockerfile.storybook and Storybook sidebar cleanup
- 2026-06-15 08:30 closed: Status changed to complete
- 2026-06-15 08:32 commented: Hero redesign tickets merge confirmation

### In-Range Day Mapping
- 2026-06-15: Task created (06:35), Commented on implementation (06:54), Commented on changes (08:28), Status changed to complete (08:30), Commented on Hero merge (08:32)

### Activity Notes
Mark created the task, implemented the Storybook-only PR preview pipeline (Dockerfile.storybook, cms-dev.yml updates, port configuration), cleaned up the Storybook sidebar to show only redesign components, and closed the task as complete. Multiple detailed comments document the implementation.
