# Markdown Docs Platform Schema Outline

## Purpose

Define the v1 domain model for a Next.js documentation platform with mutable drafts, immutable published revisions, scoped MCP clients, and immutable audit logging.

## Core Domain Rules

- `documents` own stable identity, slug, collection placement, and mutable draft state.
- `document_revisions` store immutable published snapshots only.
- Canonical public routes resolve to the latest published revision for a document.
- Drafts are private and are not routed publicly.
- Collections are human-managed only.
- Published revisions may be exported as markdown or rendered HTML.
- Remote assets are never stored by the platform.

---

## Tables

### `collections`

- `id` uuid primary key
- `parent_id` uuid nullable references `collections.id`
- `name` text not null
- `slug` text not null
- `description` text nullable
- `display_order` integer not null default `0`
- `created_by_user_id` uuid not null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Constraints:

- Unique on `(parent_id, slug)`

Purpose:

- Represents the human-curated folder/collection tree used for navigation, scope assignment, and document placement.

### `documents`

- `id` uuid primary key
- `collection_id` uuid not null references `collections.id`
- `slug` text not null
- `title` text not null
- `summary` text nullable
- `current_draft_markdown` text not null
- `current_draft_frontmatter_json` jsonb nullable
- `current_draft_warnings_json` jsonb nullable
- `current_draft_updated_by_user_id` uuid nullable
- `current_draft_updated_by_mcp_client_id` uuid nullable
- `current_draft_updated_at` timestamptz not null
- `latest_published_revision_id` uuid nullable references `document_revisions.id`
- `display_order` integer nullable
- `is_deleted` boolean not null default `false`
- `deleted_at` timestamptz nullable
- `deleted_by_user_id` uuid nullable
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Constraints:

- Unique on `(collection_id, slug)`

Purpose:

- Holds the mutable working copy and stable identity for a document.

Notes:

- If later slug reuse after soft delete is desired, convert the uniqueness rule into a partial unique index over non-deleted rows.

### `document_revisions`

- `id` uuid primary key
- `document_id` uuid not null references `documents.id`
- `revision_number` integer not null
- `markdown` text not null
- `frontmatter_json` jsonb nullable
- `title_snapshot` text not null
- `summary_snapshot` text nullable
- `validation_report_json` jsonb nullable
- `published_by_user_id` uuid nullable
- `published_by_mcp_client_id` uuid nullable
- `published_at` timestamptz not null

Constraints:

- Unique on `(document_id, revision_number)`

Purpose:

- Stores immutable published snapshots for history, rollback targets, and public revision routes.

### `roles`

- `id` uuid primary key
- `name` text not null unique
- `created_at` timestamptz not null

Expected values:

- `admin`
- `editor`
- `viewer`

### `user_roles`

- `user_id` uuid not null
- `role_id` uuid not null

Constraints:

- Unique on `(user_id, role_id)`

Purpose:

- Supports app-managed authorization on top of OAuth-based identity.

### `mcp_clients`

- `id` uuid primary key
- `name` text not null
- `slug` text not null unique
- `is_active` boolean not null default `true`
- `provision_source` text not null
- `description` text nullable
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Purpose:

- Represents a known MCP client identity, whether seeded from config or created through the admin UI.

### `mcp_client_scopes`

- `id` uuid primary key
- `mcp_client_id` uuid not null references `mcp_clients.id`
- `collection_id` uuid not null references `collections.id`
- `can_create_draft` boolean not null default `true`
- `can_publish` boolean not null default `false`

Constraints:

- Unique on `(mcp_client_id, collection_id)`

Purpose:

- Defines collection-scoped MCP permissions.

### `mcp_tokens`

- `id` uuid primary key
- `mcp_client_id` uuid not null references `mcp_clients.id`
- `token_hash` text not null
- `expires_at` timestamptz not null
- `created_at` timestamptz not null
- `revoked_at` timestamptz nullable

Purpose:

- Stores hashed short-lived tokens minted by the app for MCP authentication.

### `audit_log`

- `id` uuid primary key
- `actor_type` text not null
- `actor_user_id` uuid nullable
- `actor_mcp_client_id` uuid nullable
- `event_type` text not null
- `entity_type` text not null
- `entity_id` uuid not null
- `metadata_json` jsonb nullable
- `created_at` timestamptz not null

Purpose:

- Records immutable audit events for document lifecycle, auth, and MCP actions.

Suggested `event_type` values:

- `collection.created`
- `document.created`
- `draft.updated`
- `draft.validated`
- `document.published`
- `document.unpublished`
- `document.deleted`
- `document.restored`
- `mcp.token.minted`
- `mcp.auth.failed`

---

## Auth Tables

Use the standard Auth.js adapter tables appropriate for the chosen adapter.

Expected tables usually include:

- `users`
- `accounts`
- `sessions`
- `verification_tokens`

Keep app authorization separate from provider login state.

---

## Derived Behaviors

### Publish

Publishing should:

- run blocking validation
- create a new `document_revisions` row
- increment `revision_number`
- update `documents.latest_published_revision_id`
- refresh document title/summary fields if they are derived from the new published content
- append an audit event

### Unpublish

Unpublishing should:

- clear `documents.latest_published_revision_id`
- retain existing published revision history
- append an audit event

### Delete

Deleting should:

- set `is_deleted = true`
- set deletion metadata
- retain revisions and audit history
- append an audit event

### Restore

Restoring should:

- clear deletion metadata
- leave published history intact
- append an audit event

---

## Validation Data Shape

Recommended warning/error payload structure for draft and publish validation:

```json
{
  "warnings": [
    {
      "code": "remote_asset_unreachable",
      "message": "Remote image did not respond successfully.",
      "location": "line 18",
      "target": "https://example.com/image.png"
    }
  ],
  "errors": []
}
```

Store warnings on `documents.current_draft_warnings_json`.
Store the publish-time report snapshot on `document_revisions.validation_report_json`.

---

## Open Implementation Notes

- Decide whether `summary` is always derived from content or can be user-authored metadata.
- Decide whether document visibility will ever expand beyond public/private draft semantics.
- Decide whether future versioned docs should branch at collection level or document family level.
