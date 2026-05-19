---
date: 2026-05-20
type: research
tags: [code-review, location-frontend, react, nextjs, iframe, graphql, tailwind, p1-p2, refactoring]
related: []
---

# Location Frontend — Code Review Findings

**Date:** 2026-05-20
**Repo:** `location-frontend`
**Stack:** Next.js 16, React 19, Apollo Client, Tailwind v4, pnpm

## P1/P2 Issues Found

### P2 — Embedded Auth Expiry Can Drop in Production

- `src/lib/apollo.ts:29-33` posts `AUTH_EXPIRED` to `window.parent` with `targetOrigin="*"`.
- `src/components/common/IframeAuthListener.tsx:15-24` only accepts same-origin messages in production.
- Iframe embeds load cross-origin URLs (finance, partner, auth, support, etc.) configured in `src/app/layout.tsx:37-47`.
- `src/app/(embed)/layout.tsx:19-24` also posts height messages with `*`.
- **Result:** Auth expiry silently fails to log out the parent in production embedded flows.

### P2 — GraphQL Proxy Duplication & CSRF Gap

- Three identical proxies: `src/app/graphql/route.ts`, `src/app/partner/graphql/route.ts`, `src/app/finance/graphql/route.ts`.
- Multipart requests bypass the only explicit preflight guard (`apollo-require-preflight` check skipped for `multipart/*`).
- `process.env.INTERNAL_*_URL!` has no runtime guard — fails late with no clear error.
- `src/app/api/auth/refresh/route.ts` has no `Cache-Control: no-store`.

### P2 — Invalid Tailwind Classes

- `ml-[10]` used in:
  - `src/components/common/PageHeader.tsx:7`
  - `src/features/locations/LocationsContent.tsx:538`
  - `src/app/(main)/manage/users/page.tsx:412`
  - `src/features/statements/StatementsContent.tsx:15`
- `max-w-62.5` and `wrap-break-word` in `src/components/ui/Tooltip.tsx:42`.
  - `wrap-break-word` also appears in `src/features/locations/_components/ApplicationReviewModal.tsx:32`.
- These are not valid Tailwind v4 utilities and may not render as intended.

### P2 — Table Accessibility Gap

- `src/components/common/Table.tsx:54-72`: clickable rows use `onClick` only, no `role`, `tabIndex`, or keyboard handlers.
- `col.cell` fallback uses `(row as any)[col.id]` — no type safety.

## Refactoring / DX Opportunities

### High ROI — Shared GraphQL Proxy Helper

- Extract a shared helper from the three route handlers.
- Add env var validation at startup.
- Consider moving the set-cookie copy logic (`getSetCookie()`) into the helper.

### High ROI — Iframe Message Bridge

- Centralize message contract types and origin allowlist.
- Cover both `AUTH_EXPIRED` and `height` messages.
- Replace `*` in `postMessage` with explicit target origins where possible.

### Medium ROI — Page Shell Component

- `Header.tsx` + `TabLinks` form a repeating page layout with the same left-aligned nav, location selector, and tab strips.
- A single shell component would reduce duplication across 10+ page files.

### Medium ROI — SSR Hydration Gate

- `SearchExport.tsx:20-41` and `PageRowsDropdown.tsx:19-37` duplicate the same `isMounted` guard for hydration safety.
- Extract a shared `ClientOnly` wrapper.

### Low ROI (But Clean) — Dead Props

- `TabLinks.tsx:9` declares `navbarHeight` prop but never uses it internally.
- `user.email!` non-null assertion in `Header.tsx:307`.

## Iframe Embed Usage

`IframeEmbed` is used in **19+ page files** and potentially more. The component's loose message handling means any issue there propagates broadly.

Pages using it:
- `src/app/(main)/reporting/transactions/batches/deposits/disputes/page.tsx`
- `src/app/(main)/manage/payments/processors/integrations/page.tsx`
- `src/app/(main)/customer/*/page.tsx`
- `src/app/(main)/catalog/*/page.tsx`
- `src/app/(main)/support/tickets/page.tsx`
- `src/app/(main)/locations/equipments/page.tsx`
- `src/components/common/UserSettingsModal.tsx`

## Worktree State

Unrelated dirty changes preserved:
- `.env` — modified
- `package.json` — modified (HTTPS dev script added)
- `justfile` — untracked (cert generation/HTTPS dev)

## Notes

- No P1 issues found.
- No code changes made during review.
- All findings are from read-only inspection.
