# Handoff: Better Auth Plugin Migration Analysis for markdown2share

**Date:** 2026-06-19
**Previous agent:** deepseek-v4-pro
**Repo:** markdown2share (`$HOME/Documents/Programming/markdown2share`)

---

## What Was Analyzed

The user asked whether markdown2share should use Better Auth's built-in plugins for roles, and requested a broader analysis of plugin coverage for MCPs, audit logs, and other tables.

A full diff of the current schema vs. Better Auth's plugin model was performed. No code was modified.

---

## Key Findings

### 1. Roles — Use `admin()` Instead of Custom Tables

**Current state:**
- `lib/db/schema.ts:261-291` defines custom `roles` and `user_roles` tables with a many-to-many join.
- `features/auth/auth-guards.ts:27-46` has role-check functions (`assertRole`, `requireRole`) fully commented out, expecting a flat `user.role` field — not the join-table model.
- No active code queries or writes to `roles`/`user_roles`.
- `lib/auth/index.ts:24` only registers `username()` and `nextCookies()` plugins.
- `lib/auth-client.ts:6` only registers `inferAdditionalFields`.

**Better Auth `admin()` plugin:**
- Stores `role` as a comma-separated string directly on the `user` table.
- Adds bounded columns: `banned`, `banReason`, `banExpires` on `user`; `impersonatedBy` on `session`.
- Provides built-in server endpoints: `setRole`, `banUser`, `unbanUser`, `impersonateUser`, `listUsers`, `removeUser`, `userHasPermission`, etc.
- Client plugin `adminClient()` surfaces `authClient.admin.*` methods.
- No separate `roles`/`user_roles` tables needed.

**Recommendation:** Remove custom `roles`/`user_roles`; use `admin()`.

### 2. MCP — Custom Tables Exist; Better Auth Has `mcp()` (Deprecated) and OAuth Provider

**Current state:**
- Custom tables: `mcp_clients`, `mcp_client_scopes`, `mcp_tokens` at `lib/db/schema.ts:203-259`.
- No code actively using these tables (besides schema/relations/seed).

**Better Auth options:**
- `mcp()` plugin: uses OIDC Provider tables (`oauthApplication`, `oauthAccessToken`, `oauthConsent`). Docs state this plugin will be deprecated in favor of the OAuth Provider plugin.
- OAuth Provider (`@better-auth/oauth-provider`): the recommended forward path for MCP/OAuth support. **Not currently installed** in `package.json`.

**Recommendation:** Do not build further on the custom MCP tables. If MCP/OAuth is a real requirement, install and adopt `@better-auth/oauth-provider`.

### 3. Audit Logs — No Better Auth Plugin Exists

Better Auth 1.6.19 has no dedicated audit-log plugin. Keep the current `audit_log` table as app-owned infrastructure. Wire it via:
- Better Auth `databaseHooks` for user/session/account events.
- Organization hooks (if `organization()` is added later).
- Application-level audit writes for document/collection/MCP actions.

### 4. Schema Mismatch in `account` Table

The current `account` table at `lib/db/schema.ts:77` has a single `expiresAt` column. Better Auth 1.6.19 expects separate `accessTokenExpiresAt` and `refreshTokenExpiresAt`. This should be fixed before adding plugins to avoid migration conflicts.

### 5. Organization Plugin — Only If Needed

Better Auth's `organization()` plugin provides organizations, memberships, teams, invitations, and fine-grained RBAC via `createAccessControl`. It is appropriate if `collections` are intended to become multi-user workspaces. Otherwise, skip it.

---

## Implementation Plan (for the next agent)

### Phase 1: Fix Account Schema
Fix the `account` table to match Better Auth 1.6.19 core schema: replace `expiresAt` with `accessTokenExpiresAt` and `refreshTokenExpiresAt`. Run `drizzle-kit generate` and `drizzle-kit migrate`.

### Phase 2: Adopt `admin()` Plugin

**Server-side (`lib/auth/index.ts`):**
```ts
import { admin } from "better-auth/plugins";

export const auth = betterAuth({
  // ... existing config
  plugins: [
    admin({
      defaultRole: "user",
      adminRoles: ["admin"],
    }),
    username(),
    nextCookies(), // always last
  ],
});
```

**Client-side (`lib/auth-client.ts`):**
```ts
import { adminClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [
    adminClient(),
    inferAdditionalFields<typeof auth>(),
  ],
});
```

**Schema changes:**
- Add `role`, `banned`, `banReason`, `banExpires` to `user` table.
- Add `impersonatedBy` to `session` table.
- Drop `roles` and `user_roles` tables (if no production data to preserve).
- If data exists: backfill `user.role` from `user_roles` first.

**Guard replacement (`features/auth/auth-guards.ts`):**
- Replace commented-out `assertRole`/`requireRole` with implementations that check `session.user.role` (a string or comma-separated string from Better Auth's admin plugin).

**Database migration:**
```bash
pnpm db:generate
pnpm db:migrate
```

### Phase 3: Audit Log Wiring (App-Level)
- Add `databaseHooks` in the auth config to write to `audit_log` on user create/update/delete, session create/delete.
- Add application-level audit writes in relevant services.

### Phase 4: MCP/OAuth (If Needed)
- Install `@better-auth/oauth-provider` (not currently in dependencies).
- Replace custom `mcp_clients`, `mcp_client_scopes`, `mcp_tokens` with the OAuth Provider schema (`oauthApplication`, `oauthAccessToken`, `oauthConsent`).
- Wire MCP session handling per Better Auth docs.

### Phase 5 (Optional): Organization Plugin
- Add `organization()` only if multi-user workspaces are needed.
- Map `collections` concept to organizations if appropriate.

---

## Key Files Referenced

| File | Purpose |
|------|---------|
| `lib/auth/index.ts` | Server-side auth config (plugins declared here) |
| `lib/auth-client.ts` | Client-side auth config |
| `lib/db/schema.ts` | Full Drizzle schema (auth + app tables) |
| `lib/db/migrations/0000_legal_malcolm_colcord.sql` | Current migration |
| `lib/db/seed.ts` | Seed script (uses betterAuth for signUp) |
| `features/auth/auth-guards.ts` | Authentication/authorization guard functions |
| `features/auth/actions/auth.action.ts` | Server actions (getSession, signOut) |
| `features/auth/queries/auth-session.query.ts` | Client session query |
| `app/api/auth/[...all]/route.ts` | Auth handler route |
| `package.json` | Dependencies (better-auth 1.6.19, drizzle-orm 0.45.2) |

---

## Suggested Skills

If using OpenCode, the next agent should invoke these skills:
- **`writing-plans`** — before touching code, to produce a step-by-step migration plan.
- **`backend-dev-guidelines`** — for routes, services, and database access patterns.
- **`brainstorming`** — if any architectural decisions are still unresolved (e.g., whether to use `organization()` or adopt OAuth Provider).
- **`ticket-implementation-flow`** — to execute the phases as tracked work items.

---

## Environment

- **Platform:** win32
- **Shell:** pwsh (PowerShell 7+)
- **Package manager:** pnpm 10.29.2
- **Database:** PostgreSQL (via `postgres` + `drizzle-orm`)
- **Framework:** Next.js 16.2.9, React 19.2.4
- **Better Auth:** 1.6.19 with `@better-auth/drizzle-adapter` 1.6.19

---

## Commands

```bash
# Run dev server
pnpm dev

# Generate Drizzle migration
pnpm db:generate

# Apply migration
pnpm db:migrate

# Seed database
pnpm db:seed

# Lint
pnpm lint
```
