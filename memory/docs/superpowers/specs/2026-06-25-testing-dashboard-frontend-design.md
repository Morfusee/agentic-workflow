# Testing Dashboard Frontend Design

Date: 2026-06-25
Repo: `$HOME/Documents/Programming/mihc`
App: `nextjs`

## Goal

Create a frontend-only dark-mode dashboard for Mapua Malayan Digital College maintainers and developers to inspect smoke-test health, invoke manual smoke tests, and run mock e2e scenarios against user profiles.

The initial implementation must stay simple, reuse existing UI components, and keep mock data easy to remove when real APIs arrive.

## Scope

Build three navigable sidebar pages:

- Smoke Testing
- e2e Testing
- Settings

The implementation is frontend-only. Manual runs, filters, status changes, and scenario progress are local UI behavior backed by mock data.

## Existing Project Context

The app is a small Next.js App Router project under `nextjs/`.

Existing reusable UI components include sidebar, cards, buttons, badges, tables, sheets, drawers, dialogs, switches, checkboxes, toggles, selects, tabs, separators, and tooltips. The dashboard should use those components instead of recreating primitives.

The repo's `nextjs/AGENTS.md` requires consulting the bundled Next.js docs before implementation because the installed Next version may differ from older conventions. The relevant App Router docs confirm route folders, page files, layouts, and query-string navigation are appropriate for this implementation.

## Architecture

Use a shared app shell and page-local feature components.

- Root layout sets up the dark-first app surface.
- A dashboard shell wraps route pages with the existing sidebar component.
- Sidebar items link to `/smoke-testing`, `/e2e-testing`, and `/settings`.
- `/` should send users to Smoke Testing or provide a minimal redirect-style entry point.
- Feature data lives in one clearly named mock data module, such as `nextjs/lib/mock-testing-data.ts`.
- Feature UI can live in route-local private folders or small shared dashboard components, keeping files focused and easy to delete or replace later.

This avoids a heavy feature-folder structure while still keeping mock data and page behavior separated from the UI primitives.

## Smoke Testing Page

The Smoke Testing page is a maintainer-focused status and manual-run dashboard inspired by Uptime Kuma and public status pages, but optimized for developers who need to run checks and inspect historical runs.

Apps shown:

- Website
- Enrollmate
- Enrollmate CLP
- Self-hosted n8n instance

Each app appears as a status card showing:

- App name
- Current status
- Uptime percentage
- Last check time
- Last run result
- A compact recent-run indicator

Clicking an app selects it and reveals a history table for that app. The table includes previous smoke-test runs, result, trigger type, duration, timestamp, and short failure detail when applicable.

Controls above the history table:

- Result filter: all, success, failure
- Manual run button for the selected app

The manual run button should simulate creating or starting a smoke-test run in local state. It does not need real async execution or backend calls in this phase.

## e2e Testing Page

The e2e Testing page centers on a table of student/user profiles.

Clicking a profile updates the route to:

`/e2e-testing?profile=<profile-id>`

When `profile=` is present, a responsive Notion-like side panel opens. Closing the panel removes the query parameter and returns to the table-only view.

The profile panel contains:

- Selected profile details
- Scenario selection with Stage 1, Stage 2, Stage 3, and Stage 4
- Multi-select toggles or checkboxes for scenarios
- Two run controls: automated and manual
- GitHub Actions-like run details showing stage status, timestamps or durations, and log-style notes

Automated mode can mark selected stages as running or complete in local state. Manual mode advances through the selected stages one click at a time so the same manual button can be used again when the next stage is ready.

## Settings Page

Settings stays intentionally small for this frontend-only phase.

It should include only a minimal settings surface, such as:

- A default environment display or selector
- A disabled default runner mode control marked as mock-only
- A short integration status summary

No backend configuration, authentication, notification rules, or real environment management should be invented yet.

## Data Model

Mock data should be typed and centralized so it can be deleted or replaced by API calls later.

Suggested mock entities:

- `smokeApps`
- `smokeRuns`
- `profiles`
- `scenarios`
- `profileRuns`

The UI should read from these structures rather than scattering inline arrays throughout page components.

## Interaction Rules

- Sidebar navigation must use real routes.
- Smoke app selection can be local page state.
- Smoke test filtering can be local page state.
- e2e profile panel state must be route-tied through `profile=`.
- e2e scenario selection and run progress can be local state.
- The implementation should not persist data between reloads.

## Visual Direction

Use a dark-first operational dashboard style:

- Dense but readable layouts
- Small, clear headings
- Status badges and compact metadata
- Existing shadcn-style UI primitives
- Restrained color, with status colors used for meaning

Avoid a marketing page, oversized hero sections, decorative cards, or broad ornamental gradients.

## Verification

Before completion, verify:

- The three sidebar routes render and navigate correctly.
- Smoke Testing shows four app status cards.
- Clicking each app updates the visible history table.
- Smoke Testing filters success and failure runs.
- Manual smoke run UI behavior works locally.
- e2e Testing shows a profiles table.
- Clicking a profile opens the side panel and sets `profile=`.
- Closing the panel removes `profile=`.
- Scenario multi-selection works.
- Automated and manual run controls update mock run details.
- Settings renders a minimal KISS page.
- Existing user-owned changes remain preserved.

## Out Of Scope

- Backend APIs
- Real smoke-test execution
- Real Playwright execution
- Authentication and authorization
- Persistent storage
- Notifications
- Theming beyond a dark-first presentation
- Complex settings management
