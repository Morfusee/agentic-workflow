# Markdown Docs Platform Implementation Plan

**Goal:** Build a shareable documentation platform that stores markdown in Postgres, supports human and MCP-driven draft/publish workflows, and serves public docs pages with stable canonical URLs.

**Architecture:** Use a single Next.js application with App Router. Store canonical content in Postgres via Drizzle. Keep mutable drafts on the document record, create immutable published revisions, render public pages from published markdown through a shared markdown pipeline, and expose authenticated MCP endpoints with scoped collection permissions.

**Tech Stack:** Next.js 15, TypeScript, Postgres, Drizzle, Auth.js, `remark`, `rehype`, GitHub Flavored Markdown.

---

## Decisions Locked

- Single-tenant application.
- Database-only canonical content.
- Draft and publish workflow.
- Humans and MCP clients can publish.
- MCP permissions are role plus collection/path scoped.
- Collections are human-created only.
- Slugs are generated from collection path and title unless frontmatter overrides them.
- Frontmatter is optional.
- Title falls back to first H1, then filename/import name.
- Published revisions are immutable.
- Draft state is mutable.
- Canonical doc URL shows latest published revision.
- Optional published revision URLs are public.
- Drafts are private.
- GFM is the supported markdown baseline.
- Remote images and embeds are allowed by reference only; uploads are not stored.
- Remote assets warn on save and block on publish when invalid.
- Public pages use the current renderer/theme with ISR-style caching and revalidation.
- Public exports include original markdown and rendered HTML for published revisions only.
- Search, scheduled publishing, PDF, and versioned docs are out of scope for v1.

---

## Phase 1: Foundation

**Outcome:** A working app skeleton with auth, database connectivity, and clear route separation between public docs and authenticated authoring.

### Work

- Create the Next.js app structure with App Router and route groups for public docs and authenticated app pages.
- Add Postgres and Drizzle configuration.
- Add Auth.js with multi-provider OAuth support.
- Add a minimal protected app shell and public docs shell.
- Establish environment variable contracts for auth, database, cache revalidation, and MCP token minting.

### Verify

- Local startup succeeds with auth and database configured.
- Protected routes require login.
- Public routes render without auth.
- Drizzle migrations apply cleanly.

---

## Phase 2: Core Data Model

**Outcome:** Collections, documents, published revisions, MCP clients, scopes, and audit logging exist in the schema with service-layer access.

### Work

- Implement Drizzle tables for collections, documents, document revisions, MCP clients, scopes, tokens, roles, and audit log.
- Seed initial roles and one admin user flow.
- Add service/repository modules for collections and documents.
- Define soft-delete semantics and slug uniqueness rules.

### Verify

- Collections can be created and listed.
- Documents can be created in a collection.
- Draft state is persisted on the document record.
- Published revisions can be inserted and linked.
- Audit rows can be written and queried.

---

## Phase 3: Authoring And Import

**Outcome:** Human users can create drafts, paste markdown, import markdown from URLs, and manage doc metadata within collections.

### Work

- Build collection management UI for human admins/editors.
- Build draft creation and editing UI.
- Support paste/import of raw markdown.
- Support human URL-based import.
- Parse optional frontmatter.
- Derive title, summary, and slug defaults.
- Support explicit document ordering with fallback to title.

### Verify

- Human can create and update a draft.
- Frontmatter-free markdown still produces title and slug.
- Imported markdown lands in the correct collection.
- MCP clients cannot create collections.

---

## Phase 4: Rendering And Validation

**Outcome:** Draft preview and public rendering share the same markdown pipeline, and validation reliably separates warnings from publish-blocking failures.

### Work

- Add a shared GFM renderer based on `remark` and `rehype`.
- Detect and reject raw HTML, inline scripts, and forbidden embed forms.
- Extract remote asset references from markdown.
- Validate remote assets with `HEAD` first and `GET` fallback.
- Enforce remote asset status, content-type, and size limits.
- Save warnings for draft validation results.
- Build manual preview using the same render pipeline as publish.

### Verify

- Preview output matches published render path.
- Disallowed constructs are blocked.
- Invalid remote assets warn on draft validation.
- The same invalid assets block publish.

---

## Phase 5: Publish Lifecycle

**Outcome:** Documents can be published, unpublished, deleted, restored, and shared through canonical and revision URLs.

### Work

- Implement publish service that creates immutable published revisions.
- Track latest published revision on the document.
- Serve canonical public doc routes.
- Serve public published revision routes.
- Add unpublish flow.
- Add soft delete and restore flow.
- Add tombstone pages for unpublished and deleted docs.
- Add published-only markdown export.
- Add published-only rendered HTML export.

### Verify

- Publish creates a revision and updates the live doc route.
- Canonical URL serves the latest published revision.
- Revision URL serves the requested published revision.
- Unpublish and delete stop live content from rendering.
- Tombstone pages render consistently.
- Markdown and HTML exports map to the published revision.

---

## Phase 6: MCP Integration

**Outcome:** MCP clients can authenticate with short-lived tokens and act only within allowed collection scopes.

### Work

- Implement MCP client registry and scope assignment.
- Support config-defined trusted clients plus UI-defined clients.
- Implement short-lived token minting and validation.
- Expose workflow-first endpoints for create/update/validate/publish.
- Add optional low-level endpoints only after the workflow path exists.
- Restrict MCP remote markdown import to allowlisted hosts.
- Record all MCP actions in the audit log.

### Verify

- Scoped client can create drafts only within allowed collections.
- Scoped publisher can publish only within allowed collections.
- Out-of-scope requests fail with clear authorization errors.
- MCP auth and content actions are audited.

---

## Phase 7: Caching, Revalidation, And Hardening

**Outcome:** Public docs are fast and consistent, and renderer/theme deploys refresh the whole published site.

### Work

- Add ISR or equivalent cached rendering for public docs pages.
- Revalidate on publish, unpublish, delete, and restore where needed.
- Add whole-site invalidation for renderer/theme deploys.
- Add test coverage for auth, permissions, rendering, validation, lifecycle, and public routes.

### Verify

- Published content updates after publish.
- Unpublished/deleted content no longer serves live page content.
- Theme/renderer deploys refresh all published pages.
- Critical workflows are covered by automated tests.

---

## Risks And Intentional Tradeoffs

- Published pages re-render under the current renderer/theme instead of a stored historical renderer version. Visual output can drift after future theme changes.
- Remote asset availability is outside system control; publish validation reduces but does not eliminate later broken assets.
- DB-only canonical content keeps the system simpler for v1, but export and backup quality matter more because there is no file mirror.

---

## First Milestone Recommendation

Ship through Phase 5 first.

That yields:

- Authenticated authoring
- Collections
- Draft editing
- Validation
- Preview
- Publish/unpublish/delete/restore
- Public canonical docs pages
- Revision URLs
- Markdown and HTML export

Delay MCP integration until the human workflow is stable end-to-end.
