# BetterAuth OAuth Integration — Design Spec

**Date:** 2026-06-14
**Ticket:** MDP-03 / PROJ-113
**Project:** markdown2share

## Overview

Replace the fake cookie-based authentication in markdown2share with BetterAuth — a modern auth library — backed by GitHub OAuth and PostgreSQL (Drizzle ORM). Add middleware-based route protection for all `/app/*` routes.

## Architecture

```
middleware.ts          ← Intercepts /app/*, checks session via BetterAuth
app/api/auth/[...all]/route.ts  ← BetterAuth API handler (sign-in, callback, session)
lib/auth/index.ts      ← BetterAuth server config (Drizzle adapter, GitHub provider)
lib/auth/session.ts    ← DELETED (replaced by BetterAuth)
lib/db/schema.ts       ← + user, session, account tables
lib/db/migrations/     ← New migration
app/login/page.tsx     ← + GitHub sign-in button above existing form
app/(auth)/app/layout.tsx  ← Remove redirect guard (middleware handles it)
```

## Database Tables (BetterAuth Drizzle schema)

| Table | Columns |
|-------|---------|
| `user` | id (uuid PK), name (text), email (text not null unique), emailVerified (boolean), image (text), createdAt, updatedAt |
| `session` | id (uuid PK), expiresAt (timestamp not null), token (text not null unique), ipAddress (text), userAgent (text), userId (uuid FK→user not null), createdAt, updatedAt |
| `account` | id (uuid PK), accountId (text not null), providerId (text not null), userId (uuid FK→user not null), accessToken (text), refreshToken (text), idToken (text), expiresAt (timestamp), scope (text), password (text), createdAt, updatedAt |

## Auth Flow

1. Login page renders a "Sign in with GitHub" button above the existing email/password form (form preserved as-is).
2. Button triggers `auth.signIn.social({ provider: "github", callbackURL: "/app" })` server action.
3. BetterAuth redirects to GitHub OAuth → user authorizes → callback hits `/api/auth/callback/github`.
4. BetterAuth creates/upserts user + account + session in PostgreSQL, sets session cookie.
5. User lands on `/app` — middleware sees valid session, allows through.

## Middleware

- Matches `/app` and all sub-routes.
- Calls BetterAuth's `getSession` on incoming requests to `/app/*`.
- Redirects to `/login` if no valid session.
- Skips auth check on: `/login`, `/api/auth/*`, static/public routes (`/_next/*`, `/favicon.ico`, etc.), and the root `/` route.

## Login Page Layout

```
┌─────────────────────────────┐
│     Sign in to continue     │
│                             │
│  ┌───────────────────────┐  │
│  │ 🔐 Sign in with GitHub│  │  ← NEW: BetterAuth OAuth button
│  └───────────────────────┘  │
│                             │
│     ── or continue with ── │
│                             │
│  [ Email           ]       │  ← Existing form (preserved, not functional yet)
│  [ Password        ]       │
│  [ Sign in          ]      │
└─────────────────────────────┘
```

## Files Touched

| File | Action |
|------|--------|
| `package.json` | Add `better-auth` dependency |
| `lib/auth/index.ts` | **New** — BetterAuth server config (Drizzle adapter, GitHub provider, trustedOrigins) |
| `lib/auth/session.ts` | **Delete** — replaced by BetterAuth helpers |
| `app/api/auth/[...all]/route.ts` | **New** — `toNextJsHandler` from BetterAuth |
| `middleware.ts` | **New** — route protection via `better-auth/middleware` |
| `lib/db/schema.ts` | Add `user`, `session`, `account` tables using BetterAuth's Drizzle schema helpers |
| `lib/db/migrations/0001_*.sql` | **New** — generated via `drizzle-kit generate` |
| `lib/db/index.ts` | Re-export new tables from schema |
| `app/login/page.tsx` | Add GitHub OAuth sign-in button above existing form; add OAuth server action |
| `app/(auth)/app/layout.tsx` | Remove `hasSession()` redirect guard |
| `.env.example` | Add `BETTER_AUTH_URL`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` |

## Environment Variables

```
BETTER_AUTH_URL=http://localhost:3000     # Base URL of the app
GITHUB_CLIENT_ID=                         # From GitHub OAuth App
GITHUB_CLIENT_SECRET=                     # From GitHub OAuth App
```

## Implementation Order

1. Install `better-auth` package
2. Add BetterAuth Drizzle tables to `lib/db/schema.ts`
3. Generate and run migration (`drizzle-kit generate` + `drizzle-kit migrate`)
4. Create `lib/auth/index.ts` with BetterAuth config
5. Create `app/api/auth/[...all]/route.ts`
6. Create `middleware.ts`
7. Update `app/login/page.tsx` with OAuth button + server action
8. Update `app/(auth)/app/layout.tsx` — remove redirect guard
9. Delete `lib/auth/session.ts`
10. Update `.env.example`
11. Verify: `pnpm run build` passes, `pnpm run lint` passes
12. Test manually: GitHub OAuth sign-in, session persistence, protected route redirect

## Verification

- `pnpm run build` — no type errors
- `pnpm run lint` — no lint errors
- OAuth login: sign in with GitHub → redirect to `/app`
- Session persistence: reload `/app` → still authenticated
- Route protection: navigate to `/app` without session → redirected to `/login`
