# MDP-04: Shared Application Shells & Environment Contract

## Ticket

- **Notion:** [MDP-04: Create shared public and authenticated application shells with environment contract documentation](https://app.notion.com/p/37fee6df9a438178a09eea61c256c865)
- **ID:** PROJ-114
- **Priority:** Medium
- **Tags:** Feature

## Design Summary

Extract reusable layout shells for public and authenticated surfaces, plus expand `.env.example` with documented environment variable contracts.

## Components

### PublicShell (`components/layout/public-shell.tsx`)

Server component. Wraps all public routes (`/`, `/docs`, `/login`, `/signup`).

**Provided chrome:**
- Persistent header bar with inline SVG logo (home link), "Docs" nav link, conditional "Authoring" / "Log in" links based on session
- Footer: `© Markdown2Share`, docs link, authoring link
- Children rendered in main content area

**Data:** Fetches session via `getSession()` to determine auth state for header links.

**Migration:**
- Home page (`page.tsx`) removes its inline header markup, wraps content in `<PublicShell>`
- Docs layout (`app/(public)/docs/layout.tsx`) removes `SectionShell`, uses `<PublicShell>`

### AuthenticatedShell (`components/layout/authenticated-shell.tsx`)

Server component. Wraps `app/(auth)/app/*` routes.

**Provided chrome:**
- Sidebar: logo linking to `/app`, workspace nav links (All, Shared, Folders)
- Header: mobile logo, search bar, settings button, user avatar dropdown (name, email, log out form)
- Content area in `<main>` slot
- CSS grid layout: `lg:grid-cols-[17rem_minmax(0,1fr)] lg:grid-rows-[auto_1fr]`

**Data:** Fetches session via `getSession()` for user name, email, avatar.

**Migration:**
- Extracted verbatim from `app/(auth)/app/page.tsx` — page keeps only the `<section>` content area (data table, headings, create button, empty/error states)
- `app/(auth)/app/layout.tsx` wraps children in `<AuthenticatedShell>` after `requireAuthentication()`

### SectionShell — removed

No longer referenced after public routes switch to `PublicShell`.

## Layout Changes

| File | Change |
|---|---|
| `app/layout.tsx` | None |
| `app/page.tsx` | Wrap content in `<PublicShell>`, remove own `<header>` |
| `app/(public)/docs/layout.tsx` | Wrap in `<PublicShell>`, remove `SectionShell` |
| `app/(auth)/app/layout.tsx` | Add `<AuthenticatedShell>` wrapper |

## Environment Contract

Expand `.env.example` with descriptions for all current env vars plus commented-out placeholders for planned vars:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string for Drizzle ORM |
| `BETTER_AUTH_URL` | Application base URL used by BetterAuth |
| `BETTER_AUTH_SECRET` | BetterAuth signing secret (generate via `npx auth secret`) |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `MCP_API_KEY` (placeholder) | MCP server connection key |
| `REVALIDATE_SECRET` (placeholder) | Next.js cache revalidation token |
