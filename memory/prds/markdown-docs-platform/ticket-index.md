# Markdown Docs Platform Ticket Index

## Source Artifacts

- Implementation plan: `$HOME\Documents\Programming\agentic-workflow\memory\prds\markdown-docs-platform\implementation-plan.md`
- Schema outline: `$HOME\Documents\Programming\agentic-workflow\memory\prds\markdown-docs-platform\schema-outline.md`

## Recommended Tracker Shape

- Provider: Unspecified
- Suggested project/epic name: `Markdown Docs Platform`
- Suggested delivery style: phase-based epics with implementation tickets under each phase

## Development Phases

| Phase | Status | Objective | Ticket References |
|---|---|---|---|
| 01 | Proposed | Establish app foundation, auth, database connectivity, and route structure. | MDP-01, MDP-02, MDP-03, MDP-04 |
| 02 | Proposed | Define the core data model for collections, documents, revisions, MCP clients, and audit logging. | MDP-05, MDP-06, MDP-07 |
| 03 | Proposed | Build collection management, draft authoring, import flows, and metadata derivation. | MDP-08, MDP-09, MDP-10, MDP-11, MDP-12 |
| 04 | Proposed | Implement markdown rendering, validation, remote asset policy, and manual preview. | MDP-13, MDP-14, MDP-15, MDP-16, MDP-17, MDP-18 |
| 05 | Proposed | Implement publish lifecycle, public docs routes, tombstones, and exports. | MDP-19, MDP-20, MDP-21, MDP-22, MDP-23, MDP-24, MDP-25, MDP-26, MDP-27 |
| 06 | Proposed | Add MCP client auth, scope enforcement, import restrictions, and workflow endpoints. | MDP-28, MDP-29, MDP-30, MDP-31, MDP-32, MDP-33 |
| 07 | Proposed | Add caching, revalidation, audit visibility, and hardening tests. | MDP-34, MDP-35, MDP-36, MDP-37, MDP-38, MDP-39, MDP-40, MDP-41, MDP-42 |

## Ticket List

### Phase 01 Tickets

- MDP-01: Scaffold Next.js App Router project structure for public docs and authenticated authoring surfaces
- MDP-02: Add Postgres and Drizzle migration workflow for the docs platform
- MDP-03: Integrate BetterAuth with multi-provider OAuth and protected app routing
- MDP-04: Create shared public and authenticated application shells with environment contract documentation

### Phase 02 Tickets

- MDP-05: Define Drizzle schema for collections, documents, document revisions, MCP clients, scopes, and audit log
- MDP-06: Seed base app roles and initial authorization wiring for admin and editor flows
- MDP-07: Build service-layer access patterns for collections, documents, and published revision lookup

### Phase 03 Tickets

- MDP-08: Build human-only collection management flows with nested collection support
- MDP-09: Implement draft document creation and editing inside a collection
- MDP-10: Add markdown paste and direct-edit authoring workflow for human users
- MDP-11: Add human URL-based markdown import flow with title, summary, and slug derivation
- MDP-12: Implement explicit document ordering with fallback to title-based navigation ordering

### Phase 04 Tickets

- MDP-13: Build a shared GFM rendering pipeline for preview and public docs pages
- MDP-14: Reject raw HTML, inline scripts, and forbidden embed constructs in docs content
- MDP-15: Extract remote asset references from markdown and normalize validation targets
- MDP-16: Validate remote assets with HEAD-first GET-fallback reachability checks
- MDP-17: Enforce remote asset content-type and size-limit rules for publish readiness
- MDP-18: Add manual preview flow with saved validation warnings and exact publish-render parity

### Phase 05 Tickets

- MDP-19: Implement publish service that creates immutable document revisions from mutable drafts
- MDP-20: Serve canonical public doc routes from the latest published revision
- MDP-21: Serve public revision-specific routes for published document history
- MDP-22: Implement unpublish flow that removes live content while retaining revision history
- MDP-23: Implement soft delete and restore workflow for documents
- MDP-24: Serve tombstone pages for unpublished and deleted public docs URLs
- MDP-25: Export published revisions as original markdown
- MDP-26: Export published revisions as rendered HTML
- MDP-27: Add lifecycle authorization guards and publish-failure handling for human and MCP actors

### Phase 06 Tickets

- MDP-28: Build MCP client registry with hybrid config-defined and admin-defined provisioning
- MDP-29: Implement short-lived MCP token minting, hashing, validation, and revocation behavior
- MDP-30: Add collection-scoped MCP authorization for draft creation and publishing
- MDP-31: Expose workflow-first MCP endpoints for create draft, update draft, validate draft, and publish document
- MDP-32: Add optional low-level MCP CRUD endpoints after the workflow path is stable
- MDP-33: Restrict MCP remote markdown import to allowlisted hosts and audit all MCP actions

### Phase 07 Tickets

- MDP-34: Add immutable audit logging for document lifecycle, validation, and MCP authentication events
- MDP-35: Build audit log admin views and filters for operational review
- MDP-36: Add ISR or equivalent caching strategy for public docs pages
- MDP-37: Revalidate public docs routes on publish, unpublish, delete, and restore events
- MDP-38: Add whole-site invalidation path for renderer and theme deploys
- MDP-39: Add unit tests for slug derivation, metadata fallback, and content validation behavior
- MDP-40: Add integration tests for publish, unpublish, delete, restore, and export workflows
- MDP-41: Add authorization and scope tests for MCP clients and authenticated app roles
- MDP-42: Add end-to-end verification for draft, preview, publish, and public-read happy paths

## Recommended First Milestone

Prioritize MDP-01 through MDP-20.

That milestone yields:

- authenticated authoring
- collection management
- draft editing
- validation
- preview
- publish
- public canonical docs pages

Leave revision routes, exports, and MCP integration for the next milestone if schedule pressure appears.
