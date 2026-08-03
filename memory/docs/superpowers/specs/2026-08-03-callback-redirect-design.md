# Design: Post-Login Callback Redirect (PROJ-161)

Date: 2026-08-03
Status: Approved for implementation
Ticket: Coding Projects Tracker PROJ-161 — "Redirect users to the protected page they originally tried to access after login"
Repo: markdown2share (nextjs package)

## Problem

An unauthenticated user visiting a protected route (anything under `/app`) is
redirected to `/login`, and after signing in always lands on `/app` — the
intended destination is lost. The same applies to sign-up and GitHub OAuth
entry points.

## Goal

Preserve the originally requested protected route across the login flow:

- Unauthenticated visit to a protected route → `/login?callbackURL=<encoded path>`
- After email sign-in, GitHub sign-in, or sign-up → land back on that exact route
- No `callbackURL` present → keep today's default landing on `/app`
- No open-redirect hole: external, protocol-relative, or scheme-bearing
  `callbackURL` values are rejected and fall back to `/app`

## Architecture

A single pure helper module is the one source of truth for building and
validating callback URLs. All entry points call it; no duplicated
redirect-building logic anywhere.

```
URL path ──proxy.ts──► requireCurrentUser() ──► /login?callbackURL=<path>
                                │
                     login / signup / GitHub ──► validate via helper ──► authClient.signIn(..., { callbackURL })
```

The URL is the source of truth. No cookies, session, or client state carry the
intended destination. Better Auth's native `callbackURL` parameter handles the
server-side post-auth redirect.

## Components

### `features/auth/login-redirect.util.ts` (new)

Pure, exported helpers (unit-testable without browser/server machinery):

- `isSafeCallbackPath(value: string): boolean` — internal-path validation.
- `getSafeCallbackPath(value: string | null | undefined): string | null` —
  returns the validated path, or `null` when absent/invalid.
- `buildLoginUrl(pathname: string): string` — returns
  `/login?callbackURL=${encodeURIComponent(pathname)}`.

Default landing constant: `/app`.

Validation rules (identical at every entry point):

- Must start with `/`
- Must not start with `//` (protocol-relative)
- Must not contain a `:` scheme prefix (`http://`, `https://`, `javascript:`, ...)

Anything else → fall back to `/app`.

### `proxy.ts` (modified)

- Unauthenticated request to `/app/*` → redirect to `buildLoginUrl(pathname)`.
  Preserve the query string (`request.nextUrl.search`).
- Stamp the current path on the request as an `x-pathname` header on
  pass-through requests, so the server-component guard can rebuild the same
  callback URL for anything the proxy matcher misses.
- Signed-in visit to `/login` or `/signup` → redirect to `/app` (unchanged
  behavior; `redirectAuthenticatedUser()` semantics preserved).

### `features/auth/auth-guards.ts` (modified)

- `requireCurrentUser()`: read `x-pathname` from `headers()`. When present and
  valid, redirect to `buildLoginUrl(pathname)` instead of bare `/login`. When
  absent, redirect to bare `/login` (safe fallback).
- `redirectAuthenticatedUser()`: unchanged (signed-in `/login`/`/signup`
  visitors still land on `/app`).

### `app/(public)/login/page.tsx` (modified)

- Read `callbackURL` with `useSearchParams()`.
- Resolve via `getSafeCallbackPath()` (fallback `/app`).
- Pass the resolved value to `authClient.signIn.email({ callbackURL })`.
- Pass the resolved value to `<GitHubSignIn callbackURL={...} />`.

### `components/auth/github-sign-in.tsx` (modified)

- Accept a `callbackURL` prop (default `/app`), pass to
  `authClient.signIn.social({ provider: "github", callbackURL })`.

### `app/(public)/signup/page.tsx` (modified)

- Read `callbackURL` with `useSearchParams()`, resolve via `getSafeCallbackPath()`.
- Pass to `authClient.signUp.email({ callbackURL })` and
  `router.replace(callbackURL)`.

## Error Handling

- Invalid/absent callback → `/app` fallback at every entry point (helper
  enforces this uniformly).
- Open redirects: prevented by validation in the shared helper, applied at
  guard, proxy, login, signup, and GitHub. Better Auth's own normalization is
  defense in depth, not the primary check.
- Guard without `x-pathname` header → bare `/login` (never crashes).

## Testing

### Unit — `__tests__/unit/features/auth/login-redirect.util.test.ts`

- Validation: accepts `/app/md/<id>`, `/app/...`; rejects `https://evil.example`,
  `//evil.example`, protocol-relative values, `javascript:...`.
- `buildLoginUrl` encodes the path and defaults to `/app` when no valid value.
- `getSafeCallbackPath` returns `null` for absent/invalid input.

### Integration — `__tests__/integration/auth/auth-guards.test.ts`

Real Better Auth session against the existing test-DB harness; mock
`next/headers` and `next/navigation`:

- `requireCurrentUser()` resolves a user with a valid session.
- Without a session it throws the catchable `NEXT_REDIRECT` with the callback
  URL in the redirect target.
- `redirectAuthenticatedUser()` redirects when a session exists.

### E2E — `__tests__/e2e/login.spec.ts` (extended)

- Sign out, visit a protected route (e.g. a document under `/app/md/...`),
  assert the login URL carries `callbackURL`.
- After email sign-in, assert return to the exact route.
- Same for GitHub OAuth.
- `/login?callbackURL=https://evil.example` falls back to `/app`.
- Update existing "redirects to /app on successful login" assertions to the
  new expected behavior (plain `/login` still lands on `/app`).

Checks: `pnpm lint`, `pnpm typecheck` before handoff.

## Scope / Non-Goals

- No tRPC, Better Auth config, or DB changes.
- `redirectAuthenticatedUser()` semantics unchanged.
- No cookies, session, or client state for the callback.
- The protected route's query string is preserved by the proxy; the login
  callback itself carries only the path (search params of the destination
  route are not re-attached after login — out of scope unless explicitly
  requested).

## Files

| File | Change |
| --- | --- |
| `nextjs/features/auth/login-redirect.util.ts` | new — pure helpers |
| `nextjs/proxy.ts` | callback URL redirect + `x-pathname` header |
| `nextjs/features/auth/auth-guards.ts` | header-aware redirect |
| `nextjs/app/(public)/login/page.tsx` | propagate callback |
| `nextjs/app/(public)/signup/page.tsx` | propagate callback |
| `nextjs/components/auth/github-sign-in.tsx` | `callbackURL` prop |
| `nextjs/__tests__/unit/features/auth/login-redirect.util.test.ts` | new |
| `nextjs/__tests__/integration/auth/auth-guards.test.ts` | new |
| `nextjs/__tests__/e2e/login.spec.ts` | extended |

## Branch

`feat/proj-161-callback-redirect` off `main`.
